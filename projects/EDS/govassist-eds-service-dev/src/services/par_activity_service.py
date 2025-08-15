from typing import Callable

from loguru import logger
from sqlalchemy.orm import Session

from src.core.exceptions import InternalServerError, NotFoundError
from src.model.elasticsearch_models import ParModel
from src.repository.par_activity_repository import ParActivityRepository
from src.repository.par_repository import ParRepository
from src.schema.par_activity_schema import ParActivityFind
from src.services.base_service import BaseService


class ParActivityService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(ParActivityRepository(session_factory))
        self._par_model = ParModel()
        self._par_repository = ParRepository(session_factory)

    async def _update_par_activities_in_elasticsearch(self, par_id: int, data: dict):
        client = await self._par_model._get_client()
        script = {
            "source": """
                if (ctx._source.id == params.par_id) {
                    if (ctx._source.par_activities == null) {
                        ctx._source.par_activities = [];
                    }

                    ctx._source.par_activities.add(params.data);
                }
            """,
            "lang": "painless",
            "params": {
                "par_id": par_id,
                "data": data,
            },
        }
        query = {"query": {"term": {"id": par_id}}, "script": script}

        try:
            response = await client.update_by_query(
                index=self._par_model.index_name,
                body=query,
                conflicts="proceed",
                refresh=True,
            )
            logger.info(
                f"Updated {response.get('updated', 0)} docs for par_activities in par_id={par_id}"
            )
            logger.info(
                f"Updated {response.get('updated', 0)} docs for par_activities in par_id={par_id}"
            )
        except Exception:
            logger.error("Failed to update par_activities in ES")
            raise InternalServerError(detail="Internal Server Error")

    async def add(self, data, update_elasticsearch: bool = True):
        par = self._par_repository.read_by_id(data.par_id)
        if not par:
            raise NotFoundError(detail=f"PAR with ID {data.par_id} not found")

        created_activity = super().add(data)

        if update_elasticsearch:
            activity_data = self._par_model._get_clean_model_data(created_activity)
            await self._update_par_activities_in_elasticsearch(
                data.par_id, activity_data
            )

        return created_activity

    async def patch(self, id: int, data: dict):
        updated_activity = super().patch(id, data)

        # We are not updating the par_activities. so not updating in the elasticsearch.
        # activity_data = self._par_model._get_clean_model_data(updated_activity)
        return updated_activity

    def get_by_par_id(self, par_id: int):
        # Create a schema instance with par_id for filtering
        filter_schema = ParActivityFind(par_id=par_id)
        par_activities = self._repository.read_by_options(filter_schema)
        return par_activities

    def fetch_par_latest_activity_status(self, par_id: int):
        filter_schema = ParActivityFind(par_id=par_id)

        filter_schema.ordering = "-created_at"
        result = self._repository.read_by_options(filter_schema)
        par_activities = result.get("founds", [])

        if par_activities:
            return par_activities[0].status
        return None
