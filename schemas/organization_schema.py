from pydantic import BaseModel
from typing import Optional
from schemas.user_schema import UserSchema


class OrganizationSchema(BaseModel):
    name: str
    email: str
    phone_number: str
    password: str
    website: str
    province: str
    city: str
    type_organization: str
    address: str


class RegisterUserOrganizationRequest(BaseModel):
    admin: UserSchema
    organization: OrganizationSchema
