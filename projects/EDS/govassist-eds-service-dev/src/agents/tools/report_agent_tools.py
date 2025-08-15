from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from loguru import logger

from src.agents.report_generator.report_state import ReportAgentState
from src.schema.report_schema import (
    ReportConfigurationCreateSchema,
    ReportConfigurationCreateSchemaTool,
    ReportConfigurationResponseSchema,
    ReportConfigurationUpdateSchema,
    ReportConfigurationUpdateSchemaTool,
    SubReportBase,
)
from src.schema.report_schema import SubReportCreate as SubReportCreateSchema
from src.schema.report_schema import SubReportInfo, SubReportUpdate
from src.schema.report_template_schema import ReportTemplateFind, ReportTemplateInfo
from src.services.reports_service import (
    ReportConfigurationService,
    ReportTemplateService,
    TagService,
)
from src.services.sub_report_service import SubReportService


@tool(
    name_or_callable="update_state",
    description="Use this tool to update the current report-building session state. Always call this tool immediately after collecting any of the following information from the user: report_name, report_description, report_tags, report_schedule, template, entity, field, or formula. Call this tool even if only one of these values is provided or updated. This helps track the user's progress across multiple steps. Provide only the fields to update as a dictionary in `new_state`.",
)
def update_state(
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[ReportAgentState, InjectedState],
    new_state: dict = None,
) -> Command:
    """
    Use this tool to update the current report-building session state.
    Always call this tool immediately after collecting any of the following information from the user:

    - report_name
    - report_description
    - report_tags
    - report_schedule
    - report_configs

    Call this tool even if only one of these values is provided or updated.
    This helps track the user's progress across multiple steps.
    Provide only the fields to update as a dictionary in `new_state`.
    Args:
        new_state: The new state to update (dict of fields to update), e.g., {"report_name": "IDCR forecast FY25"}
    """
    # TODO: NEED to handle proper validation before updating the state
    state.update(new_state)
    state["messages"].append(
        ToolMessage("State updated successfully", tool_call_id=tool_call_id)
    )
    return Command(update={**state})


def create_report_tool(
    report_configuration_service: ReportConfigurationService,
    tag_service: TagService,
    current_user: dict,
):

    @tool(
        name_or_callable="create_report",
        description="Use this tool to create a new report. This tool should be called only after the user has provided all the necessary information to create a report.",
    )
    def create_report(
        tool_call_id: Annotated[str, InjectedToolCallId],
        report_schema: ReportConfigurationCreateSchemaTool,
    ) -> Command:
        """
        Use this tool to create a new report. This tool should be called only after the user has provided all the necessary information to create a report.

        Args:
            report_schema: The report schema to create a new report.
            user_id: The ID of the current user creating the report.
        """
        try:
            tags = []
            report_schema_dict = report_schema.model_dump(exclude_unset=True)
            if report_schema.tags:
                tags = tag_service.get_or_create_tags(report_schema.tags)
                report_schema_dict["tags"] = [tag["id"] for tag in tags]

            create_report_schema = ReportConfigurationCreateSchema.model_validate(
                report_schema_dict
            )
            report_config = report_configuration_service.add(
                create_report_schema, current_user.id
            )
            return ToolMessage(
                f"Report created successfully with id: {report_config.id}",
                tool_call_id=tool_call_id,
            )
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            return ToolMessage(
                f"Failed to create report: {str(e)}", tool_call_id=tool_call_id
            )

    return create_report


def update_report_tool(
    report_configuration_service: ReportConfigurationService, tag_service: TagService
):

    @tool(
        name_or_callable="update_report",
        description="Use this tool to update an existing report. This tool should be called only after the user has provided all the necessary information to update a report.",
    )
    def update_report(
        tool_call_id: Annotated[str, InjectedToolCallId],
        report_id: int,
        report_schema: ReportConfigurationUpdateSchemaTool,
    ) -> Command:
        """
        Use this tool to update an existing report. This tool should be called only after the user has provided all the necessary information to update a report.

        Args:
            report_id: The ID of the report to update.
            report_schema: The report schema with updated values.
        """
        try:
            tags = []
            report_schema_dict = report_schema.model_dump(exclude_unset=True)
            if report_schema.tags:
                tags = tag_service.get_or_create_tags(report_schema.tags)
                report_schema_dict["tags"] = [tag["id"] for tag in tags]

            update_report_schema = ReportConfigurationUpdateSchema.model_validate(
                report_schema_dict
            )
            report_config = report_configuration_service.patch(
                report_id, update_report_schema
            )
            return ToolMessage(
                f"Report updated successfully with id: {report_config.id}",
                tool_call_id=tool_call_id,
            )
        except Exception as e:
            logger.error(f"Error updating report: {e}")
            return ToolMessage(
                f"Failed to update report: {str(e)}", tool_call_id=tool_call_id
            )

    return update_report


def get_available_fields_tool(report_configuration_service: ReportConfigurationService):

    @tool(
        name_or_callable="get_available_fields",
        description="Use this tool to get the available fields for the report.",
    )
    def get_available_fields(
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """
        Use this tool to get the available fields for the report.
        """
        try:
            available_fields = report_configuration_service.get_fields([])
            return ToolMessage(
                f"Available fields: {available_fields}", tool_call_id=tool_call_id
            )
        except Exception as e:
            logger.error(f"Error getting available fields: {e}")
            return ToolMessage(
                f"Failed to get available fields: {str(e)}", tool_call_id=tool_call_id
            )

    return get_available_fields


def get_available_templates_tool(report_template_service: ReportTemplateService):

    @tool(
        name_or_callable="get_available_templates",
        description="Use this tool to get the available templates for the report.",
    )
    def get_available_templates(tool_call_id: Annotated[str, InjectedToolCallId]):
        """
        Use this tool to get the available templates for the report.
        """
        try:
            find = ReportTemplateFind(
                page_size="all",
            )
            available_templates = report_template_service.get_list(find, [],[])
            available_templates = [
                {
                    "template_name": template.name,
                    "template_id": template.id,
                    "template_description": template.description,
                }
                for template in available_templates["founds"]
            ]
            return ToolMessage(
                f"Available templates: {available_templates}", tool_call_id=tool_call_id
            )
        except Exception as e:
            logger.error(f"Error getting available templates: {e}")
            return ToolMessage(
                f"Failed to get available templates: {str(e)}",
                tool_call_id=tool_call_id,
            )

    return get_available_templates


def get_templates_details_tool(report_template_service: ReportTemplateService):

    @tool(
        name_or_callable="get_templates_details",
        description="Use this tool to get the details of the templates for the report. Args: template_id: The ID of the template to get the details of.",
    )
    def get_templates_details(
        tool_call_id: Annotated[str, InjectedToolCallId], template_id: int
    ):
        """
        Use this tool to get the details of the templates for the report.
        Args:
            template_id: The ID of the template to get the details of.
        """
        try:
            template_details = report_template_service.get_by_id(template_id)
            template_details = ReportTemplateInfo.model_validate(template_details)
            return ToolMessage(
                f"Template details: {template_details}", tool_call_id=tool_call_id
            )
        except Exception as e:
            logger.error(f"Error getting available templates: {e}")
            return ToolMessage(
                f"Failed to get available templates: {str(e)}",
                tool_call_id=tool_call_id,
            )

    return get_templates_details


def create_sub_report_tool(sub_report_service: SubReportService):

    @tool(
        name_or_callable="create_sub_report",
        description="Use this tool to create sub report for the report.",
    )
    def create_sub_report(
        tool_call_id: Annotated[str, InjectedToolCallId],
        report_id: int,
        sub_report_config: list[SubReportBase],
    ):
        """
        Use this tool to create sub report for the report.
        """
        try:
            sub_report_list = []
            for sub_report_config in sub_report_config:
                sub_report = SubReportCreateSchema(
                    report_configuration_id=report_id,
                    name=sub_report_config.name,
                    description=sub_report_config.description,
                    config=sub_report_config.config,
                )
                sub_report = sub_report_service.add(sub_report)
                sub_report_list.append(SubReportInfo.model_validate(sub_report))
            return ToolMessage(
                f"Sub report created: {sub_report_list}", tool_call_id=tool_call_id
            )
        except Exception as e:
            logger.error(f"Error getting available templates: {e}")
            return ToolMessage(
                f"Failed to get available templates: {str(e)}",
                tool_call_id=tool_call_id,
            )

    return create_sub_report


def update_sub_report_tool(sub_report_service: SubReportService):

    @tool(
        name_or_callable="update_sub_report",
        description="Use this tool to update sub report for the report.",
    )
    def update_sub_report(
        tool_call_id: Annotated[str, InjectedToolCallId],
        sub_report_id: int,
        sub_report_config: SubReportUpdate,
    ):
        """
        Use this tool to update sub report for the report.
        """
        try:
            sub_report = sub_report_service.patch(
                sub_report_id, sub_report_config, exclude_none=False, exclude_unset=True
            )
            return ToolMessage(
                f"Sub report updated: {sub_report}", tool_call_id=tool_call_id
            )
        except Exception as e:
            logger.error(f"Error updating sub report: {e}")
            return ToolMessage(
                f"Failed to update sub report: {str(e)}", tool_call_id=tool_call_id
            )

    return update_sub_report


def get_report_details_tool(report_configuration_service: ReportConfigurationService):

    @tool(
        name_or_callable="get_report_details",
        description="Use this tool to get the details of the report. Args: report_id: The ID of the report to get the details of.",
    )
    def get_report_details(
        tool_call_id: Annotated[str, InjectedToolCallId],
        report_id: int,
    ) -> Command:
        """
        Use this tool to get the details of the report.
        Args:
            report_id: The ID of the report to get the details of.
        """
        try:
            report_details = report_configuration_service.get_by_id(report_id)
            report_deatils_schema = ReportConfigurationResponseSchema.model_validate(
                report_details
            )

            return ToolMessage(
                f"Report details with it sub reports: {report_deatils_schema}",
                tool_call_id=tool_call_id,
            )
        except Exception as e:
            logger.error(f"Error getting report details: {e}")
            return ToolMessage(
                f"Failed to get report details: {str(e)}", tool_call_id=tool_call_id
            )

    return get_report_details
