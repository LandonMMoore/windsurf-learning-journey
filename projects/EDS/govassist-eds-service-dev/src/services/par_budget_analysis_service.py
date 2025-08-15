from typing import Callable, Literal, Union

from loguru import logger
from sqlalchemy.orm import Session

from src.core.exceptions import InternalServerError, NotFoundError, ValidationError
from src.model.elasticsearch_models import ParModel
from src.model.par_budget_analysis_model import ParBudgetAnalysis
from src.repository.par_budget_analysis_repository import ParBudgetAnalysisRepository
from src.schema.budget_info_schema import BudgetInfoFind
from src.schema.elastic_search_schema import ParBudgetAnalysisES
from src.schema.par_budget_analysis_schema import ParBudgetAnalysisCreate
from src.services.base_service import BaseService
from src.services.budget_info_service import BudgetInfoService
from src.services.par_service import ParService
from src.services.project_detail_service import ProjectDetailService
from src.util.par_budget_analysis import _prepare_par_budget_analysis_data


class ParBudgetAnalysisService(BaseService):
    def __init__(
        self,
        session_factory: Callable[..., Session],
        par_service: ParService,
        project_detail_service: ProjectDetailService,
        budget_info_service: BudgetInfoService,
    ):
        super().__init__(ParBudgetAnalysisRepository(session_factory))
        self._par_service = par_service
        self._project_detail_service = project_detail_service
        self._budget_info_service = budget_info_service
        self._par_model = ParModel()

    async def _update_par_budget_analysis_in_elasticsearch(
        self,
        project_details_id: int,
        updated_data: dict,
        mode: Literal["add", "update"],
    ):
        """Update specific par_budget_analysis entry inside all ES docs with the given project_details_id"""

        client = await self._par_model._get_client()

        if mode == "add":
            script = {
                "source": """
                    if (ctx._source.containsKey("project_details") &&
                        ctx._source.project_details.id == params.project_details_id) {

                        if (ctx._source.project_details.par_budget_analysis == null) {
                            ctx._source.project_details.par_budget_analysis = [];
                        }

                        ctx._source.project_details.par_budget_analysis.add(params.updated_analysis);
                    }
                """,
                "lang": "painless",
                "params": {
                    "project_details_id": project_details_id,
                    "updated_analysis": updated_data,
                },
            }

        elif mode == "update":
            # Define painless script to update array item
            script = {
                "source": """
                    if (ctx._source.containsKey("project_details") &&
                        ctx._source.project_details.id == params.project_details_id &&
                        ctx._source.project_details.par_budget_analysis != null) {
                        
                        for (int i = 0; i < ctx._source.project_details.par_budget_analysis.length; i++) {
                            def item = ctx._source.project_details.par_budget_analysis[i];
                            for (entry in params.updated_analysis.entrySet()) {
                                item[entry.getKey()] = entry.getValue();
                            }
                        }
                    }
                """,
                "lang": "painless",
                "params": {
                    "project_details_id": project_details_id,
                    "updated_analysis": updated_data,
                },
            }

        # Define the query to find all documents with matching project_details.id
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
                f"Updated {response.get('updated', 0)} documents for par_budget_analysis in project_details.id={project_details_id}"
            )

        except Exception as e:
            logger.error(f"Failed to update ES par_budget_analysis: {str(e)}")
            raise InternalServerError(detail="Internal Server Error")

    async def add(self, data: ParBudgetAnalysisCreate) -> ParBudgetAnalysis:
        created_analysis = super().add(data)
        analysis_data = _prepare_par_budget_analysis_data(created_analysis)
        await self._update_par_budget_analysis_in_elasticsearch(
            project_details_id=created_analysis.project_details_id,
            updated_data=analysis_data,
            mode="add",
        )
        return created_analysis

    async def patch(self, id: int, data: dict) -> ParBudgetAnalysis:
        updated_analysis = super().patch(id, data)
        updated_analysis_es = ParBudgetAnalysisES.construct(**updated_analysis.__dict__)
        analysis_data = updated_analysis_es.model_dump(
            exclude={"additional_fund", "par_budget_analysis_fund"}
        )
        await self._update_par_budget_analysis_in_elasticsearch(
            project_details_id=updated_analysis.project_details_id,
            updated_data=analysis_data,
            mode="update",
        )
        return updated_analysis

    def read_by_project_details_id(
        self, project_details_id: int
    ) -> Union[ParBudgetAnalysis, None]:
        with self._repository.session_factory() as session:
            return (
                session.query(ParBudgetAnalysis)
                .filter(ParBudgetAnalysis.project_details_id == project_details_id)
                .first()
            )

    def read_by_par_id(self, par_id: int) -> Union[ParBudgetAnalysis, None]:
        with self._repository.session_factory() as session:
            return (
                session.query(ParBudgetAnalysis)
                .filter(ParBudgetAnalysis.par_id == par_id)
                .first()
            )

    async def get_par_analyst_data(self, par_id: str) -> dict:
        db_par = self._par_service.get_by_id(par_id)

        project_details = db_par.project_details
        if not project_details:
            raise NotFoundError(detail="Project details not found")

        if project_details.funding_source != "federal_grant":
            raise ValidationError(detail="Funding source must be federal grant")

        if not project_details.project_number:
            raise NotFoundError(detail="DIFS ID not found")

        existing_par_entry = self.read_by_par_id(par_id)

        if not existing_par_entry:
            new_par_entry = ParBudgetAnalysisCreate(
                par_id=par_id,
                project_details_id=project_details.id,
                part_rate=80,
                fa_rate=0.8,
                dc_rate=0.2,
                justification="",
            )

            created_entry = await self.add(new_par_entry)
            existing_par_entry = created_entry

        budget_analysis_id = existing_par_entry.id

        par_data = {
            "project_details_project_number": project_details.project_number,
            "soar_project_number": (
                project_details.fhwa_soar_project_no.project_number
                if project_details.fhwa_soar_project_no
                else None
            ),
            "fap_number": project_details.fap_number,
            "stip_number": (
                project_details.fhwa_stip_reference.stip_reference
                if project_details.fhwa_stip_reference
                else None
            ),
            "program": db_par.id,
            "cost_center_name": (
                project_details.cost_center.cost_center
                if project_details.cost_center
                else None
            ),
        }

        total_changes = {}
        budget_info_result = self._budget_info_service.get_list(
            BudgetInfoFind(par_id=par_id)
        )
        budget_infos = budget_info_result.get("founds", [])

        if not budget_infos:
            raise NotFoundError(detail="No budget information found for this PAR")

        for budget_info in budget_infos:
            task_name = budget_info.task_name
            for budget_item in budget_info.budget_items:
                total_changes[task_name] = total_changes.get(task_name, 0) + (
                    budget_item.change_amount or 0
                )

        return {
            "par_data": par_data,
            "total_changes": total_changes,
            "justification": existing_par_entry.justification,
            "part_rate": existing_par_entry.part_rate,
            "budget_analysis_id": budget_analysis_id,
        }
