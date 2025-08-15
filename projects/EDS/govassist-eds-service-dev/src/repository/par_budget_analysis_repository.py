from typing import List

from src.model.par_budget_analysis_model import ParBudgetAnalysis
from src.repository.base_repository import BaseRepository


class ParBudgetAnalysisRepository(BaseRepository):
    def __init__(self, session_factory):
        super().__init__(session_factory, ParBudgetAnalysis)

    def get_by_project_details_id(
        self, project_details_id: int
    ) -> List[ParBudgetAnalysis]:
        with self.session_factory() as session:
            return (
                session.query(ParBudgetAnalysis)
                .filter(ParBudgetAnalysis.project_details_id == project_details_id)
                .all()
            )

    def get_by_par_id(self, par_id: int) -> List[ParBudgetAnalysis]:
        with self.session_factory() as session:
            return (
                session.query(ParBudgetAnalysis)
                .filter(ParBudgetAnalysis.par_id == par_id)
                .all()
            )

    def _get_eager_options(self):
        return [
            self.model.par,
            self.model.project_details,
            self.model.project_details.cost_center,
            self.model.project_details.fhwa_soar_project_no,
            self.model.project_details.fhwa_stip_reference,
        ]
