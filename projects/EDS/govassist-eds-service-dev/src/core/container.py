from abs_auth_rbac_core.auth.middleware import auth_middleware
from abs_langchain_suite.logging.db.nosql_client import NoSQLDBClient
from dependency_injector import containers, providers
from motor.motor_asyncio import AsyncIOMotorClient
from socketio import AsyncRedisManager

from src.core.config import configs
from src.core.database import Database
from src.core.redis_client import RedisClient
from src.core.redis_config import RedisConfig
from src.repository.additional_fund_repository import AdditionalFundRepository
from src.repository.award_repository import AwardRepository
from src.repository.budget_analysis_fund_repository import BudgetAnalysisFundRepository
from src.repository.budget_info_repository import BudgetInfoRepository
from src.repository.budget_items_repository import BudgetItemsRepository
from src.repository.cost_center_repository import CostCenterRepository
from src.repository.dashboard_favorite_repository import DashboardFavoriteRepository
from src.repository.dashboard_repository import DashboardRepository
from src.repository.dashboard_widget_repository import DashboardWidgetRepository
from src.repository.federal_fund_repository import FederalFundRepository
from src.repository.fhwa_award_type_repository import FhwaAwardTypeRepository
from src.repository.fhwa_repository import FhwaRepository
from src.repository.fund_repository import FundRepository
from src.repository.integration_repository import IntegrationRepository
from src.repository.integration_sql_repository import IntegrationSqlRepository
from src.repository.master_project_repository import MasterProjectRepository
from src.repository.nosql_llm_logger_repository import NosqlLLMLoggerRepository
from src.repository.organization_repository import OrganizationRepository
from src.repository.par_activity_repository import ParActivityRepository
from src.repository.par_award_association_repository import (
    ParAwardAssociationRepository,
)
from src.repository.par_budget_analysis_repository import ParBudgetAnalysisRepository
from src.repository.par_dashboard_filter_configurations_repository import (
    ParDashboardFilterConfigurationsRepository,
)
from src.repository.par_repository import ParRepository
from src.repository.preconfigured_widget_repository import PreconfiguredWidgetRepository
from src.repository.project_detail_repository import ProjectDetailRepository
from src.repository.project_location_repository import ProjectLocationRepository
from src.repository.reports_repository import (
    FormulaAssistantChatHistoryRepository,
    ReportChatHistoryRepository,
    ReportConfigurationRepository,
    ReportMetadataRepository,
    ReportTemplateRepository,
    TagRepository,
)
from src.repository.sub_report_repository import SubReportRepository
from src.repository.widget_favorite_repository import WidgetFavoriteRepository
from src.repository.workflow_crud_repository import WorkflowCrudRepository
from src.repository.workflow_status_repository import WorkflowStatusRepository
from src.services.additional_fund_service import AdditionalFundService
from src.services.award_service import AwardService
from src.services.budget_analysis_fund_service import BudgetAnalysisFundService
from src.services.budget_info_service import BudgetInfoService
from src.services.budget_items_service import BudgetItemsService
from src.services.cost_center_service import CostCenterService
from src.services.dashboard_favorite_service import DashboardFavoriteService
from src.services.dashboard_service import DashboardService
from src.services.dashboard_widget_service import DashboardWidgetService
from src.services.federal_fund_service import FederalFundService
from src.services.fhwa_award_type_service import FhwaAwardTypeService
from src.services.fhwa_service import FhwaService
from src.services.field_mapping_service import FieldMappingService
from src.services.filter_definitions_service import FilterDefinitionsService
from src.services.filter_integration_service import FilterIntegrationService
from src.services.fund_service import FundService
from src.services.index_compatibility_service import IndexCompatibilityService
from src.services.integration_service import IntegrationService
from src.services.integration_sql_service import IntegrationSqlService
from src.services.master_project_service import MasterProjectService
from src.services.nosql_llm_logger_service import NosqlLLMLoggerService
from src.services.organization_service import OrganizationService
from src.services.par_activity_service import ParActivityService
from src.services.par_award_association_service import ParAwardAssociationService
from src.services.par_budget_analysis_service import ParBudgetAnalysisService
from src.services.par_dashboard_filter_configurations_service import (
    ParDashboardFilterConfigurationsService,
)
from src.services.par_service import ParService
from src.services.par_state_service import ParStateService
from src.services.preconfigured_widget_service import PreconfiguredWidgetService
from src.services.project_detail_service import ProjectDetailService
from src.services.project_location_service import ProjectLocationService
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
from src.services.widget_favorite_service import WidgetFavoriteService
from src.services.workflow_crud_service import WorkflowCrudService
from src.services.workflow_status_service import WorkflowStatusService
from src.socket_io.server import SocketIOService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.api.endpoints.award",
            "src.api.endpoints.budget_info",
            "src.api.endpoints.budget_items",
            "src.api.endpoints.cost_center",
            "src.api.endpoints.federal_fund",
            "src.api.endpoints.fhwa",
            "src.api.endpoints.fund",
            "src.api.endpoints.master_project",
            "src.api.endpoints.fhwa_award_type",
            "src.api.endpoints.project_location",
            "src.api.endpoints.par_award_association",
            "src.api.endpoints.par_activity",
            "src.api.endpoints.project_detail",
            "src.api.endpoints.organization",
            "src.api.endpoints.par",
            "src.api.endpoints.par_meta",
            "src.api.endpoints.key_metrics",
            "src.api.endpoints.additional_fund",
            "src.api.endpoints.par_budget_analysis",
            "src.api.endpoints.budget_analysis_fund",
            "src.api.endpoints.dashboard",
            "src.api.endpoints.dashboard_widget",
            "src.api.endpoints.dashboard_favorite",
            "src.api.endpoints.preconfigured_widget",
            "src.api.endpoints.filter_definitions",
            "src.api.endpoints.filter_configurations",
            "src.api.endpoints.widget_favorite",
            "src.api.endpoints.reports",
            "src.api.endpoints.workflow_status",
            "src.api.endpoints.par_state_api",
            "src.api.endpoints.integration",
            "src.api.endpoints.reports",
            "src.api.endpoints.sub_report",
            "src.api.endpoints.workflow",
            "src.agents.rag_query_v3.summarizer_agent",
            "src.agents.rag_query_v3.unstructured_agent",
        ]
    )

    db = providers.Singleton(Database, db_url=configs.DATABASE_URI)
    session_factory = providers.Object(db().session)

    # MongoDB client for Cosmos DB
    mongo_client = providers.Singleton(
        AsyncIOMotorClient,
        configs.MONGODB_URL,
    )
    # For Gov Assist DB
    mongo_db_for_gov_assist = providers.Factory(
        lambda client: client[configs.MONGODB_DATABASE_FOR_GOV_ASSIST],
        client=mongo_client,
    )

    mongo_db_for_eds = providers.Factory(
        lambda client: client[configs.MONGODB_DATABASE_FOR_EDS],
        client=mongo_client,
    )
    no_sql_client = providers.Factory(NoSQLDBClient, db=mongo_db_for_gov_assist)
    # Redis Configuration
    redis_config = providers.Singleton(
        RedisConfig,
        connection_string=configs.REDIS_URL,
        max_connections=configs.REDIS_MAX_CONNECTIONS,
        default_ttl=configs.REDIS_DEFAULT_TTL,
    )

    # Redis Client
    redis_client = providers.Singleton(
        RedisClient,
        config=redis_config,
    )

    # Redis Service
    redis_service = providers.Factory(
        RedisService,
        redis_client=redis_client,
    )

    # Award
    award_repository = providers.Factory(
        AwardRepository, session_factory=session_factory
    )

    award_service = providers.Factory(AwardService, session_factory=session_factory)

    # Budget Info
    budget_info_repository = providers.Factory(
        BudgetInfoRepository, session_factory=session_factory
    )

    budget_info_service = providers.Factory(
        BudgetInfoService, session_factory=session_factory
    )

    # Budget Items
    budget_items_repository = providers.Factory(
        BudgetItemsRepository, session_factory=session_factory
    )

    budget_items_service = providers.Factory(
        BudgetItemsService, session_factory=session_factory
    )

    # Cost Center
    cost_center_repository = providers.Factory(
        CostCenterRepository, session_factory=session_factory
    )

    cost_center_service = providers.Factory(
        CostCenterService, session_factory=session_factory
    )

    # Federal Fund
    federal_fund_repository = providers.Factory(
        FederalFundRepository, session_factory=session_factory
    )

    federal_fund_service = providers.Factory(
        FederalFundService, session_factory=session_factory
    )

    # FHWA
    fhwa_repository = providers.Factory(FhwaRepository, session_factory=session_factory)

    fhwa_service = providers.Factory(FhwaService, session_factory=session_factory)

    # Fund
    fund_repository = providers.Factory(FundRepository, session_factory=session_factory)

    fund_service = providers.Factory(FundService, session_factory=session_factory)

    # Master Project
    master_project_repository = providers.Factory(
        MasterProjectRepository, session_factory=session_factory
    )

    master_project_service = providers.Factory(
        MasterProjectService, session_factory=session_factory
    )

    # FHWA Award Type
    fhwa_award_type_repository = providers.Factory(
        FhwaAwardTypeRepository, session_factory=session_factory
    )

    fhwa_award_type_service = providers.Factory(
        FhwaAwardTypeService, session_factory=session_factory
    )

    # Project Location
    project_location_repository = providers.Factory(
        ProjectLocationRepository, session_factory=session_factory
    )

    project_location_service = providers.Factory(
        ProjectLocationService, session_factory=session_factory
    )

    # PAR Award Association
    par_award_association_repository = providers.Factory(
        ParAwardAssociationRepository, session_factory=session_factory
    )

    par_award_association_service = providers.Factory(
        ParAwardAssociationService, session_factory=session_factory
    )

    # PAR Activity
    par_activity_repository = providers.Factory(
        ParActivityRepository, session_factory=session_factory
    )

    par_activity_service = providers.Factory(
        ParActivityService, session_factory=session_factory
    )

    # PAR
    par_repository = providers.Factory(ParRepository, session_factory=session_factory)

    par_service = providers.Factory(
        ParService,
        session_factory=session_factory,
        par_activity_service=par_activity_service,
    )

    # PAR Dashboard Filter Configurations
    par_dashboard_filter_configurations_repository = providers.Factory(
        ParDashboardFilterConfigurationsRepository, session_factory=session_factory
    )

    par_dashboard_filter_configurations_service = providers.Factory(
        ParDashboardFilterConfigurationsService, session_factory=session_factory
    )

    # Project Detail
    project_detail_repository = providers.Factory(
        ProjectDetailRepository, session_factory=session_factory
    )

    project_detail_service = providers.Factory(
        ProjectDetailService,
        session_factory=session_factory,
        par_service=par_service,
        par_award_service=par_award_association_service,
    )

    # Organization
    organization_repository = providers.Factory(
        OrganizationRepository, session_factory=session_factory
    )

    organization_service = providers.Factory(
        OrganizationService, session_factory=session_factory
    )

    # PAR Budget Analysis
    par_budget_analysis_repository = providers.Factory(
        ParBudgetAnalysisRepository, session_factory=session_factory
    )

    par_budget_analysis_service = providers.Factory(
        ParBudgetAnalysisService,
        session_factory=session_factory,
        par_service=par_service,
        project_detail_service=project_detail_service,
        budget_info_service=budget_info_service,
    )

    # Budget Analysis Fund
    budget_analysis_fund_repository = providers.Factory(
        BudgetAnalysisFundRepository, session_factory=session_factory
    )

    budget_analysis_fund_service = providers.Factory(
        BudgetAnalysisFundService,
        session_factory=session_factory,
        par_service=par_service,
        par_budget_analysis_service=par_budget_analysis_service,
        federal_fund_service=federal_fund_service,
    )

    # Additional Fund
    additional_fund_repository = providers.Factory(
        AdditionalFundRepository, session_factory=session_factory
    )

    additional_fund_service = providers.Factory(
        AdditionalFundService,
        session_factory=session_factory,
        par_budget_analysis_service=par_budget_analysis_service,
    )

    # Filter Services (moved before dashboard service)
    filter_definitions_service = providers.Singleton(
        FilterDefinitionsService,
    )

    index_compatibility_service = providers.Singleton(
        IndexCompatibilityService,
    )

    field_mapping_service = providers.Singleton(
        FieldMappingService,
    )

    filter_integration_service = providers.Factory(
        FilterIntegrationService,
        index_compatibility_service=index_compatibility_service,
    )

    # Dashboard
    dashboard_repository = providers.Factory(
        DashboardRepository, session_factory=session_factory
    )

    dashboard_favorite_repository = providers.Factory(
        DashboardFavoriteRepository, session_factory=session_factory
    )

    dashboard_favorite_service = providers.Factory(
        DashboardFavoriteService,
        dashboard_favorite_repository=dashboard_favorite_repository,
        dashboard_repository=dashboard_repository,
    )

    dashboard_service = providers.Factory(
        DashboardService,
        session_factory=session_factory,
        dashboard_favorite_service=dashboard_favorite_service,
        index_compatibility_service=index_compatibility_service,
    )

    # Dashboard Widget
    dashboard_widget_repository = providers.Factory(
        DashboardWidgetRepository, session_factory=session_factory
    )
    # Repositories
    widget_favorite_repository = providers.Factory(
        WidgetFavoriteRepository, session_factory=session_factory
    )
    # Services
    widget_favorite_service = providers.Factory(
        WidgetFavoriteService,
        widget_favorite_repository=widget_favorite_repository,
        dashboard_widget_repository=dashboard_widget_repository,
    )

    dashboard_widget_service = providers.Factory(
        DashboardWidgetService,
        widget_favorite_service=widget_favorite_service,
        session_factory=session_factory,
    )

    # Preconfigured Widget
    preconfigured_widget_repository = providers.Factory(
        PreconfiguredWidgetRepository, session_factory=session_factory
    )

    preconfigured_widget_service = providers.Factory(
        PreconfiguredWidgetService, session_factory=session_factory
    )

    # Auth middleware provider
    get_auth_middleware = providers.Factory(
        auth_middleware,
        db_session=session_factory,
        jwt_secret_key=configs.JWT_SECRET_KEY,
        jwt_algorithm=configs.JWT_ALGORITHM,
    )

    # Report Metadata
    report_metadata_repository = providers.Factory(
        ReportMetadataRepository, session_factory=session_factory
    )

    report_metadata_service = providers.Factory(
        ReportMetadataService, session_factory=session_factory
    )

    report_configuration_repository = providers.Factory(
        ReportConfigurationRepository, session_factory=session_factory
    )
    report_configuration_service = providers.Factory(
        ReportConfigurationService, session_factory=session_factory
    )

    # Tag
    tag_repository = providers.Factory(TagRepository, session_factory=session_factory)

    tag_service = providers.Factory(TagService, session_factory=session_factory)

    # Report Template
    report_template_repository = providers.Factory(
        ReportTemplateRepository,
        session_factory=session_factory,
    )

    report_template_service = providers.Factory(
        ReportTemplateService,
        session_factory=session_factory,
    )

    # Workflow Status
    workflow_status_repository = providers.Factory(
        WorkflowStatusRepository, session_factory=session_factory
    )

    workflow_status_service = providers.Factory(
        WorkflowStatusService, session_factory=session_factory
    )

    # Workflow
    workflow_crud_repository = providers.Factory(
        WorkflowCrudRepository, session_factory=session_factory
    )

    workflow_crud_service = providers.Factory(
        WorkflowCrudService, session_factory=session_factory
    )

    # PAR State Service
    par_state_service = providers.Factory(
        ParStateService,
        workflow_status_repository=workflow_status_repository,
        session_factory=session_factory,
    )

    # Sub Report
    sub_report_repository = providers.Factory(
        SubReportRepository, session_factory=session_factory
    )

    sub_report_service = providers.Factory(
        SubReportService, session_factory=session_factory
    )

    socket_io_service = providers.Singleton(
        lambda: SocketIOService(client_manager=AsyncRedisManager(configs.REDIS_URL))
    )

    # MongoDB repositories and services
    # Integration
    integration_sql_repository = providers.Factory(
        IntegrationSqlRepository, session_factory=session_factory
    )
    integration_sql_service = providers.Factory(
        IntegrationSqlService, session_factory=session_factory
    )
    integration_repository = providers.Factory(
        IntegrationRepository, db=mongo_db_for_gov_assist
    )
    integration_service = providers.Factory(
        IntegrationService,
        repository=integration_repository,
        integration_sql_repository=integration_sql_repository,
        redis_service=redis_service,
        workflow_service=workflow_crud_service,
        socket_io_service=socket_io_service,
    )
    # For tracking LLM token usage
    nosql_llm_logger_repository = providers.Factory(
        NosqlLLMLoggerRepository, db=no_sql_client
    )
    nosql_llm_logger_service = providers.Factory(
        NosqlLLMLoggerService,
        nosql_llm_logger_repository=nosql_llm_logger_repository,
    )
    # MongoDB for EDS
    report_chat_history_repository = providers.Factory(
        ReportChatHistoryRepository, db=mongo_db_for_eds
    )

    report_chat_history_service = providers.Factory(
        ReportChatHistoryService,
        report_chat_history_repository=report_chat_history_repository,
    )

    # Formula Assistant Chat History
    formula_assistant_chat_history_repository = providers.Factory(
        FormulaAssistantChatHistoryRepository, db=mongo_db_for_eds
    )

    formula_assistant_chat_history_service = providers.Factory(
        FormulaAssistantChatHistoryService,
        formula_assistant_chat_history_repository=formula_assistant_chat_history_repository,
    )
