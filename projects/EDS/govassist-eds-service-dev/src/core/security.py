from datetime import UTC, datetime, timedelta
from typing import Dict, Tuple

from fastapi import Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from passlib.context import CryptContext

from src.core.config import configs
from src.core.exceptions import AuthError, InternalServerError, UnauthorizedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def create_access_token(
    subject: dict, expires_delta: timedelta = None
) -> Tuple[str, str]:
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=configs.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    payload = {"exp": expire, **subject}
    encoded_jwt = jwt.encode(
        payload, configs.JWT_SECRET_KEY, algorithm=configs.JWT_ALGORITHM
    )
    expiration_datetime = expire

    return encoded_jwt, expiration_datetime


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(
            token, configs.JWT_SECRET_KEY, algorithms=configs.JWT_ALGORITHM
        )
        return (
            decoded_token
            if decoded_token["exp"] >= int(round(datetime.now(UTC).timestamp()))
            else None
        )
    except Exception:
        raise InternalServerError(detail="Internal Server Error")


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise AuthError(detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise AuthError(detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise AuthError(detail="Invalid authorization code.")

    def verify_jwt(self, jwt_token: str) -> bool:
        is_token_valid: bool = False
        try:
            payload = decode_jwt(jwt_token)
        except Exception:
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid


# Create security scheme with auto_error=False to handle errors ourselves
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Dict:

    try:

        if not credentials:

            raise UnauthorizedError(detail="No authorization token provided")

        token = credentials.credentials

        # Extract the token (remove 'Bearer ' prefix if present)
        if token.lower().startswith("bearer "):

            token = token[7:]

        decoded_token = decode_jwt(token)

        if not decoded_token:

            raise UnauthorizedError(detail="Invalid or expired token")

        return decoded_token

    except Exception:

        raise UnauthorizedError(detail="Invalid or expired token")
