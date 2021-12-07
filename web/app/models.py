from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str


class BaseResponse(BaseModel):
    success: bool


class GardenBase(BaseModel):
    garden_id: int


class LoginCredentials(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class RegisterCredentials(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    full_name: Optional[str] = None


class GardenCredentials(GardenBase):
    data: dict


class RegisterResponse(BaseModel):
    success: bool
    error: Optional[str] = None


class TokenData(BaseModel):
    username: Optional[str] = None
