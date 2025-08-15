from time import time
from typing import AsyncGenerator, List

from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI

from src.agents.prompts.summarizer_system_prompt import summarizer_system_prompt
from src.agents.rag_query_v3.langgraph_state import State
from src.core.config import configs
from src.mongodb.collections import EDSAssistanceStatus
from dependency_injector.wiring import inject, Provide
from src.core.container import Container
from src.services.nosql_llm_logger_service import NosqlLLMLoggerService
from fastapi import Depends




class SummarizerAgent:
    """Agent responsible for summarizing and formatting query results"""
    @inject
    def __init__(self, nosql_llm_logger_service: NosqlLLMLoggerService = Provide[Container.nosql_llm_logger_service]):
        self.nosql_llm_logger_service = nosql_llm_logger_service
        self.model = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=configs.OPENAI_API_KEY,
            streaming=True,
            stream_options={"include_usage": True},
        )


async def summarizer_chat(state: State) -> AsyncGenerator[dict, None]:
    start_time = time()
    summarizer_agent = SummarizerAgent()
    log = state.get("log")
    messages = [
        (
            "system",
            summarizer_system_prompt + f"current chat history: {state['chat_history']}",
        ),
        (
            "human",
            f"Current Data from RAG: {state['messages'][-1].content} \n\n current user query: {state['messages'][0].content}",
        ),
    ]

    response = ""

    async for chunk in summarizer_agent.model.astream(messages,config={"callbacks":[summarizer_agent.nosql_llm_logger_service.get_logger_callback(metadata={"module": "EDS","agent":"summarizer","resource":"EDS Assistance","user_id":state.get("user_id"),"query":state.get("user_query")},provider="openai",model_name="gpt-4o")]}):
        if hasattr(chunk, "content") and chunk.content:
            response += chunk.content
            yield chunk.content

    end_time = time()
    duration = end_time - start_time
    if log:
        log.processing_latency_s_summarizer = duration
        log.status = EDSAssistanceStatus.QUERY_SUMMARIZATION_SUCCESS
        log.response_summary = response
    yield {**state, "messages": [response]}
