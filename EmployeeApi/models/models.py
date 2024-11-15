from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    message: str


class TokenData(BaseModel):
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

class ScheduleGet(BaseModel):

    id: int
    date: str
    time_start: str
    time_end: str
    is_active: bool
    employee_id: int


class ScheduleCreate(BaseModel):

    id: int
    date: str
    time_start: str
    time_end: str
    is_active: bool
    employee_id: int

class PhotoGet(BaseModel):

    id: int
    filename: str
    url: str

class EmployeeCreate(BaseModel):
    name: str
    surname: str
    patronymic: str
    position: str
    department: str
    phone: str
    email: str
    photo: str
    is_active: bool
    tasks: list = []


class EmployeeGet(BaseModel):
    id: int
    name: str
    surname: str
    patronymic: str
    position: str
    department: str
    phone: str
    email: str
    photo: str
    is_active: bool
    schedules: list[ScheduleGet]
    photos: list[PhotoGet]
    tasks: list = []



