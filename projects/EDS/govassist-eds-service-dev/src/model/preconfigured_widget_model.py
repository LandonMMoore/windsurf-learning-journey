from sqlalchemy import JSON, Column, String

from src.model.base_model import BaseModel


class PreconfiguredWidget(BaseModel):
    __tablename__ = "preconfigured_widget"
    name = Column(String)
    description = Column(String)
    widget_type = Column(String)
    image_url = Column(String)
    data_source = Column(String)
    config = Column(JSON)
    category = Column(String)
    category_label = Column(String)
    filters = Column(JSON)
