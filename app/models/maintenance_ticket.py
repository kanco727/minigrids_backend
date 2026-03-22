from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey, Numeric, text
from sqlalchemy.orm import relationship
from ..db import Base


class MaintenanceTicket(Base):
    __tablename__ = "maintenance_ticket"

    # =========================
    # Identifiants
    # =========================
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    # =========================
    # Liens vers entités associées
    # =========================
    minigrid_id = Column(
        BigInteger,
        ForeignKey("mini_grid.id", ondelete="SET NULL"),
        nullable=True
    )

    equipement_id = Column(
        BigInteger,
        ForeignKey("equipement_minigrid.id", ondelete="SET NULL"),
        nullable=True
    )

    alerte_id = Column(
        BigInteger,
        ForeignKey("alerte_minigrid.id", ondelete="SET NULL"),
        nullable=True
    )

    # =========================
    # Informations principales
    # =========================
    titre = Column(Text, nullable=True)

    # preventive, corrective, curative, planifiee, urgence...
    type = Column(Text, nullable=False, server_default=text("'corrective'"))

    # manuel, alerte, inspection, systeme
    source_ticket = Column(Text, nullable=True, server_default=text("'manuel'"))

    description = Column(Text, nullable=True)

    # faible, moyenne, haute, urgente, critique
    priorite = Column(Text, nullable=False, server_default=text("'normale'"))

    # ouvert, planifie, en_cours, rapport_envoye, valide, termine, annule
    statut = Column(Text, nullable=False, server_default=text("'ouvert'"))

    # =========================
    # Dates
    # =========================
    date_creation = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    date_planifiee = Column(DateTime(timezone=True), nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    date_validation = Column(DateTime(timezone=True), nullable=True)

    # =========================
    # Rapport / observations
    # =========================
    rapport = Column(Text, nullable=True)
    observation_technicien = Column(Text, nullable=True)
    rapport_fichier = Column(Text, nullable=True)

    # =========================
    # Coûts / durées
    # =========================
    cout_estime = Column(Numeric(12, 2), nullable=True)
    cout_reel = Column(Numeric(12, 2), nullable=True)

    duree_estimee_h = Column(Numeric(8, 2), nullable=True)
    duree_reelle_h = Column(Numeric(8, 2), nullable=True)

    # =========================
    # Suivi utilisateurs
    # =========================
    cree_par = Column(
        BigInteger,
        ForeignKey("utilisateur.id", ondelete="SET NULL"),
        nullable=True
    )

    assigne_a = Column(
        BigInteger,
        ForeignKey("utilisateur.id", ondelete="SET NULL"),
        nullable=True
    )

    valide_par = Column(
        BigInteger,
        ForeignKey("utilisateur.id", ondelete="SET NULL"),
        nullable=True
    )

    # =========================
    # Relations ORM
    # =========================
    alerte = relationship("AlerteMinigrid", back_populates="ticket", lazy="selectin")
    minigrid = relationship("MiniGrid", lazy="selectin")
    equipement = relationship("EquipementMinigrid", lazy="selectin")

    createur = relationship(
        "Utilisateur",
        foreign_keys=[cree_par],
        lazy="selectin",
        viewonly=True
    )

    assigne = relationship(
        "Utilisateur",
        foreign_keys=[assigne_a],
        lazy="selectin",
        viewonly=True
    )

    validateur = relationship(
        "Utilisateur",
        foreign_keys=[valide_par],
        lazy="selectin",
        viewonly=True
    )

    def __repr__(self):
        return (
            f"<MaintenanceTicket(id={self.id}, statut='{self.statut}', "
            f"type='{self.type}', priorite='{self.priorite}', "
            f"minigrid_id={self.minigrid_id}, equipement_id={self.equipement_id})>"
        )