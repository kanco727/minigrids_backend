from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class MinigridHistoryBase(BaseModel):
    site_id: int | None = None
    minigrid_id: int
    equipment_id: int | None = None

    category: str
    event_type: str
    severity: str = "INFO"

    title: str
    description: str

    source: str = "SYSTEM"
    actor_id: int | None = None
    actor_name: str | None = None

    status: str | None = None

    old_value: str | None = None
    new_value: str | None = None

    metadata: dict[str, Any] | None = None

    related_alert_id: int | None = None
    related_ticket_id: int | None = None
    related_command_id: int | None = None


class MinigridHistoryCreate(MinigridHistoryBase):
    pass


class MinigridHistoryRead(MinigridHistoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class MinigridHistoryFilter(BaseModel):
    category: str | None = None
    severity: str | None = None
    event_type: str | None = None
    equipment_id: int | None = None
    actor_id: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    search: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedMinigridHistory(BaseModel):
    items: list[MinigridHistoryRead]
    total: int
    page: int
    page_size: int