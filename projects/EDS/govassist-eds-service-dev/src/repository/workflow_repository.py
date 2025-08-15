from abc import ABC
from typing import Any, Dict, Generic, List, Tuple, Type, TypeVar

from loguru import logger
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.model.workflow_master_model import (
    WorkflowMasterAccount,
    WorkflowMasterAward,
    WorkflowMasterCostCenter,
    WorkflowMasterFund,
    WorkflowMasterParentTask,
    WorkflowMasterProgram,
    WorkflowMasterProjectDetails,
    WorkflowMasterSponsor,
    WorkflowMasterSubTask,
    WorkflowMasterTransaction,
)

T = TypeVar("T")


class BaseRepository(Generic[T], ABC):
    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    def bulk_insert(self, items: List[T], batch_size: int = 1000) -> int:
        """Bulk insert items with batch processing"""
        if not items:
            logger.info("No items to insert")
            return 0

        total_inserted = 0
        try:
            for i in range(0, len(items), batch_size):
                batch = items[i : i + batch_size]
                self.session.bulk_save_objects(batch)
                self.session.commit()
                total_inserted += len(batch)
                logger.info(f"Inserted batch {i//batch_size + 1}: {len(batch)} records")

        except IntegrityError:
            self.session.rollback()
            logger.error("Integrity error during bulk insert")
            raise
        except SQLAlchemyError:
            self.session.rollback()
            logger.error("Database error during bulk insert")
            raise
        except Exception:
            self.session.rollback()
            logger.error("Unexpected error during bulk insert")
            raise

        return total_inserted

    def get_id_mapping(self, key_field: str = "number") -> Dict[Any, int]:
        """Get mapping of key_field to id"""
        try:
            records = (
                self.session.query(
                    getattr(self.model_class, "id"),
                    getattr(self.model_class, key_field),
                )
                .filter(getattr(self.model_class, "deleted_at").is_(None))
                .all()
            )

            # Handle None values in the mapping
            mapping = {}
            for record in records:
                key = getattr(record, key_field)
                if key is not None:  # Only add non-None keys
                    mapping[key] = record.id

            return mapping

        except AttributeError:
            logger.error(f"Model {self.model_class.__name__} missing required fields")
            raise
        except SQLAlchemyError:
            logger.error("Database error in get_id_mapping")
            raise
        except Exception:
            logger.error("Unexpected error in get_id_mapping")
            raise

    def delete_all(self) -> int:
        """Soft delete all records"""
        try:
            # TODO: Uncomment this when we have a way to handle soft delete
            # count = self.session.query(self.model_class).filter(
            #     getattr(self.model_class, 'deleted_at').is_(None)
            # ).update({
            #     'deleted_at': datetime.utcnow()
            # }, synchronize_session=False)  # More efficient for bulk updates
            count = self.session.query(self.model_class).delete()
            self.session.commit()
            return count

        except AttributeError:
            self.session.rollback()
            logger.error(f"Model {self.model_class.__name__} missing deleted_at field")
            raise
        except SQLAlchemyError:
            self.session.rollback()
            logger.error("Database error in delete_all")
            raise
        except Exception:
            self.session.rollback()
            logger.error("Unexpected error in delete_all")
            raise

    def count_active(self) -> int:
        """Count active records"""
        try:
            return (
                self.session.query(self.model_class)
                .filter(getattr(self.model_class, "deleted_at").is_(None))
                .count()
            )
        except AttributeError:
            logger.error(f"Model {self.model_class.__name__} missing deleted_at field")
            raise
        except SQLAlchemyError:
            logger.error("Database error in count_active")
            raise
        except Exception:
            logger.error("Unexpected error in count_active")
            raise


class WorkflowRepository:
    def __init__(self, session: Session):
        if not session:
            raise ValueError("Session cannot be None")

        self.session = session

        # Initialize repositories
        try:
            self.funds = BaseRepository(session, WorkflowMasterFund)
            self.programs = BaseRepository(session, WorkflowMasterProgram)
            self.cost_centers = BaseRepository(session, WorkflowMasterCostCenter)
            self.accounts = BaseRepository(session, WorkflowMasterAccount)
            self.awards = BaseRepository(session, WorkflowMasterAward)
            self.sponsors = BaseRepository(session, WorkflowMasterSponsor)
            self.projects = BaseRepository(session, WorkflowMasterProjectDetails)
            self.parent_tasks = BaseRepository(session, WorkflowMasterParentTask)
            self.sub_tasks = BaseRepository(session, WorkflowMasterSubTask)
            self.transactions = BaseRepository(session, WorkflowMasterTransaction)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize repositories: {str(e)}")

    def clear_all_data(self) -> Dict[str, int]:
        """Clear all data in proper order (respecting foreign key constraints)"""
        deletion_counts = {}

        # Define deletion order (child to parent to respect FK constraints)
        deletion_order = [
            ("transactions", self.transactions),
            ("sub_tasks", self.sub_tasks),
            ("parent_tasks", self.parent_tasks),
            ("projects", self.projects),
            ("sponsors", self.sponsors),
            ("awards", self.awards),
            ("programs", self.programs),
            ("cost_centers", self.cost_centers),
            ("accounts", self.accounts),
            ("funds", self.funds),
        ]

        try:
            for table_name, repository in deletion_order:
                try:
                    count = repository.delete_all()
                    deletion_counts[table_name] = count
                    logger.info(f"Cleared {count} records from {table_name}")
                except Exception:
                    logger.error(f"Failed to clear {table_name}")
                    deletion_counts[table_name] = 0
                    raise

            total_deleted = sum(deletion_counts.values())
            logger.info(f"Successfully cleared {total_deleted} total records")
            return deletion_counts

        except Exception:
            logger.error("Error during clear_all_data")
            raise

    def health_check(self) -> Dict[str, Any]:
        """Health check for the repository - useful for debugging in Celery tasks"""
        health_status = {
            "session_active": False,
            "tables_accessible": {},
            "total_records": {},
        }

        try:
            # Check if session is active
            health_status["session_active"] = self.session.is_active

            # Check each table
            repositories = [
                ("funds", self.funds),
                ("programs", self.programs),
                ("cost_centers", self.cost_centers),
                ("accounts", self.accounts),
                ("awards", self.awards),
                ("sponsors", self.sponsors),
                ("projects", self.projects),
                ("parent_tasks", self.parent_tasks),
                ("sub_tasks", self.sub_tasks),
                ("transactions", self.transactions),
            ]

            for table_name, repository in repositories:
                try:
                    count = repository.count_active()
                    health_status["tables_accessible"][table_name] = True
                    health_status["total_records"][table_name] = count
                except Exception as e:
                    health_status["tables_accessible"][table_name] = False
                    health_status["total_records"][table_name] = f"Error: {str(e)}"

        except Exception as e:
            health_status["error"] = str(e)

        return health_status

    def close(self):
        """Close the session - useful for cleanup in Celery tasks"""
        try:
            if self.session:
                self.session.close()
                logger.info("Repository session closed")
        except Exception:
            logger.warning("Error closing repository session")
            raise

    def get_parent_task_mapping(
        self, project_id_by_number: dict
    ) -> Dict[Tuple[int, str], int]:
        """
        Returns a mapping of (project_id, parent_task_number) - parent_task_id
        Only includes active (non-deleted) parent tasks.
        """
        try:
            records = (
                self.session.query(
                    WorkflowMasterParentTask.id,
                    WorkflowMasterParentTask.number,
                    WorkflowMasterParentTask.project_id,
                )
                .filter(WorkflowMasterParentTask.deleted_at.is_(None))
                .all()
            )

            mapping = {}
            for record in records:
                key = (project_id_by_number.get(record.project_id), record.number)
                mapping[key] = record.id

            return mapping

        except Exception as e:
            logger.error(f"Error fetching parent task mapping: {str(e)}")
            raise

    def _get_sub_task_by_project_award_map(self):
        sub_tasks = (
            self.session.query(
                WorkflowMasterSubTask.id,
                WorkflowMasterSubTask.number,
                WorkflowMasterProjectDetails.number,
                WorkflowMasterAward.number,
            )
            .join(
                WorkflowMasterParentTask,
                WorkflowMasterParentTask.id == WorkflowMasterSubTask.parent_task_id,
            )
            .join(
                WorkflowMasterProjectDetails,
                WorkflowMasterProjectDetails.id == WorkflowMasterParentTask.project_id,
            )
            .join(
                WorkflowMasterAward,
                WorkflowMasterAward.id == WorkflowMasterSubTask.award_id,
            )
            .all()
        )

        sub_task_by_project_award_map = {}
        for sub_task in sub_tasks:
            sub_task_by_project_award_map[(sub_task[2], sub_task[1], sub_task[3])] = (
                sub_task[0]
            )
        return sub_task_by_project_award_map
