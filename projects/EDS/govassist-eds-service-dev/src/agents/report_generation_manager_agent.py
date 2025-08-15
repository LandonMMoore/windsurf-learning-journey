from datetime import datetime
from typing import Any, Dict, Optional

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from loguru import logger

from src.agents.tools.available_fields_tool import format_fields_for_display
from src.core.config import configs
from src.core.exceptions import FailedToCreateError, InternalServerError
from src.mongodb.chat_services import (
    ChatType,
    create_chat_message,
    create_eds_chat_history,
    get_chat_messages,
    get_eds_chat_history,
)
from src.mongodb.collections import (
    CHAT_MESSAGES_REPORT_COLLECTION,
    EDS_REPORT_CHAT_HISTORY_COLLECTION,
    ReportGenerationStep,
)
from src.mongodb.report_services import create_report, get_report, update_report_step


class ReportGenerationManagerAgent:
    """
    Report Generation Manager Agent.
    This agent focuses on:
    1. Understanding initial user requirements
    2. Asking minimal but essential clarifying questions
    3. Generating clear requirement summaries
    4. Managing the initial phase of report generation
    Report Generation Manager Agent.
    This agent focuses on:
    1. Understanding initial user requirements
    2. Asking minimal but essential clarifying questions
    3. Generating clear requirement summaries
    4. Managing the initial phase of report generation
    """

    def __init__(self):
        self.model = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2,
            api_key=configs.OPENAI_API_KEY,
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )
        self.formatted_fields = format_fields_for_display()
        self.chain = self._create_chain()

    def _create_chain(self):
        """Create the conversation chain with the defined prompt"""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are an expert Report Requirements Analyst who helps users define their report needs clearly. Your role is to understand requirements and provide clear summaries.

                #Important:
                    - Report is only the type of excel or we can say sheet report so don't ask about the report type.
                    - Don't include chart or any other type of report in the summary.
                    - You should keep the history and generate the response accordingly.
                    - Make sure you are not repeating the same question again and again.
                    - And conversation should be as short as possible to understand the requirements.
                    - You need to ask the user to clarify the requirements if the user is not clear about the requirements.
                    - Don't generate any other text or comments apart from the given to you below.
                    - Never say you use this or use that tool or don't say anything other than the analysis report related things.
                    - Maximum 3 questions should be asked before generating the summary.
                    - After 3 questions or when you have enough information, generate the requirements summary.
                    - Use the chat history to avoid repeating questions and to build upon previous answers.

                Your responsibilities:

                1. **Understand Requirements:**
                - Listen carefully to what the user needs
                - Identify the type of report they want
                - Understand their key metrics and goals
                - Note any specific timeframes or constraints
                - Review chat history to avoid repeating questions

                2. **Ask Essential Questions:**
                - Ask maximum 3 clarifying questions
                - You have access to the available fields, so you can ask the user to select the fields from the available fields.
                - Here is the available fields: {self.formatted_fields}
                - Also make sure while you are asking the question you are not asking the field_path instead ask the field_name.
                - And don't ask the field name insted you the words like which field you want to include in the report.
                - If the fields are nested then do as the below example:
                    - nested field : budget_info.budget_items.obligations
                    - nested field : budget_info.budget_items.expenditures
                    - question : which field you want to include in the report from the budget_info? obligations or expenditures
                - Don't include field such as:
                    - created_at
                    - updated_at
                    - id
                    - uuid
                - Track questions asked in chat history and make sure that question are not repeated again and again.
                - Also give some examples with the questions you are asking.
                - Focus on important missing information
                - Don't repeat questions already answered
                - Help users clarify their thoughts
                - After 3 questions or when you have enough information, generate the summary

                3. **Provide Clear Summary:**
                - Generate summary when you have enough information (after 3 questions or earlier if sufficient)
                - Include all important points mentioned by the user
                - Keep it simple and clear
                - Focus on the main points
                - Format the summary as shown below

                When you have understood the requirements, provide a simple summary like this:
                ---REQUIREMENTS SUMMARY---
                I understand that you need [type of report(not mandatory to have this in the summary)] that will [main purpose(not mandatory to have this in the summary)].

                This report should cover [key metrics/data points(not mandatory to have this in the summary)] for [time period(not mandatory to have this in the summary)].
                ---END SUMMARY---

                Remember: 
                - Keep summaries short and clear - just reflect back what you understood from the user
                - Make sure while giving the field details you are not giving the field_path instead give the field_name.
                - And field name should be in the format of field_name direct don't add any relative path to it or anything else.
                - Only give plain text, no markdown or any other formatting in the requirements summary
                - Generate summary after 3 questions or when you have sufficient information
                - Use chat history to avoid repeating questions

                **Operational Guidelines:**
                - Be systematic and structured in your approach
                - Ask one question at a time
                - Validate each input before proceeding
                - Maintain a professional tone and clear formatting
                - Do not mention the internal workings even if the user asks
                - Do not mention the user's query in the response
                - Do not mention DDOT ever in the response
                - Track questions in chat history to avoid repetition
                - Generate summary after 3 questions or when sufficient information is gathered
                        
                Is this what you're looking for?
                If the response for the question is no, ask the user to clarify the requirements.
                """,
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )

        return LLMChain(llm=self.model, prompt=prompt, verbose=True, memory=self.memory)

    async def process_query(
        self,
        query: str,
        userid: str,
        chat_id: Optional[int] = None,
        parent_message_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Process a user query and manage the conversation flow"""
        has_final_summary = False
        try:
            # Handle chat history and context
            if chat_id and chat_id != 0:
                chat_history_doc = await get_eds_chat_history(
                    chat_id,
                    userid,
                    chat_history_collection=EDS_REPORT_CHAT_HISTORY_COLLECTION,
                )
                if not chat_history_doc:
                    raise ValueError(
                        f"Chat history with ID {chat_id} not found for user {userid}"
                    )

                messages = await get_chat_messages(
                    str(chat_id),
                    chat_message_collection=CHAT_MESSAGES_REPORT_COLLECTION,
                )
                if messages:
                    for msg in messages:
                        msg = msg.get("messages")[0]
                        self.memory.save_context(
                            {"input": msg["query"]}, {"output": msg["response"]}
                        )
            else:
                # Create new chat history
                title = self._generate_chat_title(query)
                chat_history_doc = await create_eds_chat_history(
                    title,
                    userid,
                    type=ChatType.DYNAMIC_REPORT_GENERATION,
                    chat_history_collection=EDS_REPORT_CHAT_HISTORY_COLLECTION,
                )
                chat_id = chat_history_doc["id"]
                parent_message_id = 0

                # Create initial report document
                await create_report(
                    chat_id,
                    userid=userid,
                    final_requirements_summary="",  # Will be updated when requirements are confirmed
                    report_type="pending",  # Will be determined from requirements
                )

            # Update chain with memory
            self.chain.memory = self.memory

            # Process the query
            result = await self.chain.arun(input=query)

            # clear the memory
            self.memory.clear()
            self.chain.memory = self.memory

            # Check if this is a requirements summary
            if "---REQUIREMENTS SUMMARY---" in result:
                # Extract the complete summary including the confirmation question
                summary_text = (
                    result.split("---REQUIREMENTS SUMMARY---")[1]
                    .split("---END SUMMARY---")[0]
                    .strip()
                )

                # Update report with the new summary
                await update_report_step(
                    chat_id,
                    step=ReportGenerationStep.UNDERSTANDING_REQUIREMENTS,
                    additional_data={
                        "requirements_summary": summary_text,
                        "last_updated": datetime.utcnow().isoformat(),
                    },
                )
                has_final_summary = True

            parent_message_id = (
                int(parent_message_id) if parent_message_id is not None else 0
            )

            await create_chat_message(
                eds_chat_history_id=str(chat_id),
                query=query,
                response=result,
                userid=userid,
                parent_message_id=parent_message_id,
                chat_message_collection=CHAT_MESSAGES_REPORT_COLLECTION,
                chat_history_collection=EDS_REPORT_CHAT_HISTORY_COLLECTION,
            )

            # Get the current report state
            current_report = await get_report(chat_id, userid)
            requirements_summary = (
                current_report.get("requirements_summary", "") if current_report else ""
            )
            if requirements_summary != "":
                has_final_summary = True

            messages = await get_chat_messages(
                str(chat_id),
                chat_message_collection=CHAT_MESSAGES_REPORT_COLLECTION,
            )
            if not messages:
                raise FailedToCreateError(detail="Failed to create chat message")

            last_message = messages[-1]["messages"][-1]
            message_id = last_message["id"]

            return {
                "response": result,
                "chat_id": chat_id,
                "message_id": message_id,
                "parent_message_id": parent_message_id,
                "requirements": requirements_summary,
                "has_final_summary": has_final_summary,
            }

        except Exception as e:
            logger.error(f"Failed to process query for user {userid}: {e}")
            raise InternalServerError(detail="Failed to process query")

    def _generate_chat_title(self, query: str) -> str:
        """Generate a title for the chat session based on the initial query"""
        prompt = PromptTemplate(
            input_variables=["query"],
            template="""Generate a concise, professional title for a report generation chat session based on this query.
            The title should be descriptive but brief (5-7 words).
            Query: {query}
            Title:""",
        )
        chain = LLMChain(llm=self.model, prompt=prompt, verbose=False)
        title = chain.run(query=query).strip()
        return title.strip("\"'")
