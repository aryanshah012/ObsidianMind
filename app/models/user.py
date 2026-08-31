"""
User data models for ObsidianMind authentication and multi-tenancy.
"""

from typing import Optional
from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=40, description="Unique username")
    email: str = Field(..., min_length=5, max_length=100, description="User email address")
    password: str = Field(..., min_length=6, max_length=128, description="User password")
    full_name: Optional[str] = Field(default="", max_length=100, description="Display full name")


class UserLoginRequest(BaseModel):
    username_or_email: str = Field(..., min_length=1, max_length=100, description="Username or email")
    password: str = Field(..., min_length=1, max_length=128, description="User password")


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str = ""
    created_at: float


class TokenResponse(BaseModel):
    success: bool = True
    token: str
    user: UserResponse
    message: Optional[str] = None


class UserInDB(BaseModel):
    id: str
    username: str
    email: str
    password_hash: str
    salt: str
    full_name: str = ""
    created_at: float
