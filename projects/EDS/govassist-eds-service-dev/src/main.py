import asyncio
import json
import os
from contextlib import asynccontextmanager

import redis.asyncio as redis_async
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from beanie import init_beanie
from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from loguru import logger
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED

from src.api import limiter
from src.api.routes import private_routers, routers
from src.core.config import configs
from src.core.container import Container
from src.core.exception_handlers import (
    auth_error_handler,
    bad_request_error_handler,
    duplicated_error_handler,
    failed_to_create_error_handler,
    internal_server_error_handler,
    not_found_error_handler,
    permission_denied_error_handler,
    rate_limit_exceeded_error_handler,
    request_validation_exception_handler,
    sqlalchemy_exception_handler,
    unauthorized_error_handler,
    validation_error_handler,
)
from src.core.exceptions import (
    AuthError,
    BadRequestError,
    DuplicatedError,
    FailedToCreateError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
    ValidationError,
)
from src.elasticsearch.service import es_service
from src.model.nosql_document.ns_report_model import (
    FormulaAssistantChatHistory,
    ReportChatHistory,
)
from src.mongodb.integration import Integration
from src.util.class_object import singleton


@singleton
class AppCreator:
    def __init__(self):
        root_path = os.getenv("API_ROOT_PATH", "/")
        self.redis_client = None
        self.container = Container()
        self.mongo_db_for_gov_assist = self.container.mongo_db_for_gov_assist()
        self.mongo_db_for_eds = self.container.mongo_db_for_eds()
        self.sio_service = None

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            logger.info("Starting up application...")
            try:
                await init_beanie(
                    database=self.mongo_db_for_gov_assist,
                    document_models=[Integration],
                )
                await init_beanie(
                    database=self.mongo_db_for_eds,
                    document_models=[ReportChatHistory, FormulaAssistantChatHistory],
                )
                logger.info("MongoDB initialized successfully")

                # Initialize Elasticsearch
                await es_service.initialize()
                logger.info("Elasticsearch initialized successfully")

                # Initialize Redis client
                logger.info("Starting Redis initialization...")
                self.redis_client = self.container.redis_client()
                await self.redis_client.initialize()
                logger.info("Redis client initialized successfully")

                # Store in app state for access
                self.app.state.redis_client = self.redis_client
                logger.info("Redis client stored in app state successfully")
                logger.info("Application startup completed - all services ready!")

                yield
            except Exception as e:
                logger.error(f"Error in lifespan startup: {e}")
                raise e

            # Shutdown
            logger.info("Shutting down application...")
            # Cleanup Elasticsearch
            await es_service.cleanup()
            logger.info("Elasticsearch cleanup completed")

            if self.redis_client:
                logger.info("Closing Redis client...")
                await self.redis_client.close()
                logger.info("Redis client closed successfully")
            logger.info("Application shutdown completed")

        self.app = FastAPI(
            title=configs.PROJECT_NAME,
            version="0.0.1",
            root_path=root_path,
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
            openapi_url=None,  # Disable default openapi.json
            docs_url=None,  # Disable default docs
            redoc_url=None,  # Disable default redoc
            lifespan=lifespan,
        )
        self.app.state.limiter = limiter
        security = HTTPBasic()

        DOCS_USERNAME = configs.SWAGGER_DOCS_USERNAME
        DOCS_PASSWORD = configs.SWAGGER_DOCS_PASSWORD

        # Protect Swagger docs endpoint

        @self.app.get("/docs", include_in_schema=False)
        async def get_documentation(
            credentials: HTTPBasicCredentials = Depends(security),
        ):
            if (
                credentials.username != DOCS_USERNAME
                or credentials.password != DOCS_PASSWORD
            ):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Basic"},
                )
            return get_swagger_ui_html(openapi_url="openapi.json", title="docs")

        @self.app.get("/openapi.json", include_in_schema=False)
        async def get_openapi_json(
            credentials: HTTPBasicCredentials = Depends(security),
        ):
            if (
                credentials.username != DOCS_USERNAME
                or credentials.password != DOCS_PASSWORD
            ):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Basic"},
                )
            openapi_schema = self.app.openapi()
            if root_path:
                openapi_schema["servers"] = [{"url": root_path}]
            return openapi_schema

        # Protect ReDoc endpoint
        @self.app.get("/redoc", include_in_schema=False)
        async def get_redoc(credentials: HTTPBasicCredentials = Depends(security)):
            if (
                credentials.username != DOCS_USERNAME
                or credentials.password != DOCS_PASSWORD
            ):
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Basic"},
                )

            return get_redoc_html(openapi_url="openapi.json", title="ReDoc")

        self.container = Container()
        self.db = self.container.db()
        self.auth_middleware = self.container.get_auth_middleware()
        self.app.add_middleware(SlowAPIMiddleware)

        if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
            self._configure_monitoring()

        if configs.BACKEND_CORS_ORIGINS:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in configs.BACKEND_CORS_ORIGINS],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        self.app.include_router(routers, prefix=configs.API_STR)
        self.app.include_router(
            private_routers,
            prefix=configs.API_STR,
            dependencies=[Depends(self.auth_middleware)],
        )
        self._start_redis_listener()
        self._register_exception_handlers()
        self._register_events()
        # register_listeners()

    def _configure_monitoring(self):
        """Configure Azure Monitor and instrument FastAPI application"""
        try:
            # Disable adaptive sampling by using AlwaysOnSampler (sends all traces)
            trace.set_tracer_provider(TracerProvider(sampler=ALWAYS_ON))

            # Exporter for Azure Monitor
            exporter = AzureMonitorTraceExporter()
            span_processor = BatchSpanProcessor(exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)

            # Instrument FastAPI only — skipping auto-instrumentation for requests, HTTP, DB, etc.
            FastAPIInstrumentor().instrument_app(self.app)
            logger.info("Azure Monitor instrumentation configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Azure Monitor: {str(e)}")

    def _register_exception_handlers(self):
        """Register all exception handlers for the application."""
        # FastAPI built-in exceptions
        self.app.add_exception_handler(
            RequestValidationError, request_validation_exception_handler
        )

        # Database exceptions
        self.app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)

        # Custom application exceptions
        custom_exceptions = [
            (DuplicatedError, duplicated_error_handler),
            (BadRequestError, bad_request_error_handler),
            (AuthError, auth_error_handler),
            (NotFoundError, not_found_error_handler),
            (ValidationError, validation_error_handler),
            (PermissionDeniedError, permission_denied_error_handler),
            (UnauthorizedError, unauthorized_error_handler),
            (RateLimitExceeded, rate_limit_exceeded_error_handler),
            (FailedToCreateError, failed_to_create_error_handler),
            (InternalServerError, internal_server_error_handler),
        ]

        for exception_class, handler in custom_exceptions:
            self.app.add_exception_handler(exception_class, handler)

    def _register_events(self):
        """Register startup and shutdown events."""

        @self.app.on_event("startup")
        async def startup_event():
            # Initialize Elasticsearch
            await es_service.initialize()

        @self.app.on_event("shutdown")
        async def shutdown_event():
            # Cleanup Elasticsearch
            await es_service.cleanup()

    def _start_redis_listener(self):
        """Start Redis Pub/Sub listener in background"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._redis_listener())
                logger.info("Started Redis Pub/Sub listener for workflow updates")
            else:
                logger.warning(
                    "Event loop not running, Redis listener will start when app starts"
                )
        except RuntimeError:
            logger.warning(
                "No event loop available, Redis listener will start when app starts"
            )

    async def _redis_listener(self):
        """Listen to Redis Pub/Sub channel for workflow updates"""
        try:
            # Create Redis connection for Pub/Sub
            redis_client = redis_async.from_url(configs.REDIS_URL)
            pubsub = redis_client.pubsub()

            # Subscribe to workflow updates channel
            await pubsub.subscribe(configs.WORKFLOW_UPDATES)
            logger.info(
                "Redis Pub/Sub listener connected and listening for workflow updates"
            )

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        # Parse the message
                        data = json.loads(message["data"])

                        # Handle workflow updates from Celery
                        workflow_id = data.get("workflow_id")
                        status = data.get("status")
                        workflow_data = data.get("data", {})

                        if workflow_id and status:
                            # Emit via Socket.IO
                            await self.container.socket_io_service().emit_workflow_update_with_broadcast(
                                workflow_id, status, workflow_data
                            )
                            # logger.info(f"Emitted workflow update from Redis: {workflow_id} - {status}")

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse Redis message: {e}")
                    except Exception as e:
                        logger.error(f"Error processing Redis message: {e}")

        except Exception as e:
            logger.error(f"Redis Pub/Sub listener error: {e}")
            # Retry after delay
            await asyncio.sleep(5)
            asyncio.create_task(self._redis_listener())


app_creator = AppCreator()
app = app_creator.app
app_creator.sio_service = app_creator.container.socket_io_service()
app = app_creator.sio_service.bind_app(app)
db = app_creator.db
container = app_creator.container
