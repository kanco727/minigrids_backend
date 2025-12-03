# app/models/equipement_event.py
from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..db import Base

class EquipementEvent(Base):
    __tablename__ = "equipement_event"

    id = Column(BigInteger, primary_key=True, index=True)
    equipement_id = Column(
        BigInteger,
        ForeignKey("equipement_minigrid.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    type_event = Column(Text, nullable=False)  # on/off/restart/reset/...
    message = Column(Text, nullable=True)

    old_status = Column(Text, nullable=True)
    new_status = Column(Text, nullable=True)

    source = Column(Text, nullable=True, default="system")
    horodatage = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # relation inverse
    equipement = relationship("EquipementMinigrid", back_populates="events")
