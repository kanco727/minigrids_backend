from sqlalchemy import Column, BigInteger, Integer, DateTime, ForeignKey
from ..db import Base

class Statistique(Base):
    __tablename__ = "statistique"
    id = Column(BigInteger, primary_key=True, index=True)
    date_rapport = Column(DateTime(timezone=True), nullable=False)
    site_id = Column(BigInteger, ForeignKey("site.id", ondelete="SET NULL"), nullable=True)
    intervenant_id = Column(BigInteger, ForeignKey("utilisateur.id", ondelete="SET NULL"), nullable=True)
    equip_type_id = Column(BigInteger, ForeignKey("equipement_type.id", ondelete="SET NULL"), nullable=True)
    note = Column(Integer, nullable=True)
