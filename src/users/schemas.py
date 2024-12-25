from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]


class UserUpdateSchema(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]


class UserAuthSchema(BaseModel):
    username: str
    password: str
