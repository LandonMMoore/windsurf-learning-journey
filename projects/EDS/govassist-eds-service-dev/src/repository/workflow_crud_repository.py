from typing import Callable, List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.exceptions import DuplicatedError, ValidationError
from src.model.workflow import EdsWorkflow
from src.repository.base_repository import BaseRepository
from src.schema.workflow_schema import WorkflowProgressCreate


class WorkflowCrudRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, EdsWorkflow)
        self._session_factory = session_factory

    def bulk_add_workflow_progress(
        self, progress: List[WorkflowProgressCreate]
    ) -> bool:
        with self._session_factory() as session:
            try:
                session.bulk_save_objects(progress)
                session.commit()
                return True
            except IntegrityError as e:
                session.rollback()
                raise DuplicatedError(detail=str(e.orig))
            except SQLAlchemyError as e:
                session.rollback()
                raise ValidationError(detail=str(e))
            except Exception as e:
                session.rollback()
                raise ValidationError(detail=str(e))

    def is_folder_processed(self, processed_folder_id: str) -> bool:
        with self._session_factory() as session:
            return session.query(EdsWorkflow).filter(EdsWorkflow.processed_folder_id == processed_folder_id).first()
