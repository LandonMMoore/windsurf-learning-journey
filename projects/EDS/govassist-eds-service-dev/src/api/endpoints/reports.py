from typing import Annotated, List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Query

from src.agents.report_generator.report_agent import FormulaAssistantAgent, ReportAgent, ReportAgent_v2
from src.core.container import Container
from src.core.dependencies import get_current_user
from src.core.exceptions import ValidationError
from src.elasticsearch.service import es_service
from src.schema.base_schema import UniqueValuesResult
from src.schema.report_metadata_schema import (
    ReportMetadataFind,
    ReportMetadataListResponse,
)
from src.schema.report_schema import (
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    FormulaAssistantChatHistoryResponse,
    FormulaAssistantChatRequest,
    FormulaAssistantResponse,
    MasterModelUniqueValues,
    ReportAgentResponseFeedback,
    ReportConfigurationCreateSchema,
    ReportConfigurationFind,
    ReportConfigurationListResponse,
    ReportConfigurationQueryElasticsearch,
    ReportConfigurationResponseSchema,
    ReportConfigurationUpdateSchema,
    ReportFieldsFind,
    ReportFind,
    ReportFunctionResponse,
    SharedDataFind,
    ValidSchema,
)
from src.schema.report_template_schema import (
    ReportTemplateCreate,
    ReportTemplateExtractBase,
    ReportTemplateFind,
    ReportTemplateInfo,
    ReportTemplateListResponse,
    ReportTemplateUpdate,
)
from src.schema.tag_schema import TagCreate, TagFind, TagInfo, TagListResponse
from src.schema.unique_values_schema import UniqueValuesResponse
from src.services.nosql_llm_logger_service import NosqlLLMLoggerService
from src.services.redis_service import RedisService
from src.services.reports_service import (
    FormulaAssistantChatHistoryService,
    ReportChatHistoryService,
    ReportConfigurationService,
    ReportMetadataService,
    ReportTemplateService,
    TagService,
)
from src.services.sub_report_service import SubReportService

router = APIRouter(prefix="/reports", tags=["reports"])



# Agent api with suoervisor agent
@router.post("/chat", response_model=ChatResponse)
@inject
async def chat_with_agent(
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    report_chat_history_service: ReportChatHistoryService = Depends(
        Provide[Container.report_chat_history_service]
    ),
    report_configuration_service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
    report_template_service: ReportTemplateService = Depends(
        Provide[Container.report_template_service]
    ),
    sub_report_service: SubReportService = Depends(
        Provide[Container.sub_report_service]
    ),
    nosql_llm_logger_service: NosqlLLMLoggerService = Depends(
        Provide[Container.nosql_llm_logger_service]
    ),
    tag_service: TagService = Depends(Provide[Container.tag_service]),
):
    with ReportAgent(
        report_chat_history_service=report_chat_history_service,
        report_configuration_service=report_configuration_service,
        report_template_service=report_template_service,
        sub_report_service=sub_report_service,
        tag_service=tag_service,
        nosql_llm_logger_service=nosql_llm_logger_service,
        current_user=current_user,
    ) as report_agent:
        chat_history = await report_agent.chat(
            report_configuration_service, chat_request, current_user.id
        )
    return ChatResponse(
        response=chat_history["response"],
        chat_id=chat_history["chat_id"],
        message_id=chat_history["message_id"],
    )


# Agent api with suoervisor agent
@router.post("/chat_v2", response_model=ChatResponse)
@inject
async def chat_with_agent(
    chat_request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    report_chat_history_service: ReportChatHistoryService = Depends(
        Provide[Container.report_chat_history_service]
    ),
    formula_assistant_chat_history_service: FormulaAssistantChatHistoryService = Depends(
        Provide[Container.formula_assistant_chat_history_service]
    ),
    report_configuration_service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
    report_template_service: ReportTemplateService = Depends(
        Provide[Container.report_template_service]
    ),
    sub_report_service: SubReportService = Depends(
        Provide[Container.sub_report_service]
    ),
    nosql_llm_logger_service: NosqlLLMLoggerService = Depends(
        Provide[Container.nosql_llm_logger_service]
    ),
    tag_service: TagService = Depends(Provide[Container.tag_service]),
):
    with ReportAgent_v2(
        report_chat_history_service=report_chat_history_service,
        formula_assistant_chat_history_service=formula_assistant_chat_history_service,
        report_configuration_service=report_configuration_service,
        report_template_service=report_template_service,
        sub_report_service=sub_report_service,
        tag_service=tag_service,
        nosql_llm_logger_service=nosql_llm_logger_service,
        current_user=current_user,
    ) as report_agent:
        chat_history = await report_agent.chat(
            report_configuration_service, chat_request, current_user.id
        )
    return ChatResponse(
        response=chat_history["response"],
        chat_id=chat_history["chat_id"],
        message_id=chat_history["message_id"],
    )


@router.get("/chat-history/{chat_id}", response_model=List[ChatHistoryResponse])
@inject
async def get_chat_history(
    chat_id: int,
    current_user: dict = Depends(get_current_user),
    service: ReportChatHistoryService = Depends(
        Provide[Container.report_chat_history_service]
    ),
):
    return await service.get_chat_history(chat_id, current_user.id)


@router.post("/report-agent-response-feedback")
@inject
async def report_agent_response_feedback(
    response_feedback: ReportAgentResponseFeedback,
    service: ReportChatHistoryService = Depends(
        Provide[Container.report_chat_history_service]
    ),
    current_user: dict = Depends(get_current_user),
):
    return await service.report_agent_response_feedback(
        response_feedback, current_user.id
    )


# generate formula assistant
@router.post("/formula-assistant", response_model=FormulaAssistantResponse)
@inject
async def generate_formula_assistant(
    chat_request: FormulaAssistantChatRequest,
    current_user: dict = Depends(get_current_user),
    formula_assistant_chat_history_service: FormulaAssistantChatHistoryService = Depends(
        Provide[Container.formula_assistant_chat_history_service]
    ),
    report_configuration_service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
    nosql_llm_logger_service: NosqlLLMLoggerService = Depends(
        Provide[Container.nosql_llm_logger_service]
    ),
    sub_report_service: SubReportService = Depends(
        Provide[Container.sub_report_service]
    ),
):
    with FormulaAssistantAgent(
        formula_chat_history_service=formula_assistant_chat_history_service,
        report_configuration_service=report_configuration_service,
        sub_report_service=sub_report_service,
        nosql_llm_logger_service=nosql_llm_logger_service,
        current_user=current_user,
    ) as formula_assistant_agent:
        chat_history = await formula_assistant_agent.chat(chat_request, current_user.id)
    return chat_history


@router.get(
    "/formula-assistant-chat-history/{chat_id}",
    response_model=list[FormulaAssistantChatHistoryResponse],
)
@inject
async def get_formula_assistant_chat_history(
    chat_id: int,
    current_user: dict = Depends(get_current_user),
    service: FormulaAssistantChatHistoryService = Depends(
        Provide[Container.formula_assistant_chat_history_service]
    ),
):
    return await service.get_chat_history(chat_id, current_user.id)


@router.get("/master-data-source-list")
@inject
def get_master_data_source_list(
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return service.get_master_data_source_list()


# Get Fields list api
@router.get("/fields")
@inject
def get_fields(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: ReportFieldsFind = Depends(),
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return service.get_fields(searchable_fields, find.search, find.ordering)


# tags endpoints


@router.get("/tags", response_model=TagListResponse)
@inject
def get_tags(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: TagFind = Depends(),
    service: TagService = Depends(Provide[Container.tag_service]),
):
    return service.get_list(find, searchable_fields)


@router.post("/tags", response_model=TagInfo)
@inject
def create_tag(
    tag: TagCreate,
    service: TagService = Depends(Provide[Container.tag_service]),
):
    return service.add(tag)


@router.get(
    "/unique-values",
    response_model=UniqueValuesResponse,
    status_code=200,
    summary="Get unique values from Elasticsearch field",
    description="""
    Extract unique values from a specified field in an Elasticsearch index.
    
    Features:
    - Pagination support with page and size parameters
    - Search filtering using match_phrase_prefix
    - Alphabetical ordering (asc/desc)
    - Support for both regular and nested fields
    - Proper error handling and validation
    
    Returns a paginated list of unique values with metadata.
    
    **Field Types Supported:**
    - Regular fields: `field_name`
    - Nested fields: `parent.child.grandchild` (e.g., `user.address.city`)
    
    **Examples:**
    - Regular field: `GET /api/v1/unique-values?index=users&field=department`
    - Nested field: `GET /api/v1/unique-values?index=users&field=address.city`
    - Deep nested: `GET /api/v1/unique-values?index=orders&field=items.product.category`
    """,
)
async def get_unique_values(
    index: str = Query(..., description="Elasticsearch index name"),
    field: str = Query(..., description="Field name to extract unique values for"),
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    size: int = Query(
        default=10, ge=1, le=1000, description="Number of items per page"
    ),
    search: Optional[str] = Query(
        default=None, description="Search term to filter values"
    ),
    order: str = Query(
        default="asc", pattern="^(asc|desc)$", description="Sort order: asc or desc"
    ),
) -> UniqueValuesResponse:
    """
    Get unique values from a specified field in an Elasticsearch index.

    Args:
        index: Elasticsearch index name
        field: Field name to extract unique values for
        page: Page number (1-based, default: 1)
        size: Number of items per page (default: 10, max: 1000)
        search: Optional search term to filter values
        order: Sort order - 'asc' or 'desc' (default: 'asc')

    Returns:
        UniqueValuesResponse with paginated values and metadata

    Raises:
        ValidationError: If index or field is invalid
        NotFoundError: If index doesn't exist
    """
    try:
        # Validate inputs
        if not index.strip():
            raise ValidationError("Index name cannot be empty")

        if not field.strip():
            raise ValidationError("Field name cannot be empty")

        # Get unique values from Elasticsearch
        result = await es_service.get_unique_values(
            index=index, field=field, page=page, size=size, search=search, order=order
        )

        return UniqueValuesResponse(
            values=result["values"],
            total=result["total"],
            page=page,
            size=size,
            total_pages=(result["total"] + size - 1) // size,
        )

    except ValidationError:
        raise

    except Exception as e:
        # Handle Elasticsearch-specific errors
        if "index_not_found_exception" in str(e):
            raise ValidationError(f"Index '{index}' not found")
        elif "field_not_found_exception" in str(e):
            raise ValidationError(f"Field '{field}' not found in index '{index}'")
        else:
            # Log the error and raise a generic error
            raise ValidationError("Failed to retrieve unique values")


@router.post("/data-query")
@inject
async def data_query(
    query: ReportConfigurationQueryElasticsearch,
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return await service.data_query(query)


@router.get("/metadata", response_model=ReportMetadataListResponse)
@inject
def get_report_metadata(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: ReportMetadataFind = Depends(),
    service: ReportMetadataService = Depends(
        Provide[Container.report_metadata_service]
    ),
):
    return service.get_list(find, searchable_fields)


# Report Template


@router.post("/template", response_model=ReportTemplateInfo)
@inject
def create_report_template(
    report_template: ReportTemplateCreate,
    user: dict = Depends(get_current_user),
    service: ReportTemplateService = Depends(
        Provide[Container.report_template_service]
    ),
):
    report_template.created_by_id = user.id
    return service.add(report_template)


@router.post("/template/extract", response_model=ReportTemplateInfo)
@inject
def extract_report_template(
    report_template: ReportTemplateExtractBase,
    user: dict = Depends(get_current_user),
    service: ReportTemplateService = Depends(
        Provide[Container.report_template_service]
    ),
):
    report_template.created_by_id = user.id
    return service.extract_report_template(report_template)


@router.get("/template", response_model=ReportTemplateListResponse)
@inject
def get_report_templates(
    find: ReportTemplateFind = Depends(),
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    tags: Annotated[Optional[List[str]], Query()] = [],
    service: ReportTemplateService = Depends(
        Provide[Container.report_template_service]
    ),
):
    return service.get_list(find, searchable_fields, tags)


@router.get("/supported-dynamic-filters-by-field-type")
@inject
def get_supported_data_types(
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return service.get_supported_data_types()


@router.get("/template/{report_template_id}", response_model=ReportTemplateInfo)
@inject
def get_report_template(
    report_template_id: int,
    service: ReportTemplateService = Depends(
        Provide[Container.report_template_service]
    ),
):
    return service.get_by_id(report_template_id)


@router.patch("/template/{report_template_id}", response_model=ReportTemplateInfo)
@inject
def update_report_template(
    report_template_id: int,
    report_template: ReportTemplateUpdate,
    service: ReportTemplateService = Depends(
        Provide[Container.report_template_service]
    ),
):
    return service.patch(report_template_id, report_template)


@router.delete("/template/{report_template_id}")
@inject
def delete_report_template(
    report_template_id: int,
    service: ReportTemplateService = Depends(
        Provide[Container.report_template_service]
    ),
):
    return service.delete_report_template(report_template_id)


@router.get("/report-functions", response_model=List[ReportFunctionResponse])
@inject
def get_report_functions(
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return service.get_report_functions()


@router.get("/get-shared-data")
@inject
def get_shared_data(
    schema_name: ValidSchema = Query(...),
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    find: SharedDataFind = Depends(),
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return service.get_shared_data(schema_name, find, searchable_fields)


@router.get("/master-table-unique-values", response_model=UniqueValuesResult)
@inject
def get_master_table_unique_values(
    schema: MasterModelUniqueValues = Depends(),
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return service.get_master_table_unique_values(schema)


@router.post("", response_model=ReportConfigurationResponseSchema)
@inject
def create_report(
    report: ReportConfigurationCreateSchema,
    current_user: dict = Depends(get_current_user),
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return service.add(report, current_user.id)


@router.get("", response_model=ReportConfigurationListResponse)
@inject
def get_reports(
    searchable_fields: Annotated[Optional[List[str]], Query()] = [],
    tags: Annotated[Optional[List[str]], Query()] = [],
    find: ReportConfigurationFind = Depends(),
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return service.get_list(find, searchable_fields, tags)


@router.get("/{report_id}", response_model=ReportConfigurationResponseSchema)
@inject
def get_report(
    report_id: int,
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return service.get_by_id(report_id)


@router.patch("/{report_id}", response_model=ReportConfigurationResponseSchema)
@inject
def update_report(
    report_id: int,
    report: ReportConfigurationUpdateSchema,
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return service.patch(report_id, report)


@router.delete("/{report_id}")
@inject
def delete_report(
    report_id: int,
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return service.remove_by_id(report_id)


@router.post("/{report_id}/preview/{sub_report_id}")
@inject
async def preview_report(
    report_id: int,
    sub_report_id: int,
    find: ReportFind = Body(...),
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
    redis_service: RedisService = Depends(Provide[Container.redis_service]),
):
    return await service.preview_report(report_id, sub_report_id, find, redis_service)


@router.post("/{report_id}/trigger-export")
@inject
async def export_report(
    report_id: int,
    current_user: dict = Depends(get_current_user),
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return await service.export_report(report_id, current_user.id)


@router.get("/{report_id}/export-status")
@inject
async def export_status(
    report_id: int,
    service: ReportConfigurationService = Depends(
        Provide[Container.report_configuration_service]
    ),
):
    return await service.export_status(report_id)
