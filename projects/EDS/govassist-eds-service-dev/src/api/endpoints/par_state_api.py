from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.core.container import Container
from src.core.dependencies import get_current_user
from src.core.exceptions import BadRequestError
from src.services.par_state_service import ParStateService
from src.util.par import get_latest_par_status_map

router = APIRouter(prefix="/par-status", tags=["PAR Status"])


@router.get("/{par_id}/possible-status")
@inject
async def get_possible_status(
    par_id: int,
    par_state_service: ParStateService = Depends(Provide[Container.par_state_service]),
    session_factory=Depends(Provide[Container.session_factory]),
):
    """Get all possible next statuses for a PAR"""
    status_map = get_latest_par_status_map([par_id], session_factory)
    current_status = status_map.get(par_id, "Draft")

    return par_state_service.get_possible_transitions(current_status)


@router.post("/{par_id}/transit")
@inject
async def transit_status(
    par_id: int,
    target_state: str,
    current_user: dict = Depends(get_current_user),
    par_state_service: ParStateService = Depends(Provide[Container.par_state_service]),
    session_factory=Depends(Provide[Container.session_factory]),
):
    """Transition a PAR to a new state"""
    # Get the current status for this PAR
    status_map = get_latest_par_status_map([par_id], session_factory)
    current_status = status_map.get(par_id, "Draft")

    if not par_state_service.can_transit_to_status(current_status, target_state):
        raise BadRequestError(
            detail=f"Cannot transit from {current_status} to {target_state}",
        )

    # Transition the state (this will create the activity record)
    success = par_state_service.transit_status(
        target_state, current_status, par_id, str(current_user.name)
    )

    if not success:
        raise BadRequestError(detail="Failed to transit state")

    return {
        "message": "State transition successful",
        "new_state": target_state,
        "can_view": par_state_service.can_view(target_state),
        "can_edit": par_state_service.can_edit(target_state),
    }
