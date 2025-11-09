
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class MesureMinigridBase(BaseModel):
    minigrid_id: int
    voltage: float
    courant: float
    puissance_w: float
    temperature: Optional[float] = None

class MesureMinigridCreate(MesureMinigridBase):
    pass

class MesureMinigridRead(MesureMinigridBase):
    id: int
    cree_le: datetime
    model_config = ConfigDict(from_attributes=True)
