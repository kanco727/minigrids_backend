from sqlalchemy import Column, BigInteger, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from ..db import Base

class NotificationMinigrid(Base):
    __tablename__ = "notification_minigrid"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    alerte_id = Column(BigInteger, ForeignKey("alerte_minigrid.id", ondelete="CASCADE"), nullable=True)
    message = Column(Text, nullable=False)
    type = Column(Text, nullable=True)  
    destinataire = Column(Text, nullable=True)  
    est_lu = Column(Boolean, default=False)
    cree_le = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type}', lu={self.est_lu})>"
