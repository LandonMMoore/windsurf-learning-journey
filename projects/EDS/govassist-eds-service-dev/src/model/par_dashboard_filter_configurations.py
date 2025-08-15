from sqlalchemy import JSON, Column, String

from .base_model import BaseModel


class ParDashboardFilterConfigurations(BaseModel):
    """
    Stores named filter configurations for the PAR Dashboard.

    Each filter consists of:
    - A unique filter name.
    - A structured JSON configuration containing:
        • fields: list of field names involved in the filtering logic.
        • conditions: list of condition objects for filtering logic.
        • operator: logical connector ('and', 'or', 'not') applied to conditions.
    """

    __tablename__ = "par_dashboard_filter_configurations"

    filter_name = Column(String(255), nullable=False)
    filter_configuration = Column(JSON, nullable=False)
