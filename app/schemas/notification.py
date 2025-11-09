from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class NotificationBase(BaseModel):
    alerte_id: Optional[int] = None
    message: str
    type: Optional[str] = "app"
    destinataire: Optional[str] = None
    est_lu: bool = False

class NotificationCreate(NotificationBase): pass

class NotificationRead(NotificationBase):
    id: int
    cree_le: datetime
    model_config = ConfigDict(from_attributes=True)
