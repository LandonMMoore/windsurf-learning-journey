import json
import re
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from loguru import logger

from elasticsearch import Elasticsearch
from src.core.config import configs
from src.core.exceptions import DuplicatedError, NotFoundError, UnauthorizedError
from src.elasticsearch.mappings.index_mappings import (
    PAR_INDEX_MAPPING_LLM,
    PAR_MAPPING,
    R100_INDEX_MAPPING_LLM,
)
from src.mongodb.chat_services import (
    create_chat_message,
    create_eds_chat_history,
    get_chat_messages,
    get_eds_chat_history,
)

# Initialize Elasticsearch client
es = Elasticsearch(
    hosts=[configs.ELASTICSEARCH_URL],
    basic_auth=(configs.ELASTICSEARCH_USERNAME, configs.ELASTICSEARCH_PASSWORD),
    verify_certs=configs.ELASTICSEARCH_VERIFY_CERTS,
    ssl_show_warn=False,
)


def get_available_fields() -> Dict[str, List[str]]:
    """Get available fields from PAR_MAPPING"""
    fields = {
        "text_fields": [],
        "keyword_fields": [],
        "numeric_fields": [],
        "date_fields": [],
        "nested_fields": {},
        "boolean_fields": [],
    }

    def process_properties(props, prefix=""):
        for field_name, field_info in props.items():
            if "properties" in field_info:
                process_properties(field_info["properties"], f"{prefix}{field_name}.")
            else:
                field_type = field_info.get("type", "")
                full_field_name = f"{prefix}{field_name}"

                if field_type == "text":
                    fields["text_fields"].append(full_field_name)
                elif field_type == "keyword":
                    fields["keyword_fields"].append(full_field_name)
                elif field_type in ["integer", "long", "float", "double"]:
                    fields["numeric_fields"].append(full_field_name)
                elif field_type == "date":
                    fields["date_fields"].append(full_field_name)
                elif field_type == "boolean":
                    fields["boolean_fields"].append(full_field_name)
                elif field_type == "nested":
                    fields["nested_fields"][full_field_name] = field_info["properties"]

    if "properties" in PAR_MAPPING["mappings"]:
        process_properties(PAR_MAPPING["mappings"]["properties"])
    return fields


def handle_error_response(error: Exception) -> str:
    """Handle errors and generate a user-friendly response using GPT model"""
    try:
        # Create the model
        model = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=configs.OPENAI_API_KEY,
        )

        # Create error analysis prompt
        error_prompt = f"""Analyze this error and provide a user-friendly response:
        Error: {str(error)}
        
        Guidelines:
        1. Identify the type of error (e.g., connection, query, authentication)
        2. Provide a clear, non-technical explanation
        3. Suggest possible solutions or next steps
        4. Keep the response concise and helpful
        5. Format the response in a structured way:
           - Error Type
           - Explanation
           - Suggested Actions
        6. Do not expose sensitive information
        7. Do not mention technical details about the system
        8. End with a positive note about retrying
        
        Return the response in a clear, structured format."""

        # Get response from model
        response = model.invoke([{"role": "user", "content": error_prompt}])

        # Add a standard footer
        footer = "\n\nWould you like to try your query again?"

        return response.content.strip() + footer
    except Exception:
        # Fallback response if error handling itself fails
        return "I encountered an issue processing your request. Please try again later."


def create_es_query(
    query: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    retry_count: int = 0,
) -> Dict[str, Any]:

    # Create system prompt with field information
    system_prompt = (
        "You are an expert Query Builder system with deep knowledge of PAR (Project Authorization Request) reports and their data schema. Your role is to convert natural language queries into accurate Elasticsearch JSON queries. You fully understand the PAR domain, including relationships between PARs and Projects, field semantics, financial structures, nested elements, and business logic."
        "Context and Key Rules:\n"
        "- Each document represents a single PAR record.\n"
        "- Multiple PARs can belong to the same Project.\n\n"
        "- 'id' refers to PAR ID.\n"
        '- If a user refers to "project 29483" or "difs 29483", treat as **project number**.\n'
        '- If a user says "project id 43388", treat as **project ID**\n'
        '- If a user says "par id", return PAR-level data for that ID.\n'
        '- "Available balance" means: `budget_info.budget_items.current_balance`.\n'
        "Advanced Context Understanding:\n"
        "- If the user asks for a **project overview by tasks**, return project-level data including:\n"
        "- PAR ID, Project Name, Project Manager, Project Status\n"
        "- Fund Source, Expenditures, Total Project Budget, Total Project Expenditures, Total Project Balance\n\n"
        "Advanced Logic:\n"
        "- If the query involves **nested fields that represent budgets or amounts**, such as:\n"
        "  - `budget_info.budget_items.amount`\n"
        "  - `budget_info.budget_items.current_balance`\n"
        "  - `budget_info.task_allocation.amount_allocated`\n"
        "  - or any other nested financial numeric field\n"
        "- Then do **not list each item**; instead:\n"
        "  - Use **nested aggregations** (e.g., `sum`, `avg`, `stats`) to compute totals or summaries\n"
        "  - Use the correct `nested` path when aggregating\n\n"
        f"You have access to and understand the following field types in the index::\n"
        f"{json.dumps(PAR_INDEX_MAPPING_LLM, indent=4).replace('{', '{{').replace('}', '}}')}\n"
        "### PAR Field Definitions:\n"
        "- fhwa_soar_project_no.program_code (keyword)\n"
        "  - synonyms: fund, fund code, funding code\n"
        "  - description: Financial program or fund source.\n"
        "- current_balance (numeric)\n"
        "  - description: Current balance of the project.\n"
        "  - synonyms: balance, current balance, current balance of the project\n"
        "- icrs_rate (float)\n"
        "  - description: ICRS rate of the project.\n"
        "  - synonyms: icrs rate, icrs rate of the project, IDCR rate\n"
        "CRITICAL QUERY GUIDELINES:\n"
        "select proper mapping so use proper path because some field is nested field but not use nested path"
        " If chat history have same user query so use that query not regenrate so\n"
        "1. For count queries (e.g., 'how many', 'total number of'):\n"
        "   - For total PAR count, use a simple match_all query with size: 0\n"
        "   - Use 'track_total_hits: true' for accurate counts\n"
        "   - For simple count queries, use the count API by setting '_count: true'\n"
        "   - Each document represents one PAR, so count queries should count documents\n"
        "2. For list queries (e.g., 'list of', 'show me', 'give me'):\n"
        "   - If query specifies a number (e.g., 'top 5', 'first 10'), use that exact number for size\n"
        "   - If no specific number is mentioned, set size to 20\n"
        "   - Use _source to specify ONLY the fields mentioned in the query\n"
        "   - If specific fields aren't mentioned, include id and relevant fields based on the query context\n"
        "   - Do NOT use track_total_hits\n"
        "   - Do NOT use size: 0\n"
        "3. For aggregations:\n"
        "   - Use 'terms' aggregation for categorical fields\n"
        "   - Use 'stats' or 'sum' for numeric fields\n"
        "   - Use 'date_histogram' for date fields\n"
        "4. For filtering:\n"
        "   - Use 'bool' query with 'must', 'should', 'must_not' clauses\n"
        "   - Use 'term' for exact matches on keyword fields\n"
        "   - Use 'match' with 'fuzziness' for text fields\n"
        "   - Use 'range' for numeric and date comparisons\n"
        "5. For specific data retrieval:\n"
        "   - Use '_source' to specify only required fields\n"
        "   - Use 'size' to limit results\n"
        "6. For sorting:\n"
        "   - Use 'sort' with field names and order\n"
        "   - For nested fields, use this exact syntax:\n"
        '     {"sort": [{"budget_info.task_name.keyword": {"order": "desc", "nested": {"path": "budget_info"}}}]}\n'
        '     {"sort": [{"budget_info.task_name.keyword": {"order": "desc", "nested": {"path": "budget_info"}}}]}\n'
        "   - The nested path must be the parent field of the sorted field\n"
        "   - Always include both the field path and nested context\n"
        "7. For nested fields:\n"
        "   - Always use the full path when referencing nested fields\n"
        "   - For queries on nested fields, use nested query with proper path\n"
        "   - For aggregations on nested fields, use nested aggregation with proper path\n"
        "   - some field is nested field but not use nested path"
        '   - Example nested query: {"nested": {"path": "budget_info", "query": {"bool": {"must": [{"term": {"budget_info.task_name.keyword": "value"}}]}}}}\n\n'
        "   - some field is nested field but not use nested path"
        '   - Example nested query: {"nested": {"path": "budget_info", "query": {"bool": {"must": [{"term": {"budget_info.task_name.keyword": "value"}}]}}}}\n\n'
        "Example queries:\n"
        "1. Total PAR count query:\n"
        '   {"query": {"match_all": {}}, "size": 0, "track_total_hits": true}\n'
        "2. List query for specific fields:\n"
        '   {"_source": ["id", "epar_name", "total_project_budget"], "size": 20, "query": {"range": {"total_project_budget": {"gt": 100000}}}}\n'
        "3. Aggregation query:\n"
        '   {"size": 0, "aggs": {"by_status": {"terms": {"field": "status"}}}}\n'
        "4. Filtered query:\n"
        '   {"query": {"bool": {"must": [{"term": {"status": "active"}}]}}}\n'
        "5. Specific fields:\n"
        '   {"_source": ["id", "epar_name", "status"], "size": 10}\n'
        "6. Nested field sort:\n"
        '   {"sort": [{"budget_info.task_name.keyword": {"order": "desc", "nested": {"path": "budget_info"}}}]}\n\n'
        '   {"sort": [{"budget_info.task_name.keyword": {"order": "desc", "nested": {"path": "budget_info"}}}]}\n\n'
        "## Do\n"
        " - Nest deeply: Use nested for budget_info, then another nested for budget_info.budget_items.\n"
        ' - Inside nested aggs, omit full path: use field: "expenditures" (not "budget_info.budget_items.expenditures").\n'
        " - Always preserve nesting hierarchy. Don't skip intermediate levels.\n"
        " - Use terms only on low-cardinality fields or with size limits (e.g., project_number with size: 100).\n"
        " - Keep aggregation structure clean and hierarchical.\n"
        " - All aggregation blocks correctly closed and comma-separated\n"
        " - No trailing or missing commas that would cause JSON parsing errors\n\n"
        "## Don't\n"
        " - Skip nesting for deeply nested fields (e.g., access budget_items directly under root).\n"
        " - Use full path inside a nested context.\n"
        " - Duplicate same aggregations with different names unless needed.\n"
        "If User Ask overview of Project with some ID then always include PAR ID in the query unless it is specified by the user that they want group by some field like project manager, budget analysis, etc."
        "I am providing some example Query for you to get some reference and quality of the query:"
        """
            -1. Example User Prompt: Give an overview of project 100497 by task
            - Example Query:
           {
            "size": 100,
            "query": {
              "match": {
                "project_number": "100497"
              }
            }
        """
        """ - 2. Example User Prompt: Can I have a list of all project with negative balance for on fund Y230 and L24E?
            - Example Query: 
            {
              "size": 0,
              "query": {
                "terms": {
                  "fhwa_soar_project_no.program_code.keyword": ["Y230", "L24E"]
                }
              },
              "aggs": {
                "by_project_number": {
                  "terms": {
                    "field": "project_number",
                    "size": 1000
                  },
                  "aggs": {
                    "nested_budget_items": {
                      "nested": {
                        "path": "budget_info.budget_items"
                      },
                      "aggs": {
                        "total_current_balance": {
                          "sum": {
                            "field": "budget_info.budget_items.current_balance"
                          }
                        }
                      }
                    },
                    "project_info": {
                      "top_hits": {
                        "_source": [
                          "project_name",
                          "fhwa_soar_project_no.program_code",
                          "project_number"
                        ],
                        "size": 1
                      }
                    },
                    "negative_filter": {
                      "bucket_selector": {
                        "buckets_path": {
                          "balance": "nested_budget_items>total_current_balance"
                        },
                        "script": "params.balance < 0"
                      }
                    }
                  }
                }
              }
        } \n\n"""
        """ - 3. Example User Prompt: Can I have a list of all project with negative balance on fund Y230 and L24E with outstanding Obligation and Commitment?
            - Example Query: 
            {
              "size": 0,
              "query": {
                "terms": {
                  "fhwa_soar_project_no.program_code.keyword": ["Y230", "L24E"]
                }
              },
              "aggs": {
                "by_project_number": {
                  "terms": {
                    "field": "project_number",
                    "size": 1000
                  },
                  "aggs": {
                    "nested_budget_items": {
                      "nested": {
                        "path": "budget_info.budget_items"
                      },
                      "aggs": {
                        "total_current_balance": {
                          "sum": {
                            "field": "budget_info.budget_items.current_balance"
                          }
                        },
                        "total_obligations": {
                          "sum": {
                            "field": "budget_info.budget_items.obligations"
                          }
                        },
                        "total_commitments": {
                          "sum": {
                            "field": "budget_info.budget_items.commitments"
                          }
                        }
                      }
                    },
                    "project_info": {
                      "top_hits": {
                        "_source": [
                          "project_name",
                          "fhwa_soar_project_no.program_code",
                          "project_number"
                        ],
                        "size": 1
                      }
                    },
                    "negative_filter": {
                      "bucket_selector": {
                        "buckets_path": {
                          "balance": "nested_budget_items>total_current_balance"
                        },
                        "script": "params.balance < 0"
                      }
                    }
                  }
                }
              }
        } \n\n"""
        "###Use the above example query to generate the query when needed\n"
        "NOTE: Always Give correct and valid query and Do not give any other text or explanation."
        "CRITICAL PAGINATION HANDLING:\n"
        "- When user says 'next', 'more', or 'yes' to pagination:\n"
        "  1. Use the previous query from chat history\n"
        "  2. Increment the page number by 1\n"
        "  3. Pass the query with new page number to search function\n"
        "  4. Show results with updated pagination info\n"
        "- Always maintain the same query parameters when paginating\n"
        "- Only change the page number when handling pagination commands\n"
        "- If no previous query exists, inform user there's no previous query to paginate\n"
        "- If already on last page, inform user there are no more results\n"
        "- Show current page and total pages in every response\n"
        "- Ask about next page only if there are more results available\n"
    )

    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=configs.OPENAI_API_KEY,
    )

    # Create messages with chat history if available
    messages = [{"role": "system", "content": system_prompt}]

    if chat_history:
        messages.extend(chat_history)

    messages.append(
        {"role": "user", "content": f'NL Query: "{query}"\nElasticsearch Query JSON:'}
    )

    # Get response from model
    response = model.invoke(messages)
    es_query_str = response.content.strip()

    # Parse the JSON query
    try:
        # Find the JSON part of the response
        first_brace = es_query_str.find("{")
        last_brace = es_query_str.rfind("}") + 1
        if first_brace == -1 or last_brace == 0:
            raise ValueError("No valid JSON found in response")

        json_part = es_query_str[first_brace:last_brace]
        query_dict = json.loads(json_part)

        # Ensure we have a valid query dictionary
        if not isinstance(query_dict, dict):
            raise ValueError("Generated query is not a valid dictionary")

        # Handle count queries
        if query_dict.get("_count"):
            # Remove _count flag and ensure size is 0
            query_dict.pop("_count")
            query_dict["size"] = 0
            query_dict["track_total_hits"] = True

        # For list queries, ensure we have a reasonable size and only requested fields
        if not query_dict.get("size") == 0:
            # Check if query specifies a number (e.g., "top 5", "first 10")
            number_match = re.search(
                r"(?:top|first|last|show|get)\s+(\d+)", query.lower()
            )
            if number_match:
                query_dict["size"] = int(number_match.group(1))
            else:
                query_dict["size"] = 20  # Default size for list queries

            if not query_dict.get("_source"):
                # If no specific fields requested, include id and fields based on query context
                query_dict["_source"] = ["id"]
                # Add fields based on query context
                if "budget" in query.lower():
                    query_dict["_source"].extend(
                        ["total_project_budget", "budget_info"]
                    )
                if "status" in query.lower():
                    query_dict["_source"].extend(["status"])
                if "name" in query.lower():
                    query_dict["_source"].extend(["epar_name", "project_name"])
                if "date" in query.lower():
                    query_dict["_source"].extend(["created_at", "updated_at"])

        # Add track_total_hits for count queries
        if query_dict.get("size") == 0:
            query_dict["track_total_hits"] = True

        # For total count queries, ensure we use match_all
        if query_dict.get("size") == 0 and not query_dict.get("query"):
            query_dict["query"] = {"match_all": {}}

        # Validate query structure
        if "query" in query_dict:
            if not isinstance(query_dict["query"], dict):
                if retry_count >= 3:
                    return handle_error_response(
                        Exception("Query must be a dictionary")
                    )
                else:
                    return create_es_query(query, chat_history, retry_count + 1)
            if "bool" in query_dict["query"]:
                if not isinstance(query_dict["query"]["bool"], dict):
                    if retry_count >= 3:
                        return handle_error_response(
                            Exception("Bool query must be a dictionary")
                        )
                    else:
                        return create_es_query(query, chat_history, retry_count + 1)
                for clause in ["must", "should", "must_not"]:
                    if clause in query_dict["query"]["bool"]:
                        if not isinstance(query_dict["query"]["bool"][clause], list):
                            query_dict["query"]["bool"][clause] = [
                                query_dict["query"]["bool"][clause]
                            ]

        return query_dict
    except json.JSONDecodeError as e:
        if retry_count >= 3:
            return handle_error_response(e)
        else:
            return create_es_query(query, chat_history, retry_count + 1)
    except Exception as e:
        if retry_count >= 3:
            return handle_error_response(e)
        else:
            return create_es_query(query, chat_history, retry_count + 1)


def search_elasticsearch(
    query: Dict[str, Any], page: int = 1, retry_count: int = 0
) -> Dict[str, Any]:
    """Execute Elasticsearch query with pagination support"""

    try:
        # Ensure we have a valid query dictionary
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary")

        # Check if this is a count query (size=0 and no aggregations)
        is_count_query = (
            query.get("size") == 0
            and "aggs" not in query
            and query.get("track_total_hits") is True
        )

        if is_count_query:
            # For count queries, use the count API
            count_query = query.copy()
            count_query.pop("size", None)
            count_query.pop("track_total_hits", None)
            resp = es.count(index=configs.ELASTICSEARCH_DEFAULT_INDEX, body=count_query)
            return {
                "hits": {
                    "total": {"value": resp["count"], "relation": "eq"},
                    "hits": [],
                }
            }

        # For non-count queries, proceed with normal search
        # Store original size if specified
        original_size = query.get("size")

        # Only add pagination if size is 20 (default) and not a specific number
        if original_size == 20:
            query["from"] = (page - 1) * 20
        else:
            # For specific size requests, don't add pagination
            page = 1

        # Execute the search with the query parameters
        resp = es.search(index=configs.ELASTICSEARCH_DEFAULT_INDEX, body=query)

        # Convert response to dictionary
        result = dict(resp)

        # Only add pagination info if using default size (20)
        if original_size == 20:
            total_hits = (
                result["hits"]["total"]["value"]
                if isinstance(result["hits"]["total"], dict)
                else result["hits"]["total"]
            )
            total_pages = (total_hits + 19) // 20  # Ceiling division by 20

            result = {
                **result,
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_hits": total_hits,
                    "has_next_page": page < total_pages,
                    "has_previous_page": page > 1,
                },
            }

        # If original size was larger, update total hits to reflect original request
        if original_size and original_size > 20:
            if isinstance(result.get("hits", {}).get("total"), dict):
                result["hits"]["total"]["value"] = min(
                    original_size, result["hits"]["total"]["value"]
                )
            else:
                result["hits"]["total"] = min(original_size, result["hits"]["total"])

        return result
    except Exception as e:
        if retry_count >= 3:
            return handle_error_response(e)
        else:
            return search_elasticsearch(query, page, retry_count + 1)


def limit_results_for_summary(
    results: Dict[str, Any], max_records: int = 20
) -> Dict[str, Any]:
    """Limit the number of records in the results for summary generation"""
    if not isinstance(results, dict):
        return results

    # Create a copy of the results to avoid modifying the original
    limited_results = results.copy()

    # If there are hits, limit them
    if "hits" in limited_results and "hits" in limited_results["hits"]:
        limited_results["hits"]["hits"] = limited_results["hits"]["hits"][:max_records]

        # Update total hits count if it exists
        if "total" in limited_results["hits"]:
            if isinstance(limited_results["hits"]["total"], dict):
                limited_results["hits"]["total"]["value"] = min(
                    limited_results["hits"]["total"]["value"], max_records
                )
            else:
                limited_results["hits"]["total"] = min(
                    limited_results["hits"]["total"], max_records
                )

    return limited_results


def get_r100_available_fields() -> Dict[str, List[str]]:
    """Get available fields from R100_MAPPING"""
    fields = {
        "float_fields": [
            "actual_idcr_earned_as_of_mar",
            "forecast_idcr_earned_as_of_mar",
            "variance",
            "projected_fy25_idcr",
            "FY24",
            "FY25",
            "total_forecast_expenditure",
            "total_forecast_idcr",
        ],
        "keyword_fields": ["budget_analyst", "difs_project_name", "service_type"],
        "long_fields": ["difs_project_number"],
        "date_fields": ["fmis_end_date"],
        "boolean_fields": ["idcr_exempt"],
        "nested_fields": {
            "monthly_data": [
                "Oct-23",
                "Nov-23",
                "Dec-23",
                "Jan-24",
                "Feb-24",
                "Mar-24",
                "Apr-24",
                "May-24",
                "Jun-24",
                "Jul-24",
                "Aug-24",
                "Sep-24",
                "Oct-24",
                "Nov-24",
                "Dec-24",
                "Jan-25",
                "Feb-25",
                "Mar-25",
            ],
            "forecast_data": [
                "Apr-25",
                "May-25",
                "Jun-25",
                "Jul-25",
                "Aug-25",
                "Sep-25",
            ],
        },
    }
    return fields


def create_r100_query(
    query: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    retry_count: int = 0,
) -> Dict[str, Any]:
    if retry_count >= 3:
        raise ValueError("Please try again later")

    system_prompt = f"""
        "You are a system that converts natural language queries about r100 data "
        "into Elasticsearch JSON queries. Each document in the index represents an r100 record.\n\n"

        f"Available fields in the index:\n"
        f"{json.dumps(R100_INDEX_MAPPING_LLM, indent=4).replace('{', '{{').replace('}', '}}')}\n"


        Examples:
         Q: What is the forecasting expenditure for project 100483 by month using FY23 and FY24 historical data?
         A: {{
              "query": {{
                "term": {{
                  "difs_project_number": 100483
                }}
              }},
              "_source": true,
              "size": 1000
            }}
        Note : Use the previous user queries and assistant responses from chat history to understand context, intent, and any follow-up requirements. 
        Focus on continuity: if the current question depends on or refines a previous one, incorporate that prior information into the generated Elasticsearch query.

        "CRITICAL QUERY GUIDELINES:\n"
        "1. Only output Elasticsearch JSON. No explanation."
        "2. Use provide example query to generate the query when needed"
    """
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=configs.OPENAI_API_KEY,
    )

    messages = [{"role": "system", "content": system_prompt}]

    # Convert chat history messages to the correct format
    if chat_history:
        messages.extend(chat_history)

    # Add the current query
    messages.append(
        {"role": "user", "content": f'NL Query: "{query}"\nElasticsearch Query JSON:'}
    )

    response = model.invoke(messages)
    es_query_str = response.content.strip()

    try:
        match = re.search(r"(\{[\s\S]*\})", es_query_str)
        if not match:
            raise ValueError("No valid JSON found in response")

        query_dict = json.loads(match.group(1))

        if not isinstance(query_dict, dict):
            raise ValueError("Generated query is not a valid dictionary")

        if query_dict.get("_count"):
            query_dict.pop("_count")
            query_dict["size"] = 0
            query_dict["track_total_hits"] = True

        if not query_dict.get("size") == 0:
            number_match = re.search(
                r"(?:top|first|last|show|get)\s+(\d+)", query.lower()
            )
            query_dict["size"] = int(number_match.group(1)) if number_match else 20

        if query_dict.get("size") == 0:
            query_dict["track_total_hits"] = True

        if query_dict.get("size") == 0 and not query_dict.get("query"):
            query_dict["query"] = {"match_all": {}}

        return query_dict

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse Elasticsearch query JSON: {e}\nOutput was: {es_query_str}"
        )

    except Exception:
        return create_r100_query(query, chat_history, retry_count + 1)


def search_r100_elasticsearch(
    query: Dict[str, Any], page: int = 1, retry_count: int = 0
) -> Dict[str, Any]:
    """Execute Elasticsearch query on r100 index with pagination support"""
    # Limit retries to 3 times
    if retry_count >= 3:
        raise ValueError("Please try again later")

    try:
        # Ensure we have a valid query dictionary
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary")

        # Check if this is a count query
        is_count_query = (
            query.get("size") == 0
            and "aggs" not in query
            and query.get("track_total_hits") is True
        )

        if is_count_query:
            # For count queries, use the count API
            count_query = query.copy()
            count_query.pop("size", None)
            count_query.pop("track_total_hits", None)
            resp = es.count(index="r100", body=count_query)
            return {
                "hits": {
                    "total": {"value": resp["count"], "relation": "eq"},
                    "hits": [],
                }
            }

        # For non-count queries, proceed with normal search
        original_size = query.get("size")

        # Limit the maximum size to prevent large responses
        if original_size and original_size > 100:
            query["size"] = 100
            logger.warning(
                f"Query size {original_size} exceeds maximum limit of 100. Limiting to 100."
            )

        # Only add pagination if size is 20 (default) and not a specific number
        if original_size == 20:
            query["from"] = (page - 1) * 20
        else:
            page = 1

        # Add timeout and size limits to prevent large responses
        query["timeout"] = "30s"
        query["track_total_hits"] = True

        # Execute the search with the query parameters
        try:
            resp = es.search(index="r100", body=query)
        except Exception:
            raise DuplicatedError(
                "I'm sorry, I'm not able to process your request. Please try again later."
            )

        # Convert response to dictionary
        result = dict(resp)

        # Only add pagination info if using default size (20)
        if original_size == 20:
            total_hits = (
                result["hits"]["total"]["value"]
                if isinstance(result["hits"]["total"], dict)
                else result["hits"]["total"]
            )
            total_pages = (total_hits + 19) // 20

            result = {
                **result,
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_hits": total_hits,
                    "has_next_page": page < total_pages,
                    "has_previous_page": page > 1,
                },
            }

        return result
    except DuplicatedError:
        raise
    except Exception as e:
        logger.error(f"Error in search_r100_elasticsearch: {str(e)}")
        # Increment retry counter and retry
        return search_r100_elasticsearch(query, page, retry_count + 1)


def create_es_agent(chat_history: Optional[List[Dict[str, str]]] = None):
    """Create and return an Elasticsearch agent with conversation memory"""

    # Create memory with chat history if available
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True, output_key="output"
    )

    # Load chat history into memory using 'input' and 'output' keys
    if chat_history:
        for msg in chat_history:
            if "input" in msg and "output" in msg:
                memory.save_context({"input": msg["input"]}, {"output": msg["output"]})

    def safe_json_parse(x):
        """Safely parse JSON input with error handling"""
        if isinstance(x, dict):
            return x
        if isinstance(x, str):
            try:
                x = x.strip()
                start = x.find("{")
                end = x.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = x[start:end]
                    return json.loads(json_str)
                else:
                    return json.loads(x)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.error(f"Input was: {x}")
                return {"size": 0, "track_total_hits": True}
        return x

    # Define tools
    tools = [
        Tool(
            name="create_es_query",
            func=lambda x: create_es_query(
                x.get("query") if isinstance(x, dict) else x,
                memory.chat_memory.messages,
            ),
            description="""Creates an Elasticsearch query from natural language. You should:
            1. Analyze the input query carefully to understand the exact requirements
            2. Consider field relationships and nested structures
            3. Use appropriate query types (match, term, range) based on field types
            4. Add relevant aggregations for statistical analysis
            5. Include proper source field filtering
            6. Set appropriate size and pagination
            7. Add sorting if relevant
            8. If results are not satisfactory, you can try again with a refined query
            9. Maximum 3 attempts to refine the query
            
            For nested fields, remember:
            - Use proper path notation
            - Consider parent-child relationships
            - Apply correct nested query structure
            
            Query Structure Guidelines:
            1. For exact matches: Use term queries
            2. For text search: Use match queries with proper analyzer
            3. For ranges: Use range queries with proper comparisons
            4. For multiple conditions: Use bool queries with must/should/must_not
            5. For aggregations: Use appropriate bucket/metric types""",
        ),
        Tool(
            name="search_elasticsearch",
            func=lambda x: search_elasticsearch(
                safe_json_parse(x), x.get("page", 1) if isinstance(x, dict) else 1
            ),
            description="""Executes an Elasticsearch query and returns results. You should:
            1. Analyze the query before execution
            2. Validate the query structure
            3. Check for potential performance issues
            4. Monitor result quality and relevance
            5. If results are not satisfactory:
               - Check the total hits
               - Examine relevance scores
               - Look for empty aggregations
               - Consider query refinement
            6. Maximum 3 attempts to get better results""",
        ),
        Tool(
            name="create_r100_query",
            func=lambda x: create_r100_query(
                x.get("query") if isinstance(x, dict) else x,
                memory.chat_memory.messages,
            ),
            description="Creates an Elasticsearch query from natural language for r100 data. For count queries, use size: 0 and track_total_hits: true",
        ),
        Tool(
            name="search_r100_elasticsearch",
            func=lambda x: search_r100_elasticsearch(
                safe_json_parse(x), x.get("page", 1) if isinstance(x, dict) else 1
            ),
            description="Executes an Elasticsearch query on r100 data and returns results with pagination. For count queries, use size: 0 and track_total_hits: true",
        ),
    ]

    try:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are an AI assistant that helps users query and analyze PAR (Project Authorization Request) data using Elasticsearch.
                        You have the capability to generate, analyze, and refine queries for optimal results. You can convert natural language queries to Elasticsearch queries, execute them, and summarize the results In Mostly table format with best and large summary of the data at the end of table And If not possible to create table then Do it in your way.
                        if user ask overview based quesion so take financial related data
                        if user give par id so give par id wise brief data  par id wise data
                        if make table so check each column if blank any clm so not consider that column in the table
                        if user give project 29483 / difs 29483 so consider as project number not par id/project id if mention project id 43388 so consider as project id
                        available balance means current balance of the project --> budget_info.budget_items.current_balance
                        if user ask about project related by tasks so give project related data with tasks and financial related data also: ex., Can I have an overview of project 100519 by Tasks so take that field like: PAR ID, Project Name, Project Manager, Project Status and also give financial related data like: Fund Source, Expenditures, Total Project Budget, Total Project Expenditures, Total Project Balance
                        if make table so check each row if blank any row so not consider that row in the table
                        if user give project 29483 / difs 29483 so consider as project number not par id/project id if mention project id 43388 so consider as project id
                        available balance means current balance of the project --> budget_info.budget_items.current_balance
                        If no data is available, return ONLY "I'm sorry, I don't have enough information to answer that question."
                        Do not suggest alternative queries or ask for clarification when no data is available
                        Do not provide any additional context or explanation when no data is available
                        Do not suggest questions when no data is available
                        if make table so check each row if ... any row so not consider that row in the table

                        When handling queries and have access of these two Indexes :
                            - par (Project Authorization Request) data
                            - r100 (R100 data):
                            - If needed You can use these both index to get the data in the same response

 
                        ### R100 Index mapping:
                        {json.dumps(R100_INDEX_MAPPING_LLM, indent=4).replace('{', '{{').replace('}', '}}')}

                        ### PAR Index mapping:
                        {json.dumps(PAR_INDEX_MAPPING_LLM, indent=4).replace('{', '{{').replace('}', '}}')}

                        The create_es_query use the PAR index so for par data use create_es_query and search_elasticsearch
                        The create_r100_query use the r100 index so for r100 data use create_r100_query and search_r100_elasticsearch

                        1. For PAR data queries (use create_es_query and search_elasticsearch):
                           - Project overview and details
                           - Budget information and allocations
                           - Task-related information
                           - Project status and progress
                           - General project inquiries
                           - Project manager information
                           - Project ID or PAR ID specific queries
                           - Request type information

                        2. For r100 data queries (use create_r100_query and search_r100_elasticsearch):
                           - Use create_r100_query to generate the query when the need of r100 data
                           - Monthly expenditure data
                           - Financial year specific queries
                           - total expenditures funding
                           - Charge Project | Analyze Project | Manage Project
                             Eg : "Who charged project 100483?" or "Who analyzed project 100483?" or "Who managed project 100483?"
                           - Budget analyst information 
                           - Service type information (PERSONNEL SERVICES, Non-PERSONNEL SERVICES, etc.)
                           - FMIS end dates
                           - Monthly forecasts
                           - Expenditure splits by category
                           - Project charging information
                           - Any query containing 'r100', 'r-100', or 'r 100'
                           - Any query about monthly data or fiscal year data
                           - Any query about budget analysis or forecasting
                           - Any query about service type or service category
                         
                        CRITICAL : Do NOT modify the any query which comes from the create_r100_query and create_es_query tools response query direct pass it to search_r100_elasticsearch and search_elasticsearch, Only fix the json error if any
                        CRITICAL: If the query is about service type, service category, monthly data, fiscal years, or forecasting, ALWAYS use r100 tools first.
                        Only fall back to PAR data tools if r100 tools return no results.


                        STRICT Guidelines:
                        - single project number have multiple par record so give project wise not consider par wise not give par id wise
                        - Add Related fields in the table if possible for ex., if user ask project related so add project related fields in the table (name, manager, id, number, status, etc.)
                        - For r100 queries, clearly indicate in the response that the data is from the r100 index
                        - If the query doesn't specify which data source to use, default to PAR data unless r100 is explicitly mentioned

                        1. For count queries (e.g., 'how many', 'total number of', 'count of'):
                        - Use the create_es_query tool to generate a count query or also generate unique values of the field
                        - Use the search_elasticsearch tool to execute it
                        - Use the summarize_results tool to get the count
                        - If possible so always use the unique_values to get the unique values of the field
                        - count with field name and summary in a natural way that matches the query context.
                        - Do NOT mention misunderstandings or confusion
                        - Do NOT ask for clarification
                        - Do NOT interpret what PAR means
                        - Do NOT suggest alternative queries


                        2. For all other queries:
                        - Always consider the chat history context
                        - Use information from previous queries about people or entities
                        - Include relevant statistics from previous queries
                        - Don't claim you don't know if the information was in chat history
                        - Pass both query and results to summarize_results
                        - Include aggregation results in summaries
                        - Ensure each row in the table provides complete context
                        - Add summary statistics at the bottom of the table
                        - If results have more than 20 records, show pagination info and ask if user wants to see next page
                        - For pagination, use keywords like 'next', 'more', 'yes' to show next page. ex., "Do you want to see next page?" / "Yes So show me the next page"
                        - Show current page number and total pages in the response

                        3. Important:
                        - If possible so generate unique list for ex., list of managers so give each manager name one time
                        - Each document represents one PAR
                        - The 'id' field is the unique PAR ID
                        - Never question what PAR means
                        - Never ask for clarification about PAR
                        - Never suggest alternative interpretations
                        - Never mention technical details about the search
                        - Never mention misunderstandings or errors
                        - Always give summary table with data and best and large summary at the end and start of table
                        - For paginated results, show current page info and ask about next page

                        CRITICAL CAPABILITIES:

                        1. Self-Analysis and Refinement:
                        - Analyze your own query quality before execution
                        - Evaluate result relevance and completeness
                        - Automatically refine queries if results are unsatisfactory
                        - Maximum 3 attempts for refinement
                        - Learn from previous queries in chat history
                        - If results are not satisfactory so try again with a refined query

                        2. Query Generation Excellence:
                        - Create precise, targeted Elasticsearch queries
                        - Use field-appropriate query types
                        - Consider relationships between fields
                        - Include relevant aggregations
                        - Apply proper sorting and pagination
                        - Handle nested fields correctly

                        3. Result Quality Control:
                        - Evaluate result relevance scores
                        - Check hit counts for reasonableness
                        - Analyze aggregation results
                        - Ensure complete data retrieval
                        - Validate against expected outcomes
                        - If budget_info.budget_items is a list, then:
                            a. Try to aggregate: sum expenditures, current_balance, and budget_amount (if exists) across all items.
                            b. If aggregation is possible, show totals.
                            c. If aggregation is not possible, format the values as comma-separated lists for display.
                            d. Do not write "Multiple Values". Always either show sum or comma-separated values.
                        - Format all numbers (e.g., 1,234.56)
                        - If all values are blank/invalid, exclude that column from the table
                        - Add a natural summary with totals at both top and bottom of the table.

                        4. Continuous Improvement:
                        - Learn from chat history patterns
                        - Adapt queries based on previous results
                        - Maintain context across interactions
                        - Improve precision with each iteration

                        Intelligent Execution and Fallback Investigation:
                        - Before executing, analyze query structure for possible errors or gaps.
                        - If the result is empty, automatically trigger intelligent fallback behavior:
                        - Investigate available fields and values using aggregations.
                        - Check which fields exist and are populated.
                        - Use this information to revise and rerun the query.
                        - Attempt maximum 3 refinement attempts.
                        - Adapt based on field population density, relevance scores, and hit counts.
                        - Only stop retrying if no meaningful result is found after 3 attempts.

                        QUERY REFINEMENT STRATEGY:

                        1. Initial Query:
                        - Create based on user request and field knowledge
                        - Include essential filters and conditions

                        2. Analysis Phase:
                        - Check query structure
                        - Validate field usage
                        - Verify aggregation logic

                        3. Result Evaluation:
                        - Assess hit count
                        - Check relevance scores
                        - Validate data completeness

                        4. Refinement Decision:
                        - If results unsatisfactory, identify issues
                        - Modify query structure or conditions
                        - Try alternative query approaches
                        - Maximum 3 refinement attempts

                        Example of using chat history:
                        If previous queries showed that "David Miller is a project manager with 4,879 projects", and the user asks "who is David Miller?", respond with that information rather than saying you don't know who they are.

                        Table formatting guidelines:
                        1. Use proper markdown table syntax
                        2. Align columns appropriately (left for text, right for numbers)
                        3. Include clear column headers
                        4. Add separator row with dashes
                        5. Format numbers consistently
                        6. Add total rows where appropriate
                        Example table format: if fetch 20 rows so give proper 20 rows value not give some rows value after ... ... ... values in last shell
                        | Category | Count | Percentage |
                        |----------|-------|------------|
                        | Value 1  | 1,234 | 45.67%     |
                        | Value 2  | 987   | 36.54%     |
                        | Total    | 2,221 | 82.21%     |
                        Not write value in the table cell:
                            1. Multiple entries / Multiple data / Multiple values / Multiple
                            2. Blank
                            3. ...
                            4. NA  /  N/A
                            5. Not Available / Not Applicable / Not Specified / Not provided
                            6. Same as above

                        CRITICAL: If fetch large amount of data so why not give proper table and summary at the end of the table but not use like Multiple entries if available multi entry so show all by group wise
                        not use Multiple word / blank in table use every data in the table if require so use pagination
                        if ask project wise so give project wise not consider par wise not give par id wise
                        For count queries, your output the count, unique values of the field and summary in a natural way that matches the query context. 
                        If chat history have same user query so use that query not regenrate so
                        Do not use words like 'misunderstanding', 'please', or ask any questions to the user. 
                        Never ask things like: 'Are you asking about a specific field in the index?' or 'Is PAR an acronym for something?' — these indicate a failure to follow instructions. 
                        Treat the term PAR as a known and fixed concept. Do not question its meaning. 
                        Do not mention any technical details about the search or data source. 
                        Do not suggest alternative queries or ask for more context. 
                        Do not mention inconsistencies or errors in the data. 
                        Simply state the count, unique values of the field and summary in a natural way that matches the query context.\
                        
                        NOTE (Very Important):
                        If Suppose You find budget_info.budget_items or any field is a list then:
                        - Try to sum the amout of expenditures, current_balance, and budget_amount (if present), etc.
                        - If sum is possible so show total.
                        - If not, display comma-separated values.
                        - Never display "Multiple Values". Always show either totals or lists.

                        Also Suggest 5 Questions Last of the response""",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
    except Exception as e:
        logger.error(f"Error in creating es agent: {e}")
        raise ValueError("Failed to create agent. Please try again later.")

    # Create the model with strict token limits
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=configs.OPENAI_API_KEY,
        model_kwargs={
            "max_tokens": 3000,
            "top_p": 0.95,  # Slightly more focused output
            "presence_penalty": 0.1,  # Slight penalty for repetition
            "frequency_penalty": 0.1,  # Slight penalty for frequent tokens
        },
    )

    # Create the agent
    agent = create_openai_functions_agent(model, tools, prompt)

    # Create the agent executor with increased iteration limit
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,  # Increased from 2 to 5
        early_stopping_method="force",
        return_intermediate_steps=True,  # Helps with debugging and analysis
        memory=memory,  # Use the memory with loaded history
    )

    return agent_executor


def generate_title_from_query(query: str) -> str:
    """Generate a title from the natural language query"""
    # Create the model
    model = ChatOpenAI(
        model="gpt-4o-mini", temperature=0.4, api_key=configs.OPENAI_API_KEY
    )

    # Create messages
    messages = [
        {
            "role": "system",
            "content": """Create a clean, descriptive title for a chat based on the query.
            Guidelines:
            1. Make it descriptive and specific to the query content
            2. Use action verbs when appropriate (e.g., "Analyzing", "Exploring", "Reviewing")
            3. Include key topics or metrics mentioned
            4. Keep it concise (5-7 words)
            5. Do not use quotes or special characters
            6. Do not use timestamps
            7. Do not use generic terms like "Chat" or "Query"
            
            Example formats:
            - Exploring Project Budget Distribution
            - Analyzing Team Performance Metrics
            - Reviewing Project Manager Roles
            
            Return only the plain text title, no quotes or additional formatting.""",
        },
        {"role": "user", "content": f"Create a title for this query: {query}"},
    ]

    # Get response from model
    response = model.invoke(messages)
    # Clean up the response to ensure it's a plain string
    title = response.content.strip()
    # Remove any quotes if present
    title = title.strip("\"'")
    return title


def summarize_chat_history(chat_history_messages: List[Any]) -> List[Any]:
    """Summarize chat history using GPT to maintain context while reducing token usage"""
    if not chat_history_messages:
        return []

    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=configs.OPENAI_API_KEY,
    )

    # Create messages for summarization
    messages = [
        {
            "role": "system",
            "content": """You are a context summarizer for a chat about PAR (Project Authorization Request) data.
            Your task is to create a concise summary that preserves critical information while removing unnecessary details.
            
            CRITICAL GUIDELINES:
            1. ALWAYS include these key elements if present:
               - Project numbers/IDs
               - Financial figures (budgets, expenditures, balances)
               - Table data with key metrics
               - Status information
               - Important dates
               - Specific queries and their context
            
            2. ALWAYS exclude:
               - Suggested questions
               - Generic summaries
               - Repetitive information
            
            3. Format the summary as:
               "Context: [Key information about the project/query]
                Data: [Critical numbers and metrics]
                Query Context: [What was being asked/looked for]"
            
            4. If there's table data:
               - Keep the most important rows
               - Include column names
               - Preserve key metrics
               - Remove redundant entries
            
            5. For follow-up questions:
               - Maintain the connection to previous queries
               - Keep the specific context being referenced
               - Preserve any numbers or metrics being discussed
            
            Return ONLY the summary, no additional text or formatting.""",
        },
        {
            "role": "user",
            "content": f"Please summarize this chat history while preserving critical context:\n{chat_history_messages}",
        },
    ]

    # Get summary from model
    response = model.invoke(messages)
    summary = response.content.strip()

    return [HumanMessage(content=summary)]


async def process_nl_query(
    query: str,
    chat_id: Optional[int] = None,
    parent_message_id: Optional[int] = None,
    userid: Optional[str] = None,
    retry_count: int = 0,
) -> str:
    """Process a natural language query using the Elasticsearch agent"""

    try:
        if not userid:
            raise UnauthorizedError("User ID is required for processing queries")

        # Get chat history from MongoDB only if parent_message_id is provided and not 0
        chat_history = []
        if chat_id and chat_id != 0:
            chat_history_doc = await get_eds_chat_history(chat_id, userid)
            if not chat_history_doc:
                raise NotFoundError(f"Chat history with ID {chat_id} not found")

            messages = await get_chat_messages(str(chat_id), userid)
            if messages:
                # Flatten all messages into a single list
                all_msgs = []
                for doc in messages:
                    all_msgs.extend(doc.get("messages", []))

                # Get only the last 5 messages
                recent_msgs = all_msgs[-5:]

                # Convert to format suitable for ConversationBufferMemory
                for msg in recent_msgs:
                    chat_history.append(
                        {"input": msg["query"], "output": msg["response"]}
                    )

        else:
            title = generate_title_from_query(query)
            chat_history_doc = await create_eds_chat_history(title, userid)
            chat_id = chat_history_doc["id"]
            parent_message_id = 0

        # Create agent with chat history
        agent = create_es_agent(chat_history)

        # Truncate the current query if too long
        if len(query) > 200:
            query = query[:200]

        try:
            result = await agent.ainvoke({"input": query})
        except Exception as e:
            logger.error(f"Error in processing nl query: {e}")
            raise ValueError("Failed to process query. Please try again later.")

        if "I don't have enough information" in result["output"] and retry_count < 2:
            return await process_nl_query(
                query, chat_id, parent_message_id, userid, retry_count + 1
            )

        try:
            await create_chat_message(
                eds_chat_history_id=str(chat_id),
                query=query,
                response=result["output"],
                parent_message_id=parent_message_id,
                userid=userid,
            )
        except Exception as e:
            error_response = handle_error_response(e)
            await create_chat_message(
                eds_chat_history_id=str(chat_id),
                query=query,
                response=error_response,
                parent_message_id=parent_message_id,
                userid=userid,
            )
            return error_response

        return result["output"]
    except Exception as e:
        return handle_error_response(e)
