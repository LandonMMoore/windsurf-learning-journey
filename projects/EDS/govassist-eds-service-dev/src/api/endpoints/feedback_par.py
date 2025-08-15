from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends

from src.core.dependencies import get_current_user
from src.schema.feedback_par_schema import FeedbackPayload
from src.util.send_email import feedback_par_create

router = APIRouter(prefix="/feedback-par", tags=["Feedback Par"])


@router.post("")
@inject
def submit_feedback(
    feedback: FeedbackPayload, current_user: dict = Depends(get_current_user)
):
    return feedback_par_create(feedback, current_user)
