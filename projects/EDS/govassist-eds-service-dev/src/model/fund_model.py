from sqlalchemy import Column, Integer, String

from src.model.base_model import BaseModel


class Fund(BaseModel):
    __tablename__ = "funds"
    fund_number = Column(Integer, nullable=False)
    fund_name = Column(String, nullable=False)
