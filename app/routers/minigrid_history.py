from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.minigrid_history import (
    MinigridHistoryCreate,
    MinigridHistoryRead,
    MinigridHistoryFilter,
    PaginatedMinigridHistory,
)
from app.services.minigrid_history_service import MinigridHistoryService

router = APIRouter(prefix="/history", tags=["Minigrid History"])


@router.post("/", response_model=MinigridHistoryRead)
async def create_history_event(
    payload: MinigridHistoryCreate,
    db: AsyncSession = Depends(get_db),
):
    return await MinigridHistoryService.log_event(db, payload)


@router.get("/minigrids/{minigrid_id}", response_model=PaginatedMinigridHistory)
async def get_minigrid_history(
    minigrid_id: int,
    category: str | None = Query(None),
    severity: str | None = Query(None),
    event_type: str | None = Query(None),
    equipment_id: UUID | None = Query(None),
    actor_id: UUID | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    filters = MinigridHistoryFilter(
        category=category,
        severity=severity,
        event_type=event_type,
        equipment_id=equipment_id,
        actor_id=actor_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
        page=page,
        page_size=page_size,
    )
    return await MinigridHistoryService.get_minigrid_history(db, minigrid_id, filters)