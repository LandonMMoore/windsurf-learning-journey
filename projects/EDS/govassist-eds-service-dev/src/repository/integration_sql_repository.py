from typing import Callable, List

from sqlalchemy import update, select
from sqlalchemy.orm import Session

from src.model.integration_model import EdsIntegration
from src.repository.base_repository import BaseRepository
from src.schema.integration_schema import (
    ActiveIntegration,
    IntegrationCreate,
    SubscribeDirectory,
)


class IntegrationSqlRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, EdsIntegration)

    def get_user_subscription(self, user_id: int):
        with self.session_factory() as session:
            subscription = (
                session.query(EdsIntegration)
                .filter(EdsIntegration.user_id == user_id, EdsIntegration.is_active)
                .first()
            )
            if not subscription:
                return None
            return subscription

    def get_active_integration(self):
        with self.session_factory() as session:
            integration = (
                session.query(EdsIntegration).filter(EdsIntegration.is_active).first()
            )
            if not integration:
                return None
            return ActiveIntegration(
                name=integration.user.name, **integration.__dict__
            ).model_dump()

    def manage_integration(self, user_id: int, result: dict, data: SubscribeDirectory):
        with self.session_factory() as session:
            # deactivate all integrations
            session.execute(update(EdsIntegration).values(is_active=False))

            integration = (
                session.query(EdsIntegration)
                .filter(EdsIntegration.integration_id == data.integration_id)
                .first()
            )

            if integration:
                # update the integration
                integration.user_id = user_id
                integration.integration_uuid = data.integration_uuid
                integration.webhook_info = result
                integration.folder_id = data.folder_id
                integration.folder_name = data.folder_name
                integration.site_id = data.site_id
                integration.drive_id = data.drive_id
                integration.path = data.path
                integration.list_id = data.list_id
                integration.is_active = True
                session.commit()
            else:
                # create the integration
                validated_data = IntegrationCreate(
                    user_id=user_id,
                    integration_id=data.integration_id,
                    integration_uuid=data.integration_uuid,
                    webhook_info=result,
                    folder_id=data.folder_id,
                    folder_name=data.folder_name,
                    site_id=data.site_id,
                    drive_id=data.drive_id,
                    path=data.path,
                    list_id=data.list_id,
                    is_active=True,
                )
                integration = EdsIntegration(**validated_data.model_dump())
                session.add(integration)
                session.commit()


    async def get_all_subscriptions(self)->List[str]:
        with self.session_factory() as session:
            try:
                query = select(EdsIntegration.webhook_info["id"].as_string())
                rows = session.execute(query).all()
            except Exception:
                return []
            ids = [row[0] for row in rows]
            return ids
