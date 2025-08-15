from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.schema.key_metrics_schema import KeyMetrics
from src.services.par_service import ParService

router = APIRouter(prefix="/key-metrics", tags=["Key Metrics"])


@router.get("", response_model=KeyMetrics)
@inject
def get_key_metrics(
    service: ParService = Depends(Provide[Container.par_service]),
):
    return service.get_key_metrics()
