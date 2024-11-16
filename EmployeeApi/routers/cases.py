import pathlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from starlette.responses import JSONResponse

from api.tasks import get_tasks
from db.interfaces.EmployeePhotoInterface import EmployeePhotoInterface
from db.interfaces.PhotoInterface import PhotoInterface
from db.minioTool import minioApi
from db.models import User, Employee, \
    PhotoEmployee  # Обязательно укажите правильный путь к вашей модели Task
from db.interfaces.DatabaseInterface import \
    DatabaseInterface  # Убедитесь, что импортируете правильный интерфейс базы данных
from db.database import get_db_session  # Импортируйте свою зависимость для получения сессии базы данных
from models.models import TaskCreate, TaskUpdate, Task as pdTask, Message, PdPhoto, EmployeeCreate, EmployeeGet, Task
from rabbit.producer import send_task_status
from security.security import get_current_user

router = APIRouter(
    prefix="/cases",
    tags=["cases"],
)


@router.post("/send_rabbit_status_task_by_employee")
async def create_employee(employee_id: int,
                          user: Annotated[User, Depends(get_current_user)],
                          db: Annotated[AsyncSession, Depends(get_db_session)]):
    db_interface = DatabaseInterface(db)

    # Fetch the employee from the database
    employee = await db_interface.get(Employee, employee_id)

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Assuming that the Task model has an 'employee_id' field to relate tasks to employees
    tasks = get_tasks()
    employee_tasks =  [t for t in tasks if t.id in employee.tasks]

    if not employee_tasks:
        raise HTTPException(status_code=404, detail="No tasks found for this employee")

    # Process the tasks or prepare them for RabbitMQ
    task_statuses = []
    for task in employee_tasks:
        await send_task_status(task.id, "In Progress")

    # For the sake of simplicity, we're just returning the task statuses as a JSON response
    return JSONResponse(content={"employee_id": employee_id, "task_statuses": task_statuses}, status_code=200)