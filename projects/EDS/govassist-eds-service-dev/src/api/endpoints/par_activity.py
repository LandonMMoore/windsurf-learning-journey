from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.schema.par_activity_schema import ParActivityCreate, ParActivityInfo
from src.services.par_activity_service import ParActivityService

router = APIRouter(prefix="/par-activities", tags=["PAR Activities"])


@router.get("/{id}")
@inject
def get_par_activity(
    id: int,
    service: ParActivityService = Depends(Provide[Container.par_activity_service]),
):
    return service.get_by_par_id(id)


@router.post("", response_model=ParActivityInfo)
@inject
async def create_par_activity(
    data: ParActivityCreate,
    service: ParActivityService = Depends(Provide[Container.par_activity_service]),
):
    return await service.add(data)
