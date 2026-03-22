from sqlalchemy import String, Text, Integer, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db import Base


class MinigridHistory(Base):
    __tablename__ = "minigrid_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    site_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    minigrid_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    equipment_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="INFO", index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    source: Mapped[str] = mapped_column(String(50), nullable=False, default="SYSTEM")
    actor_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)

    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)

    related_alert_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    related_ticket_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    related_command_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )