import asyncio
from typing import Callable

from loguru import logger
from sqlalchemy.orm import Session

from src.core.exceptions import InternalServerError
from src.model.elasticsearch_models import ParModel
from src.repository.additional_fund_repository import AdditionalFundRepository
from src.schema.elastic_search_schema import AdditionalFundES
from src.services.base_service import BaseService
from src.services.par_budget_analysis_service import ParBudgetAnalysisService
from src.util.additional_fund import serialize_fund


class AdditionalFundService(BaseService):
    def __init__(
        self,
        session_factory: Callable[..., Session],
        par_budget_analysis_service: ParBudgetAnalysisService,
    ):
        super().__init__(AdditionalFundRepository(session_factory))
        self._par_budget_analysis_service = par_budget_analysis_service
        self._par_model = ParModel()

    async def _update_additional_fund_in_elasticsearch(
        self,
        project_details_id: int,
        par_budget_analysis_id: int,
        updated_data: dict,
        is_delete: bool = False,
    ):
        client = await self._par_model._get_client()

        script = {
            "source": """
                if (ctx._source.project_details?.id == params.project_details_id) {
                    def analyses = ctx._source.project_details.par_budget_analysis;
                    if (analyses != null) {
                        for (a in analyses) {
                            if (a.id != null && a.id == params.par_budget_analysis_id) {
                                if (a.additional_funds == null) {
                                    a.additional_funds = [];
                                }

                                if (params.is_delete == true) {
                                    // Delete mode: remove by ID
                                    a.additional_funds.removeIf(f -> f.id == params.updated_data.id);
                                } else {
                                    // Upsert mode: update if exists, else add
                                    boolean updated = false;
                                    for (int i = 0; i < a.additional_funds.length; i++) {
                                        if (a.additional_funds[i].id == params.updated_data.id) {
                                            a.additional_funds[i] = params.updated_data;
                                            updated = true;
                                            break;
                                        }
                                    }
                                    if (!updated) {
                                        a.additional_funds.add(params.updated_data);
                                    }
                                }
                            }
                        }
                    }
                }
            """,
            "lang": "painless",
            "params": {
                "project_details_id": project_details_id,
                "par_budget_analysis_id": par_budget_analysis_id,
                "updated_data": updated_data,
                "is_delete": is_delete,
            },
        }

        query = {
            "query": {"term": {"project_details.id": project_details_id}},
            "script": script,
        }

        try:
            response = await client.update_by_query(
                index=self._par_model.index_name,
                body=query,
                conflicts="proceed",
                refresh=True,
            )
            logger.info(
                f"Updated {response.get('updated', 0)} documents for additional_fund in project_details.id={project_details_id}"
            )
            logger.info(
                f"Updated {response.get('updated', 0)} documents for additional_fund in project_details.id={project_details_id}"
            )
        except Exception:
            logger.error("Failed to update ES additional_fund")
            raise InternalServerError(detail="Internal Server Error")

    def add(self, data):
        created_fund = super().add(data)

        additional_fund_es = AdditionalFundES.model_validate(created_fund)
        additional_fund_es_data = additional_fund_es.model_dump()

        budget_analysis = self._par_budget_analysis_service.get_by_id(
            data.par_budget_analysis_id
        )

        # Update in Elasticsearch
        asyncio.run(
            self._update_additional_fund_in_elasticsearch(
                project_details_id=budget_analysis.project_details_id,
                par_budget_analysis_id=data.par_budget_analysis_id,
                updated_data=additional_fund_es_data,
            )
        )

        return created_fund

    def patch(self, id: int, data: dict):
        updated_fund = super().patch(id, data)

        # Prepare ES data
        additional_fund_es = AdditionalFundES.model_validate(updated_fund)
        additional_fund_es_data = additional_fund_es.model_dump()

        # Get project_details_id from related budget_analysis
        budget_analysis = self._par_budget_analysis_service.get_by_id(
            data.par_budget_analysis_id
        )

        # Update in Elasticsearch
        asyncio.run(
            self._update_additional_fund_in_elasticsearch(
                project_details_id=budget_analysis.project_details_id,
                par_budget_analysis_id=data.par_budget_analysis_id,
                updated_data=additional_fund_es_data,
            )
        )

        return updated_fund

    def remove_by_id(self, id: int):
        additional_fund = self.get_by_id(id)
        additional_fund_es = AdditionalFundES.construct(**additional_fund.__dict__)
        additional_fund_es_data = additional_fund_es.model_dump(
            exclude={"federal_fund"}
        )

        deleted_fund = super().remove_by_id(id)

        asyncio.run(
            self._update_additional_fund_in_elasticsearch(
                project_details_id=additional_fund.par_budget_analysis.project_details_id,
                par_budget_analysis_id=additional_fund.par_budget_analysis_id,
                updated_data=additional_fund_es_data,
                is_delete=True,
            )
        )

        return deleted_fund

    def get_by_budget_analysis_id(self, budget_analysis_id: int):
        par_budget_analysis_data = self._par_budget_analysis_service.get_by_id(
            budget_analysis_id
        )
        if par_budget_analysis_data.additional_fund:
            return [
                serialize_fund(fund)
                for fund in par_budget_analysis_data.additional_fund
            ]
        else:
            return []
