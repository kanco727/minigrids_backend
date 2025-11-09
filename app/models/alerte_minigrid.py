from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..db import Base

class AlerteMinigrid(Base):
    __tablename__ = "alerte_minigrid"

    id = Column(BigInteger, primary_key=True, index=True)
    minigrid_id = Column(BigInteger, ForeignKey("mini_grid.id", ondelete="CASCADE"), nullable=False)
    type_alerte = Column(Text, nullable=False)
    niveau = Column(Text, nullable=False)  # ex: 'critique', 'moyen', 'faible'
    message = Column(Text, nullable=False)
    statut = Column(Text, nullable=False, default="active")  # active, en_traitement, resolue
    time_stamp = Column(DateTime(timezone=True), nullable=False)

    # relation avec maintenance
    ticket = relationship("MaintenanceTicket", back_populates="alerte", uselist=False)
