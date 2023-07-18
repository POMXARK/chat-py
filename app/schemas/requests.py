import uuid

from pydantic import BaseModel, EmailStr, UUID4


class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str


class UserCreateRequest(BaseRequest):
    email: EmailStr
    password: str


class MessageRequest(BaseRequest):
    text: str
    user_id: UUID4
    stmt_id: UUID4
