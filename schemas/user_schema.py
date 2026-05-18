from pydantic import BaseModel
from typing import Optional


class UserSchema(BaseModel):
    username: str
    email: str
    address: str | None
    phone_number: str
    password: str
    is_active: bool = True
    type_user: str = "user"
    created_at: str
    last_login: str


class LoginRequest(BaseModel):
    identifier: str
    password: str


class ResendVerificationRequest(BaseModel):
    email: str


class ForgotPasswordRequest(BaseModel):
    identifier: str


class ResetPasswordRequest(BaseModel):
    code: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    identifier: str
    old_password: str
    new_password: str
