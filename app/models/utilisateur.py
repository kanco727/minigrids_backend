from sqlalchemy import Column, BigInteger, Text, Boolean, DateTime, func
from . import Base  # type: ignore
from ..db import Base as _Base  # ensure Base is imported for linters

class Utilisateur(Base):  # type: ignore
    __tablename__ = "utilisateur"
    id = Column(BigInteger, primary_key=True, index=True)
    nom = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    mot_de_passe = Column(Text, nullable=False)
    role = Column(Text, default="technicien")
    date_creation = Column(DateTime(timezone=True), server_default=func.now())