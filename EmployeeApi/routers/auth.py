from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi import Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from security.security import get_password_hash, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, \
    create_access_token
from db.models import User
from db.interfaces.UserInterface import UserInterface
from models.models import Message
from db.database import get_db_session

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register",
             responses={
                 200: {"model": Message, "description": "Successful registration"},
                 409: {"model": Message, "description": "User already exists"}
             },
             summary="Register a new user",
             description="Creates a new user account with the provided username, password, and email."
             )
async def register_post(login: Annotated[str, Form()],
                        password: Annotated[str, Form()],
                        email: Annotated[str, Form()],
                        db_session: AsyncSession = Depends(get_db_session)
                        ):
    db = UserInterface(db_session)
    u = await db.get_by_username(login)
    if u is None:
        user = User(username=login, hashed_password=get_password_hash(password), email=email)
        await db.add(user)
        return JSONResponse(status_code=200, content={"message": "Successful register"})
    else:
        return JSONResponse(status_code=409, content={"message": "Already exist"})


@router.post("/login",
             responses={
                 200: {"model": Message, "description": "Successful login"},
                 401: {"model": Message, "description": "Incorrect username or password"}
             },
             summary="User login",
             description="Authenticates a user and returns an access token if successful."
             )
async def login_post(
        login: Annotated[str, Form()],
        password: Annotated[str, Form()],
        db_session: AsyncSession = Depends(get_db_session)
):
    user = await authenticate_user(login, password, db_session)

    if not user:
        return JSONResponse(status_code=401,
                            content={"message": "Incorrect username or password"},
                            headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    res = JSONResponse(status_code=200,
                       headers={"access_token": access_token, "token_type": "bearer"},
                       content={"message": "Successful login"})

    res.set_cookie(key="access_token", value=access_token)
    res.set_cookie(key="token_type", value="bearer")

    return res
