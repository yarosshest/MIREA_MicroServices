

import aio_pika
import json

async def send_task_status(task_id: int, status: str):
    connection = await aio_pika.connect_robust("amqp://rmuser:rmpassword@rabbitmq:5672/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("task_status", durable=True, auto_delete=True)

        message = {
            "task_id": task_id,
            "status": status
        }

        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=queue.name
        )
        print(f"[x] Sent: {message}")
