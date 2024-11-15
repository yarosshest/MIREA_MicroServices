import pathlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from starlette.responses import JSONResponse

from db.interfaces.PhotoInterface import PhotoInterface
from db.minioTool import minioApi
from db.models import Task, User, Photo  # Обязательно укажите правильный путь к вашей модели Task
from db.interfaces.DatabaseInterface import \
    DatabaseInterface  # Убедитесь, что импортируете правильный интерфейс базы данных
from db.database import get_db_session  # Импортируйте свою зависимость для получения сессии базы данных
from models.models import TaskCreate, TaskUpdate, Task as pdTask, Message, PdPhoto
from security.security import get_current_user


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)
@router.post("/", response_model=Message,
             responses={401: {"model": Message, "description": "Could not validate credentials"},},
             summary="Create a new task",
             description="Create a new task by providing the task details. "
                         "This endpoint requires authentication and the user must be logged in.",
             response_description="The created task object with its details.")
async def create_task(task: TaskCreate,
                      user: Annotated[User, Depends(get_current_user)],
                      db: Annotated[AsyncSession, Depends(get_db_session)]):
    db_interface = DatabaseInterface(db)
    new_task = Task(**task.dict())
    return await db_interface.add(new_task)


@router.get("/", response_model=List[pdTask],
            responses={
                401: {"model": Message, "description": "Could not validate credentials"},
                200: {"description": "A list of tasks", "model": List[pdTask]},
                404: {"description": "No tasks found"}
            },
            summary="Retrieve a list of tasks",
            description="Fetches a list of tasks from the database. "
                        "The result can be paginated using the skip and limit query parameters."
)
async def read_tasks(user: Annotated[User, Depends(get_current_user)],
                     skip: int = 0,
                     limit: int = 10,
                     db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    tasks = await db_interface.get_all(Task)
    return tasks[skip: skip + limit]


@router.get("/{task_id}", response_model=pdTask,
            summary="Retrieve a specific task",
            description="Fetches a specific task by its ID. "
                        "This endpoint requires authentication, and the user must be logged in.",
            responses={
                200: {"description": "Task found", "model": pdTask},
                401: {"model": Message, "description": "Could not validate credentials"},
                404: {"description": "Task not found"}
            }
)
async def read_task(task_id: int,
                    user: Annotated[User, Depends(get_current_user)],
                    db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    task = await db_interface.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=pdTask,
            summary="Update a specific task",
            description="Updates the details of a specific task identified by its ID. "
                        "Only the fields provided in the request body will be updated.",
            responses={
                200: {"description": "Task updated successfully", "model": pdTask},
                404: {"description": "Task not found"},
                401: {"model": Message, "description": "Could not validate credentials"},
                400: {"description": "Invalid input data"}
            }
)
async def update_task(task_id: int,
                      user: Annotated[User, Depends(get_current_user)],
                      task_update: TaskUpdate, db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    task = await db_interface.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Обновляем только те поля, которые были переданы
    updated_task = await db_interface.update(task, **task_update.dict(exclude_unset=True))
    return updated_task


@router.delete("/{task_id}", response_model=Message,
               summary="Delete a specific task",
               description="Deletes a task identified by its ID. "
                           "Returns a confirmation message upon successful deletion.",
               responses={
                   200: {"model": Message, "description": "Task deleted successfully"},
                   404: {"model": Message, "description": "Task not found"},
                   401: {"model": Message, "description": "Could not validate credentials"},
               }
)
async def delete_task(task_id: int,
                      user: Annotated[User, Depends(get_current_user)],
                      db: AsyncSession = Depends(get_db_session)):
    db_interface = DatabaseInterface(db)
    task = await db_interface.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    await db_interface.delete(task)
    return {"detail": "Task deleted successfully"}


@router.post("/{task_id}/photos/", response_model=Message,
             summary="Upload a photo for a specific task",
             description="Uploads a photo for a task identified by its ID. "
                         "Returns a confirmation message upon successful upload.",
             responses={
                 200: {"model": Message, "description": "Photo uploaded successfully"},
                 404: {"model": Message, "description": "Task not found"},
                 422: {"model": Message, "description": "Invalid file format or upload issue"},
                 401: {"model": Message, "description": "Could not validate credentials"},
             }
)
async def upload_photo(task_id: int,
                       user: Annotated[User, Depends(get_current_user)],
                       db: Annotated[AsyncSession, Depends(get_db_session)],
                       file: UploadFile = File(...)):
    db_interface = DatabaseInterface(db)

    # Проверяем, существует ли задача
    task = await db_interface.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    unique_filename = f"{uuid.uuid4()}{pathlib.Path(file.filename).suffix}"

    await minioApi.put_task_photo(file, unique_filename)

    # Создаем запись Photo в базе данных
    photo = Photo(
        filename=unique_filename,
        url=f"http://localhost:9000/task_photo/{unique_filename}",
        task_id=task_id,
    )
    await db_interface.add(photo)

    return JSONResponse(status_code=200, content={"message": "Photo uploaded"})


@router.get("/{task_id}/photos/", response_model=List[PdPhoto],
            summary="Retrieve photos associated with a task",
            description="Fetches a list of photos related to a specific task identified by its ID.",
            responses={
                200: {
                    "description": "A list of photos associated with the task.",
                    "content": {
                        "application/json": {
                            "example": [
                                {
                                    "id": 1,
                                    "url": "http://example.com/photo1.png"
                                },
                                {
                                    "id": 2,
                                    "url": "http://example.com/photo2.png"
                                }
                            ]
                        }
                    },
                },
                404: {"description": "Task not found"},
                401: {"model": Message, "description": "Could not validate credentials"},
            }
)
async def get_task_photos(task_id: int,
                          user: Annotated[User, Depends(get_current_user)],
                          db: Annotated[AsyncSession, Depends(get_db_session)]):
    db_interface = PhotoInterface(db)

    # Проверяем, существует ли задача
    task = await db_interface.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Получаем все фото, связанные с задачей
    photos = await db_interface.get_by_task(task_id)
    return minioApi.convertFromDbPhoto(photos)

