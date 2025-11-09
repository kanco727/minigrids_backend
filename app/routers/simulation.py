from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..db import get_db
from .. import models
import random
from datetime import datetime, timedelta

router = APIRouter(prefix="/simulate", tags=["simulation"])

# ==========================================================
# 🧩 1️⃣ SIMULATION DES MESURES ET ALERTES
# ==========================================================
@router.post("/cycle")
async def simulate_cycle(db: AsyncSession = Depends(get_db)):
    """
    Génère aléatoirement des mesures et déclenche des alertes.
    """
    minigrids = (await db.execute(select(models.MiniGrid))).scalars().all()
    results = []

    if not minigrids:
        return {"message": "Aucune mini-grid trouvée."}

    for mg in minigrids:
        voltage = round(random.uniform(200, 250), 1)
        courant = round(random.uniform(10, 50), 1)
        puissance_w = round(voltage * courant, 2)
        temperature = round(random.uniform(20, 60), 1)

        # 🔍 Trouver un équipement associé
        equipement = (await db.execute(
            select(models.EquipementMinigrid)
            .where(models.EquipementMinigrid.minigrid_id == mg.id)
        )).scalars().first()

        equip_id = equipement.id if equipement else None
        if not equip_id:
            equipement_defaut = (await db.execute(select(models.EquipementMinigrid))).scalars().first()
            if not equipement_defaut:
                continue
            equip_id = equipement_defaut.id

        # 🔹 Créer la mesure
        mesure = models.MesureMinigrid(
            equip_id=equip_id,
            minigrid_id=mg.id,
            voltage=voltage,
            courant=courant,
            puissance_w=puissance_w,
            temperature=temperature,
            time_stamp=datetime.utcnow(),
        )
        db.add(mesure)
        await db.flush()

        # 🔸 Détection d’anomalies
        alerts = []
        if temperature > 50:
            alerts.append(("Température critique", f"{temperature} °C"))
        if voltage < 210:
            alerts.append(("Sous-tension", f"{voltage} V"))
        if courant > 45:
            alerts.append(("Surcharge de courant", f"{courant} A"))

        for typ, msg in alerts:
            alerte = models.AlerteMinigrid(
                minigrid_id=mg.id,
                type_alerte=typ,
                niveau="crit",
                message=msg,
                time_stamp=datetime.utcnow(),
                statut="active"
            )
            db.add(alerte)
            await db.flush()

            notif = models.NotificationMinigrid(
                alerte_id=alerte.id,
                message=f"Alerte {typ} détectée sur {mg.nom}: {msg}",
                type="app",
                destinataire="superviseur",
                est_lu=False
            )
            db.add(notif)

        results.append({
            "minigrid": mg.nom,
            "mesure": dict(voltage=voltage, courant=courant, puissance=puissance_w, temp=temperature),
            "alertes": len(alerts)
        })

    await db.commit()
    return {"cycle": datetime.utcnow(), "resultats": results}

# ==========================================================
# 🧠 2️⃣ ENDPOINTS DE MONITORING (UTILISÉS PAR LE DASHBOARD)
# ==========================================================

@router.get("/monitoring/{mg_id}/kpis")
async def get_monitoring_kpis(mg_id: int, db: AsyncSession = Depends(get_db)):
    """Retourne les KPI calculés à partir des dernières mesures"""
    q = await db.execute(
        select(
            func.avg(models.MesureMinigrid.voltage),
            func.avg(models.MesureMinigrid.courant),
            func.avg(models.MesureMinigrid.puissance_w),
            func.avg(models.MesureMinigrid.temperature)
        ).where(models.MesureMinigrid.minigrid_id == mg_id)
    )
    voltage, courant, puissance, temp = q.one()

    return {
        "productionTotale_kw": round((puissance or 0) / 1000, 2),
        "consommation_kw": round(((puissance or 0) * 0.8) / 1000, 2),
        "batterie_pourcentage": random.randint(40, 95),
        "utilisateurs_connectes": random.randint(10, 50),
        "temperature_c": round(temp or random.uniform(25, 40), 1),
        "reseau_statut": random.choice(["online", "alerte", "offline"]),
        "timestamp": datetime.utcnow().isoformat()
    }

# ==========================================================
# 🔋 3️⃣ COURBES D'ÉNERGIE
# ==========================================================
@router.get("/monitoring/{mg_id}/energy-curves")
async def get_energy_curves(mg_id: int, db: AsyncSession = Depends(get_db)):
    """Retourne les courbes de production/consommation (7 derniers jours)"""
    data = []
    now = datetime.utcnow()
    for i in range(7):
        date_label = (now - timedelta(days=i)).strftime("%d/%m")
        prod = round(random.uniform(1200, 2000), 1)
        conso = round(prod * random.uniform(0.7, 0.9), 1)
        batterie = random.randint(50, 100)
        data.append({
            "date_label": date_label,
            "timestamp": (now - timedelta(days=i)).isoformat(),
            "production_kw": prod,
            "consommation_kw": conso,
            "batterie_pourcentage": batterie
        })
    return list(reversed(data))

# ==========================================================
# ⚙️ 4️⃣ RÉPARTITION DE L'ÉNERGIE
# ==========================================================
@router.get("/monitoring/{mg_id}/energy-distribution")
async def get_energy_distribution(mg_id: int):
    """Répartition énergétique simulée"""
    parts = [
        {"name": "Pompage", "value": random.randint(10, 25)},
        {"name": "Éclairage", "value": random.randint(15, 30)},
        {"name": "Maisons", "value": random.randint(20, 40)},
        {"name": "Santé", "value": random.randint(10, 25)},
    ]
    total = sum(p["value"] for p in parts)
    for p in parts:
        p["pourcentage"] = round(p["value"] * 100 / total, 1)
    return parts

# ==========================================================
# 🛰️ 5️⃣ ÉTAT DES SITES
# ==========================================================
@router.get("/monitoring/{mg_id}/sites")
async def get_sites_status(mg_id: int, db: AsyncSession = Depends(get_db)):
    """Statut simulé des sites liés à une mini-grid"""
    sites = (await db.execute(select(models.Site).where(models.Site.projet_id == mg_id))).scalars().all()
    res = []
    for s in sites:
        res.append({
            "id": s.id,
            "name": s.localite or "Site inconnu",
            "status": random.choice(["online", "alerte", "offline"]),
            "production_kw": round(random.uniform(5, 25), 1),
            "users_count": random.randint(2, 10),
            "last_update": datetime.utcnow().isoformat()
        })
    return res
