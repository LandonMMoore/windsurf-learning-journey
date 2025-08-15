from typing import Callable, List

from sqlalchemy.orm import Session

from src.repository.workflow_crud_repository import WorkflowCrudRepository
from src.schema.workflow_schema import WorkflowProgressCreate
from src.services.base_service import BaseService


class WorkflowCrudService(BaseService):
    def __init__(self, session_factory: Callable[..., Session]):
        self.repository = WorkflowCrudRepository(session_factory)
        super().__init__(self.repository)

    def bulk_add_workflow_progress(
        self, progress: List[WorkflowProgressCreate]
    ) -> List[WorkflowProgressCreate]:
        return self.repository.bulk_add_workflow_progress(progress)

    def is_folder_processed(self, processed_folder_id: str) -> bool:
        return self.repository.is_folder_processed(processed_folder_id)
