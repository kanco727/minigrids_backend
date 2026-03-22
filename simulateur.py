import asyncio
import random
from datetime import datetime, timezone

from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models import (
    MesureMinigrid,
    MiniGrid,
    EquipementMinigrid,
    EquipementType,
    AlerteMinigrid,
    NotificationMinigrid,
)

SCENARIOS = ["normal", "panne_soudaine", "hausse_conso", "coupure_reseau"]


# ============================================================
# Génération d'une mesure cohérente selon le type d'équipement
# ============================================================
async def generer_mesure(session, minigrid, equipement, type_label, scenario):
    type_lower = (type_label or "").lower()

    voltage = 0.0
    courant = 0.0
    temperature = None

    if "panneau" in type_lower:
        if scenario == "normal":
            voltage = round(random.uniform(42, 58), 1)
            courant = round(random.uniform(8, 14), 1)
            temperature = round(random.uniform(28, 42), 1)
        elif scenario == "hausse_conso":
            voltage = round(random.uniform(44, 60), 1)
            courant = round(random.uniform(10, 16), 1)
            temperature = round(random.uniform(32, 45), 1)
        elif scenario in ["panne_soudaine", "coupure_reseau"]:
            voltage = 0
            courant = 0
            temperature = round(random.uniform(25, 35), 1)

    elif "batterie" in type_lower:
        if scenario == "normal":
            voltage = round(random.uniform(48, 53), 1)
            courant = round(random.uniform(4, 10), 1)
            temperature = round(random.uniform(26, 36), 1)
        elif scenario == "hausse_conso":
            voltage = round(random.uniform(46, 51), 1)
            courant = round(random.uniform(10, 18), 1)
            temperature = round(random.uniform(30, 42), 1)
        elif scenario in ["panne_soudaine", "coupure_reseau"]:
            voltage = round(random.uniform(40, 45), 1)
            courant = 0
            temperature = round(random.uniform(25, 34), 1)

    elif "onduleur" in type_lower:
        if scenario == "normal":
            voltage = round(random.uniform(220, 235), 1)
            courant = round(random.uniform(3, 8), 1)
            temperature = round(random.uniform(30, 42), 1)
        elif scenario == "hausse_conso":
            voltage = round(random.uniform(218, 232), 1)
            courant = round(random.uniform(12, 20), 1)
            temperature = round(random.uniform(40, 55), 1)
        elif scenario == "panne_soudaine":
            voltage = 0
            courant = 0
            temperature = round(random.uniform(28, 36), 1)
        elif scenario == "coupure_reseau":
            voltage = 0
            courant = 0
            temperature = None

    elif "compteur" in type_lower:
        if scenario == "normal":
            voltage = round(random.uniform(220, 230), 1)
            courant = round(random.uniform(2, 6), 1)
            temperature = round(random.uniform(28, 38), 1)
        elif scenario == "hausse_conso":
            voltage = round(random.uniform(220, 230), 1)
            courant = round(random.uniform(15, 25), 1)
            temperature = round(random.uniform(30, 40), 1)
        elif scenario in ["panne_soudaine", "coupure_reseau"]:
            voltage = 0
            courant = 0
            temperature = None

    else:
        if scenario == "normal":
            voltage = round(random.uniform(220, 230), 1)
            courant = round(random.uniform(3, 6), 1)
            temperature = round(random.uniform(28, 38), 1)
        elif scenario == "hausse_conso":
            voltage = round(random.uniform(220, 230), 1)
            courant = round(random.uniform(10, 18), 1)
            temperature = round(random.uniform(35, 48), 1)
        else:
            voltage = 0
            courant = 0
            temperature = None

    puissance_w = round(voltage * courant, 2) if voltage and courant else 0

    mesure = MesureMinigrid(
        equip_id=equipement.id,
        minigrid_id=minigrid.id,
        voltage=voltage,
        courant=courant,
        puissance_w=puissance_w,
        temperature=temperature,
        time_stamp=datetime.now(timezone.utc),
    )

    session.add(mesure)
    await session.flush()

    print(
        f"📊 {minigrid.nom} | {type_label} | "
        f"{voltage}V, {courant}A, {puissance_w}W, temp={temperature}"
    )

    return mesure


# ============================================================
# Analyse de l'état et gestion des alertes
# ============================================================
async def analyser_et_alerter(session, minigrid, mesure, scenario):
    ancien_statut = minigrid.statut or "inconnu"
    nouveau_statut = ancien_statut

    if scenario == "normal" and mesure.voltage > 0 and mesure.courant > 0:
        nouveau_statut = "en_service"
    elif scenario in ["panne_soudaine", "coupure_reseau"] or (mesure.voltage == 0 and mesure.courant == 0):
        nouveau_statut = "hors_service"
    elif scenario == "hausse_conso" and mesure.courant > 12:
        nouveau_statut = "maintenance"
    elif mesure.temperature and mesure.temperature > 50:
        nouveau_statut = "maintenance"

    if nouveau_statut != ancien_statut:
        print(f"🌀 {minigrid.nom}: {ancien_statut} → {nouveau_statut}")
        minigrid.statut = nouveau_statut
        minigrid.maj_le = datetime.now(timezone.utc)
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

    # --- Création d'alerte ---
    if scenario == "panne_soudaine":
        msg = "Panne soudaine détectée"
        al = AlerteMinigrid(
            minigrid_id=minigrid.id,
            type_alerte="Panne",
            niveau="critique",
            message=msg,
            statut="active",
            time_stamp=datetime.now(timezone.utc),
        )
        session.add(al)
        await session.flush()

        notif = NotificationMinigrid(
            alerte_id=al.id,
            message=msg,
            type="alerte",
            destinataire="superviseur",
            est_lu=False,
        )
        session.add(notif)
        print(f"🚨 {msg} → {minigrid.nom}")

    elif scenario == "hausse_conso" and mesure.courant > 12:
        msg = f"Surcharge détectée ({mesure.courant}A)"
        al = AlerteMinigrid(
            minigrid_id=minigrid.id,
            type_alerte="Surcharge",
            niveau="élevé",
            message=msg,
            statut="active",
            time_stamp=datetime.now(timezone.utc),
        )
        session.add(al)
        print(f"⚠️ {msg} → {minigrid.nom}")

    elif mesure.temperature and mesure.temperature > 50:
        msg = f"Température critique ({mesure.temperature}°C)"
        al = AlerteMinigrid(
            minigrid_id=minigrid.id,
            type_alerte="Température critique",
            niveau="critique",
            message=msg,
            statut="active",
            time_stamp=datetime.now(timezone.utc),
        )
        session.add(al)
        print(f"🔥 {msg} → {minigrid.nom}")

    # --- Résolution automatique si retour à la normale ---
    elif scenario == "normal":
        for al in alertes_actives:
            if al.type_alerte.lower() in ["panne", "surcharge", "température critique"]:
                al.statut = "resolue"
                al.message = f"{al.type_alerte} résolue automatiquement"
                session.add(al)
                print(f"✅ Alerte {al.type_alerte} résolue sur {minigrid.nom}")

    await session.commit()


# ============================================================
# Boucle principale
# ============================================================
async def boucle_continue(intervalle=5):
    async with AsyncSessionLocal() as session:
        print("🔄 Chargement des mini-grids et équipements...")

        minigrids = (await session.execute(select(MiniGrid))).scalars().all()
        equipements = (await session.execute(select(EquipementMinigrid))).scalars().all()
        equipement_types = (await session.execute(select(EquipementType))).scalars().all()

        if not minigrids:
            print("⚠️ Aucun mini-grid trouvé.")
            return

        if not equipements:
            print("⚠️ Aucun équipement trouvé.")
            return

        types_by_id = {t.id: t.type for t in equipement_types}

        equipements_par_minigrid = {}
        for eq in equipements:
            equipements_par_minigrid.setdefault(eq.minigrid_id, []).append(eq)

        print(f"🟢 Simulation active ({len(minigrids)} mini-grid(s)).")

        while True:
            minigrid = random.choice(minigrids)
            equipements_du_minigrid = equipements_par_minigrid.get(minigrid.id, [])

            if not equipements_du_minigrid:
                print(f"⚠️ Aucun équipement associé à {minigrid.nom}")
                await asyncio.sleep(intervalle)
                continue

            equipement = random.choice(equipements_du_minigrid)
            type_label = types_by_id.get(equipement.type_id, "Équipement")
            scenario = random.choice(SCENARIOS)

            print(f"\n--- Simulation: {scenario} sur {minigrid.nom} ({type_label}) ---")

            mesure = await generer_mesure(session, minigrid, equipement, type_label, scenario)
            await analyser_et_alerter(session, minigrid, mesure, scenario)

            await asyncio.sleep(intervalle)


if __name__ == "__main__":
    try:
        asyncio.run(boucle_continue(intervalle=5))
    except KeyboardInterrupt:
        print("\n🛑 Simulation arrêtée.")