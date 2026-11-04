from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
import re

class RegisterRequest(BaseModel):
    email: str
    password: str
    password_confirmation: str
    
    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.lower().strip()
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, clean):
            raise ValueError("Invalid email format")
        return clean
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v
    
    @field_validator("password_confirmation")
    @classmethod
    def validate_password_confirmation(cls, v: str, info) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v

class LoginRequest(BaseModel):
    email: str
    password: str
    
    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.lower().strip()

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
