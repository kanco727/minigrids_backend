# app/models/minigrid.py
from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey
from ..db import Base

class MiniGrid(Base):
    __tablename__ = "mini_grid"

    id = Column(BigInteger, primary_key=True, index=True)
    site_id = Column(BigInteger, ForeignKey("site.id", ondelete="CASCADE"), nullable=False)
    nom = Column(Text, nullable=False)
    statut = Column(Text, nullable=True)
    cree_le = Column(DateTime(timezone=True), nullable=True)
    maj_le = Column(DateTime(timezone=True), nullable=True)
