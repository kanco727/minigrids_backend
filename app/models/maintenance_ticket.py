from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from ..db import Base

class MaintenanceTicket(Base):
    __tablename__ = "maintenance_ticket"

    # === Identifiants ===
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    # === Liens vers les entités associées ===
    minigrid_id = Column(
        BigInteger,
        ForeignKey("mini_grid.id", ondelete="SET NULL"),
        nullable=True
    )
    alerte_id = Column(
        BigInteger,
        ForeignKey("alerte_minigrid.id", ondelete="SET NULL"),
        nullable=True
    )

    # === Informations principales ===
    type = Column(Text, nullable=False, server_default=text("'corrective'"))
    description = Column(Text, nullable=True)
    priorite = Column(Text, nullable=False, server_default=text("'normale'"))

    # Statut du ticket : ouvert, en_cours, rapport_envoye, termine
    statut = Column(Text, nullable=False, server_default=text("'ouvert'"))

    # === Dates et rapports ===
    date_creation = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")  # auto timestamp à la création
    )

    # Rapport du technicien
    rapport = Column(Text, nullable=True)  # texte explicatif
    rapport_fichier = Column(Text, nullable=True)  # lien ou chemin vers fichier joint (PDF, docx, etc.)

    # === Suivi des utilisateurs ===
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

    # === Relations ORM ===
    alerte = relationship("AlerteMinigrid", back_populates="ticket", lazy="selectin")
    minigrid = relationship("MiniGrid", lazy="selectin")

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
            f"type='{self.type}', priorite='{self.priorite}', minigrid_id={self.minigrid_id})>"
        )
