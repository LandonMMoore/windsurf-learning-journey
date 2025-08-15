import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import aiohttp
from fastapi.responses import JSONResponse
from loguru import logger

from src.core.config import configs
from src.core.exceptions import NotFoundError, ValidationError
from src.schema.integration_schema import (
    SharepointFile,
    SharepointFolder,
    SharepointFolderList,
    SharepointSite,
    SharepointSiteLists,
    SharepointSubscription,
    SubscribeDirectory,
)
from src.schema.workflow_schema import (
    FolderProcessingContext,
    FolderType,
    WorkflowCreate,
    WorkflowStatusEnum,
    WorkflowTypeEnum,
)
from src.services.redis_service import RedisService
from src.services.workflow_crud_service import WorkflowCrudService
from src.services.workflow_redis_manager import WorkflowRedisSchema
from src.socket_io.server import SocketIOService
from src.tasks.sharepoint_webhook_handler import process_sharepoint_workflow
from src.util.regex_validator import REGEX_DAILY_FOLDER_NAME, REGEX_WEEKLY_FOLDER_NAME


class SharepointHandler:
    BASE_URL = configs.SHAREPOINT_GRAPH_BASE_URL

    def __init__(
        self,
        access_token: str,
        redis_service: RedisService,
        workflow_service: WorkflowCrudService,
        socket_io_service: SocketIOService = None,
    ):
        self.access_token = access_token
        self.redis_service = redis_service
        self.workflow_service = workflow_service
        self.socket_io_service = socket_io_service
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def _make_async_request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:

        async with aiohttp.ClientSession(headers=self.headers) as session:
            if method.upper() == "GET":
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    return None
            elif method.upper() == "POST":
                async with session.post(url, json=json_data, data=data) as resp:
                    if resp.status in [200, 201]:
                        return await resp.json()
                    return None

            elif method.upper() == "DELETE":
                async with session.delete(url) as resp:
                    if resp.status in [200, 204]:
                        return {"status": "deleted"}
                    return None

            else:
                logger.warning(f"Unsupported HTTP method: {method}")
                return None

    async def get_sites(self) -> List[SharepointSite]:
        url = f"{self.BASE_URL}/sites?search=*"
        result = await self._make_async_request(url)
        if not result:
            return []
        return [
            SharepointSite(display_name=site["displayName"], **site)
            for site in result.get("value", [])
        ]

    async def get_all_lists(self, site_id: str) -> List[SharepointSiteLists]:
        url = f"{self.BASE_URL}/sites/{site_id}/lists"
        result = await self._make_async_request(url)
        if not result:
            return []
        return [
            SharepointSiteLists(
                display_name=list["displayName"],
                created_datetime=list["createdDateTime"],
                last_modified_dateTime=list["lastModifiedDateTime"],
                template=list["list"]["template"],
                **list,
            )
            for list in result.get("value", [])
            if list.get("list", {}).get("template") == "documentLibrary"
        ]

    async def get_default_drive_id(self, site_id: str, list_id: str) -> Optional[str]:
        url = f"{self.BASE_URL}/sites/{site_id}/lists/{list_id}/drive"
        result = await self._make_async_request(url)
        return result.get("id") if result else None

    async def get_folder_items(
        self, site_id: str, list_id: str, path: Optional[str] = None
    ) -> SharepointFolderList:
        drive_id = await self.get_default_drive_id(site_id, list_id)
        if not drive_id:
            raise NotFoundError(detail="Drive not found")

        if path:
            encoded_path = quote(path.strip("/"), safe="")
            url = f"{self.BASE_URL}/drives/{drive_id}/root:/{encoded_path}:/children"
        else:
            url = f"{self.BASE_URL}/drives/{drive_id}/root/children"

        data = await self._make_async_request(url)
        if not data:
            raise NotFoundError(detail="Folder not found")

        folders, files = [], []

        for item in data.get("value", []):
            if item.get("folder"):
                folders.append(
                    SharepointFolder(
                        has_children=item["folder"].get("childCount", 0) > 0,
                        path=item["parentReference"]["path"].split("root:")[-1]
                        + "/"
                        + item["name"],
                        drive_id="/drives/" + drive_id + "/root",
                        **item,
                    )
                )
            elif item.get("file"):
                files.append(
                    SharepointFile(
                        type=item["file"]["mimeType"],
                        drive_id=drive_id,
                        **item,
                    )
                )

        return SharepointFolderList(
            folders=folders, files=files, current_path=path or "/"
        )

    async def get_subscriptions(self) -> List[Dict[str, Any]]:
        """Get all existing subscriptions for the current user/application."""
        url = f"{self.BASE_URL}/subscriptions"
        result = await self._make_async_request(url, method="GET")
        if not result:
            return []
        return result.get("value", [])

    async def delete_subscription(self, subscription_id: str) -> bool:
        """Delete a specific subscription by ID."""
        url = f"{self.BASE_URL}/subscriptions/{subscription_id}"
        result = await self._make_async_request(url, method="DELETE")
        # Clear subscription cache
        await self.redis_service.cache_delete(
            f"subscription:sharepoint:{subscription_id}"
        )
        return result is not None

    async def unsubscribe_all(self, existing_subscriptions: List[str]) -> bool:
        """Unsubscribe from all existing subscriptions."""
        try:
            subscriptions = await self.get_subscriptions()
            if not subscriptions:
                logger.info("No existing subscriptions found to unsubscribe from")
                return True

            success_count = 0
            failed_count = 0
            for subscription in subscriptions:
                subscription_id = subscription.get("id")
                if subscription_id and subscription_id in existing_subscriptions:
                    try:
                        if await self.delete_subscription(subscription_id):
                            success_count += 1
                            logger.info("Successfully unsubscribed from subscription")
                        else:
                            failed_count += 1
                            logger.warning("Failed to unsubscribe from subscription")
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Error unsubscribing from subscription: {str(e)}")
                else:
                    logger.warning("Subscription without ID found, skipping")

            logger.info(
                f"Unsubscribed from {success_count}/{len(subscriptions)} subscriptions (failed: {failed_count})"
            )
            return failed_count == 0
        except Exception:
            return False

    async def subscribe_directory(self, data: SubscribeDirectory, existing_subscriptions: List[str]):
        # Unsubscribe from all existing subscriptions
        is_unsubscribed = await self.unsubscribe_all(existing_subscriptions)
        if not is_unsubscribed:
            raise ValidationError(
                detail="Failed to unsubscribe from all existing subscriptions"
            )

        subscription_data = SharepointSubscription(
            changeType=configs.SHAREPOINT_EVENT_TYPE,
            clientState=configs.SHAREPOINT_CLIENT_SECRET_CODE,
            notificationUrl=configs.SHAREPOINT_WEBHOOK_URL,
            resource=data.resource,
            expirationDateTime=(
                datetime.now(timezone.utc) + timedelta(days=1)
            ).isoformat(),
        ).model_dump(mode="json")

        url = f"{self.BASE_URL}/subscriptions"
        result = await self._make_async_request(
            url, method="POST", json_data=subscription_data
        )

        # Cache the subscription info
        if result and result.get("id"):
            await self.redis_service.cache_set(
                f"subscription:sharepoint:{result['id']}", result, ttl=None
            )

        return result

    async def handle_uploaded_content(
        self, drive_id: str, folder_id: str, integration_id: int
    ):
        # get all the folders in the integration
        last_modified_objects = await self.get_last_modified_objects(
            drive_id, folder_id
        )
        if not last_modified_objects:
            logger.info("No last modified object found")
            return JSONResponse(content={"status": "ignored"}, status_code=200)

        # get the parent site id and list id
        for last_modified_object in last_modified_objects:
            if "folder" in last_modified_object:
                site_id = last_modified_object.get("parentReference", {}).get(
                    "siteId", None
                )
                child_folder_id = last_modified_object.get("id", None)
            else:
                logger.info("Last modified object is not a folder")
                continue

            if not site_id or not child_folder_id:
                logger.info("Parent site or child folder id not found")
                continue

            # check if the parent folder is a weekly or daily folder
            folder_name = last_modified_object.get("name", None)
            updated_folder_id = last_modified_object.get("id", None)
            if updated_folder_id:
                # check if the folder is already processed
                is_folder_processed = self.workflow_service.is_folder_processed(processed_folder_id=updated_folder_id)
                if is_folder_processed:
                    logger.info("Folder is already processed, skipping")
                    continue
                else:
                    logger.info("Folder is not processed, processing")
            else:
                logger.info("Folder is not processable")


            if not folder_name:
                logger.info("Folder name not found in parentReference")
                continue

            is_weekly_folder = (
                re.match(REGEX_WEEKLY_FOLDER_NAME, folder_name) is not None
            )
            is_daily_folder = re.match(REGEX_DAILY_FOLDER_NAME, folder_name) is not None

            if not is_weekly_folder and not is_daily_folder:
                logger.info("No weekly or daily folder found")
                continue

            # get the child folder items
            child_folder_items = await self.get_folders_all_items(
                site_id, child_folder_id
            )
            if not child_folder_items:
                logger.info("No child folder items found")
                continue

            # check if the file names are valid
            processable_items = []
            all_file_names = []

            for item in child_folder_items:
                if (
                    "file" in item
                    and item.get("file", {}).get("mimeType")
                    == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ):
                    name = item.get("name")
                    all_file_names.append(name)
                    if name in configs.SHAREPOINT_FILE_NAMES_FOR_WEEKLY_FOLDER.union(
                        configs.SHAREPOINT_FILE_NAMES_FOR_DAILY_FOLDER
                    ):
                        processable_items.append(item)

            folder_processing_context = FolderProcessingContext(
                drive_id=drive_id,
                folder_id=folder_id,
                folder_type=FolderType.WEEKLY if is_weekly_folder else FolderType.DAILY,
                integration_id=integration_id,
                folder_name=folder_name,
                processed_folder_id=updated_folder_id,
            )

            if is_weekly_folder:
                missing_files = configs.SHAREPOINT_FILE_NAMES_FOR_WEEKLY_FOLDER - set(
                    all_file_names
                )
                if missing_files:
                    logger.info("Missing files found in weekly folder.")
                    continue
                else:
                    # TODO: Store status
                    return await self.handle_folder_processing(
                        processable_items, folder_processing_context
                    )

            elif is_daily_folder:
                missing_files = configs.SHAREPOINT_FILE_NAMES_FOR_DAILY_FOLDER - set(
                    all_file_names
                )
                if missing_files:
                    logger.info("Missing files found in daily folder.")
                    continue
                else:
                    # TODO: Store status
                    return await self.handle_folder_processing(
                        processable_items, folder_processing_context
                    )

            else:
                logger.info("No weekly or daily folder found or missing files found")
                continue

        logger.info("No eligible folder processed.")
        return JSONResponse(content={"status": "ignored"}, status_code=200)

    async def get_last_modified_objects(self, drive_id: str, folder_id: str):
        url = f"{self.BASE_URL}/drives/{drive_id}/items/{folder_id}/children?$orderby=lastModifiedDateTime desc&$top={configs.SHAREPOINT_LAST_MODIFIED_OBJECTS_THRESHOLD}"
        result = await self._make_async_request(url)
        if not result:
            return None
        items = result.get("value", [])
        return items if items else None

    async def get_folders_all_items(self, site_id: str, folder_id: str):
        url = f"{self.BASE_URL}/sites/{site_id}/drive/items/{folder_id}/children"
        result = await self._make_async_request(url)
        if not result:
            return None
        items = result.get("value", [])
        return items if items else None

    async def handle_folder_processing(
        self,
        processable_items: List[Dict[str, Any]],
        folder_processing_context: FolderProcessingContext,
    ):
        """Folder processing with workflow management using workflow crud service (no deduplication)"""
        try:
            schema = WorkflowRedisSchema()
            # Check if the workflow is already running
            if await self.redis_service.cache_get(
                schema.workflow_status_key(folder_processing_context.folder_id)
            ):
                logger.info(
                    f"Workflow {folder_processing_context.folder_id} is already running"
                )
                return JSONResponse(
                    content={"status": "already_running"},
                    status_code=200,
                )

            # Create workflow record in database using CRUD service
            workflow_data = WorkflowCreate(
                integration_id=folder_processing_context.integration_id,
                drive_id=folder_processing_context.drive_id,
                folder_id=folder_processing_context.folder_id,
                folder_name=folder_processing_context.folder_name,
                folder_type=folder_processing_context.folder_type,
                status=WorkflowStatusEnum.INITIATED,
                type=WorkflowTypeEnum.AUTOMATED,
                workflow_created_at=datetime.now(timezone.utc),
                processed_folder_id=folder_processing_context.processed_folder_id,
            )

            # Create the workflow in database
            db_workflow = self.workflow_service.add(workflow_data)
            # Set the workflow status to started in Redis for immediate status tracking
            await self.redis_service.cache_set(
                schema.workflow_status_key(folder_processing_context.folder_id),
                {"status": "started", "workflow_id": str(db_workflow.id)},
                86400 * 7,
            )
            workflow_id = await self.redis_service.workflow.create_workflow(
                drive_id=folder_processing_context.drive_id,
                folder_id=folder_processing_context.folder_id,
                folder_name=folder_processing_context.folder_name,
                folder_type=folder_processing_context.folder_type,
                processable_items=processable_items,
                db_workflow_id=db_workflow.id,
            )

            # Start Celery task
            task = process_sharepoint_workflow.delay(
                workflow_id, processable_items, db_workflow.id
            )

            # Register task with workflow
            await self.redis_service.workflow.register_task(workflow_id, task.id)
            workflow_obj = self.workflow_service.get_by_id(id=db_workflow.id)
            self.workflow_service.patch_attr(
                id=workflow_obj.id, attr="task_id", value=task.id
            )

            # Store legacy processing info for backward compatibility
            processing_info = {
                "type": folder_processing_context.folder_type,
                "items_count": len(processable_items),
                "workflow_id": workflow_id,
                "task_id": task.id,
                "processed_at": datetime.now(timezone.utc).isoformat(),
                "status": "started",
            }

            await self.redis_service.cache_set(
                schema.folder_last_processing_key(
                    folder_processing_context.drive_id,
                    folder_processing_context.folder_id,
                    folder_processing_context.folder_type.value,
                ),
                processing_info,
                86400 * 7,  # 7 days
            )

            logger.info(f"Started workflow {workflow_id} for folder processing")

            return JSONResponse(
                content={
                    "status": "started",
                    "workflow_id": workflow_id,
                    "task_id": task.id,
                },
                status_code=200,
            )

        except Exception:
            logger.error("Failed to start folder processing")
            return JSONResponse(
                content={
                    "status": "error",
                    "message": "An internal error occurred. Please try again later.",
                },
                status_code=500,
            )
