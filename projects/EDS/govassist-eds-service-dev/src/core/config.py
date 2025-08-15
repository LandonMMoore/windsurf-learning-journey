import logging
import os
from typing import ClassVar, List, Optional, Set
from urllib.parse import quote_plus

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

from src.core.exceptions import InternalServerError
from src.schema.workflow_schema import ExcelSheetName

load_dotenv(override=True)

ENV: str = ""

try:
    credential = DefaultAzureCredential()
    client = SecretClient(
        vault_url=f"https://{os.getenv('KEYVAULT_NAME')}.vault.azure.net",
        credential=credential,
    )

    def get_secret(
        secret_key: str, required: bool = True, module_name: str = None
    ) -> Optional[str]:
        """Get secret from Azure Key Vault with error handling."""
        env = os.getenv("ENV", "prod")
        # For dev environment, use environment variables
        if env == "local":
            env_value = os.getenv(secret_key.replace("-", "_"))
            if env_value:
                return env_value
            if required:
                raise ValueError(
                    f"Required secret {secret_key} not found in environment variables"
                )
            return None
        # For other environments, use Azure Key Vault
        try:
            # Automatically prepend TENANT_NAME and MODULE_NAME to the secret key

            tenant_name = os.getenv("TENANT_NAME", "").strip()
            if module_name:
                module_name = module_name.strip()
            else:
                module_name = os.getenv("MODULE_NAME", "").strip()

            full_secret_key = (
                f"{tenant_name}-{module_name}-{secret_key}"
                if tenant_name and module_name
                else secret_key
            )
            retrieved_secret = client.get_secret(full_secret_key)
            return retrieved_secret.value.strip()
        except Exception:
            if required:
                raise ValueError("Required secret key not found")
            return None

except Exception:
    logging.error("Failed to initialize configuration")
    raise InternalServerError(detail="Internal Server Error")


class Configs(BaseSettings):
    # base
    ENV: str = os.getenv("ENV", "dev")
    API: str = "/api"
    API_STR: str = "/api"
    PROJECT_NAME: str = "EDS"

    ENV_DATABASE_MAPPER: dict = {
        "ddot": "sqldb-govt-assist-ddot-prd",
        "prod": "sqldb-govt-assist-main-prd",
        "stage": "sqldb-govt-assist-main-stg",
        "dev": "sqldb-govt-assist-development",
        "test": "test-eds",
        "local": "sqldb-govt-assist-development",
    }
    DB_ENGINE_MAPPER: dict = {
        "postgresql": "postgresql",
        "mysql": "mysql+pymysql",
        "mssql": "mssql+pyodbc",
    }

    SQLALCHEMY_LOGGING: bool = (
        os.getenv("SQLALCHEMY_LOGGING", "False").lower() == "true"
    )

    # CORS
    cors_origins_str: ClassVar[str] = get_secret("CORS-ALLOWED-ORIGINS", required=False)
    BACKEND_CORS_ORIGINS: List[str] = (
        [origin.strip() for origin in cors_origins_str.split(",")]
        if cors_origins_str
        else ["*"]
    )

    # Email
    SENDGRID_API_KEY: str = get_secret("SENDGRID-API-KEY")
    FEEDBACK_EMAIL: str = get_secret("EMAIL-FROM")
    FEEDBACK_EMAIL_RECIPIENTS: str = get_secret("FEEDBACK-EMAIL-RECIPIENTS")

    # Database
    DB: str = get_secret("DB", required=False) or "mssql"
    DB_USER: str = get_secret("DB-USER")
    DB_PASSWORD: str = get_secret("DB-PASSWORD")
    DB_HOST: str = get_secret("DB-HOST")
    DB_PORT: str = get_secret("DB-PORT", required=False) or "1433"
    DB_ENGINE: str = DB_ENGINE_MAPPER.get(DB, "mssql")
    DB_DRIVE: str = "ODBC+Driver+18+for+SQL+Server"

    # Cosmos DB
    COSMOS_DB_ENDPOINT: str = get_secret("COSMOS-DB-URL")
    COSMOS_DB_KEY: str = get_secret("COSMOS-DB-KEY")
    COSMOS_DB_CONTAINER_NAME: str = get_secret("COSMOS-DB-CONTAINER-NAME")
    COSMOS_DB_DATABASE_NAME: str = get_secret("COSMOS-DB-DATABASE-NAME")

    # JWT settings
    JWT_SECRET_KEY: str = get_secret("JWT-SECRET-KEY", module_name="GA")

    JWT_ALGORITHM: str = get_secret("JWT-ALGORITHM", module_name="GA") or "HS256"
    # Encode password for use in URI
    encoded_password: ClassVar[str] = quote_plus(DB_PASSWORD)

    DATABASE_URI_FORMAT: str = (
        "{db_engine}://{user}:{password}@{host}:{port}/{database}"
    )
    DATABASE_URI: str = (
        "{db_engine}://{user}:{password}@{host}:{port}/{database}{driver}".format(
            db_engine=DB_ENGINE,
            user=DB_USER,
            password=encoded_password,
            host=DB_HOST,
            port=DB_PORT,
            database=ENV_DATABASE_MAPPER[ENV],
            driver="" if DB_ENGINE == "postgresql" else f"?driver={DB_DRIVE}",
        )
    )
    # find query
    PAGE: int = 1
    PAGE_SIZE: int = 20
    ORDERING: str = "-id"

    # JWT settings

    # TODO: temporary remove JWT settings
    # JWT_SECRET_KEY: str = get_secret("JWT-SECRET-KEY")
    # JWT_ALGORITHM: str = get_secret("JWT-ALGORITHM")
    # JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = get_secret("JWT-ACCESS-TOKEN-EXPIRE-MINUTES")
    # JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = get_secret(
    #     "JWT-REFRESH-TOKEN-EXPIRE-MINUTES"
    # )

    # Elasticsearch settings
    ELASTICSEARCH_URL: str = (
        get_secret("ELASTIC-SEARCH-URL", required=False) or "http://localhost:9200"
    )

    ELASTICSEARCH_USERNAME: Optional[str] = get_secret(
        "ELASTIC-SEARCH-USERNAME", required=False
    )
    ELASTICSEARCH_PASSWORD: Optional[str] = get_secret(
        "ELASTIC-SEARCH-PASSWORD", required=False
    )

    # ELASTICSEARCH_API_KEY: Optional[str] = get_secret(
    #     "ELASTIC-SEARCH-API-KEY", required=False
    # )
    ELASTICSEARCH_VERIFY_CERTS: bool = False
    ELASTICSEARCH_DEFAULT_INDEX: str = (
        get_secret("ELASTIC-SEARCH-DEFAULT-INDEX", required=False) or "par"
    )

    OPENAI_API_KEY: str = get_secret("OPENAI-API-KEY")
    ANTHROPIC_API_KEY: str = get_secret("ANTHROPIC-API-KEY")
    # MongoDB settings
    MONGODB_URL: str = (
        get_secret("COSMOS-DATABASE-URL", required=False, module_name="GA")
        or "mongodb://localhost:27017"
    )
    MONGODB_DATABASE: str = get_secret("MONGODB-DATABASE", required=False) or "EDS"
    MONGODB_CHAT_COLLECTION: str = (
        get_secret("MONGODB-CHAT-COLLECTION", required=False) or "chat_history"
    )
    ENABLE_EDS_ASSISTANCE_LOGGING: bool = True

    REDIS_URL: str = get_secret("REDIS-URL", required=True) or "redis://localhost:6379"

    SWAGGER_DOCS_USERNAME: str = get_secret("SWAGGER-DOCS-USERNAME")
    SWAGGER_DOCS_PASSWORD: str = get_secret("SWAGGER-DOCS-PASSWORD")

    # TODO: Maybe need to add the integration in KV
    MONGODB_DATABASE_FOR_GOV_ASSIST: str = "govassist-db"

    MONGODB_DATABASE_FOR_EDS: str = "EDS"

    # fernet key for decryption of access token
    FERNET_KEY: str = get_secret("FERNET-KEY", required=True) or "fernet-key"

    # sharepoint settings
    SHAREPOINT_GRAPH_BASE_URL: str = "https://graph.microsoft.com/v1.0"
    SHAREPOINT_EVENT_TYPE: str = "updated"
    SHAREPOINT_WEBHOOK_URL: str = get_secret("SHAREPOINT-WEBHOOK-URL")
    SHAREPOINT_CLIENT_SECRET_CODE: str = get_secret("SHAREPOINT-CLIENT-SECRET-CODE")
    SHAREPOINT_LAST_MODIFIED_OBJECTS_THRESHOLD: int = 3

    # sharepoint file name
    SHAREPOINT_FILE_NAMES_FOR_DAILY_FOLDER: Set[str] = {
        "EDS-Extract-Sample-Data-Template-1.xlsx",
        # "test_book1.xlsx",
        # "test_book2.xlsx",
        # "test_book3.xlsx",
    }
    SHAREPOINT_FILE_NAMES_FOR_WEEKLY_FOLDER: Set[str] = {
        "EDS-Extract-Sample-Data-Template-1.xlsx",
        # "award_project_master_data.xlsx",
        # "coa_master_data.xlsx",
        # "summary_balances.xlsx",
        # "transactional_detail_data.xlsx",
    }

    # Redis Configuration
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_DEFAULT_TTL: int = 3600

    BROKER_URL: str = (
        get_secret("BROKER-URL", required=True) or "redis://localhost:6379"
    )

    # File download chunk size
    FILE_DOWNLOAD_CHUNK_SIZE: int = 524288

    AZURE_STORAGE_CONNECTION_STRING: str = get_secret(
        "AZURE-STORAGE-CONNECTION-STRING", required=True
    )

    AZURE_STORAGE_CONTAINER_NAME: str = (
        get_secret("AZURE-STORAGE-CONTAINER-NAME", required=False)
        or "eds-report-exports"
    )

    # Excel files sheet names
    EXCEL_FILE_SHEET_NAMES: Set[str] = {sheet.value for sheet in ExcelSheetName}

    # Excel files valid headers
    COA_MASTER_DATA_VALID_HEADERS: Set[str] = {
        "Segment Name",
        "Segment Value",
        "Segment Value Description",
        "Parent 1Segment Name",
        "Parent Value1",
        "Parent Value1 Description",
        "Parent 2 Segment Name",
        "Parent Value 2",
        "Parent Value Description2",
        "Parent 3 Segment Name",
        "Parent Value 3",
        "Parent Value Description3",
        "Parent 4 Segment Name",
        "Parent Value 4",
        "Parent Value Description4",
    }

    AWARD_PROJECT_MASTER_DATA_VALID_HEADERS: Set[str] = {
        "Owning_Agency",
        "AWARD_NUMBER",
        "AWARD_NAME",
        "AWARD_ORGANIZATION",
        "AWARD_START_DATE",
        "AWARD_END_DATE",
        "AWARD_CLOSE_DATE",
        "AWARD_STATUS",
        "PRIMARY_SPONSOR",
        "SPONSOR_NUMBER",
        "SPONSOR_NAME",
        "SPONSOR_AWARD_NUMBER",
        "PRINCIPAL_INVESTIGATOR",
        "AWARD_TYPE",
        "PROJECT_NUMBER",
        "PROJECT_NAME",
        "PROJECT_DESCRIPTION",
        "PROJECT_TYPE",
        "PROJECT_ORGANIZATION",
        "Master_Project_Number",
        "Primary_Category",
        "Project_Category",
        "Project_Classification",
        "Ward",
        "FHWA_IMPROVEMENT_TYPES",
        "FHWA_FUNCTIONAL_CODE",
        "FHWA_CAPITAL_OUTLAY_CATEGORY",
        "FHWA_SYSTEM_CODE",
        "NHS",
        "PROJECT_START_DATE",
        "PROJECT_END_DATE",
        "PROJECT_STATUS_CODE",
        "PROJECT_OWNER_AGENCY",
        "PARENT_TASK_NUMBER",
        "PARENT_TASK_NAME",
        "SUB_TASK_NUMBER",
        "SUB_TASK_NAME",
        "PROGRAM",
        "COST_CENTER",
        "SUBTASK_START_DATE",
        "SUBTASK_COMPLETION_DATE",
        "Award_Project_Burden_Schedule_Name",
        "FUND_NUMBER",
        "IBA_PROJECT_NUMBER",
        "Burden_Rate_Multiplier",
        "Burden_Schedule_Version_Start_Date",
        "Burden_Schedule_Version_End_Date",
        "Burden_Schedule_Version_Name",
        "IND_RATE_SCH_ID",
        "CHARGEABLE_FLAG",
        "BILLABLE_FLAG",
        "CAPITALIZABLE_FLAG",
    }

    SUMMARY_BALANCES_VALID_HEADERS: Set[str] = {
        "AGENCY",
        "AWARD",
        "FUND",
        "PROJECT",
        "TASK NUMBER",
        "AWARD_FUNDING_AMOUNT",
        "PNG_LIFETIME_BUDGET",
        "PNG_LIFETIME_ALLOTMENT",
        "COMMITMENT",
        "OBLIGATION",
        "EXPENDITURE",
        "RECEIVABLES",
        "REVENUE",
    }

    TRANSACTIONAL_DETAIL_DATA_VALID_HEADERS: Set[str] = {
        "Project Number",
        "Subtask Number",
        "Award Number",
        "Transaction Number",
        "Transaction Source",
        "Expenditure Type",
        "Expenditure Category",
        "Expenditure Organization",
        "Expenditure Item Date",
        "Accounting Period",
        "Unit of Measure",
        "Incurred By Person",
        "Person Number",
        "Position Number",
        "Vendor Name",
        "PO Number",
        "PO Line Number",
        "AP Invoice Number",
        "AP Invoice Line Number",
        "Dist Line Num",
        "Invoice Date",
        "Check Number",
        "Check Date",
        "Expenditure Batch",
        "Expenditure Comment",
        "Orig Transaction Reference",
        "Capitalizable Flag",
        "Billable Flag",
        "Bill Hold Flag",
        "Revenue status",
        "Transaction AR Invoice Status",
        "ServiceDate From",
        "ServiceDate To",
        "GL Batch Name",
        "Quantity",
        "Transaction Amount",
        "Burdened Amount",
        "Rate",
    }
    WORKFLOW_UPDATES: str = get_secret("WORKFLOW-UPDATES", required=True)

    class Config:
        case_sensitive = True


class TestConfigs(Configs):
    ENV: str = "test"


configs = Configs()

if ENV == "prod":
    pass
elif ENV == "ddot":
    pass
elif ENV == "stage":
    pass
elif ENV == "test":
    setting = TestConfigs()
