from sqlalchemy import Column, BigInteger, Integer, Text, Boolean, DateTime
from ..db import Base

class Projet(Base):
    __tablename__ = "projet"
    id = Column(BigInteger, primary_key=True, index=True)
    locataire_id = Column(BigInteger, nullable=True)
    nom = Column(Text, nullable=False)
    pays = Column(Text, nullable=True)
    niveau_admin = Column(Integer, nullable=True)
    visibilite_sur_carte = Column(Boolean, nullable=True)
    style_carte_json = Column(Text, nullable=True)
    cree_le = Column(DateTime(timezone=True), nullable=True)
    maj_le = Column(DateTime(timezone=True), nullable=True)
