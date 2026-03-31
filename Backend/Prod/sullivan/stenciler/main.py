"""
Point d'entrée FastAPI avec CORS pour Sullivan Stenciler

Lancement :
cd Backend/Prod
uvicorn sullivan.stenciler.main:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sullivan.stenciler.api import router

# Créer l'application FastAPI
app = FastAPI(
    title="Sullivan Stenciler API",
    description="API REST Backend pour Sullivan Stenciler - Phase 3",
    version="1.0.0"
)

# CORS : Autoriser le Frontend (port 9998) à appeler le Backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:9998",
        "http://127.0.0.1:9998",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, etc.
    allow_headers=["*"],  # Content-Type, etc.
)

# Inclure les routes de l'API
app.include_router(router)


# Health check (vérifier que le serveur répond)
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Sullivan Stenciler API",
        "version": "1.0.0"
    }


# Message de bienvenue
@app.get("/")
async def root():
    return {
        "message": "Sullivan Stenciler API - Backend Ready",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/genome"
    }
