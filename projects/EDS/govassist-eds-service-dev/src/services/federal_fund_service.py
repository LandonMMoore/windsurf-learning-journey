from typing import Callable, List, Optional

from sqlalchemy.orm import Session

from src.model.federal_fund_model import FederalFund
from src.repository.federal_fund_repository import FederalFundRepository
from src.schema.federal_fund_schema import FederalFundFind
from src.services.base_service import BaseService


class FederalFundService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(FederalFundRepository(session_factory))

    def get_list(
        self,
        find: Optional[FederalFundFind] = None,
        exclude_fund_id: Optional[List[int]] = None,
    ) -> List[FederalFund]:
        if find is None:
            find = FederalFundFind()

        result = super().get_list(find)

        if exclude_fund_id and "founds" in result:
            original_total = (
                result["search_options"]["total_count"]
                if "search_options" in result
                and "total_count" in result["search_options"]
                else 0
            )

            original_page_count = len(result["founds"])
            result["founds"] = [
                fund for fund in result["founds"] if fund.id not in exclude_fund_id
            ]
            items_removed = original_page_count - len(result["founds"])

            if "search_options" in result and "total_count" in result["search_options"]:
                result["search_options"]["total_count"] = max(
                    0, original_total - items_removed
                )

        return result
