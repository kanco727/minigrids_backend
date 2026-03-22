# app/routers/statistiques.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from ..db import get_db
from .. import models, schemas

router = APIRouter(prefix="/statistiques", tags=["statistiques"])


# ============================================================
# ✅ 1️⃣ Lister toutes les statistiques enregistrées
# ============================================================
@router.get("/", response_model=List[schemas.StatistiqueRead])
async def list_statistiques(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(
        select(models.Statistique).order_by(models.Statistique.date_rapport.desc())
    )).scalars().all()
    return rows


# ============================================================
# ✅ 2️⃣ Créer une statistique manuelle
# ============================================================
@router.post("/", response_model=schemas.StatistiqueRead)
async def create_statistique(payload: schemas.StatistiqueCreate, db: AsyncSession = Depends(get_db)):
    obj = models.Statistique(**payload.model_dump(exclude_unset=True))
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# ============================================================
# ✅ 3️⃣ Mettre à jour une statistique existante
# ============================================================
@router.patch("/{statistique_id}", response_model=schemas.StatistiqueRead)
async def update_statistique(statistique_id: int, payload: schemas.StatistiqueUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.Statistique, statistique_id)
    if not obj:
        raise HTTPException(404, "Statistique introuvable")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


# ============================================================
# ✅ 4️⃣ Supprimer une statistique
# ============================================================
@router.delete("/{statistique_id}")
async def delete_statistique(statistique_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(models.Statistique, statistique_id)
    if not obj:
        raise HTTPException(404, "Statistique introuvable")
    await db.delete(obj)
    await db.commit()
    return {"deleted": statistique_id}


# ============================================================
# ✅ 5️⃣ Rapports de maintenance (tickets avec rapport ou terminés)
# ============================================================
@router.get("/maintenance_rapports")
async def get_maintenance_reports(db: AsyncSession = Depends(get_db)):
    """
    Retourne les tickets de maintenance terminés ou avec rapport joint.
    Sert à alimenter l’onglet “Rapports de Maintenance” du frontend.
    """
    stmt = select(models.MaintenanceTicket).where(
        models.MaintenanceTicket.statut.in_(["rapport_envoye", "termine"])
    )
    tickets = (await db.execute(stmt)).scalars().all()

    data = []
    for t in tickets:
        data.append({
            "id": t.id,
            "minigrid_id": t.minigrid_id,
            "type": t.type,
            "priorite": t.priorite,
            "statut": t.statut,
            "rapport": t.rapport,
            "rapport_fichier": t.rapport_fichier,
            "date_creation": t.date_creation.isoformat() if t.date_creation else None
        })

    return data


# ============================================================
# ✅ 6️⃣ Statistiques globales (pour tableau de bord principal)
# ============================================================
@router.get("/globales")
async def statistiques_globales(db: AsyncSession = Depends(get_db)):
    """
    Fournit un résumé global pour le tableau de bord :
    - nombre de mini-grids
    - nombre d’alertes
    - nombre de tickets de maintenance
    - tickets en cours / terminés
    - nombre de rapports envoyés
    """
    total_minigrids = (await db.execute(select(func.count(models.MiniGrid.id)))).scalar()
    total_alertes = (await db.execute(select(func.count(models.AlerteMinigrid.id)))).scalar()
    total_tickets = (await db.execute(select(func.count(models.MaintenanceTicket.id)))).scalar()
    tickets_en_cours = (await db.execute(
        select(func.count(models.MaintenanceTicket.id)).where(models.MaintenanceTicket.statut == "en_cours")
    )).scalar()
    tickets_termines = (await db.execute(
        select(func.count(models.MaintenanceTicket.id)).where(models.MaintenanceTicket.statut == "termine")
    )).scalar()
    tickets_rapport = (await db.execute(
        select(func.count(models.MaintenanceTicket.id)).where(models.MaintenanceTicket.statut == "rapport_envoye")
    )).scalar()

    return {
        "total_minigrids": total_minigrids or 0,
        "total_alertes": total_alertes or 0,
        "total_tickets": total_tickets or 0,
        "tickets_en_cours": tickets_en_cours or 0,
        "tickets_termines": tickets_termines or 0,
        "tickets_rapport_envoye": tickets_rapport or 0,
    }
# ============================================================
# ✅ 7️⃣ Production vs consommation sur 7 jours
# ============================================================
@router.get("/energie-semaine")
async def energie_semaine(db: AsyncSession = Depends(get_db)):
    """
    Retourne une estimation réaliste de la production et de la consommation
    sur les 7 derniers jours pour alimenter le graphique du dashboard.

    Hypothèses :
    - production = puissance moyenne des panneaux × 6 h solaires / jour
    - consommation = puissance moyenne des compteurs/onduleurs × 24 h / jour

    Résultat renvoyé en kWh.
    """

    query = text("""
        WITH jours AS (
            SELECT generate_series(
                CURRENT_DATE - INTERVAL '6 days',
                CURRENT_DATE,
                INTERVAL '1 day'
            )::date AS date_jour
        ),
        mesures_jour AS (
            SELECT
                DATE(m.time_stamp) AS date_jour,

                AVG(
                    CASE
                        WHEN LOWER(et.type) LIKE '%panneau%' THEN m.puissance_w
                        ELSE NULL
                    END
                ) AS avg_production_w,

                AVG(
                    CASE
                        WHEN LOWER(et.type) LIKE '%compteur%'
                          OR LOWER(et.type) LIKE '%onduleur%'
                        THEN m.puissance_w
                        ELSE NULL
                    END
                ) AS avg_consommation_w

            FROM mesure_minigrid m
            JOIN equipement_minigrid e ON e.id = m.equip_id
            JOIN equipement_type et ON et.id = e.type_id
            WHERE m.time_stamp >= NOW() - INTERVAL '7 days'
            GROUP BY DATE(m.time_stamp)
        )
        SELECT
            TO_CHAR(j.date_jour, 'Dy') AS jour_brut,
            j.date_jour,

            ROUND(
                COALESCE((mj.avg_production_w * 6.0) / 1000.0, 0)::numeric,
                2
            ) AS production_kwh,

            ROUND(
                COALESCE((mj.avg_consommation_w * 24.0) / 1000.0, 0)::numeric,
                2
            ) AS consommation_kwh

        FROM jours j
        LEFT JOIN mesures_jour mj ON mj.date_jour = j.date_jour
        ORDER BY j.date_jour ASC
    """)

    rows = (await db.execute(query)).mappings().all()

    jours_map = {
        "Mon": "Lun",
        "Tue": "Mar",
        "Wed": "Mer",
        "Thu": "Jeu",
        "Fri": "Ven",
        "Sat": "Sam",
        "Sun": "Dim",
    }

    jours = []
    production_totale = 0.0
    consommation_totale = 0.0

    for r in rows:
        production = float(r["production_kwh"] or 0)
        consommation = float(r["consommation_kwh"] or 0)

        jours.append({
            "jour": jours_map.get((r["jour_brut"] or "").strip(), (r["jour_brut"] or "").strip()),
            "production": production,
            "consommation": consommation,
        })

        production_totale += production
        consommation_totale += consommation

    return {
        "jours": jours,
        "production_totale": round(production_totale, 2),
        "consommation_totale": round(consommation_totale, 2),
    }