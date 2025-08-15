import json

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import StructuredTool, Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from loguru import logger

from src.agents.tools.available_fields_tool import format_fields_for_display
from src.agents.tools.es_tools import es_query_tool
from src.core.config import configs
from src.mongodb.report_services import update_selected_fields

# Initialize the OpenAI model
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    api_key=configs.OPENAI_API_KEY,
)


def create_agent():
    """Create an agent for analyzing field requirements"""
    # Define tools
    tools = [
        Tool(
            name="get_available_fields",
            description="""Get all available fields from Elasticsearch mapping.
                No input required.
                Returns a dictionary containing field names and their types.
            """,
            func=format_fields_for_display,
        ),
        StructuredTool.from_function(
            func=es_query_tool,
            name="es_query_tool",
            description="""Execute an Elasticsearch query.
            Input must be a dictionary containing the query structure.
            The query must be passed as a query_input parameter.
            
            Example:
            {{
                "size": 100,
                "query": {{
                    "bool": {{
                    "must": [
                        {{
                        "nested": {{
                            "path": "budget_info.budget_items",
                            "query": {{
                            "match_all": {{}}
                            }}
                        }}
                        }}
                    ]
                    }}
                }},
                "_source": [
                    "budget_analyst",
                    "budget_info.budget_items.lifetime_budget",
                    "budget_info.budget_items.account"
                ]
            }}
            
            Note: The query must be wrapped in a query_input object, with index as a separate parameter.""",
        ),
    ]

    # Create prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
            You are a field analyzer agent. Your task is to:
            1. Extract fields from requirements summary
            2. Generate and execute Elasticsearch queries
            3. Analyze query results
            4. Validate field presence and data quality

            Follow these steps in sequence:

            Step 1: Field Mapping Analysis
            - Use get_available_fields tool to get field mappings don't give any input parameters to the tool.
            - Analyze available fields in both PAR and R100 indices
            - Note field types and nested structures
            - CONTINUE TO STEP 2

            Step 2: Requirements Analysis
            - Analyze requirements summary to identify:
              * Required fields
              * Field types needed
              * Index to use (PAR/R100)
            - If index not specified:
              * Look for keywords indicating index
              * Default to PAR if unclear
            - Extract fields matching requirements
            - CONTINUE TO STEP 3

            Step 3: Query Generation
            - Create Elasticsearch query using selected fields
            - Include proper field types and paths
            - Use this format:
            {{
                "size": 100,
                "query": {{
                    "bool": {{
                    "must": [
                        {{
                        "nested": {{
                            "path": "budget_info.budget_items",
                            "query": {{
                            "match_all": {{}}
                            }}
                        }}
                        }}
                    ]
                    }}
                }},
                "_source": [
                    "budget_analyst",
                    "budget_info.budget_items.lifetime_budget",
                    "budget_info.budget_items.account"
                ]
            }}
            - CONTINUE TO STEP 4

            Step 4: Query Execution
            - Execute query using es_query_tool
            - Verify field presence in results
            - Check data quality
            - CONTINUE TO STEP 5

            Step 5: Response Generation
            - Generate JSON response:
            {{
                "selected_fields": [
                    {{
                        "field_name": "field_name",
                        "field_type": "field_type",
                        "field_path": "full.field.path",
                    }}
                ],
                "data_sources_status": true/false,
                "data_structure_status": true/false,
                "assessing_data_quality_status": true/false,
                "validation_result": {{
                    "status": "success/error",
                    "field_validations": [...],
                    "validation_summary": {{
                        "total_fields": 0,
                        "fields_present": 0,
                        "fields_missing": 0,
                        "overall_valid": true/false
                    }}
                }}
            }}

            ##CRITICAL REQUIREMENTS:
            1. MUST use get_available_fields in Step 1
            2. MUST execute query in Step 4
            3. MUST validate all fields in results
            4. MUST wrap final response in ```json and ``` markers
            5. MUST include field types and paths
            6. MUST check data quality
            7. MUST handle nested fields correctly
            8. MUST wrap query in query_input object when using es_query_tool
            9. MUST put index as a separate parameter, not inside query

            Error Handling:
            - If any step fails, return:
            {{
                "selected_fields": [],
                "data_sources_status": false,
                "data_structure_status": false,
                "assessing_data_quality_status": false
            }}
            """,
            ),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    # Create agent
    agent = create_openai_functions_agent(llm=model, tools=tools, prompt=prompt)

    return AgentExecutor(agent=agent, tools=tools, verbose=True)


async def process_requirements_summary(requirements_summary: str, chat_id: int):
    """
    Process the requirements summary and analyze the data structure.

    Args:
        requirements_summary: A string describing the required fields and their usage
        chat_id: The chat ID to associate with the report

    Returns:
        Dict containing:
        - selected_fields: List of selected fields with their paths and types
        - validation_results: Results of field validation including status and sample values
    """
    agent = create_agent()

    # Run the agent with the requirements summary
    result = await agent.ainvoke({"input": requirements_summary})
    result = result["output"]

    # Extract JSON from markdown output
    try:
        # Find the JSON block in the markdown
        json_start = result.find("```json")
        if json_start == -1:
            json_start = result.find("```")
        if json_start == -1:
            raise ValueError("No JSON block found in agent output")

        # Find the end of the JSON block
        json_end = result.find("```", json_start + 3)
        if json_end == -1:
            raise ValueError("No closing JSON block found")

        # Extract the JSON string
        json_str = result[json_start:json_end]
        # Remove the ```json and ``` markers
        json_str = json_str.replace("```json", "").replace("```", "").strip()

        # Parse the JSON
        result_json = json.loads(json_str)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse agent output as JSON: {str(e)}")
        raise ValueError("Invalid JSON output from agent")
    except Exception as e:
        logger.error(f"Error processing agent output: {str(e)}")
        raise ValueError("Error processing agent output")

    data_sources_status = False
    data_structure_status = False
    assessing_data_quality_status = False
    if result_json.get("data_sources_status"):
        data_sources_status = True
    if result_json.get("data_structure_status"):
        data_structure_status = True
    if result_json.get("assessing_data_quality_status"):
        assessing_data_quality_status = True

    # update the selected fields in the database
    await update_selected_fields(chat_id, result_json.get("selected_fields"))

    return {
        "data_sources_status": data_sources_status,
        "data_structure_status": data_structure_status,
        "assessing_data_quality_status": assessing_data_quality_status,
    }
