from typing import Callable, List, Optional

from sqlalchemy.orm import Session, joinedload

from src.model.budget_analysis_fund_model import ParBudgetAnalysisFund
from src.model.par_budget_analysis_model import ParBudgetAnalysis
from src.repository.base_repository import BaseRepository


class BudgetAnalysisFundRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, ParBudgetAnalysisFund)

    def read_by_par_budget_id_and_federal_fund_id_and_fund_type(
        self, par_budget_id: int, federal_fund_id: int, fund_type: str
    ) -> Optional[ParBudgetAnalysisFund]:
        """Read a ParBudgetAnalysisFund by par budget ID, federal fund ID, and fund type."""
        with self.session_factory() as session:
            return (
                session.query(ParBudgetAnalysisFund)
                .filter(
                    ParBudgetAnalysisFund.par_budget_id == par_budget_id,
                    ParBudgetAnalysisFund.federal_fund_id == federal_fund_id,
                    ParBudgetAnalysisFund.fund_type == fund_type,
                )
                .first()
            )

    def read_by_par_budget_id_and_analysis_fund_id(
        self, par_budget_id: int, analysis_fund_id: int
    ) -> Optional[ParBudgetAnalysisFund]:
        with self.session_factory() as session:
            return (
                session.query(ParBudgetAnalysisFund)
                .filter(
                    ParBudgetAnalysisFund.par_budget_id == par_budget_id,
                    ParBudgetAnalysisFund.id == analysis_fund_id,
                )
                .first()
            )

    def get_budget_analysis_fund(self, par_id: int) -> List[ParBudgetAnalysisFund]:
        """Get all budget analysis funds for a given PAR ID."""
        with self.session_factory() as session:
            return (
                session.query(ParBudgetAnalysisFund)
                .join(ParBudgetAnalysis)
                .filter(ParBudgetAnalysis.par_id == par_id)
                .options(
                    joinedload(ParBudgetAnalysisFund.federal_fund),
                    joinedload(ParBudgetAnalysisFund.par_budget_analysis),
                )
                .all()
            )
