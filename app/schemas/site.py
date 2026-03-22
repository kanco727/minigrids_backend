from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SiteBase(BaseModel):
    point_wkt: Optional[str] = None   # "POINT(lon lat)"
    zone_wkt: Optional[str] = None    # "POLYGON((...))"
    niveau_securite: Optional[str] = None
    population_estimee: Optional[int] = None
    notes: Optional[str] = None
    statut: Optional[str] = "maintenance"
    visibilite: Optional[bool] = True


class SiteCreate(SiteBase):
    projet_id: int
    localite: str
    score_acces: int


class SiteUpdate(BaseModel):
    projet_id: Optional[int] = None
    localite: Optional[str] = None
    point_wkt: Optional[str] = None
    zone_wkt: Optional[str] = None
    score_acces: Optional[int] = None
    niveau_securite: Optional[str] = None
    population_estimee: Optional[int] = None
    notes: Optional[str] = None
    statut: Optional[str] = None
    visibilite: Optional[bool] = None


class SiteRead(BaseModel):
    id: int
    projet_id: Optional[int] = None
    localite: Optional[str] = None
    point_wkt: Optional[str] = None
    zone_wkt: Optional[str] = None
    score_acces: Optional[int] = None
    niveau_securite: Optional[str] = None
    population_estimee: Optional[int] = None
    notes: Optional[str] = None
    statut: Optional[str] = None
    visibilite: Optional[bool] = None
    cree_le: Optional[datetime] = None
    maj_le: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)