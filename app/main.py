# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    health, projet, site, minigrid,
    equipement_type, equipement_minigrid,
    alerte_minigrid, maintenance_ticket,
    statistique, utilisateur, parametre,
    notification_minigrid, simulation, monitoring,
    auth, minigrid_history
)

app = FastAPI(title="Écosystème Mini-Grid API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
   allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://frontend-solarpro-1.vercel.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/__routes", tags=["debug"], include_in_schema=False)
def list_routes():
    return [{"path": getattr(r, "path", None), "methods": list(getattr(r, "methods", []))} for r in app.router.routes]

app.include_router(auth.router)
app.include_router(health.router)
app.include_router(projet.router)
app.include_router(site.router)
app.include_router(minigrid.router)
app.include_router(equipement_type.router)
app.include_router(equipement_minigrid.router)
app.include_router(alerte_minigrid.router)
app.include_router(maintenance_ticket.router)
app.include_router(statistique.router)
app.include_router(utilisateur.router)
app.include_router(parametre.router)
app.include_router(notification_minigrid.router)
app.include_router(simulation.router)
app.include_router(monitoring.router)
app.include_router(minigrid_history.router)

@app.get("/")
def root():
    return {"message": "Bienvenue sur l’API Mini-Grid 🚀"}