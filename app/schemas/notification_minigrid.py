from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class NotificationMinigridBase(BaseModel):
    alerte_id: Optional[int] = None
    message: str
    type: Optional[str] = None
    destinataire: Optional[str] = None
    est_lu: Optional[bool] = False
    est_archivee: Optional[bool] = False


class NotificationMinigridCreate(NotificationMinigridBase):
    pass


class NotificationMinigridRead(NotificationMinigridBase):
    id: int
    cree_le: Optional[datetime] = None
    archivee_le: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)