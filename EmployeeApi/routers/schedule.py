import pathlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from starlette.responses import JSONResponse

from db.interfaces.PhotoInterface import PhotoInterface
from db.minioTool import minioApi
from db.models import Task, User, Photo, Schedule  # Обязательно укажите правильный путь к вашей модели Task
from db.interfaces.DatabaseInterface import \
    DatabaseInterface  # Убедитесь, что импортируете правильный интерфейс базы данных
from db.database import get_db_session  # Импортируйте свою зависимость для получения сессии базы данных
from models.models import TaskCreate, TaskUpdate, Task as pdTask, Message, PdPhoto, EmployeeCreate, EmployeeGet, \
    ScheduleCreate, ScheduleGet
from security.security import get_current_user

router = APIRouter(
    prefix="/schedule",
    tags=["schedule"],
)


@router.post("/",
             summary="Create a new schedule record",
             description="Creates a new schedule record in the database. ",
             responses={
                 401: {"model": Message, "description": "Could not validate credentials"},
                 200: {"description": "Employee created", "model": Message},
                 404: {"description": "No tasks found"}
             },
             )
async def create_schedule(schedule: ScheduleCreate,
                          user: Annotated[User, Depends(get_current_user)],
                          db: Annotated[AsyncSession, Depends(get_db_session)]):
    db_interface = DatabaseInterface(db)
    return await db_interface.add(Schedule(**schedule.dict()))


@router.get("/", response_model=List[ScheduleGet],
            responses={
                401: {"model": Message, "description": "Could not validate credentials"},
                200: {"description": "A list of schedules", "model": List[ScheduleGet]},
                404: {"description": "No schedules found"}
            },
            summary="Retrieve a list of schedules",
            description="Fetches a list of schedules from the database. "
                        "The result can be paginated using the skip and limit query parameters."
            )
async def read_schedules(user: Annotated[User, Depends(get_current_user)],
                         skip: int = 0,
                         limit: int = 10,
                         db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    schedules = await db_interface.get_all(Schedule)
    return schedules[skip: skip + limit]


@router.get("/{schedule_id}", response_model=ScheduleGet,
            summary="Retrieve a specific schedule",
            description="Fetches a specific schedule by its ID. "
                        "This endpoint requires authentication, and the user must be logged in.",
            responses={
                200: {"description": "Employee found", "model": ScheduleGet},
                401: {"model": Message, "description": "Could not validate credentials"},
                404: {"description": "Employee not found"}
            }
            )
async def read_task(schedule_id: int,
                    user: Annotated[User, Depends(get_current_user)],
                    db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    schedule = await db_interface.get(Schedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleCreate,
            summary="Update a specific schedule",
            description="Updates the details of a specific schedule identified by its ID. "
                        "Only the fields provided in the request body will be updated.",
            responses={
                200: {"description": "Schedule updated successfully", "model": Message},
                404: {"description": "Schedule not found"},
                401: {"model": Message, "description": "Could not validate credentials"},
                400: {"description": "Invalid input data"}
            }
            )
async def update_task(schedule_id: int,
                      user: Annotated[User, Depends(get_current_user)],
                      employee_update: EmployeeCreate, db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    schedule = await db_interface.get(Schedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Обновляем только те поля, которые были переданы
    updated_employee = await db_interface.update(schedule, **employee_update.dict(exclude_unset=True))
    return updated_employee


@router.delete("/{schedule_id}", response_model=Message,
               summary="Delete a specific schedule",
               description="Deletes a schedule identified by its ID. "
                           "Returns a confirmation message upon successful deletion.",
               responses={
                   200: {"description": "schedule deleted successfully"},
                   404: {"description": "schedule not found"},
                   401: {"model": Message, "description": "Could not validate credentials"},
               }
               )
async def delete_task(schedule_id: int,
                      user: Annotated[User, Depends(get_current_user)],
                      db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    schedule = await db_interface.get(Schedule, schedule_id)
    if schedule is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    await db_interface.delete(schedule)
    return {"detail": "Employee deleted successfully"}
