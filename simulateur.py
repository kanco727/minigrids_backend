import asyncio
import random
from datetime import datetime, timezone
from app.db import AsyncSessionLocal
from sqlalchemy import select
from app.models import (
    MesureMinigrid,
    MiniGrid,
    EquipementMinigrid,
    AlerteMinigrid,
    NotificationMinigrid,
)

SCENARIOS = ["normal", "panne_soudaine", "hausse_conso", "coupure_reseau"]

# --- Génération de mesures ---
async def generer_mesure(session, minigrid, equipement, scenario):
    if scenario == "normal":
        voltage = round(random.uniform(210, 240), 1)
        courant = round(random.uniform(10, 30), 1)
        temperature = round(random.uniform(25, 40), 1)
    elif scenario == "panne_soudaine":
        voltage = 0
        courant = 0
        temperature = round(random.uniform(25, 40), 1)
    elif scenario == "hausse_conso":
        voltage = round(random.uniform(210, 240), 1)
        courant = round(random.uniform(40, 60), 1)
        temperature = round(random.uniform(25, 40), 1)
    elif scenario == "coupure_reseau":
        voltage = 0
        courant = 0
        temperature = None
    else:
        voltage, courant, temperature = 220, 20, 30

    mesure = MesureMinigrid(
        equip_id=equipement.id,
        minigrid_id=minigrid.id,
        voltage=voltage,
        courant=courant,
        puissance_w=voltage * courant,
        temperature=temperature,
        time_stamp=datetime.now(timezone.utc),
    )
    session.add(mesure)
    await session.flush()
    print(f"📊 {minigrid.nom}: {voltage}V, {courant}A, temp={temperature}°C")
    return mesure


# --- Analyse et génération d'alertes / résolutions ---
async def analyser_et_alerter(session, minigrid, mesure, scenario):
    ancien_statut = minigrid.statut
    nouveau_statut = ancien_statut

    if scenario == "normal" and mesure.voltage > 200 and mesure.courant > 5:
        nouveau_statut = "En Service"
    elif scenario in ["panne_soudaine", "coupure_reseau"] or (mesure.voltage == 0 and mesure.courant == 0):
        nouveau_statut = "Hors Service"
    elif scenario == "hausse_conso" and mesure.courant > 50:
        nouveau_statut = "Maintenance"
    elif mesure.temperature and mesure.temperature > 50:
        nouveau_statut = "Maintenance"

    if nouveau_statut != ancien_statut:
        print(f"🌀 {minigrid.nom}: {ancien_statut} → {nouveau_statut}")
        minigrid.statut = nouveau_statut
        minigrid.last_update = datetime.now(timezone.utc)
        session.add(minigrid)
        await session.flush()

    alertes_actives = (
        await session.execute(
            select(AlerteMinigrid).where(
                AlerteMinigrid.minigrid_id == minigrid.id,
                AlerteMinigrid.statut == "active",
            )
        )
    ).scalars().all()

    # Création d'alerte
    if scenario == "panne_soudaine":
        msg = "Panne soudaine détectée"
        al = AlerteMinigrid(minigrid_id=minigrid.id, type_alerte="Panne", niveau="critique", message=msg, statut="active")
        session.add(al)
        notif = NotificationMinigrid(alerte_id=None, message=msg, type="app", destinataire="superviseur")
        session.add(notif)
        print(f"🚨 {msg} → {minigrid.nom}")

    elif scenario == "hausse_conso" and mesure.courant > 50:
        msg = f"Surcharge détectée ({mesure.courant}A)"
        al = AlerteMinigrid(minigrid_id=minigrid.id, type_alerte="Surcharge", niveau="élevé", message=msg, statut="active")
        session.add(al)
        print(f"⚠️ {msg} → {minigrid.nom}")

    elif mesure.temperature and mesure.temperature > 50:
        msg = f"Température critique ({mesure.temperature}°C)"
        al = AlerteMinigrid(minigrid_id=minigrid.id, type_alerte="Température critique", niveau="critique", message=msg, statut="active")
        session.add(al)
        print(f"🔥 {msg} → {minigrid.nom}")

    # Résolution automatique si normal
    elif scenario == "normal":
        for al in alertes_actives:
            if al.type_alerte.lower() in ["panne", "surcharge", "température critique"]:
                al.statut = "resolue"
                al.message = f"{al.type_alerte} résolue automatiquement"
                print(f"✅ Alerte {al.type_alerte} résolue sur {minigrid.nom}")
                session.add(al)
                await session.flush()

    await session.commit()


# --- Boucle de simulation continue ---
async def boucle_continue(intervalle=5):
    async with AsyncSessionLocal() as session:
        minigrids = (await session.execute(select(MiniGrid))).scalars().all()
        equipements = (await session.execute(select(EquipementMinigrid))).scalars().all()
        if not minigrids or not equipements:
            print("⚠️ Aucun mini-grid trouvé.")
            return

        print(f"🟢 Simulation active ({len(minigrids)} sites).")
        while True:
            minigrid = random.choice(minigrids)
            equipement = random.choice(equipements)
            scenario = random.choice(SCENARIOS)
            print(f"\n--- Simulation: {scenario} sur {minigrid.nom} ---")
            mesure = await generer_mesure(session, minigrid, equipement, scenario)
            await analyser_et_alerter(session, minigrid, mesure, scenario)
            await asyncio.sleep(intervalle)


if __name__ == "__main__":
    try:
        asyncio.run(boucle_continue(intervalle=5))
    except KeyboardInterrupt:
        print("\n🛑 Simulation arrêtée.")
