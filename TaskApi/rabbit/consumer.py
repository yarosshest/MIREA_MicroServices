import asyncio
import json

from db.database import get_db_session
from db.interfaces.DatabaseInterface import DatabaseInterface
import aio_pika

from db.models import Task


async def callback(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        data = json.loads(message.body)
        db_interface = DatabaseInterface(get_db_session())
        task = await db_interface.get(Task, int(data['task_id']))
        task.status = data['status']
        await db_interface.update(task, **task.dict(exclude_unset=True))

        print(f"[x] Received: Task ID {data['task_id']} with status {data['status']}")


async def consuming():
    connection = await aio_pika.connect_robust("amqp://rmuser:rmpassword@rabbitmq:5672/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("task_status", durable=True, auto_delete=True)

        await queue.consume(callback)


def start_consumer_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(consuming())
