from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class StatistiqueBase(BaseModel):
    date_rapport: Optional[datetime] = None
    site_id: Optional[int] = None
    intervenant_id: Optional[int] = None
    equip_type_id: Optional[int] = None
    note: Optional[int] = None

class StatistiqueCreate(StatistiqueBase): pass
class StatistiqueUpdate(StatistiqueBase): pass

class StatistiqueRead(StatistiqueBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
