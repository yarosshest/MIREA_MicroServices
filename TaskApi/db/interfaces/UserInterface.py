from sqlalchemy import select
from db.models import User
from typing import Optional
from .DatabaseInterface import DatabaseInterface

class UserInterface(DatabaseInterface):
    async def get_by_username(self, username: str) -> Optional[User]:
        """Получает пользователя по username."""
        result = await self.session.execute(select(User).filter_by(username=username))
        return result.scalar_one_or_none()
