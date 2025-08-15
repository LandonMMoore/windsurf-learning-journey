from pydantic import BaseModel


class KeyMetrics(BaseModel):
    total_pars: int
    pending_pars: int
    active_wards: int
    total_amount: float
