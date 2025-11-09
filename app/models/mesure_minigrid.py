from sqlalchemy import Column, BigInteger, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from ..db import Base

class MesureMinigrid(Base):
    __tablename__ = "mesure_minigrid"
    id = Column(BigInteger, primary_key=True)
    equip_id = Column(BigInteger, ForeignKey("equipement_minigrid.id", ondelete="CASCADE"), nullable=False)
    minigrid_id = Column(BigInteger, ForeignKey("mini_grid.id", ondelete="CASCADE"))
    voltage = Column(Float, nullable=False)
    courant = Column(Float, nullable=False)
    puissance_w = Column(Float, nullable=False)
    temperature = Column(Float, nullable=True)
    time_stamp = Column(DateTime(timezone=True), nullable=True)
    cree_le = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def get_default_equip_id(session):
        # Retourne le premier equipement existant ou None
        equip = session.query_by_table_name("equipement_minigrid").first()
        return equip.id if equip else None
