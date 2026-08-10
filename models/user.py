from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True)
    password: str
    full_name: str
    is_admin: bool = False


class UserResponse(SQLModel):
    id: int
    username: str
    email: str
    full_name: str
    is_admin: bool