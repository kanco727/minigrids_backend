from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey
from ..db import Base

class EquipementMinigrid(Base):
    __tablename__ = "equipement_minigrid"
    id = Column(BigInteger, primary_key=True, index=True)
    minigrid_id = Column(BigInteger, ForeignKey("mini_grid.id", ondelete="CASCADE"), nullable=False)
    type_id = Column(BigInteger, ForeignKey("equipement_type.id", ondelete="RESTRICT"), nullable=False)
    numero_serie = Column(Text, nullable=False)
    modele = Column(Text, nullable=True)
    date_installation = Column(DateTime(timezone=True), nullable=True)
    statut = Column(Text, nullable=True)
    cree_le = Column(DateTime(timezone=True), nullable=True)
    maj_le = Column(DateTime(timezone=True), nullable=True)
