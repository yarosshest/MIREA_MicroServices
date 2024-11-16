import asyncio
import json

import uvicorn as uvicorn
from fastapi import FastAPI

from db.database import init_db
from rabbit.consumer import consuming
from routers.auth import router as auth
from routers.task import router as task
from routers.token import router as token_route

api = FastAPI()


@api.on_event("startup")
async def save_openapi_json():
    await init_db()
    openapi_data = api.openapi()
    # Change "openapi.json" to desired filename
    with open("openapi.json", "w") as file:
        json.dump(openapi_data, file)

    asyncio.create_task(consuming())


api.include_router(token_route)
api.include_router(auth)
api.include_router(task)


def app_main():
    # asyncio.run(init_db())
    uvicorn.run(api, host="0.0.0.0", port=8031)
    # uvicorn.run('main:api', host="localhost", port=8032, workers=4)


if __name__ == "__main__":
    app_main()
