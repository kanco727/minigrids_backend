from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SiteBase(BaseModel):
    projet_id: Optional[int] = None
    localite: Optional[str] = None
    point_wkt: Optional[str] = None  # "POINT(lon lat)"
    zone_wkt: Optional[str]  = None  # "POLYGON((...))"
    score_acces: Optional[int] = None
    niveau_securite: Optional[str] = None
    population_estimee: Optional[int] = None
    notes: Optional[str] = None
    statut: Optional[str] = None
    visibilite: Optional[bool] = None

class SiteCreate(SiteBase): pass
class SiteUpdate(SiteBase): pass

class SiteRead(SiteBase):
    id: int
    cree_le: Optional[datetime] = None
    maj_le: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)









