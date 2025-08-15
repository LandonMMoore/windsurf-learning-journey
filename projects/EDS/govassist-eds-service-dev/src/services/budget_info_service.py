from typing import Callable

from loguru import logger
from sqlalchemy.orm import Session

from src.core.exceptions import InternalServerError
from src.model.elasticsearch_models import ParModel
from src.repository.budget_info_repository import BudgetInfoRepository
from src.schema.budget_info_schema import (
    BudgetInfoCreate,
    BudgetInfoInfo,
    BudgetInfoUpdate,
)
from src.schema.elastic_search_schema import BudgetInfoBaseES
from src.services.base_service import BaseService


class BudgetInfoService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(BudgetInfoRepository(session_factory))
        self._par_model = ParModel()

    async def _update_budget_info_in_elasticsearch(
        self, par_id: int, updated_data: dict
    ):
        client = await self._par_model._get_client()
        script = {
            "source": """
                if (ctx._source.id == params.par_id) {
                    if (ctx._source.budget_info == null) {
                        ctx._source.budget_info = [];
                    }

                    boolean found = false;
                    for (int i = 0; i < ctx._source.budget_info.length; i++) {
                        def b = ctx._source.budget_info[i];
                        if (b.id == params.updated_data.id) {
                            // Only update scalar fields
                            for (entry in params.updated_data.entrySet()) {
                                if (entry.getKey() != 'budget_items') {
                                    b[entry.getKey()] = entry.getValue();
                                }
                            }
                            found = true;
                            break;
                        }
                    }

                    if (!found) {
                        ctx._source.budget_info.add(params.updated_data);
                    }
                }
            """,
            "lang": "painless",
            "params": {
                "par_id": par_id,
                "updated_data": updated_data,
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
                f"Updated {response.get('updated', 0)} docs for budget_info in par_id={par_id}"
            )
            logger.info(
                f"Updated {response.get('updated', 0)} docs for budget_info in par_id={par_id}"
            )
        except Exception:
            logger.error("Failed to update budget_info in ES")
            raise InternalServerError(detail="Internal Server Error")

    async def add(self, data: BudgetInfoCreate) -> BudgetInfoInfo:
        created_budget_info = super().add(data)

        budget_info_es = BudgetInfoBaseES.model_validate(created_budget_info)
        budget_info_es_data = budget_info_es.model_dump()
        await self._update_budget_info_in_elasticsearch(
            data.par_id, budget_info_es_data
        )

        return created_budget_info

    async def patch(self, id: int, schema: BudgetInfoUpdate) -> BudgetInfoInfo:
        updated_budget_info = super().patch(id, schema)

        budget_info_es = BudgetInfoBaseES.model_validate(updated_budget_info)
        budget_info_es_data = budget_info_es.model_dump()
        await self._update_budget_info_in_elasticsearch(
            updated_budget_info.par_id, budget_info_es_data
        )

        return updated_budget_info
