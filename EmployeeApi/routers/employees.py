import pathlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from starlette.responses import JSONResponse

from db.interfaces.EmployeePhotoInterface import EmployeePhotoInterface
from db.interfaces.PhotoInterface import PhotoInterface
from db.minioTool import minioApi
from db.models import User, Employee, \
    PhotoEmployee  # Обязательно укажите правильный путь к вашей модели Task
from db.interfaces.DatabaseInterface import \
    DatabaseInterface  # Убедитесь, что импортируете правильный интерфейс базы данных
from db.database import get_db_session  # Импортируйте свою зависимость для получения сессии базы данных
from models.models import TaskCreate, TaskUpdate, Task as pdTask, Message, PdPhoto, EmployeeCreate, EmployeeGet
from security.security import get_current_user

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
)



@router.post("/",
             summary="Create a new employee record",
             description="Creates a new employee record in the database. "
                         "Requires fields such as name, surname, position, department, phone, email, and is_active status. "
                         "This endpoint checks for an existing employee with the same email before creating a new record.",
             responses={
                 401: {"model": Message, "description": "Could not validate credentials"},
                 200: {"description": "Employee created", "model": Message},
                 404: {"description": "No tasks found"}
             },
             )
async def create_employee(task: EmployeeCreate,
                          user: Annotated[User, Depends(get_current_user)],
                          db: Annotated[AsyncSession, Depends(get_db_session)]):
    db_interface = DatabaseInterface(db)
    new_emp = Employee(**task.dict())
    return await db_interface.add(new_emp)


@router.get("/", response_model=List[EmployeeGet],
            responses={
                401: {"model": Message, "description": "Could not validate credentials"},
                200: {"description": "A list of employees", "model": List[EmployeeGet]},
                404: {"description": "No employees found"}
            },
            summary="Retrieve a list of employees",
            description="Fetches a list of employees from the database. "
                        "The result can be paginated using the skip and limit query parameters."
            )
async def read_employees(user: Annotated[User, Depends(get_current_user)],
                     skip: int = 0,
                     limit: int = 10,
                     db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    employees = await db_interface.get_all(Employee)
    return employees[skip: skip + limit]

@router.get("/{employee_id}", response_model=EmployeeGet,
            summary="Retrieve a specific task",
            description="Fetches a specific employee by its ID. "
                        "This endpoint requires authentication, and the user must be logged in.",
            responses={
                200: {"description": "Employee found", "model": EmployeeGet},
                401: {"model": Message, "description": "Could not validate credentials"},
                404: {"description": "Employee not found"}
            }
            )
async def read_task(employee_id: int,
                    user: Annotated[User, Depends(get_current_user)],
                    db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    employee = await db_interface.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/{employee_id}", response_model=EmployeeCreate,
            summary="Update a specific employee",
            description="Updates the details of a specific employee identified by its ID. "
                        "Only the fields provided in the request body will be updated.",
            responses={
                200: {"description": "Employee updated successfully", "model": Message},
                404: {"description": "Employee not found"},
                401: {"model": Message, "description": "Could not validate credentials"},
                400: {"description": "Invalid input data"}
            }
            )
async def update_task(employee_id: int,
                      user: Annotated[User, Depends(get_current_user)],
                      employee_update: EmployeeCreate, db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    employee = await db_interface.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Обновляем только те поля, которые были переданы
    updated_employee = await db_interface.update(employee, **employee_update.dict(exclude_unset=True))
    return updated_employee


@router.delete("/{employee_id}", response_model=Message,
               summary="Delete a specific employee",
               description="Deletes a employee identified by its ID. "
                           "Returns a confirmation message upon successful deletion.",
               responses={
                   200: {"description": "employee deleted successfully"},
                   404: {"description": "employee not found"},
                   401: {"model": Message, "description": "Could not validate credentials"},
               }
               )
async def delete_task(employee_id: int,
                      user: Annotated[User, Depends(get_current_user)],
                      db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    employee = await db_interface.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    await db_interface.delete(employee)
    return {"detail": "Employee deleted successfully"}

@router.post("/{employee_id}/photos/", response_model=Message,
             summary="Upload a photo for a specific employee",
             description="Uploads a photo for a employee identified by its ID. "
                         "Returns a confirmation message upon successful upload.",
             responses={
                 200: {"description": "Photo uploaded successfully"},
                 404: {"description": "Employee not found"},
                 422: {"description": "Invalid file format or upload issue"},
                 401: {"model": Message, "description": "Could not validate credentials"},
             }
             )
async def upload_photo(employee_id: int,
                       user: Annotated[User, Depends(get_current_user)],
                       db: Annotated[AsyncSession, Depends(get_db_session)],
                       file: UploadFile = File(...)):
    db_interface = DatabaseInterface(db)

    # Проверяем, существует ли задача
    employee = await db_interface.get(Employee, employee_id)
    if employee is None:
        raise HTTPException(status_code=404, detail="Task not found")

    unique_filename = f"{uuid.uuid4()}{pathlib.Path(file.filename).suffix}"

    await minioApi.put_task_photo(file, unique_filename)

    # Создаем запись Photo в базе данных
    photo = PhotoEmployee(
        filename=unique_filename,
        url=f"http://localhost:9000/task_photo/{unique_filename}",
        employee_id=employee_id,
    )
    await db_interface.add(photo)

    return JSONResponse(status_code=200, content={"message": "Photo uploaded"})


@router.get("/{employee_id}/photos/", response_model=PdPhoto,
            summary="Retrieve photos associated with a employee",
            description="Fetches a list of photos related to a specific employee identified by its ID.",
            responses={
                200: {
                    "description": "A list of photos associated with the employee.",
                    "content": {
                        "application/json": {
                            "example": [
                                {
                                    "id": 1,
                                    "url": "http://example.com/photo1.png"
                                }
                            ]
                        }
                    },
                },
                404: {"description": "employee not found"},
                401: {"model": Message, "description": "Could not validate credentials"},
            }
            )
async def get_task_photos(employee_id: int,
                          user: Annotated[User, Depends(get_current_user)],
                          db: Annotated[AsyncSession, Depends(get_db_session)]):
    db_interface = EmployeePhotoInterface(db)

    # Проверяем, существует ли задача
    task = await db_interface.get(Task, employee_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Получаем все фото, связанные с задачей
    photos = await db_interface.get_by_employee(employee_id)
    return minioApi.convertFromDbPhoto(photos)
