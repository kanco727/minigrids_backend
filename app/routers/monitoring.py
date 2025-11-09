from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from datetime import datetime, timedelta

router = APIRouter(prefix="/minigrids/{minigrid_id}/monitoring", tags=["monitoring"])

@router.get("/kpis")
async def get_minigrid_kpis(minigrid_id: int, db: AsyncSession = Depends(get_db)):
    # TODO: Connecter à la base pour vraies données
    return {
        "production_kw": 2.5,
        "consommation_kw": 1.8,
        "batterie_pourcentage": 85,
        "utilisateurs_connectes": 47,
        "temperature_c": 28.5,
        "reseau_statut": "online",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/energy-curves")
async def get_energy_curves(minigrid_id: int, period: str = "7d", db: AsyncSession = Depends(get_db)):
    # TODO: Connecter à la base pour vraies données
    now = datetime.now()
    return [
        {
            "timestamp": (now - timedelta(days=i)).isoformat(),
            "date_label": (now - timedelta(days=i)).strftime("%a"),
            "production_kw": 2.1 + i*0.1,
            "consommation_kw": 1.5 + i*0.1,
            "batterie_pourcentage": 80 + i
        } for i in range(7)
    ]

@router.get("/energy-distribution")
async def get_energy_distribution(minigrid_id: int, db: AsyncSession = Depends(get_db)):
    # TODO: Connecter à la base pour vraies données
    return [
        {"name": "production", "value": 65, "pourcentage": 65},
        {"name": "consommation", "value": 28, "pourcentage": 28},
        {"name": "pertes", "value": 7, "pourcentage": 7}
    ]

@router.get("/sites")
async def get_sites_status(minigrid_id: int, db: AsyncSession = Depends(get_db)):
    # TODO: Connecter à la base pour vraies données
    return [
        {
            "id": 1,
            "name": "Site Principal",
            "status": "online",
            "production_kw": 1.2,
            "users_count": 25,
            "last_update": datetime.now().isoformat()
        }
    ]
