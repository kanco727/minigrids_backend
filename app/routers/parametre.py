from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.parametre import Parametre
from app.schemas.parametre import ParametreCreate, ParametreRead, ParametreUpdate

router = APIRouter(
    prefix="/parametres",
    tags=["parametres"]
)

@router.get("/", response_model=list[ParametreRead])
def list_parametres(db: Session = Depends(get_db)):
    return db.query(Parametre).all()

@router.get("/{parametre_id}", response_model=ParametreRead)
def get_parametre(parametre_id: int, db: Session = Depends(get_db)):
    param = db.query(Parametre).filter(Parametre.id == parametre_id).first()
    if not param:
        raise HTTPException(status_code=404, detail="Paramètre non trouvé")
    return param

@router.post("/", response_model=ParametreRead)
def create_parametre(parametre: ParametreCreate, db: Session = Depends(get_db)):
    db_param = Parametre(**parametre.dict())
    db.add(db_param)
    db.commit()
    db.refresh(db_param)
    return db_param

@router.put("/{parametre_id}", response_model=ParametreRead)
def update_parametre(parametre_id: int, parametre: ParametreUpdate, db: Session = Depends(get_db)):
    db_param = db.query(Parametre).filter(Parametre.id == parametre_id).first()
    if not db_param:
        raise HTTPException(status_code=404, detail="Paramètre non trouvé")
    for key, value in parametre.dict(exclude_unset=True).items():
        setattr(db_param, key, value)
    db.commit()
    db.refresh(db_param)
    return db_param

@router.delete("/{parametre_id}")
def delete_parametre(parametre_id: int, db: Session = Depends(get_db)):
    db_param = db.query(Parametre).filter(Parametre.id == parametre_id).first()
    if not db_param:
        raise HTTPException(status_code=404, detail="Paramètre non trouvé")
    db.delete(db_param)
    db.commit()
    return {"ok": True}
