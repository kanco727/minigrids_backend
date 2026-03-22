from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.minigrid_history import MinigridHistory
from app.schemas.minigrid_history import (
    MinigridHistoryCreate,
    MinigridHistoryFilter,
)


class MinigridHistoryService:
    @staticmethod
    async def log_event(
        db: AsyncSession, payload: MinigridHistoryCreate
    ) -> MinigridHistory:
        data = payload.model_dump()

        if "metadata" in data:
            data["event_metadata"] = data.pop("metadata")

        event = MinigridHistory(**data)
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def get_minigrid_history(
        db: AsyncSession,
        minigrid_id: int,
        filters: MinigridHistoryFilter
    ):
        stmt = select(MinigridHistory).where(
            MinigridHistory.minigrid_id == minigrid_id
        )
        count_stmt = select(func.count()).select_from(MinigridHistory).where(
            MinigridHistory.minigrid_id == minigrid_id
        )

        if filters.category:
            stmt = stmt.where(MinigridHistory.category == filters.category)
            count_stmt = count_stmt.where(MinigridHistory.category == filters.category)

        if filters.severity:
            stmt = stmt.where(MinigridHistory.severity == filters.severity)
            count_stmt = count_stmt.where(MinigridHistory.severity == filters.severity)

        if filters.event_type:
            stmt = stmt.where(MinigridHistory.event_type == filters.event_type)
            count_stmt = count_stmt.where(MinigridHistory.event_type == filters.event_type)

        if filters.equipment_id is not None:
            stmt = stmt.where(MinigridHistory.equipment_id == filters.equipment_id)
            count_stmt = count_stmt.where(MinigridHistory.equipment_id == filters.equipment_id)

        if filters.actor_id is not None:
            stmt = stmt.where(MinigridHistory.actor_id == filters.actor_id)
            count_stmt = count_stmt.where(MinigridHistory.actor_id == filters.actor_id)

        if filters.start_date:
            stmt = stmt.where(MinigridHistory.created_at >= filters.start_date)
            count_stmt = count_stmt.where(MinigridHistory.created_at >= filters.start_date)

        if filters.end_date:
            stmt = stmt.where(MinigridHistory.created_at <= filters.end_date)
            count_stmt = count_stmt.where(MinigridHistory.created_at <= filters.end_date)

        if filters.search:
            search_term = f"%{filters.search}%"
            condition = or_(
                MinigridHistory.title.ilike(search_term),
                MinigridHistory.description.ilike(search_term),
                MinigridHistory.actor_name.ilike(search_term),
                MinigridHistory.event_type.ilike(search_term),
            )
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        stmt = stmt.order_by(MinigridHistory.created_at.desc())
        stmt = stmt.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)

        result = await db.execute(stmt)
        items = result.scalars().all()

        total_result = await db.execute(count_stmt)
        total = total_result.scalar_one()

        return {
            "items": items,
            "total": total,
            "page": filters.page,
            "page_size": filters.page_size,
        }