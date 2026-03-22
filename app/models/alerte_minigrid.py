from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from ..db import Base


class AlerteMinigrid(Base):
    __tablename__ = "alerte_minigrid"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    minigrid_id = Column(
        BigInteger,
        ForeignKey("mini_grid.id", ondelete="CASCADE"),
        nullable=False
    )

    type_alerte = Column(Text, nullable=False)
    niveau = Column(Text, nullable=False)  # critique, haute, moyenne, faible
    message = Column(Text, nullable=False)

    statut = Column(
        Text,
        nullable=False,
        server_default=text("'active'")
    )  # active, en_traitement, resolue

    time_stamp = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    time_resolution = Column(DateTime(timezone=True), nullable=True)

    # relation avec maintenance : une alerte peut ouvrir un ticket
    ticket = relationship(
        "MaintenanceTicket",
        back_populates="alerte",
        uselist=False,
        lazy="selectin"
    )

    minigrid = relationship("MiniGrid", lazy="selectin")

    def __repr__(self):
        return (
            f"<AlerteMinigrid(id={self.id}, minigrid_id={self.minigrid_id}, "
            f"type_alerte='{self.type_alerte}', niveau='{self.niveau}', statut='{self.statut}')>"
        )