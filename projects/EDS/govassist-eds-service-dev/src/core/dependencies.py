from typing import Optional

from abs_exception_core.exceptions import UnauthorizedError
from fastapi import HTTPException, Request
from jwt.exceptions import ExpiredSignatureError


async def get_current_user(request: Request) -> Optional[dict]:
    """Dependency function to get the current user from request state."""
    try:
        user = request.state.user
        if not user:
            raise HTTPException(
                status_code=401, detail="Not authenticated. Please log in to continue."
            )
        return user
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401, detail="Your session has expired. Please log in again."
        )
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e.detail) if hasattr(e, "detail") else "Authentication failed",
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed. Please try logging in again.",
        )


def require_auth():
    """Decorator to require authentication for routes."""

    async def dependency(request: Request):
        return await get_current_user(request)

    return dependency
