from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class LoginForm(BaseModel):
    username: str
    password: str


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    complete: bool

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    complete: bool

class PdPhoto(BaseModel):
    id: int
    url: str



