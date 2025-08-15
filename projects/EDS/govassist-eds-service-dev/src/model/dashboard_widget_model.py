from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.model.base_model import BaseModel


class DashboardWidget(BaseModel):
    __tablename__ = "dashboard_widget"

    name = Column(String)
    description = Column(String)
    dashboard_id = Column(
        Integer, ForeignKey("dashboard.id", ondelete="CASCADE"), nullable=False
    )
    widget_type = Column(String)
    image_url = Column(String)
    data_source = Column(String)
    filters = Column(JSON)
    show_legend = Column(Boolean, default=True)
    x_position = Column(String)
    y_position = Column(String)
    width = Column(String)
    height = Column(String)
    config = Column(JSON)

    dashboard = relationship("Dashboard", back_populates="dashboard_widgets")
    favorites = relationship(
        "WidgetFavorite", back_populates="widget", cascade="all, delete-orphan"
    )
