from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, List, Optional

from src.core.exceptions import BadRequestError, InternalServerError
from src.model.par_model import Par
from src.repository.par_activity_repository import ParActivityRepository
from src.repository.workflow_status_repository import WorkflowStatusRepository
from src.schema.par_activity_schema import ParActivityCreate


class ParStatus(Enum):
    DRAFT_UNSUBMITTED = "Draft"
    SUBMITTED = "Submitted"
    IN_PROGRESS = "In Progress"
    PENDING_OCFO_BUDGET_VALIDATION = "Pending OCFO Budget Validation"
    READY_FOR_REVIEW = "Ready for Review"
    SUBMITTED_TO_PROTRACK = "Submitted to Protrack+"


@dataclass
class StatusTransition:
    to_status: ParStatus
    action: Optional[Callable] = None
    conditions: Optional[List[Callable]] = None


@dataclass
class StatusConfig:
    actions: Optional[List[Callable]] = None
    allowed_transitions: List[StatusTransition] = None


class ParStateService:
    def __init__(
        self,
        workflow_status_repository: WorkflowStatusRepository,
        session_factory: Callable,
    ):
        self.workflow_status_repository = workflow_status_repository
        self.session_factory = session_factory

    def get_possible_next_statuses(self, par: Par) -> List[str]:
        """Get all possible next statuses for the PAR"""
        try:
            current_status = par.current_status
            if not self.validate_status(current_status):
                raise BadRequestError(f"Invalid current status: {current_status}")
            return self.get_possible_transitions(current_status)
        except Exception:
            raise InternalServerError("Failed to get next statuses")

    def transit_status(
        self, target_status: str, current_status: str, par_id: int, user_id: str = None
    ) -> bool:
        """Attempt to transition the PAR to a new status"""
        try:
            if not self.validate_status(target_status):
                raise BadRequestError(f"Invalid target status: {target_status}")
            return self.transition(target_status, current_status, par_id, user_id)
        except Exception:
            raise InternalServerError("Failed to transit status")

    def get_current_status(self, par: Par) -> str:
        """Get the current status of the PAR"""
        if not par.current_status:
            raise BadRequestError("PAR has no current status")
        return par.current_status

    def can_view(self, status: str) -> bool:
        """Check if the current status allows viewing"""
        try:
            if not self.validate_status(status):
                return False
            return self.workflow_status_repository.can_view(status)
        except Exception:
            raise InternalServerError("Failed to check view permission")

    def can_edit(self, status: str) -> bool:
        """Check if the current status allows editing"""
        try:
            if not self.validate_status(status):
                return False
            return self.workflow_status_repository.can_edit(status)
        except Exception:
            raise InternalServerError("Failed to check edit permission")

    def get_status_description(self, status: str) -> Optional[str]:
        """Get the description for a status"""
        try:
            if not self.validate_status(status):
                return None
            workflow_status = self.workflow_status_repository.get_by_name(status)
            return workflow_status.description if workflow_status else None
        except Exception:
            raise InternalServerError("Failed to get status description")

    # Status machine core methods
    def get_possible_transitions(self, current_status: str) -> List[str]:
        """Get all possible transitions from the current status"""
        try:
            return self.workflow_status_repository.get_next_status(current_status)
        except Exception:
            raise InternalServerError("Failed to get next transitions")

    def transition(
        self,
        target_status: str,
        current_status: str,
        par_id: int,
        user_name: str = None,
    ) -> bool:
        """Attempt to transition the PAR to a new status and create activity record"""
        if not self.can_transit_to_status(current_status, target_status):
            raise BadRequestError(
                f"Cannot transition from {current_status} to {target_status}"
            )

        # Create PAR activity record to persist the status change
        par_activity_repo = ParActivityRepository(self.session_factory)

        activity_data = ParActivityCreate(
            par_id=par_id,
            activity=f"Status changed from {current_status} to {target_status}",
            status=target_status,
            date=datetime.now(),
            user=user_name or "system",
            comments=f"Status transition to {target_status}",
        )

        par_activity_repo.create(activity_data)

        # Update the in-memory current_status
        # par.current_status = target_status
        return True

    def can_transit_to_status(self, current_status: str, target_status: str) -> bool:
        """Check if a transition from current_status to target_status is possible"""
        try:
            possible_transitions = self.get_possible_transitions(current_status)
            return target_status in possible_transitions
        except (KeyError, AttributeError):
            return False

    def validate_status(self, status: str) -> bool:
        """Validate if a status exists in the workflow"""
        try:
            return self.workflow_status_repository.get_by_name(status) is not None
        except Exception:
            return False
