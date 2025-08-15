import asyncio
import json
from time import time
from typing import Dict, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from langchain.memory import ConversationSummaryMemory
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from loguru import logger

from elasticsearch import Elasticsearch
from src.agents.prompts.nl2el_system_prompt import nl2el_system_prompt_v3
from src.agents.rag_query_v3.embedding_similarity_service import (
    EmbeddingSimilarityService,
)
from src.agents.rag_query_v3.langgraph_state import State
from src.agents.rag_query_v3.summarizer_agent import summarizer_chat
from src.core.config import configs
from src.core.container import Container
from src.mongodb.collections import EDSAssistanceLog, EDSAssistanceStatus
from src.mongodb.eds_assistance_log import eds_assistance_log_service
from src.services.nosql_llm_logger_service import NosqlLLMLoggerService
from src.util.response_sanitizer import detect_sensitive_info_response


class UnstructuredAgent:
    @inject
    def __init__(
        self,
        nosql_llm_logger_service: NosqlLLMLoggerService = Depends(
            Provide[Container.nosql_llm_logger_service]
        ),
    ):
        self.nosql_llm_logger_service = nosql_llm_logger_service
        self.model = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.3,
            api_key=configs.ANTHROPIC_API_KEY,
        )
        self.es = Elasticsearch(
            hosts=[configs.ELASTICSEARCH_URL],
            basic_auth=(configs.ELASTICSEARCH_USERNAME, configs.ELASTICSEARCH_PASSWORD),
            verify_certs=configs.ELASTICSEARCH_VERIFY_CERTS,
            ssl_show_warn=False,
        )


async def unstructured_chat(state: State):
    start_time = time()
    unstructured_agent = UnstructuredAgent()

    # Get the current user query
    current_query = state["messages"][-1].content

    # Find similar queries using embedding similarity (async call)
    similar_queries_section = await EmbeddingSimilarityService().find_similar_queries(
        user_query=current_query, top_k=3
    )

    # Add chat history if available
    messages = []
    if state.get("chat_history"):
        for msg in state["chat_history"]:
            messages.append(HumanMessage(content=msg["query"]))
            messages.append(AIMessage(content=msg["response"]))

    # Create the enhanced system prompt with similar queries
    enhanced_system_prompt = (
        nl2el_system_prompt_v3
        + similar_queries_section
        + f"\ncurrent chat history: {messages}"
    )

    messages = [
        (
            "system",
            enhanced_system_prompt,
        ),
        ("human", current_query),
    ]

    llm_response = unstructured_agent.model.invoke(messages,config={"callbacks":[unstructured_agent.nosql_llm_logger_service.get_logger_callback(metadata={"module": "EDS","agent":"unstructured","resource":"EDS Assistance","user_id":state.get("user_id"),"query":state.get("user_query")},provider="anthropic",model_name="claude-3-5-sonnet-20241022")]})
    end_time = time()
    duration = end_time - start_time
    # Get user_id from state log for sensitive info detection
    log = state.get("log")
    user_id = getattr(log, "user_id", None)
    chat_id = getattr(log, "chat_id", None)
    parent_message_id = getattr(log, "parent_message_id", None)
    sensitive_check_result = await detect_sensitive_info_response(
        llm_response.content, user_id, chat_id, parent_message_id
    )

    content = llm_response.content
    status = EDSAssistanceStatus.QUERY_GENERATION_SUCCESS
    if sensitive_check_result:
        content = sensitive_check_result
        status = EDSAssistanceStatus.MALICIOUS

    if log:
        log.processing_latency_s_query = duration
        log.status = status
        log.generated_es_query = content

    return {**state, "messages": [content]}


def fetch_data(state: State):
    """Fetch data using the validated query"""
    log = state.get("log")
    result = None
    try:
        start_time = time()
        query_dict = json.loads(state["messages"][-1].content)

        # Check if required fields exist
        if "index" not in query_dict:
            raise ValueError("Missing required field: 'index'")
        if "query" not in query_dict:
            raise ValueError("Missing required field: 'query'")

        # Extract index and query from the input
        index = query_dict["index"]
        query = query_dict["query"]
        # Validate index
        if index not in ["r085", "r100", "r025"]:
            raise ValueError(f"Invalid index: {index}")

        # Ensure we have a valid query dictionary
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary")

        # Handle nested query structure
        # size = 20  # default size
        # inner_query = None

        # # Extract size and inner query from nested structure
        # while isinstance(query, dict) and "query" in query:
        #     # Extract size if it exists at this level
        #     if "size" in query:
        #         size = query["size"]
        #     # Move to next level of nesting
        #     query = query["query"]

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
            resp = UnstructuredAgent().es.count(index=index, body=count_query)
            result = {
                "hits": {
                    "total": {"value": resp["count"], "relation": "eq"},
                    "hits": [],
                }
            }
            return result

        # For non-count queries, proceed with normal search
        original_size = query.get("size", 20)

        # Add timeout and size limits to prevent large responses
        query["timeout"] = "30s"
        query["track_total_hits"] = True

        # Execute the search with filter_path to only get needed fields
        resp = UnstructuredAgent().es.search(index=index, body=query)
        # Handle empty or None response
        if not resp:
            result = {"hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}}
            return result

        # Convert ObjectApiResponse to dict for MongoDB
        result = resp.body if hasattr(resp, "body") else resp
        # Ensure we have a valid response structure
        page = 1  # Default to page 1
        # Add pagination info if using default size (20)
        if original_size == 20:
            total_hits = (
                result["hits"]["total"]["value"]
                if isinstance(result["hits"]["total"], dict)
                else result["hits"]["total"]
            )
            total_pages = (total_hits + 19) // 20

            result = {
                **resp,
                "pagination": {
                    "current_page": page,
                    "total_pages": total_pages,
                    "total_hits": total_hits,
                    "has_next_page": page < total_pages,
                    "has_previous_page": page > 1,
                },
            }
        end_time = time()
        duration = end_time - start_time

        if log:
            log.processing_latency_s_executor = duration
            log.status = EDSAssistanceStatus.QUERY_EXECUTION_SUCCESS
            log.generated_es_response = result or {}
        return {
            **state,
            "messages": [
                *state["messages"],
                ToolMessage(
                    content=result, role="tool", tool_call_id="call_fetch_data"
                ),
            ],
        }

    except Exception as e:
        if log:
            log.processing_latency_s_executor = 0
            log.status = EDSAssistanceStatus.QUERY_EXECUTION_FAILED
            log.generated_es_response = result if result else {}
            log.error_message = str(e)

        raise ValueError("Failed to fetch data")


async def query_process(
    query: str,
    chat_id: Optional[int] = None,
    parent_message_id: Optional[int] = None,
    userid: Optional[str] = None,
    chat_history: Optional[List[Dict]] = None,
):
    start_time = time()
    summary = ""
    memory = None
    if chat_history:

        memory = ConversationSummaryMemory(
            memory_key="chat_history",
            return_messages=True,
            llm=ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.3,
                api_key=configs.ANTHROPIC_API_KEY,
            ),
        )
        messages = []
        for msg in chat_history:
            messages.append(HumanMessage(content=msg["query"]))
            messages.append(AIMessage(content=msg["response"]))

        summary = memory.predict_new_summary(
            messages, existing_summary=memory.buffer or ""
        )

    supervisor_graph = (
        StateGraph(State)
        .add_node("unstructured_chat", unstructured_chat, is_async=True)
        .add_node("fetch_data", fetch_data)
        .add_node("summarizer_chat", summarizer_chat, is_streaming=True)
        .add_edge(START, "unstructured_chat")
        .add_conditional_edges(
            "unstructured_chat",
            lambda x: (
                "fetch_data"
                if x["messages"][-1].content.startswith("{")
                else "summarizer_chat"
            ),
        )
        .add_edge("fetch_data", "summarizer_chat")
        .add_edge("summarizer_chat", END)
        .compile()
    )
    summary_response = ""
    log = EDSAssistanceLog(
        user_query=query,
        user_id=userid,
        chat_id=chat_id,
        parent_message_id=parent_message_id,
        status=EDSAssistanceStatus.PROCESSING,
    )
    async for chunk in supervisor_graph.astream(
        {
            "messages": [{"role": "user", "content": query}],
            "summary": summary,
            "chat_history": chat_history,
            "log": log,
            "user_id": userid,
            "user_query": query,
        },
        stream_mode="messages",
    ):
        if isinstance(chunk, tuple) and chunk:
            message_chunk, metadata = chunk
            if metadata.get("langgraph_node") == "summarizer_chat":
                summary_response += message_chunk.content
                yield message_chunk.content
    end_time = time()
    duration = end_time - start_time

    summary_response = (
        "Oops! Something went wrong. Please try again in a moment!"
        if not summary_response
        else summary_response
    )
    if log:
        try:
            log.total_processing_latency_s = duration
            log.status = EDSAssistanceStatus.SUCCESS
            log.response_summary = summary_response
            # Run the log creation as a background task
            asyncio.create_task(
                eds_assistance_log_service.create_eds_assistance_log(log)
            )
        except Exception as e:
            logger.error(f"Error creating EDSAssistanceLog: {e}")

    if memory:
        memory.clear()
