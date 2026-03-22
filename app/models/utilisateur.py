from sqlalchemy import Column, BigInteger, Text, Boolean, DateTime, func
from . import Base  # type: ignore
from ..db import Base as _Base  # ensure Base is imported for linters
from ..enums import RoleEnum

class Utilisateur(Base):  # type: ignore
    __tablename__ = "utilisateur"
    id = Column(BigInteger, primary_key=True, index=True)
    nom = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True, index=True)
    mot_de_passe = Column(Text, nullable=False)  # Hashed password
    role = Column(Text, default=RoleEnum.TECHNICIEN, nullable=False)
    actif = Column(Boolean, default=True, nullable=False)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_modification = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Utilisateur(id={self.id}, email='{self.email}', role='{self.role}', actif={self.actif})>"