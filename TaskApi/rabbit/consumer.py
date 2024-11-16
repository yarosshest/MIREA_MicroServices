import asyncio
import json

from db.database import get_db_session
from db.interfaces.DatabaseInterface import DatabaseInterface
import aio_pika

from db.models import Task


async def callback(message: aio_pika.abc.AbstractIncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode())
        session = await get_db_session()
        db_interface = DatabaseInterface(session)
        task = await db_interface.get(Task, int(data['task_id']))
        task.status = data['status']
        await db_interface.update(task, **task.to_dict())
        await message.channel.basic_ack(message.delivery_tag)
        print(f"[x] Received: Task ID {data['task_id']} with status {data['status']}")
        session.clouse()


async def consuming():
    connection = await aio_pika.connect_robust("amqp://rmuser:rmpassword@rabbitmq:5672/")

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue("task_status", durable=True, auto_delete=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await callback(message)
