from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ticket.models.sla import SLA


async def create(db: AsyncSession, data: dict[str, Any]) -> SLA | None:
    try:
        sla = SLA(**dict(data))
        db.add(sla)
        await db.commit()
        await db.refresh(sla)
        return sla
    except SQLAlchemyError as err:
        print(err)
        return None
