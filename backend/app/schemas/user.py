from pydantic import BaseModel, EmailStr, validator
import re
from typing import List, Optional
from .test import TestBase


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str

    @validator("username")
    def validate_username(cls, v):
        if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", v):
            raise ValueError("Invalid username")
        return v

    @validator("password")
    def validate_password(cls, v):
        if (
            len(v) < 8
            or not re.search(r"[A-Z]", v)
            or not re.search(r"[a-z]", v)
            or not re.search(r"\d", v)
        ):
            raise ValueError("Weak password")
        return v


class User(UserBase):
    id: int
    tests: List[TestBase] = []

    class Config:
        orm_mode = True
