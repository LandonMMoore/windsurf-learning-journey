from typing import Any, Dict, List, Optional

from abs_exception_core.exceptions import NotFoundError
from abs_nosql_repository_core.schema import (
    FieldOperatorCondition,
    FilterSchema,
    ListFilter,
    LogicalCondition,
    LogicalOperator,
    Operator,
)
from abs_nosql_repository_core.service.base_service import BaseService
from fastapi.responses import JSONResponse
from loguru import logger

from src.core.exceptions import ValidationError
from src.core.sharepoint_handler import SharepointHandler
from src.repository.integration_repository import IntegrationRepository
from src.repository.integration_sql_repository import IntegrationSqlRepository
from src.schema.integration_schema import (
    ActiveIntegrationResponse,
    SharepointFolderList,
    SharepointIntegration,
    SharepointSite,
    SharepointSiteLists,
    SubscribeDirectory,
    SubscriptionSuccessResponse,
)
from src.services.redis_service import RedisService
from src.services.workflow_crud_service import WorkflowCrudService
from src.socket_io.server import SocketIOService
from src.util.utils import decrypt_token


class IntegrationService(BaseService):
    def __init__(
        self,
        repository: IntegrationRepository,
        integration_sql_repository: IntegrationSqlRepository,
        redis_service: RedisService,
        workflow_service: WorkflowCrudService,
        socket_io_service: SocketIOService,
    ):
        self.repository = repository
        self.integration_sql_repository = integration_sql_repository
        self.redis_service = redis_service
        self.workflow_service = workflow_service
        self.socket_io_service = socket_io_service
        super().__init__(repository)

    async def get_active_subscription(self, user: dict):
        active_integration = self.integration_sql_repository.get_active_integration()
        if not active_integration:
            return ActiveIntegrationResponse(
                success=False, message="No active subscription found"
            )
        try:
            sharepoint_integration = await self.repository.get_by_attr(
                "id", active_integration["integration_id"]
            )
        except NotFoundError:
            raise NotFoundError(detail="Sharepoint integration expired")
        except Exception:
            raise Exception("Error getting sharepoint integration")

        if sharepoint_integration and sharepoint_integration.get("user_id") == user.id:
            active_integration["email"] = sharepoint_integration.get("email")
        return ActiveIntegrationResponse(
            success=True, message="Active subscription found", data=active_integration
        )

    async def get_connections(self, user):
        filters = FilterSchema(
            operator=LogicalOperator.AND,
            conditions=[
                LogicalCondition(
                    operator=LogicalOperator.AND,
                    conditions=[
                        FieldOperatorCondition(
                            field="provider_name",
                            operator=Operator.EQ,
                            value="sharepoint",
                        ),
                        FieldOperatorCondition(
                            field="user_id", operator=Operator.EQ, value=user.id
                        ),
                        FieldOperatorCondition(
                            field="is_draft", operator=Operator.EQ, value=False
                        ),
                    ],
                )
            ],
        )
        user_integrations: Dict[str, Any] = await self.repository.get_all(
            find=ListFilter(filters=filters)
        )
        founds = user_integrations.get("founds", [])
        return [
            SharepointIntegration(
                id=integration.get("_id"),
                uuid=integration.get("uuid"),
                user_id=user.id,
                email=user.email,
                provider_name="sharepoint",
            )
            for integration in founds
        ]

    async def get_all_sites(self, integration_id: str) -> List[SharepointSite]:
        sharepoint_integration = await self.repository.get_by_attr("id", integration_id)
        if not sharepoint_integration:
            raise NotFoundError(detail="Sharepoint integration not found")
        decrypted_token = decrypt_token(sharepoint_integration["access_token"])
        sharepoint_handler = SharepointHandler(
            access_token=decrypted_token,
            redis_service=self.redis_service,
            workflow_service=self.workflow_service,
            socket_io_service=self.socket_io_service,
        )
        return await sharepoint_handler.get_sites()

    async def get_all_lists(
        self, integration_id: str, site_id: str
    ) -> List[SharepointSiteLists]:
        sharepoint_integration = await self.repository.get_by_attr("id", integration_id)
        if not sharepoint_integration:
            raise NotFoundError(detail="Sharepoint integration not found")
        decrypted_token = decrypt_token(sharepoint_integration["access_token"])
        sharepoint_handler = SharepointHandler(
            access_token=decrypted_token,
            redis_service=self.redis_service,
            workflow_service=self.workflow_service,
            socket_io_service=self.socket_io_service,
        )
        return await sharepoint_handler.get_all_lists(site_id)

    async def get_folder_list(
        self,
        integration_id: str,
        site_id: str,
        list_id: str,
        path: Optional[str] = None,
    ) -> SharepointFolderList:
        sharepoint_integration = await self.repository.get_by_attr("id", integration_id)
        if not sharepoint_integration:
            raise NotFoundError(detail="Sharepoint integration not found")
        decrypted_token = decrypt_token(sharepoint_integration["access_token"])
        sharepoint_handler = SharepointHandler(
            access_token=decrypted_token,
            redis_service=self.redis_service,
            workflow_service=self.workflow_service,
            socket_io_service=self.socket_io_service,
        )
        return await sharepoint_handler.get_folder_items(site_id, list_id, path)

    async def subscribe_directory(
        self, data: SubscribeDirectory
    ) -> SubscriptionSuccessResponse:
        try:
            sharepoint_integration = await self.repository.get_by_attr(
                "id", data.integration_id
            )
        except NotFoundError:
            raise NotFoundError(detail="Sharepoint integration expired")
        except Exception:
            raise Exception("Error getting sharepoint integration")

        if not sharepoint_integration:
            raise NotFoundError(detail="Sharepoint integration not found")
        decrypted_token = decrypt_token(sharepoint_integration["access_token"])
        sharepoint_handler = SharepointHandler(
            access_token=decrypted_token,
            redis_service=self.redis_service,
            workflow_service=self.workflow_service,
            socket_io_service=self.socket_io_service,
        )
        # collect all the subscriptions and delete them in bulk
        existing_subscriptions = await self.get_all_subscriptions()
        result = await sharepoint_handler.subscribe_directory(data, existing_subscriptions)

        if result:
            subscription_id = result.get("id")
            if subscription_id:
                try:
                    self.integration_sql_repository.manage_integration(
                        sharepoint_integration["user_id"], result, data
                    )
                    return SubscriptionSuccessResponse(
                        success=True,
                        message="Directory subscription created successfully",
                        data=result,
                    )
                except Exception as e:
                    raise Exception(f"Error saving integration: {e}")
        return SubscriptionSuccessResponse(
            success=False, message="Failed to create subscription", data={}
        )
    async def get_all_subscriptions(self)->List[str]:
        return await self.integration_sql_repository.get_all_subscriptions()

    async def unsubscribe_all(self, integration_id: str):
        """Unsubscribe from all subscriptions for a given integration."""
        sharepoint_integration = await self.repository.get_by_attr("id", integration_id)
        if not sharepoint_integration:
            raise NotFoundError(detail="Sharepoint integration not found")
        decrypted_token = decrypt_token(sharepoint_integration["access_token"])
        sharepoint_handler = SharepointHandler(
            access_token=decrypted_token,
            redis_service=self.redis_service,
            workflow_service=self.workflow_service,
            socket_io_service=self.socket_io_service,
        )
        existing_subscriptions = await self.get_all_subscriptions()
        is_unsubscribed = await sharepoint_handler.unsubscribe_all(existing_subscriptions)
        if not is_unsubscribed:
            raise ValidationError(
                detail="Failed to unsubscribe from all existing subscriptions"
            )
        return SubscriptionSuccessResponse(
            success=True,
            message="Unsubscribed from all existing subscriptions successfully",
            data=None,
        )

    async def handle_sharepoint_webhook(self):
        current_integration = self.integration_sql_repository.get_active_integration()
        if not current_integration:
            logger.info("Sharepoint integration not found")
            return JSONResponse(content={"status": "ignored"}, status_code=200)

        user_integration: Dict[str, Any] = await self.repository.get_by_attr(
            attr="id", value=current_integration["integration_id"]
        )
        decrypted_token = decrypt_token(user_integration["access_token"])
        sharepoint_handler = SharepointHandler(
            access_token=decrypted_token,
            redis_service=self.redis_service,
            workflow_service=self.workflow_service,
            socket_io_service=self.socket_io_service,
        )
        return await sharepoint_handler.handle_uploaded_content(
            current_integration["drive_id"],
            current_integration["folder_id"],
            current_integration["id"],
        )

    async def delete_subscription(self, integration_id: str):
        sharepoint_integration = await self.repository.get_by_attr("id", integration_id)
        if not sharepoint_integration:
            raise NotFoundError(detail="Sharepoint integration not found")
        decrypted_token = decrypt_token(sharepoint_integration["access_token"])
        sharepoint_handler = SharepointHandler(
            access_token=decrypted_token,
            redis_service=self.redis_service,
            workflow_service=self.workflow_service,
            socket_io_service=self.socket_io_service,
        )

        users_subscription = self.integration_sql_repository.get_user_subscription(
            sharepoint_integration["user_id"]
        )
        if not users_subscription:
            raise NotFoundError(detail="Subscription not found")
        subscription_id = users_subscription.webhook_info.get("id")
        is_unsubscribed = await sharepoint_handler.delete_subscription(subscription_id)
        if not is_unsubscribed:
            raise ValidationError(detail="Failed to delete subscription")
        self.integration_sql_repository.delete_by_id(users_subscription.id)
        return SubscriptionSuccessResponse(
            success=True,
            message="Subscription deleted successfully",
            data=None,
        )
