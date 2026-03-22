from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ..db import get_db
from .. import schemas

router = APIRouter(prefix="/sites", tags=["sites"])


# LECTURE : ST_AsText pour renvoyer WKT
@router.get("/", response_model=List[schemas.SiteRead])
async def list_sites(db: AsyncSession = Depends(get_db)):
    q = text("""
      SELECT id, projet_id, localite,
             ST_AsText(point) AS point_wkt,
             ST_AsText(zone)  AS zone_wkt,
             score_acces, niveau_securite, population_estimee, notes, statut,
             visibilite, cree_le, maj_le
      FROM site
      ORDER BY id DESC
    """)
    rows = (await db.execute(q)).mappings().all()
    return [dict(r) for r in rows]


@router.get("/{site_id}", response_model=schemas.SiteRead)
async def get_site(site_id: int, db: AsyncSession = Depends(get_db)):
    q = text("""
      SELECT id, projet_id, localite,
             ST_AsText(point) AS point_wkt,
             ST_AsText(zone)  AS zone_wkt,
             score_acces, niveau_securite, population_estimee, notes, statut,
             visibilite, cree_le, maj_le
      FROM site
      WHERE id = :id
    """)
    row = (await db.execute(q, {"id": site_id})).mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail="Site introuvable")

    return dict(row)


# CREATION : ST_GeomFromText pour WKT entrant
@router.post("/", response_model=schemas.SiteRead)
async def create_site(payload: schemas.SiteCreate, db: AsyncSession = Depends(get_db)):
    d = payload.model_dump()
    point_wkt = d.pop("point_wkt", None)
    zone_wkt = d.pop("zone_wkt", None)

    cols = [
        "projet_id",
        "localite",
        "score_acces",
        "niveau_securite",
        "population_estimee",
        "notes",
        "statut",
        "visibilite"
    ]
    vals = [
        ":projet_id",
        ":localite",
        ":score_acces",
        ":niveau_securite",
        ":population_estimee",
        ":notes",
        ":statut",
        ":visibilite"
    ]

    if point_wkt is not None:
        cols.append("point")
        vals.append("ST_GeomFromText(:point_wkt, 4326)")
        d["point_wkt"] = point_wkt

    if zone_wkt is not None:
        cols.append("zone")
        vals.append("ST_GeomFromText(:zone_wkt, 4326)")
        d["zone_wkt"] = zone_wkt

    q = text(f"""
      INSERT INTO site ({", ".join(cols)})
      VALUES ({", ".join(vals)})
      RETURNING id, projet_id, localite,
                ST_AsText(point) AS point_wkt,
                ST_AsText(zone)  AS zone_wkt,
                score_acces, niveau_securite, population_estimee, notes, statut,
                visibilite, cree_le, maj_le
    """)

    try:
        row = (await db.execute(q, d)).mappings().first()
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du site: {str(e)}")

    if not row:
        raise HTTPException(status_code=400, detail="Insertion site échouée")

    return dict(row)


# MISE À JOUR : mix champs simples + géométrie
@router.patch("/{site_id}", response_model=schemas.SiteRead)
async def update_site(site_id: int, payload: schemas.SiteUpdate, db: AsyncSession = Depends(get_db)):
    d = payload.model_dump(exclude_unset=True)
    sets = []

    # Géométrie
    if "point_wkt" in d:
        sets.append("point = ST_GeomFromText(:point_wkt, 4326)")

    if "zone_wkt" in d:
        sets.append("zone = ST_GeomFromText(:zone_wkt, 4326)")

    # Champs simples
    for k in [
        "projet_id",
        "localite",
        "score_acces",
        "niveau_securite",
        "population_estimee",
        "notes",
        "statut",
        "visibilite"
    ]:
        if k in d:
            sets.append(f"{k} = :{k}")

    if not sets:
        return await get_site(site_id, db)

    d["id"] = site_id

    q = text(f"""
      UPDATE site
      SET {", ".join(sets)}, maj_le = now()
      WHERE id = :id
      RETURNING id, projet_id, localite,
                ST_AsText(point) AS point_wkt,
                ST_AsText(zone)  AS zone_wkt,
                score_acces, niveau_securite, population_estimee, notes, statut,
                visibilite, cree_le, maj_le
    """)

    try:
        row = (await db.execute(q, d)).mappings().first()
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du site: {str(e)}")

    if not row:
        raise HTTPException(status_code=404, detail="Site introuvable")

    return dict(row)


@router.delete("/{site_id}")
async def delete_site(site_id: int, db: AsyncSession = Depends(get_db)):
    q = text("DELETE FROM site WHERE id = :id RETURNING id")

    try:
        val = (await db.execute(q, {"id": site_id})).scalar()
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression du site: {str(e)}")

    if val is None:
        raise HTTPException(status_code=404, detail="Site introuvable")

    return {"deleted": site_id}