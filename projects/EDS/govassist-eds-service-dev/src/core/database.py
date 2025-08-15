import logging
from contextlib import AbstractContextManager, contextmanager
from typing import Any, Generator

from fastapi import HTTPException
from sqlalchemy import create_engine, orm
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session

from src.core.config import configs
from src.core.exceptions import InternalServerError

# Configure SQLAlchemy logging based on configuration
if configs.SQLALCHEMY_LOGGING:
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)


@as_declarative()
class BaseModel:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(
            db_url,
            echo=configs.SQLALCHEMY_LOGGING,
            echo_pool=configs.SQLALCHEMY_LOGGING,
            pool_pre_ping=True,
            pool_recycle=3600,
            query_cache_size=0,
        )
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        BaseModel.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Generator[Any, Any, AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except HTTPException:
            # Re-raise HTTPException subclasses (like NotFoundError) without modification
            session.rollback()
            raise
        except Exception:
            session.rollback()
            raise InternalServerError(detail="Internal Server Error")
        finally:
            session.close()
