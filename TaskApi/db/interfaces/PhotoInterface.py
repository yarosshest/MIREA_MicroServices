from typing import Optional

from sqlalchemy import select

from db.interfaces.DatabaseInterface import DatabaseInterface
from db.models import Photo


class PhotoInterface(DatabaseInterface):
    async def get_by_task(self, task_id: int) -> list[Photo]:
        """Получает пользователя по username."""
        result = await self.session.execute(select(Photo).where(Photo.task_id == task_id))
        return list(result.scalars().unique().all())
