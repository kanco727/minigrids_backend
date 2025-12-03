from sqlalchemy import (
    Column, BigInteger, Integer, Text, DateTime,
    Float, ForeignKey, String
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db import Base


class AlerteMinigrid(Base):
    __tablename__ = "alerte_minigrid"

    id = Column(BigInteger, primary_key=True, index=True)
    minigrid_id = Column(BigInteger, ForeignKey("mini_grid.id", ondelete="CASCADE"), nullable=False)
    type_alerte = Column(Text, nullable=False)
    niveau = Column(Text, nullable=False)  # ex: 'crit', 'warn', 'info'
    message = Column(Text, nullable=False)
    statut = Column(String, default="active")  # active | en_traitement | resolue | archivee
    time_stamp = Column(DateTime(timezone=True), server_default=func.now())

    # 🆕 Champs enrichis
    categorie = Column(String)                      # "electrique", "thermique", "communication"
    valeur_mesuree = Column(Float)
    seuil_declenchement = Column(Float)
    origine = Column(String, default="automatique")
    responsable_id = Column(Integer, nullable=True)  # ID utilisateur
    commentaire = Column(Text)
    time_resolution = Column(DateTime(timezone=True))

    # relation historique
    historiques = relationship(
        "AlerteHistorique",
        back_populates="alerte",
        cascade="all, delete-orphan"
    )

    # relation maintenance (déjà présente)
    ticket = relationship("MaintenanceTicket", back_populates="alerte", uselist=False)


class AlerteHistorique(Base):
    __tablename__ = "alerte_historique"

    id = Column(Integer, primary_key=True, index=True)
    alerte_id = Column(Integer, ForeignKey("alerte_minigrid.id", ondelete="CASCADE"), nullable=False)
    action = Column(String, nullable=False)   # "creation", "assignation", "commentaire", "statut_change", "resolution"
    acteur_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    time_action = Column(DateTime(timezone=True), server_default=func.now())

    alerte = relationship("AlerteMinigrid", back_populates="historiques")
