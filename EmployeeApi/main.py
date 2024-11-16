import asyncio
import json

import uvicorn as uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import init_db
from routers.token import router as token
from routers.auth import router as auth
from routers.employees import router as employees
from routers.schedule import router as schedule
from routers.cases import router as cases

api = FastAPI()

@api.on_event("startup")
async def save_openapi_json():
    await init_db()
    openapi_data = api.openapi()
    # Change "openapi.json" to desired filename
    with open("openapi.json", "w") as file:
        json.dump(openapi_data, file)


api.include_router(token)
api.include_router(auth)
api.include_router(schedule)
api.include_router(employees)
api.include_router(cases)


def app_main():
    asyncio.run(init_db())
    # uvicorn.run(api, host="0.0.0.0", port=8031)
    uvicorn.run('main:api', host="0.0.0.0", port=8031, workers=4)


if __name__ == "__main__":
    app_main()
