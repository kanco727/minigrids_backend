# app/schemas/notification_minigrid.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# 🔹 Modèle de base
class NotificationMinigridBase(BaseModel):
    alerte_id: Optional[int] = None
    message: str
    type: Optional[str] = None
    destinataire: Optional[str] = None
    est_lu: Optional[bool] = False


# 🔹 Création
class NotificationMinigridCreate(NotificationMinigridBase):
    pass


# 🔹 Lecture (réponse API)
class NotificationMinigridRead(NotificationMinigridBase):
    id: int
    cree_le: Optional[datetime] = None

    # ✅ Compatible Pydantic v2
    model_config = ConfigDict(from_attributes=True)
