from sqlalchemy import Column, BigInteger, Integer, Text, Boolean, DateTime, ForeignKey
from geoalchemy2 import Geometry
from ..db import Base

class Site(Base):
    __tablename__ = "site"
    id = Column(BigInteger, primary_key=True, index=True)
    projet_id = Column(BigInteger, ForeignKey("projet.id", ondelete="CASCADE"), nullable=False)
    localite = Column(Text, nullable=True)
    point = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    zone  = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=True)
    score_acces = Column(Integer, nullable=True)
    niveau_securite = Column(Text, nullable=True)
    population_estimee = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    statut = Column(Text, nullable=True)
    visibilite = Column(Boolean, nullable=True)
    cree_le = Column(DateTime(timezone=True), nullable=True)
    maj_le = Column(DateTime(timezone=True), nullable=True)
