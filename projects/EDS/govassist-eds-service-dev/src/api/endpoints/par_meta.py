from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.schema.par_meta_schema import ParMeta, ParMetaUpdate
from src.services.par_service import ParService
from src.services.project_detail_service import ProjectDetailService

router = APIRouter(prefix="/par-meta", tags=["Par Meta"])


@router.get("/{par_id}", response_model=ParMeta)
@inject
async def get_par_meta(
    par_id: int,
    service: ParService = Depends(Provide[Container.par_service]),
):
    return await service.get_par_meta(par_id)


@router.patch("/{par_id}")
@inject
async def update_par_meta(
    par_id: int,
    par_meta: ParMetaUpdate,
    service: ProjectDetailService = Depends(Provide[Container.project_detail_service]),
):
    return await service.update_par_meta(par_id, par_meta)
