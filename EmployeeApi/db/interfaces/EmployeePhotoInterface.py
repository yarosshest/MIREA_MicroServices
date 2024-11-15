from typing import Optional

from sqlalchemy import select

from db.interfaces.DatabaseInterface import DatabaseInterface
from db.models import PhotoEmployee


class EmployeePhotoInterface(DatabaseInterface):
    async def get_by_employee(self, employee_id: int) -> list[PhotoEmployee]:
        """Получает пользователя по username."""
        result = await self.session.execute(select(PhotoEmployee).where(PhotoEmployee.employee_id == employee_id))
        return list(result.scalars().unique().all())
