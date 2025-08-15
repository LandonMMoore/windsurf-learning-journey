import uuid
from datetime import UTC
from datetime import datetime as dt
from typing import Callable, TypeVar

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.exceptions import DuplicatedError, NotFoundError, ValidationError
from src.model.base_model import BaseModel
from src.model.report_model import ReportExport
from src.model.sub_report_model import SubReport
from src.repository.base_repository import BaseRepository

T = TypeVar("T", bound=BaseModel)


class SubReportRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., Session]):
        super().__init__(session_factory, SubReport)

    def create(self, schema: T):
        with self.session_factory() as session:
            query = self.model(
                **schema.model_dump(),
                index_name=str(uuid.uuid4()),
            )
            try:
                session.add(query)
                session.commit()
                session.refresh(query)
                query = self.read_by_id(query.id, eager=True)
            except IntegrityError as e:
                raise DuplicatedError(detail=str(e.orig))
            except SQLAlchemyError as e:
                raise ValidationError(detail=str(e))
            return query

    def update(
        self, id: int, schema: T, exclude_none: bool = True, exclude_unset: bool = False
    ):
        with self.session_factory() as session:
            try:
                data_to_update = schema.model_dump(
                    exclude_none=exclude_none, exclude_unset=exclude_unset
                )
                # Apply updates
                affected_rows = (
                    session.query(self.model)
                    .filter(self.model.id == id)
                    .update(data_to_update, synchronize_session="fetch")
                )
                if not affected_rows:
                    raise NotFoundError(detail=f"not found id : {id}")
                if "config" in data_to_update:
                    report_id = (
                        session.query(SubReport)
                        .filter(SubReport.id == id)
                        .first()
                        .report_configuration_id
                    )
                    session.query(ReportExport).filter(
                        ReportExport.report_id == report_id
                    ).update({"stale_at": dt.now(UTC)}, synchronize_session="fetch")
                session.commit()

                # Fetch updated record WITH RELATIONSHIPS loaded
                query = self.read_by_id(id, eager=True)

                return query  # FastAPI will serialize correctly

            except IntegrityError as e:
                session.rollback()
                raise DuplicatedError(detail=str(e.orig))
            except SQLAlchemyError as e:
                session.rollback()
                raise ValidationError(detail=str(e))
