from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from ..db import get_db
from .. import models, schemas
from ..dependencies import get_current_user, require_permission
from ..enums import PermissionEnum

router = APIRouter(prefix="/minigrids", tags=["minigrids"])


# =====================================================
# ✅ 1️⃣ Liste complète avec coordonnées et données récentes réalistes
# =====================================================
@router.get("/geo", summary="Liste des minigrids avec coordonnées et données récentes")
async def list_minigrids_geo(db: AsyncSession = Depends(get_db)):
    """
    Retourne toutes les mini-grids avec :
    - coordonnées GPS
    - nom + statut
    - production récente moyenne
    - batterie moyenne récente
    - température moyenne récente
    - estimation des utilisateurs actifs
    - statut réseau basé sur les alertes
    """

    query = text("""
        WITH recent_mesures AS (
            SELECT
                m.equip_id,
                m.minigrid_id,
                m.voltage,
                m.courant,
                m.puissance_w,
                m.temperature,
                m.time_stamp
            FROM mesure_minigrid m
            WHERE m.time_stamp >= NOW() - INTERVAL '10 minutes'
        ),
        agg AS (
            SELECT
                rm.minigrid_id,

                -- Production moyenne récente des panneaux en kW
                ROUND(
                    COALESCE(AVG(
                        CASE
                            WHEN LOWER(et.type) LIKE '%panneau%' THEN rm.puissance_w
                            ELSE NULL
                        END
                    ), 0)::numeric / 1000.0,
                    2
                ) AS production_kw,

                -- Batterie moyenne récente en %
                ROUND(
                    COALESCE(AVG(
                        CASE
                            WHEN LOWER(et.type) LIKE '%batterie%' THEN
                                GREATEST(
                                    0,
                                    LEAST(100, ((rm.voltage - 44.0) / 10.0) * 100)
                                )
                            ELSE NULL
                        END
                    ), 0)::numeric,
                    0
                ) AS batterie_soc,

                -- Température moyenne récente
                ROUND(
                    COALESCE(AVG(rm.temperature), 0)::numeric,
                    1
                ) AS temperature,

                -- Estimation simple des usagers actifs selon activité compteur
                COALESCE(SUM(
                    CASE
                        WHEN LOWER(et.type) LIKE '%compteur%' AND rm.courant > 0 THEN 10
                        ELSE 0
                    END
                ), 0) AS utilisateurs_actifs,

                MAX(rm.time_stamp) AS last_measure_at
            FROM recent_mesures rm
            JOIN equipement_minigrid e ON e.id = rm.equip_id
            JOIN equipement_type et ON et.id = e.type_id
            GROUP BY rm.minigrid_id
        ),
        active_alerts AS (
            SELECT
                minigrid_id,
                COUNT(*) AS nb_alertes
            FROM alerte_minigrid
            WHERE LOWER(statut) = 'active'
            GROUP BY minigrid_id
        )
        SELECT
            m.id,
            m.nom,
            m.statut,
            m.site_id,
            s.localite AS site_localite,
            ST_Y(s.point::geometry) AS latitude,
            ST_X(s.point::geometry) AS longitude,
            ST_AsText(s.point) AS site_point_wkt,

            COALESCE(a.production_kw, 0) AS production_kw,
            COALESCE(a.batterie_soc, 0) AS batterie_soc,
            COALESCE(a.temperature, 0) AS temperature,
            COALESCE(a.utilisateurs_actifs, 0) AS utilisateurs_actifs,

            CASE
                WHEN COALESCE(al.nb_alertes, 0) > 0 THEN 'alerte'
                ELSE 'normal'
            END AS statut_reseau

        FROM mini_grid m
        JOIN site s ON s.id = m.site_id
        LEFT JOIN agg a ON a.minigrid_id = m.id
        LEFT JOIN active_alerts al ON al.minigrid_id = m.id
        WHERE s.point IS NOT NULL
        ORDER BY m.id DESC
    """)

    rows = (await db.execute(query)).mappings().all()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "nom": r["nom"],
            "statut": r["statut"],
            "site_id": r["site_id"],
            "localite": r["site_localite"],
            "latitude": float(r["latitude"]) if r["latitude"] is not None else None,
            "longitude": float(r["longitude"]) if r["longitude"] is not None else None,
            "site_point_wkt": r["site_point_wkt"],
            "production_kw": float(r["production_kw"] or 0),
            "batterie_soc": int(r["batterie_soc"] or 0),
            "temperature": float(r["temperature"] or 0),
            "utilisateurs_actifs": int(r["utilisateurs_actifs"] or 0),
            "statut_reseau": r["statut_reseau"],
        })

    return results


# =====================================================
# ✅ 2️⃣ Liste simple
# =====================================================
@router.get("/", response_model=List[schemas.MiniGridRead])
async def list_minigrids(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.MiniGrid).order_by(models.MiniGrid.id.desc()))
    rows = result.scalars().all()
    return [schemas.MiniGridRead.from_orm(r) for r in rows]


# =====================================================
# ✅ 3️⃣ Création d’un mini-grid + équipements de démo
# =====================================================
@router.post("/", response_model=schemas.MiniGridRead, summary="Créer un mini-grid")
async def create_minigrid(
    payload: schemas.MiniGridCreate,
    db: AsyncSession = Depends(get_db),    current_user: models.Utilisateur = Depends(require_permission(PermissionEnum.MANAGE_MINIGRIDS))):
    """
    Crée une mini-grid.
    En mode démo, lui associe automatiquement :
    - 1 panneau solaire
    - 1 batterie
    - 1 onduleur
    - 1 compteur intelligent
    """
    try:
        existing = await db.execute(
            select(models.MiniGrid).where(models.MiniGrid.nom == payload.nom)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail="Une mini-grid avec ce nom existe déjà."
            )

        now = datetime.utcnow()

        obj = models.MiniGrid(**payload.dict(exclude_unset=True))
        obj.cree_le = now
        obj.maj_le = now

        db.add(obj)
        await db.flush()  # pour récupérer obj.id avant le commit

        # Récupérer les types d’équipements existants
        types_result = await db.execute(select(models.EquipementType))
        equipement_types = types_result.scalars().all()

        def find_type(*keywords):
            for t in equipement_types:
                t_lower = (t.type or "").lower()
                if any(k in t_lower for k in keywords):
                    return t
            return None

        t_panneau = find_type("panneau", "pv")
        t_batterie = find_type("batterie", "battery")
        t_onduleur = find_type("onduleur", "inverter")
        t_compteur = find_type("compteur", "meter")

        equipements_to_create = []

        if t_panneau:
            equipements_to_create.append(
                models.EquipementMinigrid(
                    minigrid_id=obj.id,
                    type_id=t_panneau.id,
                    numero_serie=f"PV-{obj.id}-001",
                    modele="Panneau Demo 550W",
                    date_installation=now,
                    statut="actif",
                    cree_le=now,
                    maj_le=now,
                )
            )

        if t_batterie:
            equipements_to_create.append(
                models.EquipementMinigrid(
                    minigrid_id=obj.id,
                    type_id=t_batterie.id,
                    numero_serie=f"BAT-{obj.id}-001",
                    modele="Batterie Demo 48V",
                    date_installation=now,
                    statut="actif",
                    cree_le=now,
                    maj_le=now,
                )
            )

        if t_onduleur:
            equipements_to_create.append(
                models.EquipementMinigrid(
                    minigrid_id=obj.id,
                    type_id=t_onduleur.id,
                    numero_serie=f"INV-{obj.id}-001",
                    modele="Onduleur Demo 5kVA",
                    date_installation=now,
                    statut="actif",
                    cree_le=now,
                    maj_le=now,
                )
            )

        if t_compteur:
            equipements_to_create.append(
                models.EquipementMinigrid(
                    minigrid_id=obj.id,
                    type_id=t_compteur.id,
                    numero_serie=f"CPT-{obj.id}-001",
                    modele="Compteur Demo",
                    date_installation=now,
                    statut="actif",
                    cree_le=now,
                    maj_le=now,
                )
            )

        for eq in equipements_to_create:
            db.add(eq)

        await db.commit()
        await db.refresh(obj)

        print(f"✅ Mini-grid créée : {obj.nom} ({len(equipements_to_create)} équipements auto)")
        return obj

    except HTTPException:
        raise

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Erreur d’intégrité : site_id invalide ou doublon."
        )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur serveur : {str(e)}"
        )