from sqlalchemy import Column, String, Text

from src.model.base_model import BaseModel


class Log(BaseModel):
    __tablename__ = "logs"

    table_name = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)
