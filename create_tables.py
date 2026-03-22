import asyncio
from sqlalchemy import text
from app.db import engine, Base

# importer les modèles
from app.models import (
    projet,
    site,
    minigrid,
    equipement_minigrid,
    equipement_type,
    alerte_minigrid,
    maintenance_ticket,
    mesure_minigrid,
    notification_minigrid,
    statistique,
    utilisateur,
    parametre
)

async def init_db():
    async with engine.begin() as conn:
        # PostGIS est requis pour les types Geometry (GeoAlchemy2)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_db())