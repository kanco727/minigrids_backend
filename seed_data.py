import asyncio
import random
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, text

from app.db import AsyncSessionLocal
from app.models.projet import Projet
from app.models.site import Site
from app.models.minigrid import MiniGrid
from app.models.equipement_type import EquipementType
from app.models.equipement_minigrid import EquipementMinigrid
from app.models.mesure_minigrid import MesureMinigrid
from app.models.alerte_minigrid import AlerteMinigrid
from app.models.notification_minigrid import NotificationMinigrid
from app.models.maintenance_ticket import MaintenanceTicket
from app.models.utilisateur import Utilisateur
from app.models.parametre import Parametre
from app.models.statistique import Statistique


async def seed():
    async with AsyncSessionLocal() as db:
        existing_site = await db.execute(select(Site).limit(1))
        existing_minigrid = await db.execute(select(MiniGrid).limit(1))

        if existing_site.scalar_one_or_none() or existing_minigrid.scalar_one_or_none():
            print("Des données de démonstration existent déjà. Seed annulé.")
            return

        now = datetime.now(timezone.utc)
        # =========================
        # Paramètres plateforme
        # =========================
        param = Parametre(
            nom_plateforme="SolarPro",
            langue="fr"
        )
        db.add(param)

        # =========================
        # Utilisateurs
        # =========================
        admin = Utilisateur(
            nom="Administrateur SolarPro",
            email="admin@solarpro.local",
            mot_de_passe="admin123",
            role="admin",
        )
        tech = Utilisateur(
            nom="Technicien Kanco",
            email="technicien@solarpro.local",
            mot_de_passe="tech123",
            role="technicien",
        )
        db.add_all([admin, tech])
        await db.flush()

        # =========================
        # Projet principal
        # =========================
        projet = Projet(
            nom="Supervision des mini-réseaux solaires Burkina",
            pays="Burkina Faso",
            niveau_admin=1,
            visibilite_sur_carte=True,
            style_carte_json='{"theme":"light"}',
            cree_le=now,
            maj_le=now,
        )
        db.add(projet)
        await db.flush()

        # =========================
        # Types équipements
        # =========================
        t_panneau = EquipementType(
            type="Panneau solaire",
            description="Module photovoltaïque"
        )
        t_batterie = EquipementType(
            type="Batterie",
            description="Stockage énergie"
        )
        t_onduleur = EquipementType(
            type="Onduleur",
            description="Conversion DC/AC"
        )
        t_compteur = EquipementType(
            type="Compteur intelligent",
            description="Mesure consommation"
        )

        db.add_all([t_panneau, t_batterie, t_onduleur, t_compteur])
        await db.flush()

        # =========================
        # Sites à créer
        # =========================
        sites_data = [
            {
                "localite": "Kamsonghin",
                "point": "POINT(-1.5339 12.3714)",
                "zone": """POLYGON((
                    -1.5350 12.3705,
                    -1.5328 12.3705,
                    -1.5328 12.3722,
                    -1.5350 12.3722,
                    -1.5350 12.3705
                ))""",
                "population_estimee": 2500,
            },
            {
                "localite": "Goughin",
                "point": "POINT(-1.5345 12.3650)",
                "zone": """POLYGON((
                    -1.5355 12.3644,
                    -1.5332 12.3644,
                    -1.5332 12.3660,
                    -1.5355 12.3660,
                    -1.5355 12.3644
                ))""",
                "population_estimee": 2100,
            },
            {
                "localite": "Rimkieta",
                "point": "POINT(-1.5600 12.4000)",
                "zone": """POLYGON((
                    -1.5610 12.3990,
                    -1.5588 12.3990,
                    -1.5588 12.4010,
                    -1.5610 12.4010,
                    -1.5610 12.3990
                ))""",
                "population_estimee": 3200,
            },
        ]

        created_sites = []
        created_minigrids = []
        created_equipements = []

        # =========================
        # Création des sites + mini-grids + équipements
        # =========================
        for idx, s in enumerate(sites_data, start=1):
            site = Site(
                projet_id=projet.id,
                localite=s["localite"],
                score_acces=8,
                niveau_securite="bon",
                population_estimee=s["population_estimee"],
                notes=f"Site de démonstration {s['localite']}",
                statut="actif",
                visibilite=True,
                cree_le=now,
                maj_le=now,
            )
            db.add(site)
            await db.flush()

            await db.execute(
                text("""
                    UPDATE site
                    SET point = ST_GeomFromText(:point, 4326),
                        zone  = ST_GeomFromText(:zone, 4326)
                    WHERE id = :site_id
                """),
                {
                    "point": s["point"],
                    "zone": s["zone"],
                    "site_id": site.id,
                },
            )

            created_sites.append(site)

            mg = MiniGrid(
                site_id=site.id,
                nom=f"MiniGrid {s['localite']} 01",
                statut="en_ligne",
                cree_le=now,
                maj_le=now,
            )
            db.add(mg)
            await db.flush()
            created_minigrids.append(mg)

            # Équipements pour chaque mini-grid
            eq_panneau = EquipementMinigrid(
                minigrid_id=mg.id,
                type_id=t_panneau.id,
                numero_serie=f"PV-{s['localite'][:3].upper()}-001",
                modele="Jinko 550W",
                date_installation=now,
                statut="actif",
                cree_le=now,
                maj_le=now,
            )

            eq_batterie = EquipementMinigrid(
                minigrid_id=mg.id,
                type_id=t_batterie.id,
                numero_serie=f"BAT-{s['localite'][:3].upper()}-001",
                modele="Lithium 48V",
                date_installation=now,
                statut="actif",
                cree_le=now,
                maj_le=now,
            )

            eq_onduleur = EquipementMinigrid(
                minigrid_id=mg.id,
                type_id=t_onduleur.id,
                numero_serie=f"INV-{s['localite'][:3].upper()}-001",
                modele="Victron 5kVA",
                date_installation=now,
                statut="actif",
                cree_le=now,
                maj_le=now,
            )

            eq_compteur = EquipementMinigrid(
                minigrid_id=mg.id,
                type_id=t_compteur.id,
                numero_serie=f"CPT-{s['localite'][:3].upper()}-001",
                modele="Smart Meter V2",
                date_installation=now,
                statut="actif",
                cree_le=now,
                maj_le=now,
            )

            db.add_all([eq_panneau, eq_batterie, eq_onduleur, eq_compteur])
            await db.flush()

            created_equipements.extend([eq_panneau, eq_batterie, eq_onduleur, eq_compteur])

            # Mesures initiales pour chaque équipement
            for equip in [eq_panneau, eq_batterie, eq_onduleur, eq_compteur]:
                for j in range(5):
                    timestamp = now - timedelta(minutes=(5 - j) * 5)

                    if equip.type_id == t_panneau.id:
                        voltage = round(random.uniform(40, 60), 1)
                        courant = round(random.uniform(8, 15), 1)
                    elif equip.type_id == t_batterie.id:
                        voltage = round(random.uniform(48, 53), 1)
                        courant = round(random.uniform(5, 12), 1)
                    elif equip.type_id == t_onduleur.id:
                        voltage = round(random.uniform(220, 235), 1)
                        courant = round(random.uniform(3, 8), 1)
                    else:
                        voltage = round(random.uniform(220, 230), 1)
                        courant = round(random.uniform(1, 6), 1)

                    mesure = MesureMinigrid(
                        equip_id=equip.id,
                        minigrid_id=mg.id,
                        voltage=voltage,
                        courant=courant,
                        puissance_w=round(voltage * courant, 2),
                        temperature=round(random.uniform(28, 40), 1),
                        time_stamp=timestamp,
                    )
                    db.add(mesure)

            # Alerte initiale
            alerte = AlerteMinigrid(
                minigrid_id=mg.id,
                type_alerte="surchauffe" if idx == 1 else "maintenance préventive",
                niveau="moyen" if idx == 1 else "faible",
                message=(
                    f"Température de l’onduleur légèrement élevée sur {mg.nom}."
                    if idx == 1
                    else f"Contrôle préventif recommandé sur {mg.nom}."
                ),
                statut="active",
                time_stamp=now,
            )
            db.add(alerte)
            await db.flush()

            # Notification
            notif = NotificationMinigrid(
                alerte_id=alerte.id,
                message=f"Alerte détectée sur {mg.nom}",
                type="alerte",
                destinataire="admin",
                est_lu=False,
            )
            db.add(notif)

            # Ticket maintenance
            ticket = MaintenanceTicket(
                minigrid_id=mg.id,
                alerte_id=alerte.id,
                type="corrective" if idx == 1 else "préventive",
                description=f"Inspection recommandée pour {mg.nom}.",
                priorite="normale",
                statut="ouvert",
                rapport=None,
                rapport_fichier=None,
                cree_par=admin.id,
                assigne_a=tech.id,
                valide_par=None,
            )
            db.add(ticket)

            # Statistique
            stat = Statistique(
                date_rapport=now,
                site_id=site.id,
                intervenant_id=tech.id,
                equip_type_id=t_onduleur.id,
                note=80 + idx,
            )
            db.add(stat)

        await db.commit()

        print("Seed terminé avec succès.")
        print(f"Projet créé : {projet.nom}")
        print(f"Sites créés : {len(created_sites)}")
        print(f"Mini-grids créés : {len(created_minigrids)}")
        print(f"Équipements créés : {len(created_equipements)}")
        print("Compte admin : admin@solarpro.local / admin123")
        print("Compte tech  : technicien@solarpro.local / tech123")


if __name__ == "__main__":
    asyncio.run(seed())