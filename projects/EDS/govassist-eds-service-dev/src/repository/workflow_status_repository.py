from typing import Callable, List, Optional

from sqlalchemy.orm import Session

from src.model.workflow_status_model import WorkflowStatus
from src.repository.base_repository import BaseRepository


class WorkflowStatusRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, WorkflowStatus)

    def get_all_statuses(self) -> List[WorkflowStatus]:
        """Get all workflow statuses"""
        with self.session_factory() as session:
            return session.query(self.model).all()

    def get_by_name(self, name: str) -> Optional[WorkflowStatus]:
        """Get workflow status by name (status_code)"""
        with self.session_factory() as session:
            return (
                session.query(self.model).filter(self.model.state_code == name).first()
            )

    def get_next_status(self, current_state: str) -> List[str]:
        """Get possible next states for a given current status"""
        with self.session_factory() as session:
            workflow_status = (
                session.query(self.model)
                .filter(self.model.state_code == current_state)
                .first()
            )
            if workflow_status and workflow_status.next_state_codes:
                return workflow_status.next_state_codes
            return []

    def can_view(self, status: str) -> bool:
        """Check if the current status allows viewing"""
        # This can be enhanced later when the rbac needs to implemented
        return True

    def can_edit(self, status: str) -> bool:
        """Check if the current status allows editing"""
        # This can be enhanced later when the rbac needs to implemented
        return True
