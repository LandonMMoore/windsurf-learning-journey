import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.prebuilt import create_react_agent
from loguru import logger

from src.agents.prompts.report_generator_prompt import (
    report_formula_assistant_prompt,
    report_generator_prompt,
)
from src.agents.report_generator.formula_output_parser import FormulaOutputParser
from src.agents.report_generator.report_state import ReportAgentState
from src.agents.tools.report_agent_tools import (
    create_report_tool,
    create_sub_report_tool,
    get_available_fields_tool,
    get_available_templates_tool,
    get_report_details_tool,
    get_templates_details_tool,
    update_report_tool,
    update_state,
    update_sub_report_tool,
)
from src.core.config import configs
from src.core.exceptions import BadRequestError, InternalServerError, NotFoundError
from src.model.nosql_document.ns_report_model import (
    FormulaAssistantChatHistory,
    ReportChatHistory,
)
from src.schema.report_schema import (
    FUNCTION_REGISTRY,
    ChatRequest,
    FormulaAssistantChatRequest,
    ReportConfigurationUpdateSchema,
)
from src.services.nosql_llm_logger_service import NosqlLLMLoggerService
from src.services.reports_service import (
    FormulaAssistantChatHistoryService,
    ReportChatHistoryService,
    ReportConfigurationService,
    ReportTemplateService,
    TagService,
)
from src.services.sub_report_service import SubReportService
from src.util.reports import get_supported_function_list
from langgraph_supervisor import create_supervisor
from src.agents.prompts.report_generator_prompt import supervisor_prompt

class ReportAgent:

    def __init__(
        self,
        report_chat_history_service: ReportChatHistoryService = None,
        report_configuration_service: ReportConfigurationService = None,
        report_template_service: ReportTemplateService = None,
        sub_report_service: SubReportService = None,
        tag_service: TagService = None,
        nosql_llm_logger_service: NosqlLLMLoggerService = None,
        current_user: dict = None,
    ):
        self.nosql_llm_logger_service = nosql_llm_logger_service
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=configs.OPENAI_API_KEY,
        )
        self.report_chat_history_service = report_chat_history_service
        self.report_configuration_service = report_configuration_service
        self.tools = [update_state]
        if report_configuration_service and current_user:
            self.tools.extend(
                [
                    get_available_fields_tool(report_configuration_service),
                    get_report_details_tool(report_configuration_service),
                ]
            )
        if report_template_service:
            self.tools.extend(
                [
                    get_available_templates_tool(report_template_service),
                    get_templates_details_tool(report_template_service),
                ]
            )
        if sub_report_service:
            self.tools.extend(
                [
                    create_sub_report_tool(sub_report_service),
                    update_sub_report_tool(sub_report_service),
                ]
            )
        if tag_service and report_configuration_service and current_user:
            self.tools.extend(
                [
                    create_report_tool(
                        report_configuration_service, tag_service, current_user
                    ),
                    update_report_tool(report_configuration_service, tag_service),
                ]
            )
        self.agent = None
        self.checkpointer_ctx = None
        self.checkpointer = None


    async def chat(
        self,
        report_configuration_service: ReportConfigurationService,
        chat_request: ChatRequest,
        user_id: int,
    ):
        message_id = chat_request.message_id
        chat_id = chat_request.chat_id

        if message_id is not None and chat_id is None:
            raise BadRequestError(
                detail="Message ID cannot be provided without chat ID"
            )

        if chat_id is not None:
            is_chat_exists = (
                await self.report_chat_history_service.check_if_chat_exists(
                    chat_id, user_id
                )
            )
            if not is_chat_exists:
                raise NotFoundError(detail="Chat ID does not exist")
        else:
            chat_id = await self.report_chat_history_service.get_next_chat_id()

        message_object_id = None
        if message_id is not None:
            message = await self.report_chat_history_service.get_message(
                chat_id, message_id, user_id
            )
            if not message:
                raise NotFoundError(
                    detail="Message ID does not exist in the chat history"
                )
            message_object_id = message["_id"]

        else:
            message_id = await self.report_chat_history_service.get_next_message_id(
                chat_id, user_id
            )

        if chat_request.report_id is not None and message_id == 1:
            # update the report id in the chat history
            report_config = ReportConfigurationUpdateSchema(chat_id=chat_id)
            report_configuration_service.patch(chat_request.report_id, report_config)

        response = self.agent.invoke(
            {
                "messages": [
                    SystemMessage(
                        content=f" Report ID: {chat_request.report_id} Chat ID: {chat_id} "
                    ),
                    HumanMessage(
                        content=f"User query: {chat_request.query} Report ID: {chat_request.report_id} Chat ID: {chat_id}"
                    ),
                ]
            },
            config={"configurable": {"thread_id": chat_id}},
        )
        response = response["messages"][-1].content

        # TODO: Uncomment this when we want to stream the response
        # # pretty_print_messages(response)
        # logger.info(f"Response: {response}")
        # response = response["messages"][-1].content
        # response = ""
        # logger.info(f"Streaming response for chat_id:{chat_id}")
        # for chunk in self.agent.stream({"messages":[HumanMessage(content=chat_request.query)]},config={"configurable":{"thread_id":chat_id}}):
        #     # response += chunk["messages"][-1].content
        #     pretty_print_messages(chunk)
        #     # response += chunk

        if message_object_id is not None:
            chat_history = await self.report_chat_history_service.update(
                message_object_id,
                {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "user_query": chat_request.query,
                    "response": response,
                },
            )
        else:
            chat_history = await self.report_chat_history_service.add(
                ReportChatHistory(
                    user_id=user_id,
                    chat_id=chat_id,
                    user_query=chat_request.query,
                    response=response,
                    message_id=message_id,
                )
            )

        return chat_history

    def __enter__(self):
        try:
            if self.checkpointer_ctx is None:
                self.checkpointer_ctx = MongoDBSaver.from_conn_string(
                    configs.MONGODB_URL,
                    db_name=configs.MONGODB_DATABASE,
                    checkpoint_collection_name="report_generator_checkpoints",
                    writes_collection_name="report_generator_writes",
                )
            if self.checkpointer is None:
                self.checkpointer = self.checkpointer_ctx.__enter__()
            if self.agent is None:

                self.agent = create_react_agent(
                    model=self.llm,
                    tools=self.tools,
                    state_schema=ReportAgentState,
                    debug=True if configs.ENV == "local" else False,
                    prompt=report_generator_prompt,
                    checkpointer=self.checkpointer,
                )

        except Exception:
            if hasattr(self, "checkpointer_ctx") and self.checkpointer_ctx is not None:
                self.checkpointer_ctx.__exit__(None, None, None)
            logger.error("Error while initializing agent")
            raise InternalServerError(detail="Error while initializing agent")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self, "checkpointer_ctx") and self.checkpointer_ctx is not None:
            self.checkpointer_ctx.__exit__(exc_type, exc_value, traceback)

class ReportAgent_v2:
    def __init__(
        self,
        report_chat_history_service: ReportChatHistoryService = None,
        formula_assistant_chat_history_service: FormulaAssistantChatHistoryService = None,
        report_configuration_service: ReportConfigurationService = None,
        report_template_service: ReportTemplateService = None,
        sub_report_service: SubReportService = None,
        tag_service: TagService = None,
        nosql_llm_logger_service: NosqlLLMLoggerService = None,
        current_user: dict = None,
    ):
        self.nosql_llm_logger_service = nosql_llm_logger_service
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=configs.OPENAI_API_KEY,
        )
        self.report_chat_history_service = report_chat_history_service
        self.report_configuration_service = report_configuration_service
        self.tools = [update_state]
        if report_configuration_service and current_user:
            self.tools.extend(
                [
                    get_available_fields_tool(report_configuration_service),
                    get_report_details_tool(report_configuration_service),
                ]
            )
        if report_template_service:
            self.tools.extend(
                [
                    get_available_templates_tool(report_template_service),
                    get_templates_details_tool(report_template_service),
                ]
            )
        if sub_report_service:
            self.tools.extend(
                [
                    create_sub_report_tool(sub_report_service),
                    update_sub_report_tool(sub_report_service),
                ]
            )
        if tag_service and report_configuration_service and current_user:
            self.tools.extend(
                [
                    create_report_tool(
                        report_configuration_service, tag_service, current_user
                    ),
                    update_report_tool(report_configuration_service, tag_service),
                ]
            )
        self.agent = None
        self.checkpointer_ctx = None
        self.checkpointer = None
        self.formula_agent = FormulaAssistantAgent(
            formula_chat_history_service=formula_assistant_chat_history_service,
            report_configuration_service=report_configuration_service,
            sub_report_service=sub_report_service,
            nosql_llm_logger_service=nosql_llm_logger_service,
            current_user=current_user,
        )
        self.supervisor_agent = None


    async def chat(
        self,
        report_configuration_service: ReportConfigurationService,
        chat_request: ChatRequest,
        user_id: int,
    ):
        message_id = chat_request.message_id
        chat_id = chat_request.chat_id

        if message_id is not None and chat_id is None:
            raise BadRequestError(
                detail="Message ID cannot be provided without chat ID"
            )

        if chat_id is not None:
            is_chat_exists = (
                await self.report_chat_history_service.check_if_chat_exists(
                    chat_id, user_id
                )
            )
            if not is_chat_exists:
                raise NotFoundError(detail="Chat ID does not exist")
        else:
            chat_id = await self.report_chat_history_service.get_next_chat_id()

        message_object_id = None
        if message_id is not None:
            message = await self.report_chat_history_service.get_message(
                chat_id, message_id, user_id
            )
            if not message:
                raise NotFoundError(
                    detail="Message ID does not exist in the chat history"
                )
            message_object_id = message["_id"]

        else:
            message_id = await self.report_chat_history_service.get_next_message_id(
                chat_id, user_id
            )

        if chat_request.report_id is not None and message_id == 1:
            # update the report id in the chat history
            report_config = ReportConfigurationUpdateSchema(chat_id=chat_id)
            report_configuration_service.patch(chat_request.report_id, report_config)

        response = self.supervisor_agent.invoke(
            chat_request.query,
            chat_id,
            config={"configurable": {"thread_id": chat_id,"recursion_limit": 50},"callbacks":[self.nosql_llm_logger_service.get_logger_callback(metadata={
                "module": "EDS",
                "agent": "report_generator",
                "resource": "Report Agent",
                "user_id": user_id,
                "query": chat_request.query,
            },provider="openai",model_name="gpt-4o")]},
        )
        # response = response["messages"][-1].content

        # TODO: Uncomment this when we want to stream the response
        # # pretty_print_messages(response)
        # logger.info(f"Response: {response}")
        # response = response["messages"][-1].content
        # response = ""
        # logger.info(f"Streaming response for chat_id:{chat_id}")
        # for chunk in self.agent.stream({"messages":[HumanMessage(content=chat_request.query)]},config={"configurable":{"thread_id":chat_id}}):
        #     # response += chunk["messages"][-1].content
        #     pretty_print_messages(chunk)
        #     # response += chunk

        if message_object_id is not None:
            chat_history = await self.report_chat_history_service.update(
                message_object_id,
                {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "user_query": chat_request.query,
                    "response": response,
                },
            )
        else:
            chat_history = await self.report_chat_history_service.add(
                ReportChatHistory(
                    user_id=user_id,
                    chat_id=chat_id,
                    user_query=chat_request.query,
                    response=response,
                    message_id=message_id,
                )
            )

        return chat_history

    def __enter__(self):
        try:
            if self.checkpointer_ctx is None:
                self.checkpointer_ctx = MongoDBSaver.from_conn_string(
                    configs.MONGODB_URL,
                    db_name=configs.MONGODB_DATABASE,
                    checkpoint_collection_name="report_generator_checkpoints",
                    writes_collection_name="report_generator_writes",
                )
            if self.checkpointer is None:
                self.checkpointer = self.checkpointer_ctx.__enter__()
            if self.agent is None:

                self.agent = create_react_agent(
                    model=self.llm,
                    tools=self.tools,
                    state_schema=ReportAgentState,
                    debug=True if configs.ENV == "local" else False,
                    prompt=report_generator_prompt,
                    checkpointer=self.checkpointer,
                    name="report_agent",
                )
            
            if not hasattr(self.formula_agent, '_initialized') or not self.formula_agent._initialized:
                self.formula_agent.__enter__()
                self.formula_agent._initialized = True

            if self.supervisor_agent is None:
                self.supervisor_agent = SupervisorAgent(self, self.formula_agent)
        except Exception:
            if hasattr(self, "checkpointer_ctx") and self.checkpointer_ctx is not None:
                self.checkpointer_ctx.__exit__(None, None, None)
            logger.error("Error while initializing agent")
            raise InternalServerError(detail="Error while initializing agent")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self, "checkpointer_ctx") and self.checkpointer_ctx is not None:
            self.checkpointer_ctx.__exit__(exc_type, exc_value, traceback)
        # Clean up formula agent if it was initialized
        if hasattr(self.formula_agent, '_initialized') and self.formula_agent._initialized:
            self.formula_agent.__exit__(exc_type, exc_value, traceback)

class FormulaAssistantAgent:
    def __init__(
        self,
        formula_chat_history_service: FormulaAssistantChatHistoryService = None,
        report_configuration_service: ReportConfigurationService = None,
        sub_report_service: SubReportService = None,
        nosql_llm_logger_service: NosqlLLMLoggerService = None,
        current_user: dict = None,
    ):
        self.nosql_llm_logger_service = nosql_llm_logger_service
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=configs.OPENAI_API_KEY
        )
        self.formula_chat_history_service = formula_chat_history_service
        self.report_configuration_service = report_configuration_service
        self.sub_report_service = sub_report_service
        self.current_user = current_user
        self.output_parser = FormulaOutputParser(sub_report_service)

        self.agent = None
        self.checkpointer_ctx = None
        self.checkpointer = None

    def __enter__(self):
        try:
            if self.checkpointer_ctx is None:
                self.checkpointer_ctx = MongoDBSaver.from_conn_string(
                    configs.MONGODB_URL,
                    db_name=configs.MONGODB_DATABASE,
                    checkpoint_collection_name="formula_assistant_agent_checkpoints",
                    writes_collection_name="formula_assistant_agent_writes",
                )
            if self.checkpointer is None:
                self.checkpointer = self.checkpointer_ctx.__enter__()
            
            if self.agent is None:
                formula_prompt = (
                    report_formula_assistant_prompt.replace("{sub_report_config}", "")
                    .replace("{supported_functions}", get_supported_function_list(FUNCTION_REGISTRY))
                    .replace("{format_instructions}", "")
                )
                
                self.agent = create_react_agent(
                    model=self.llm,
                    tools=[],
                    debug=True if configs.ENV == "local" else False,
                    prompt=formula_prompt,
                    checkpointer=self.checkpointer,
                    name="formula_agent",
                )

        except Exception:
            if hasattr(self, "checkpointer_ctx") and self.checkpointer_ctx is not None:
                self.checkpointer_ctx.__exit__(None, None, None)
            logger.error("Error while initializing formula assistant agent")
            raise InternalServerError(
                detail="Error while initializing formula assistant agent"
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "checkpointer_ctx") and self.checkpointer_ctx is not None:
            self.checkpointer_ctx.__exit__(exc_type, exc_val, exc_tb)

    async def chat(
        self, chat_request: FormulaAssistantChatRequest, user_id: int
    ) -> dict:
        message_id = chat_request.message_id
        chat_id = chat_request.chat_id

        sub_report_id = chat_request.sub_report_id
        if sub_report_id is not None:
            sub_report = self.report_configuration_service.get_sub_report(sub_report_id)
            if not sub_report:
                raise NotFoundError(detail="Sub report ID does not exist")
        else:
            sub_report = None

        if message_id is not None and chat_id is None:
            raise BadRequestError(
                detail="Message ID cannot be provided without chat ID"
            )

        if chat_id is not None:
            is_chat_exists = (
                await self.formula_chat_history_service.check_if_chat_exists(
                    chat_id, user_id
                )
            )
            if not is_chat_exists:
                raise NotFoundError(detail="Chat ID does not exist")
        else:
            chat_id = await self.formula_chat_history_service.get_next_chat_id()

        message_object_id = None
        if message_id is not None:
            message = await self.formula_chat_history_service.get_message(
                chat_id, message_id, user_id
            )
            if not message:
                raise NotFoundError(
                    detail="Message ID does not exist in the chat history"
                )
            message_object_id = message["_id"]
        else:
            message_id = await self.formula_chat_history_service.get_next_message_id(
                chat_id, user_id
            )

        # Use JSON to serialize the sub_report_config
        json_config = json.dumps(sub_report.config, indent=2) if sub_report else ""

        format_instructions = self.output_parser.get_format_instructions()

        # Format the prompt with the sub_report_config and format instructions
        formatted_prompt = (
            report_formula_assistant_prompt.replace("{sub_report_config}", json_config)
            .replace(
                "{supported_functions}", get_supported_function_list(FUNCTION_REGISTRY)
            )
            .replace("{format_instructions}", format_instructions)
        )

        formula_agent = create_react_agent(
            model=self.llm,
            tools=[],
            debug=True if configs.ENV == "local" else False,
            prompt=formatted_prompt,
            checkpointer=self.checkpointer,
        )

        response = formula_agent.invoke(
            {"messages": [HumanMessage(content=chat_request.query)]},
            config={"configurable": {"thread_id": chat_id},"callbacks":[self.nosql_llm_logger_service.get_logger_callback(metadata={
                "module": "EDS",
                "agent": "formula_assistant",
                "resource": "Formula Assistant Agent",
                "user_id": user_id,
                "query": chat_request.query,
            },provider="openai",model_name="gpt-4o")]},
        )["messages"][-1].content

        parsed_response = self.output_parser.parse_response(response)

        if message_object_id is not None:
            await self.formula_chat_history_service.update(
                message_object_id,
                {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "user_query": chat_request.query,
                    "response": parsed_response,
                },
            )
        else:
            await self.formula_chat_history_service.add(
                FormulaAssistantChatHistory(
                    user_id=user_id,
                    chat_id=chat_id,
                    user_query=chat_request.query,
                    response=parsed_response,
                    message_id=message_id,
                    sub_report_id=sub_report_id,
                )
            )

        return {
            "formula": parsed_response["formula"],
            "explanation": parsed_response["explanation"],
            "chat_id": chat_id,
            "message_id": message_id,
        }

class SupervisorAgent:
    def __init__(self, report_agent: "ReportAgent_v2", formula_agent: "FormulaAssistantAgent"):
        self.report_agent = report_agent
        self.formula_agent = formula_agent

        # Supervisor LLM
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.3,
            api_key=configs.OPENAI_API_KEY
        )

        # Ensure both agents are properly initialized
        if not hasattr(self.report_agent, 'agent') or self.report_agent.agent is None:
            raise ValueError("Report agent is not properly initialized")
        
        if not hasattr(self.formula_agent, 'agent') or self.formula_agent.agent is None:
            raise ValueError("Formula agent is not properly initialized")

        self.supervisor = create_supervisor(
            model=self.llm,
            agents=[self.report_agent.agent, self.formula_agent.agent],
            prompt=supervisor_prompt,
            add_handoff_back_messages=True,
            output_mode="full_history",
        ).compile()

    def invoke(self, query: str, chat_id = None,config = None) -> str:
        if chat_id is not None:
            response = self.supervisor.invoke(
                {"messages": [HumanMessage(content=query)]},
                config=config,
            )
        else:
            response = self.supervisor.invoke({"messages": [HumanMessage(content=query)]})
        
        try:
            return response["messages"][-1].content
        except Exception:
            return "Something Went Wrong"
