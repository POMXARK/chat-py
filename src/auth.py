from datetime import datetime
from http import HTTPStatus
from uuid import UUID
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from pydantic import BaseModel, ValidationError

from config import WebApiSettings

oauth2_scheme = HTTPBearer(auto_error=True)


class BaseUser(BaseModel):
    id: UUID
    login: str


class JWTPayload(BaseModel):
    user: BaseUser
    sub: str
    iat: datetime
    exp: datetime


class BaseAPIException(HTTPException):
    ...


class BaseAuthError(BaseAPIException):
    def __init__(self, *, detail: str):
        super().__init__(detail=detail, status_code=HTTPStatus.FORBIDDEN)


class InvalidTokenError(BaseAuthError):
    pass


def get_current_user(token):
    if not token:
        return

    settings = WebApiSettings()
    try:
        payload_raw = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        payload = JWTPayload.parse_obj(payload_raw)
    except (JWTError, ValidationError):
        raise InvalidTokenError(detail="Could not validate credentials")
    return payload.user
