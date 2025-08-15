from datetime import datetime
from typing import Callable, Dict, Set

from sqlalchemy.orm import Session

from src.core.exceptions import DuplicatedError, NotFoundError, ValidationError
from src.model.budget_analysis_fund_model import ParBudgetAnalysisFund
from src.repository.budget_analysis_fund_repository import BudgetAnalysisFundRepository
from src.schema.budget_analysis_fund_schema import (
    BudgetAnalysisFundDelete,
    BudgetAnalysisFundRequest,
)
from src.services.base_service import BaseService
from src.services.federal_fund_service import FederalFundService
from src.services.par_budget_analysis_service import ParBudgetAnalysisService
from src.services.par_service import ParService
from src.util.budget_analysis_fund import (
    serialize_fund,
    validate_fund_availability,
    validate_fund_duplicates,
    validate_fund_types,
    validate_part_rate_and_splits,
)


class BudgetAnalysisFundService(BaseService):
    def __init__(
        self,
        session_factory: Callable[..., Session],
        par_service: ParService,
        par_budget_analysis_service: ParBudgetAnalysisService,
        federal_fund_service: FederalFundService,
    ):
        super().__init__(BudgetAnalysisFundRepository(session_factory))
        self._par_service = par_service
        self._par_budget_analysis_service = par_budget_analysis_service
        self._federal_fund_service = federal_fund_service
        self._session_factory = session_factory

    def create_budget_analysis_fund(
        self, request_data: BudgetAnalysisFundRequest
    ) -> Dict:
        db_par = self._par_service.get_by_id(request_data.par_id)

        project_details = db_par.project_details
        if not project_details:
            raise NotFoundError(detail="Project details not found")

        if project_details.project_number != request_data.difs_id:
            raise ValidationError(detail="DIFS ID mismatch")

        if project_details.funding_source != "federal_grant":
            raise ValidationError(detail="Funding source must be federal grant")

        existing_par_entry = (
            self._par_budget_analysis_service.read_by_project_details_id(
                project_details.id
            )
        )

        if not existing_par_entry:
            raise NotFoundError(detail="PAR budget analysis not found")

        validate_part_rate_and_splits(
            request_data.part_rate, request_data.fa, request_data.dc
        )

        fund_id_count: Dict[int, int] = {}
        fund_type_map: Dict[int, Set[str]] = {}
        valid_fund_types = {"F.A.", "DC Match"}

        validate_fund_duplicates([fund.dict() for fund in request_data.funds])

        for fund in request_data.funds:
            if fund.fund_type not in valid_fund_types:
                raise ValidationError(detail=f"Invalid fund type: {fund.fund_type}")

            fund_id_count[fund.fund_id] = fund_id_count.get(fund.fund_id, 0) + 1
            if fund.fund_id in fund_type_map:
                fund_type_map[fund.fund_id].add(fund.fund_type)
            else:
                fund_type_map[fund.fund_id] = {fund.fund_type}

        validate_fund_types(fund_type_map, request_data.part_rate)

        for fund in request_data.funds:
            federal_fund = self._federal_fund_service.get_by_id(fund.fund_id)
            if not federal_fund:
                raise NotFoundError(detail=f"Invalid fund ID: {fund.fund_id}")

            if fund.fund_type == "F.A.":
                total_deduction = sum(
                    [
                        fund.ce or 0,
                        fund.construction or 0,
                        fund.feasibility_studies or 0,
                        fund.design or 0,
                        fund.rights_of_way or 0,
                        fund.equipment or 0,
                    ]
                )

                validate_fund_availability(
                    fund.fund_id,
                    fund.fund_type,
                    total_deduction,
                    federal_fund.fund_available,
                )

            existing_fund = self._repository.read_by_par_budget_id_and_federal_fund_id_and_fund_type(
                existing_par_entry.id,
                fund.fund_id,
                fund.fund_type,
            )

            if existing_fund:
                existing_fund.ce = (existing_fund.ce or 0) + (fund.ce or 0)
                existing_fund.construction = (existing_fund.construction or 0) + (
                    fund.construction or 0
                )
                existing_fund.feasibility_studies = (
                    existing_fund.feasibility_studies or 0
                ) + (fund.feasibility_studies or 0)
                existing_fund.design = (existing_fund.design or 0) + (fund.design or 0)
                existing_fund.rights_of_way = (existing_fund.rights_of_way or 0) + (
                    fund.rights_of_way or 0
                )
                existing_fund.equipment = (existing_fund.equipment or 0) + (
                    fund.equipment or 0
                )
                existing_fund.updated_at = datetime.utcnow()
            else:
                new_fund = ParBudgetAnalysisFund(
                    federal_fund_id=fund.fund_id,
                    par_budget_id=existing_par_entry.id,
                    fund_type=fund.fund_type,
                    ce=fund.ce or 0,
                    construction=fund.construction or 0,
                    feasibility_studies=fund.feasibility_studies or 0,
                    design=fund.design or 0,
                    rights_of_way=fund.rights_of_way or 0,
                    equipment=fund.equipment or 0,
                )
                with self._repository.session_factory() as session:
                    session.add(new_fund)
                    session.commit()

        with self._repository.session_factory() as session:
            session.commit()

        return {"message": "Budget analysis fund created successfully"}

    def get_budget_analysis_fund(self, par_id: int) -> Dict:
        funds = self._repository.get_budget_analysis_fund(par_id)
        par_budget_analysis = self._par_budget_analysis_service.read_by_par_id(par_id)
        if not par_budget_analysis:
            raise NotFoundError(detail="PAR budget analysis not found")

        response = {
            "par_id": par_id,
            "part_rate": par_budget_analysis.part_rate,
            "fa_rate": par_budget_analysis.fa_rate,
            "dc_rate": par_budget_analysis.dc_rate,
            "justification": par_budget_analysis.justification,
            "approved_funds": [serialize_fund(f) for f in funds],
        }

        return response

    def delete_budget_analysis_fund(self, data: BudgetAnalysisFundDelete) -> Dict:
        fa_fund = self._repository.read_by_par_budget_id_and_analysis_fund_id(
            data.budget_analysis_id,
            data.FA_fund_id,
        )

        dc_fund = self._repository.read_by_par_budget_id_and_analysis_fund_id(
            data.budget_analysis_id,
            data.DC_fund_id,
        )

        if not fa_fund or not dc_fund:
            raise NotFoundError(
                detail="One or both funds not found under the specified budget analysis ID"
            )

        if fa_fund.federal_fund_id != dc_fund.federal_fund_id:
            raise ValidationError(detail="Fund IDs do not match the specified IDs")

        if not fa_fund.is_requested_fund:
            raise DuplicatedError(detail="FA fund is Approved, cannot delete")

        self._repository.delete_by_id(fa_fund.id)
        self._repository.delete_by_id(dc_fund.id)

        return {"message": "Budget analysis fund deleted successfully"}
