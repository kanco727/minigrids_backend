from sqlalchemy import Column, Integer, String
from app.db import Base

class Parametre(Base):
    __tablename__ = "parametres"

    id = Column(Integer, primary_key=True, index=True)
    nom_plateforme = Column(String, nullable=False, default="SolarPro")
    langue = Column(String, nullable=False, default="fr")
