import json
from typing import Any, Dict, List, Optional

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import StructuredTool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from loguru import logger

from src.agents.tools.available_fields_tool import format_fields_for_display
from src.agents.tools.es_tools import es_query_tool
from src.core.config import configs
from src.core.exceptions import InternalServerError
from src.mongodb.report_services import (
    add_additional_section_question,
    add_clarifying_question,
    get_report,
    update_requirement_summary,
    update_selected_fields,
)

model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    api_key=configs.OPENAI_API_KEY,
)


class ClarifyAgent:
    def __init__(
        self,
        list_of_fields: List[str] = None,
        requirement_summary: str = None,
        query: str = None,
    ):
        self.selected_fields = list_of_fields or []
        self.requirement_summary = requirement_summary or ""
        self.available_fields = format_fields_for_display()
        # self.query = query if query != "" else "Work upon the query and generate the clarifying questions and sample question."
        self.query = query
        self.tool = [
            StructuredTool.from_function(
                func=es_query_tool,
                name="es_query_tool",
                description="""Example:
                    {{
                        "size": 20,
                        "query": {{
                            "bool": {{
                                "must": [
                                    {{
                                        "nested": {{
                                            "path": "budget_info",
                                            "query": {{
                                                "match_all": {{}}
                                            }}
                                        }}
                                    }}
                                ]
                            }}
                        }},
                        "_source": [
                            "total_project_budget",
                            "budget_info.budget_items.lifetime_budget",
                            "budget_info.budget_items.initial_allotment",
                        ]
                    }}
                    
                Note: The query must be wrapped in a query_input object, with index as a separate parameter.
            """,
            )
        ]

    def get_prompt_template_clarify_section(self):
        if self.query == "":
            return ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        content=f"""
                    You are a world-class requirements analyst and clarifying question generator.
                    Your objective is to analyze the requirement summary and generate precise, meaningful clarifying questions to resolve ambiguities and ensure accurate report generation.
                    Follow the step-by-step instructions in order. Do not skip any steps.

                    Requirements Summary: {self.requirement_summary}
                    Selected Fields: {self.selected_fields}
                    Available Fields: {self.available_fields}

                    Step 1: Requirements Summary Analysis
                        - Identify the selected fields mentioned in the summary.
                        - Proceed to Step 2 with this information.

                    Step 2: (Generate the elastic search query)
                        - Based on the selected fields, generate a valid Elasticsearch query.
                        - Ensure query format adheres to Elasticsearch standards.
                        - Use the following structure:
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
                        - Make sure that the query is generated will be in the format of the elastic search query.
                        - Generate a valid query for the elastic search for search.
                        - Continue immediately to Step 3.

                    Step 3: Execution of the Elasticsearch Query
                        - Use the generated query as-is.
                        - Pass it to es_query_tool.
                        - Retrieve the result and:
                            - Check which selected fields are present in the response.
                            - Separate fields that are found vs. missing.
                            - List only those fields that exist in the actual response.
                        - Continue immediately to Step 4.

                    Step 4: (Analyze the result and question generation)
                        - After getting the result from the Step 2 you need to analyze the result and generate some clarification questions which you found that needed to generate the report.
                        - Make sure the clarification questions are related to the requriements summary and selected fields and data which you have recevied from Step 2.
                        - You are having the list of available fields so you can even generate the clarification questions based on the available fields.
                        - Make sure that the clarification questions are related to the requirements summary and if something is already cleared in the requirements summary then don't generate the clarification questions for that.
                        - Don't generate more than 4 clarification questions at a time.
                        - Question example:
                            - Fiscal Year: which fiscal year this report covers? I'm assuming FY 2024(current), but please confirm specific year.
                            - Project manager: which project manager should be there in the report? I'm assuming John Doe, but please confirm specific name.

                        - As you can see the above question format it is like first part is field name and second part is the question with some sample data you found from the elastic search result.
                        - Don't generate the same question as given in the example.
                        - Also don't generate those type of questions which could be answered in the requirements summary.
                        - Also make sure that the clarification questions are not related to the data which is not present in the result.
                        - Clarification field questions should not be like 
                            - "Created at: What is the created at date of the project \"KA0.PM000A.PLANNING, MANAGEMENT & COMPLIANCE\"? I'm assuming 2024-01-01, but please confirm."
                            - "Updated at: What is the updated at date of the project \"KA0.PM000A.PLANNING, MANAGEMENT & COMPLIANCE\"? I'm assuming 2024-01-01, but please confirm."
                            - "Total Project Budget: What is the total project budget for the project \"KA0.PM000A.PLANNING, MANAGEMENT & COMPLIANCE\"? I'm assuming 12879.6043, but please confirm."
                        - As the above question is not helpful to generate the report.

                        - Question are kind of filtering questions which are related to the data which is present in the result.
                        - Question should help to generate the report.
                        
                        - After generating the clarification questions you need to generate the final question which is combination of above 4 or whatever number of questions you have generated.
                        - Final sample question example:
                            - generate the report for the fiscal year 2024 with the project manager John Doe.

                        - Don't generate the sample question as the same in the example.
                        - Sample question should be generate from the above generated clarification fields based questions.
                        - Don't return any question here just generate the clarification questions and sample question and pass it to the Step 5.
                        - Continue immediately to Step 5.

                    Step 5: Final Output Generation
                        - Generate the final output in this exact Markdown format:
                            # Clarifying Questions
                            1. [Question 1]
                            2. [Question 2]
                            3. [Question 3]

                            # Sample Question
                            [Combined sample question based on the above questions]

                        - Don't generate anything else except the markdown format given in the example.
                        - And make sure the markdown format should be correct and as given in the example.
                        - Output should be in the only above format if there is no data to display then only give the title of those response.
                        - Continue immediately to Step 5.

                    #Important:
                        - Only return the output in the specified Markdown format.
                        - And response should only be generated from the step 5 till that don't generate any other thing and don't break the flow till you complete this steps.
                        - Do not generate questions that are already answered in the input.
                        - The sample question must be derived only from the generated clarifying questions.
                        - When creating the Elasticsearch query, use the correct nested structure and source fields.
                        - Be precise, logical, and avoid random or speculative output.
                        - Give the final output in the format of markdown and the markdown should be same as the example final output format.
                        - DO NOT include any intermediate steps, thought process, or analysis in the final output.
                        - ONLY return the final formatted response as specified in Step 5.
                """
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                    HumanMessage(
                        content="Generate the clarifying questions and sample question for the given requirement summary and selected fields and available fields."
                    ),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
        else:
            return ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        content=f"""
                    You are a world-class requirements analyst and help the user to optimize it's report configuration.
                    Your objective is to analyze the requirement summary and generate precise, meaningful requirement summary and selected fields which will be used to generate the report.
                    Follow the step-by-step instructions in order. Do not skip any steps.

                    Requirements Summary: {self.requirement_summary}
                    Selected Fields: {self.selected_fields}
                    Available Fields: {self.available_fields}

                    Step 1: (query is given to you)
                        - You need to generate the response from the given user query.
                        - User query is having the value for the selected fields or filters for the report.
                        - Here is the sample user query for just example purpose:
                            - Generate the report focusing on the master projects "KA0.MNT00A.MAINTENANCE" and "KA0.PM000A.PLANNING, MANAGEMENT & COMPLIANCE", highlighting expenditures over 1 million, and include all transactions up to the current date.
                        - so by given example you can see that the query is having the value for the selected fields or filters for the report.
                        - After analyzing the user query if user want to add more fields into the report with the filtered result or without the filtered result then you will update the selected fields and requirement summary.
                        - Also update the requirement summary based on the user query so you need to process both the things user query and requirement summary and then generate the updated report configuration and requirement summary.
                        - By reviewing the query you need to generate the updated report configuration.
                        - As above example the updated report configuration is like:
                            - Fiscal Year: 2024
                            - Project Manager: John Doe
                            - Project highlighted: 
                                - KA0.MNT00A.MAINTENANCE
                                - KA0.PM000A.PLANNING, MANAGEMENT & COMPLIANCE
                                - No need to provide all the projects in the report configuration just provide three or four and then add etc at the end.
                            - Expenditure: Over 1 million
                            - Date: Current date
                        - Don't make the report configuration as the same as the user query.
                        - Make the report configuration based on the user query and requirement summary and selected fields as you will have the data of the elastic search result.
                        - But before updating the report configuration you need to review it with the elastic search data.
                        - Generate the elastic search query which will fetch the data from the elastic search.
                            - Use the following structure:
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
                        - And pass the query to the es_query_tool.
                        - After that go to step 7 and generate the final output.
                        - Continue immediately to Step 7.

                    Step 2: (Process the elastic search result)
                        - Use the elastic search result and user query to generate the report configuration.
                        - Also you are having the access to the selected fields and available fields and requirement summary.
                        - You need to have all this things and generate the report configuration.
                        - And mentioned all the things which you think that need to present in the report that should be present in the report configuration.
                        - As above example the updated report configuration is like:
                            - Fiscal Year: 2024
                            - Project Manager: John Doe
                            - Project: KA0.MNT00A.MAINTENANCE, KA0.PM000A.PLANNING, MANAGEMENT & COMPLIANCE
                            - Expenditure: Over 1 million
                            - Date: Current date
                        - Don't make the report configuration as the same as the user query.
                        - Don't give this type of response in the report configuration:
                            - Additional Fields: Include project organization and award associations
                        - instead of this type of response give the response like:
                            - Project Organization: Include project organization : {{value}}
                            - Award Associations: Include award associations : {{value}}
                        - Above is just the example format don't generate the sample response as the same as the example. and for the value you need to pass the actual value form the elastic search result.
                        - Make the report configuration based on the user query and requirement summary and selected fields as you will have the data of the elastic search result..
                        - If user looking for new fields then verify the fields with the elastic search data and if possible then add the fields into the report configuration and update the requirement summary and also update the selected fields.
                        - And add the data associated with the fields if it is like fieltering or sorting or grouping or any other type of data then add the data into the report configuration and update the requirement summary and also update the selected fields.
                        - Add data from the elastic search result into the report configuration and update the requirement summary and also update the selected fields.
                        - Requirement summary should be updated based on the user query and elastic search result and with all the selected fields mentiond in the requirement summary.
                        - Requirement summary should be in more descriptive way so that it could be easy to understand by the user.
                        - Add the selected fields data type in the final output also make sure you will attech the field type from the available fields.
                        - if the field tpye is unknown then attach the field type from the (text, number, date, boolean, array, object) based on the field name and it's data received from the elastic search result.
                        - But before updating the report configuration you need to review it with the elastic search data.
                        - Go to step 8 for the final output generation.

                    Step 3: (Final output generation)
                        - After reviewing the elastic search result and user query you need to generate the final output.
                        - Final output contain the updated requirement summary, selected fields and report configuration given by the user.
                        - Follow up questions should be like:
                            - Would you like to make any changes to the selected fields in the report? Please specify which fields you want to add or remove.
                            - If you would like to update the filtered data in the report? Please specify which field data you would like to update.
                        - Regenerate the follow up question based on the example given in the follow up question section.
                        - Generate the selected field in the below format:
                            "selected_fields": [
                                {{
                                    "field_name": "field_name",
                                    "field_type": "field_type", (fetch it from the available fields)
                                    "field_path": "full.field.path",
                                }}
                            ],
                        - Generate the final output in this exact Markdown format:
                            # Report Configuration
                            [Report configuration]
                            # Selected Fields
                            ```json
                            [Selected fields]
                            ```
                            # Requirement Summary
                            ```json
                            [Requirement summary]
                            ```
                            # Follow up questions
                            [Follow up questions]
                        - Don't generate anything else except the markdown format given in the example.
                        - Output should be in the only above format if there is no data to display then only give the title of those response.

                    #Important:
                        - Only return the output in the specified Markdown format.
                        - And response should only be generated from the step 3 till that don't generate any other thing and don't break the flow till you complete this steps.
                        - Do not generate questions that are already answered in the input.
                        - The sample question must be derived only from the generated clarifying questions.
                        - When creating the Elasticsearch query, use the correct nested structure and source fields.
                        - Be precise, logical, and avoid random or speculative output.
                        - Give the final output in the format of markdown and the markdown should be same as the example final output format.
                        - DO NOT include any intermediate steps, thought process, or analysis in the final output.
                        - ONLY return the final formatted response as specified in Step 3.
                """
                    ),
                    MessagesPlaceholder(variable_name="chat_history"),
                    HumanMessage(content=f"{self.query}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )

    def get_prompt_template_additional_section(self):
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=f"""
                You are a world-class requirements analyst and help the user to optimize it's report configuration.
                Your objective is to analyze the requirement summary and generate precise, meaningful requirement summary and selected fields which will be used to generate the report.
                Follow the step-by-step instructions in order. Do not skip any steps.
                - Analyze the user prompt and generate the response accordingly.

                Requirements Summary: {self.requirement_summary}
                Selected Fields: {self.selected_fields}
                Available Fields: {self.available_fields}

                Step 1: Requirements Summary Analysis
                    - Whatever the user query you need to analyze it and response it properly if possible then generate the elastic search query pass it to step 2 and follow the process with the proper response.
                    - Analyze the requirement summary and selected fields and available fields and user prompt.
                    - If user is looking for the example or dummy data then you need to generate the elastic search query for the selected fields and requirement summary and generate the response accordingly.
                    - And if user is looking for the data then you need to generate the elastic search query for the selected fields and requirement summary and generate the response accordingly.
                    - And user prompt given to you in human message.
                    - After analyzing store it in your memory like:
                        - requirement_summary: [requirement_summary]
                        - selected_fields: [selected_fields]
                        - available_fields: [available_fields]
                        - user_prompt: [user_prompt]
                    - Continue immediately to Step 2.
                    
                Step 2: (Analyzing the user prompt and generate the elastic search query)
                    - Analyze the user prompt and generate the elastic search query.
                    - You are having the access to the selected fields and available fields so try to generate the fields as possbile as you can based on the user prompt.
                    - It should have all the related data which is present in the user prompt and also it should cover those data which are in selected fields and available fields so it could be easy to generate the further response.
                    - After that make sure the requirement summary should be in the mind and along with that the elastic search query should be generated.
                    - Use the below structure to generate the elastic search query:
                            {{
                                "size": 20,
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
                    - Make sure the generate elastic search query is correct and valid in es query format.
                    - After generating the elastic search query go to step 3.



                Step 3: (Analyzing the elastic search query and generate the requirement summary and selected fields)
                    - After receving the es query pass it to the es_query_tool.
                    - If you don't have the data in the elastic search then update elastic search query and pass it to the es_query_tool.
                    - After that you will get the result from the elastic search.
                    - Analyze the result and generate the requirement summary and selected fields.
                    - Make sure you preseve the old requirement summary into the new requirement summary and it should be the updated verision of requriement summary.
                    - Here is example of selected fields:
                        {{
                            "field_name": "field_name",
                            "field_type": "field_type", (fetch it from the available fields)
                            "field_path": "full.field.path",
                        }}
                    - After having the selected fields you need to generate the report configuration and requirement summary from those data related to the selected fields.
                    - And from the recevied result, requriement summary, selected fields and available fields you need to generate the report configuration.
                        - Report configuration should be in the below format:
                            - Fiscal Year: 2024
                            - Project Manager: John Doe
                            - Project: 
                                - KA0.MNT00A.MAINTENANCE
                                - KA0.PM000A.PLANNING, MANAGEMENT & COMPLIANCE
                                - No need to provide all the projects in the report configuration just provide three or four and then add etc at the end.
                            - Expenditure: Over 1 million
                            - Date: Current date
                    - Above format is just an example don't generate the sample response as the same as the example.
                    - Don't make the report configuration as the same as the user query.
                    - Don't give this type of response in the report configuration:
                        - Additional Fields: Include project organization and award associations
                    - instead of this type of response give the response like:
                        - Project Organization: Include project organization : {{value}}
                        - Award Associations: Include award associations : {{value}}
                    - Above is just the example format don't generate the sample response as the same as the example. and for the value you need to pass the actual value form the elastic search result.
                    - Make the report configuration based on the user query and requirement summary and selected fields as you will have the data of the elastic search result.
                    - For requirement summary, follow these steps:
                        1. First, identify all filters from the report configuration and user query
                        2. Then, identify grouping criteria based on the selected fields
                        3. Finally, determine sorting criteria based on the data requirements
                        4. Generate the description by combining these elements in a natural language format
                    - The requirement summary should be structured as:
                        {{
                            "description": "Generate a comprehensive description that includes:
                                - All filters identified (e.g., 'positive current balances', 'expenditures over threshold')
                                - Grouping criteria (e.g., 'by budget analyst', 'by project')
                                - Sorting criteria (e.g., 'by expenditures descending')
                                - Any specific date ranges or fiscal years
                                - Key metrics or thresholds to be highlighted",
                            "filters": ["list of all identified filters"],
                            "grouping": ["list of grouping criteria"],
                            "sorting": ["list of sorting criteria"]
                        }}
                    - The description should be a single, coherent paragraph that incorporates all filters, grouping, and sorting criteria.
                    - Example of a good description:
                        "The report forecasts FY25 based on FY24 expenditure, focusing on accounts with positive current balances, expenditures over a certain threshold, and outstanding obligations. It includes all transactions up to the current date and covers various projects managed by analysts Alicia, Nicole, Latasha, Connie, and Tyler."
                    - After generating the selected fields go to step 4.
                    - After generating the report configuration, selected fields and requirement summary go to step 4.
                    - After generating the requirement summary and selected fields go to step 4.

                Step 4: (Final output generation)
                    - Analyze the user prompt and generate the response accordingly.
                    - And user prompt given to you in human message so you must need to genereate the response like below format.
                    - Generate the final output in this Markdown format:
                        # Overall review
                        [simple string format like a summary of report configuration and selected fields and requirement summary]

                        # Report Configuration
                        [Report configuration in bullet points]

                        # Selected Fields
                        ```json
                        {{
                            "selected_fields": [
                                // Array of field objects
                            ]
                        }}
                        ```

                        # Requirement Summary
                        ```json
                        {{
                            "description": "string",
                            "filters": ["string"],
                            "grouping": ["string"],
                            "sorting": ["string"]
                        }}
                        ```

                        # Follow up questions
                        [List of specific follow-up questions]
                    - And make sure the markdown format should be correct and as given in the example.
                    - Make sure the output should be in the markdown format.

                #Important:
                    - Don't generate any other response then step 4 and output should be in the same format as the step 4 or else it could be in simple markdown format.
                    - Only return the output in the specified Markdown format.
                    - And response should only be generated from the step 1 to step 4 till that don't generate any other thing and don't break the flow till you complete this steps.
                    - Do not generate questions that are already answered in the input.
                    - The sample question must be derived only from the generated clarifying questions.
                    - When creating the Elasticsearch query, use the correct nested structure and source fields.
                    - Be precise, logical, and avoid random or speculative output.
                    - Give the final output in the format of markdown and the markdown should be same as the example final output format.
                    - DO NOT include any intermediate steps, thought process, or analysis in the final output.
                    - ONLY return the final formatted response as specified in Step 4.
            """
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessage(content=f"{self.query}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )


async def clarify_section_agent(
    query: Optional[str] = None,
    userid: str = None,
    chat_id: Optional[int] = None,
    parent_message_id: Optional[int] = None,
):
    try:
        # Handle chat history and context
        if chat_id and chat_id != 0:
            report = await get_report(chat_id, userid)
            if not report:
                raise ValueError(f"Report with ID {chat_id} not found")

            clarifying_questions = report.get("clarifying_questions", [])
            selected_fields = report.get("selected_fields", [])
            requirement_summary = report.get("final_requirements_summary", "")

            clarify_agent = ClarifyAgent(selected_fields, requirement_summary, query)

            # Create memory for the agent
            memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )

            if clarifying_questions:
                for q in clarifying_questions:
                    memory.save_context(
                        {"input": q.get("query", "")}, {"output": q.get("response", "")}
                    )

            # Create the agent
            agent = create_openai_functions_agent(
                llm=model,
                tools=clarify_agent.tool,
                prompt=clarify_agent.get_prompt_template_clarify_section(),
            )

            # Create the agent executor
            agent_executor = AgentExecutor(
                agent=agent, tools=clarify_agent.tool, memory=memory, verbose=True
            )

            response = await agent_executor.ainvoke({"input": query})

            # Extract the JSON response
            response_text = response["output"]

            # Find the markdown content in the response
            if (
                "# Clarifying Questions" in response_text
                and "# Sample Question" in response_text
            ):
                try:
                    # Split the response into sections
                    sections = response_text.split("#")
                    clarifying_questions_section = sections[1].strip()
                    sample_question_section = sections[2].strip()

                    # Extract questions
                    questions = []
                    for line in clarifying_questions_section.split("\n"):
                        if line.strip().startswith(("1.", "2.", "3.", "4.")):
                            questions.append(line.strip().split(". ", 1)[1])

                    # Extract sample question
                    sample_question = sample_question_section.split("\n")[1].strip()

                    # Format the response
                    formatted_response = (
                        "# Clarifying Questions\n"
                        f"{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(questions)])}\n"
                        "# Sample Question\n"
                        f"{sample_question}\n"
                    )

                    # update the clarifying questions in the database
                    result = await add_clarifying_question(
                        chat_id=chat_id,
                        userid=userid,
                        query=query,
                        response=formatted_response,
                        parent_message_id=parent_message_id,
                    )

                    clarifying_question_last_id = result.get("clarifying_questions")[
                        -1
                    ].get("id")
                    parent_message_id = result.get("clarifying_questions")[-1].get(
                        "parent_message_id"
                    )

                    return {
                        "chat_id": chat_id,
                        "message_id": clarifying_question_last_id,
                        "response": formatted_response,
                        "parent_message_id": parent_message_id,
                        "additional_section": False,
                    }
                except Exception as e:
                    logger.error(f"Error parsing markdown response: {e}")
            elif (
                "# Report Configuration" in response_text
                and "# Selected Fields" in response_text
                and "# Requirement Summary" in response_text
            ):
                try:
                    # Split the response into sections
                    sections = response_text.split("#")
                    report_configuration_section = sections[1].strip()
                    selected_fields_section = sections[2].strip()
                    requirement_summary_section = sections[3].strip()
                    follow_up_questions_section = (
                        sections[4].strip() if len(sections) > 4 else ""
                    )

                    # Extract report configuration (handle multiple lines)
                    report_configuration_lines = report_configuration_section.split(
                        "\n"
                    )[1:]
                    report_configuration = "\n".join(
                        [
                            line.strip()
                            for line in report_configuration_lines
                            if line.strip()
                        ]
                    )

                    # Extract selected fields (handle multiple lines)
                    selected_fields_lines = selected_fields_section.split("\n")[1:]
                    selected_fields = "\n".join(
                        [line.strip() for line in selected_fields_lines if line.strip()]
                    )

                    # Extract requirement summary (handle multiple lines)
                    requirement_summary_lines = requirement_summary_section.split("\n")[
                        1:
                    ]
                    requirement_summary = "\n".join(
                        [
                            line.strip()
                            for line in requirement_summary_lines
                            if line.strip()
                        ]
                    )

                    # Extract follow up questions (handle multiple lines)
                    follow_up_questions = ""
                    if follow_up_questions_section:
                        follow_up_questions_lines = follow_up_questions_section.split(
                            "\n"
                        )[1:]
                        follow_up_questions = "\n".join(
                            [
                                line.strip()
                                for line in follow_up_questions_lines
                                if line.strip()
                            ]
                        )

                    # Format the response
                    formatted_response = (
                        "# Report Configuration\n"
                        f"{report_configuration}\n"
                        "# Follow up questions\n"
                        f"{follow_up_questions}\n"
                    )

                    selected_fields_clean = (
                        selected_fields.replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )
                    selected_fields_json = json.loads(selected_fields_clean)

                    # Clean and parse requirement summary
                    requirement_summary_clean = (
                        requirement_summary.replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )
                    requirement_summary_json = json.loads(requirement_summary_clean)
                    requirement_summary_str = requirement_summary_json.get(
                        "description", ""
                    )

                    # Update the selected fields and requirement summary in the database
                    await update_selected_fields(
                        chat_id=chat_id, fields=selected_fields_json
                    )

                    await update_requirement_summary(
                        chat_id=chat_id, summary=requirement_summary_str
                    )

                    result = await add_clarifying_question(
                        chat_id=chat_id,
                        userid=userid,
                        query=query,
                        response=formatted_response,
                        parent_message_id=parent_message_id,
                    )

                    clarifying_question_last_id = result.get("clarifying_questions")[
                        -1
                    ].get("id")
                    parent_message_id = result.get("clarifying_questions")[-1].get(
                        "parent_message_id"
                    )

                    return {
                        "chat_id": chat_id,
                        "message_id": clarifying_question_last_id,
                        "response": formatted_response,
                        "parent_message_id": parent_message_id,
                        "additional_section": False,
                    }
                except Exception as e:
                    logger.error(f"Error parsing markdown response: {e}")
            else:
                logger.error("No markdown content found in response")
            return {
                "chat_id": chat_id,
                "response": """# Clarifying Questions

                    # Sample Question
                """,
                "message_id": parent_message_id,
                "additional_section": False,
            }
        else:
            raise ValueError("Chat ID is required")

    except Exception as e:
        logger.error(f"Error in clarify_question_agent: {e}")
        raise InternalServerError(detail="Internal Server Error")


async def additional_section_agent(
    query: Optional[str] = None,
    userid: str = None,
    chat_id: Optional[int] = None,
    parent_message_id: Optional[int] = None,
) -> Dict[str, Any]:
    try:
        # Handle chat history and context
        if chat_id and chat_id != 0:
            report = await get_report(chat_id, userid)
            if not report:
                raise ValueError(f"Report with ID {chat_id} not found")

            additional_section = report.get("additional_sections", [])
            selected_fields = report.get("selected_fields", [])
            requirement_summary = report.get("final_requirements_summary", "")

            clarify_agent = ClarifyAgent(selected_fields, requirement_summary, query)

            # Create memory for the agent
            memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True
            )

            if additional_section:
                for q in additional_section:
                    memory.save_context(
                        {"input": q.get("query", "")}, {"output": q.get("response", "")}
                    )

            # Create the agent
            agent = create_openai_functions_agent(
                llm=model,
                tools=clarify_agent.tool,
                prompt=clarify_agent.get_prompt_template_additional_section(),
            )

            # Create the agent executor
            agent_executor = AgentExecutor(
                agent=agent, tools=clarify_agent.tool, memory=memory, verbose=True
            )
            response = await agent_executor.ainvoke({"input": query})
            # Extract the JSON response
            response_text = response["output"]

            # Find the markdown content in the response
            if (
                "# Overall review" in response_text
                and "# Report Configuration" in response_text
                and "# Selected Fields" in response_text
                and "# Requirement Summary" in response_text
            ):
                try:
                    # Split the response into sections
                    sections = response_text.split("#")
                    overall_review_section = sections[1].strip()
                    report_configuration_section = sections[2].strip()
                    selected_fields_section = sections[3].strip()
                    requirement_summary_section = sections[4].strip()
                    follow_up_questions_section = (
                        sections[4].strip() if len(sections) > 4 else ""
                    )

                    # Extract overall review (handle multiple lines)

                    overall_review_lines = overall_review_section.split("\n")[1:]
                    overall_review = "\n".join(
                        [line.strip() for line in overall_review_lines if line.strip()]
                    )

                    # Extract report configuration (handle multiple lines)
                    report_configuration_lines = report_configuration_section.split(
                        "\n"
                    )[1:]
                    report_configuration = "\n".join(
                        [
                            line.strip()
                            for line in report_configuration_lines
                            if line.strip()
                        ]
                    )

                    # Extract selected fields (handle multiple lines)
                    selected_fields_lines = selected_fields_section.split("\n")[1:]
                    selected_fields = "\n".join(
                        [line.strip() for line in selected_fields_lines if line.strip()]
                    )

                    # Extract requirement summary (handle multiple lines)
                    requirement_summary_lines = requirement_summary_section.split("\n")[
                        1:
                    ]
                    requirement_summary = "\n".join(
                        [
                            line.strip()
                            for line in requirement_summary_lines
                            if line.strip()
                        ]
                    )

                    # Extract follow up questions (handle multiple lines)
                    follow_up_questions = ""
                    if follow_up_questions_section:
                        follow_up_questions_lines = follow_up_questions_section.split(
                            "\n"
                        )[1:]
                        follow_up_questions = "\n".join(
                            [
                                line.strip()
                                for line in follow_up_questions_lines
                                if line.strip()
                            ]
                        )

                    # Format the response
                    formatted_response = (
                        "# Overall review\n"
                        f"{overall_review}\n"
                        "# Report Configuration\n"
                        f"{report_configuration}\n"
                        "# Follow up questions\n"
                        f"{follow_up_questions}\n"
                    )

                    selected_fields_clean = (
                        selected_fields.replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )
                    selected_fields_json = json.loads(selected_fields_clean)

                    # Clean and parse requirement summary
                    requirement_summary_clean = (
                        requirement_summary.replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )
                    requirement_summary_json = json.loads(requirement_summary_clean)
                    requirement_summary_str = requirement_summary_json.get(
                        "description", ""
                    )

                    # Update the selected fields and requirement summary in the database
                    await update_selected_fields(
                        chat_id=chat_id, fields=selected_fields_json
                    )

                    await update_requirement_summary(
                        chat_id=chat_id, summary=requirement_summary_str
                    )

                    result = await add_additional_section_question(
                        chat_id=chat_id,
                        userid=userid,
                        query=query,
                        response=formatted_response,
                        parent_message_id=parent_message_id,
                    )

                    additional_section_question_last_id = result.get(
                        "additional_sections"
                    )[-1].get("id")
                    parent_message_id = result.get("additional_sections")[-1].get(
                        "parent_message_id"
                    )

                    return {
                        "chat_id": chat_id,
                        "message_id": additional_section_question_last_id,
                        "response": formatted_response,
                        "parent_message_id": parent_message_id,
                        "additional_section": True,
                    }
                except Exception as e:
                    logger.error(f"Error parsing markdown response: {e}")
            else:
                result = await add_additional_section_question(
                    chat_id=chat_id,
                    userid=userid,
                    query=query,
                    response=response_text,
                    parent_message_id=parent_message_id,
                )
                additional_section_question_last_id = result.get("additional_sections")[
                    -1
                ].get("id")
                parent_message_id = result.get("additional_sections")[-1].get(
                    "parent_message_id"
                )
                return {
                    "chat_id": chat_id,
                    "message_id": additional_section_question_last_id,
                    "response": response_text,
                    "parent_message_id": parent_message_id,
                    "additional_section": True,
                }
            return {
                "chat_id": chat_id,
                "message_id": parent_message_id,
                "response": """# Report Configuration

                    # Follow up questions
                """,
                "parent_message_id": parent_message_id,
                "additional_section": True,
            }
        else:
            raise ValueError("chat_id is required")
    except Exception as e:
        logger.error(f"Error in additional_section_agent: {e}")
        return {
            "chat_id": chat_id,
            "message_id": parent_message_id,
            "response": """# Report Configuration

                # Follow up questions
            """,
            "parent_message_id": parent_message_id,
            "additional_section": True,
        }


async def clarify_question_agent(
    query: Optional[str] = None,
    userid: str = None,
    chat_id: Optional[int] = None,
    parent_message_id: Optional[int] = None,
    additional_section: bool = False,
) -> Dict[str, Any]:
    try:
        if not additional_section:
            return await clarify_section_agent(
                query=query,
                userid=userid,
                chat_id=chat_id,
                parent_message_id=parent_message_id,
            )
        else:
            return await additional_section_agent(
                query=query,
                userid=userid,
                chat_id=chat_id,
                parent_message_id=parent_message_id,
            )
    except Exception as e:
        logger.error(
            f"Error in clarify_question_agent or additional_section_agent: {e}"
        )
        raise InternalServerError(detail="Internal Server Error")
