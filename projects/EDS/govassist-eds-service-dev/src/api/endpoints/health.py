from fastapi import APIRouter, Request

from src.api import limiter
from src.core.middleware import inject

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", status_code=200)
@inject
@limiter.limit("1000/minute")
async def health(request: Request):
    """API Health Check"""
    return {"status": "ok"}
