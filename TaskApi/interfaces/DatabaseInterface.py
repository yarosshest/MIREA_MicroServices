from sqlalchemy import select, Row, RowMapping
from typing import Type, Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseInterface:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, instance: Any) -> Any:
        """Добавляет объект в базу данных."""
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get(self, model: Type, item_id: int) -> Any:
        """Получает объект по ID."""
        result = await self.session.execute(select(model).filter_by(id=item_id))
        return result.scalar_one_or_none()

    async def get_all(self, model: Type) -> Sequence[Row[Any] | RowMapping | Any]:
        """Получает все записи модели."""
        result = await self.session.execute(select(model))
        return result.scalars().all()

    async def update(self, instance: Any, **kwargs) -> Any:
        """Обновляет объект с новыми значениями."""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: Any) -> None:
        """Удаляет объект из базы данных."""
        await self.session.delete(instance)
        await self.session.commit()