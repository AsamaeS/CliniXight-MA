"""
CliniVIEW MA+ — API Backend (FastAPI)
Point d'entrée de l'application. Connecte le frontend (Next.js) au pipeline LangGraph.
"""

import os
import logging
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.models.schemas import UploadResponse, PatientListItem, HealthResponse
from src.pipeline.graph import executer_pipeline

# Config logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialisation FastAPI
app = FastAPI(
    title="CliniVIEW MA+ API",
    description="API backend pour la plateforme santé CliniVIEW MA+ (HackEurope 2025)",
    version="1.0.0",
)

# Configuration CORS (Accepte les requêtes du frontend Next.js)
origins = [
    "http://localhost:3000",
    "http://localhost:5173", # Si utilisation de Vite par erreur
    os.getenv("FRONTEND_URL", "https://cliniview-ma.vercel.app")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Racine de l'API")
async def root():
    return {"message": "Bienvenue sur l'API CliniVIEW MA+"}


@app.get("/api/health", response_model=HealthResponse, summary="Healthcheck")
async def health_check():
    """Vérifie que l'API et les modules sous-jacents sont opérationnels."""
    # En production, vérifier la connexion DB et les clés API ici
    return HealthResponse(status="ok")


@app.post("/api/upload", response_model=UploadResponse, summary="Uploader et analyser un document PDF")
async def upload_document(file: UploadFile = File(...)):
    """
    Reçoit un fichier PDF (ordonnance, compte-rendu), lance le pipeline LangGraph :
    1. Extraction (Claude)
    2. Anonymisation (Loi 09-08)
    3. Analyse épidémiologique
    4. Retourne le profil anonymisé
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")

    try:
        # Lire le fichier en mémoire
        contents = await file.read()
        logger.info(f"Fichier reçu : {file.filename} ({len(contents)} bytes)")

        # Appeler le pipeline LangGraph
        resultat = await executer_pipeline(pdf_bytes=contents, filename=file.filename)
        
        # En production, on sauvegarderait le résultat dans Supabase ici
        # patient_data = format_for_supabase(resultat)
        # supabase.table("patients").insert(patient_data).execute()

        # Construire la réponse
        patient_code = resultat.get("anonymized_profile", {}).get("patient", {}).get("nom", "Inconnu")
        
        # Extraire les alertes médicales depuis le profil original (elles sont conservées dans l'anonymisé)
        profil_anon = resultat.get("anonymized_profile", {})
        alertes_med = profil_anon.get("alertes", [])

        return UploadResponse(
            success=True,
            patient_code=patient_code,
            anonymized_profile=profil_anon,
            privacy_score=resultat.get("privacy_score", 0),
            alertes_medicales=alertes_med,
            supply_alerts=resultat.get("supply_alerts", []),
            processing_time_ms=resultat.get("processing_time_ms", 0)
        )

    except Exception as e:
        logger.error(f"Erreur lors du traitement : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne lors du traitement : {str(e)}")


# ═══════════════════════════════════════════════════════════
# Endpoints Mockés pour la démo (En prod -> Supabase)
# ═══════════════════════════════════════════════════════════

@app.get("/api/patients", response_model=List[PatientListItem], summary="Liste des patients (anonymisés)")
async def get_patients():
    """
    Retourne la liste des patients. 
    En production, ceci interroge Supabase.
    Ici, données mockées pour l'UI.
    """
    return [
        PatientListItem(
            id="uuid-1",
            patient_code="Patient_A3F2",
            region="Région Casablanca-Settat",
            age_range="55-60 ans",
            couverture="CNSS",
            pathologies=["Diabète type 2", "Hypertension artérielle"],
            privacy_score=100,
            created_at="2025-03-15T10:00:00Z"
        ),
        PatientListItem(
            id="uuid-2",
            patient_code="Patient_B9E1",
            region="Région Marrakech-Safi",
            age_range="30-35 ans",
            couverture="RAMED",
            pathologies=["Tuberculose pulmonaire"],
            privacy_score=85,
            created_at="2025-03-14T14:30:00Z"
        )
    ]

@app.get("/api/patients/{id}", summary="Détails d'un patient (anonymisé)")
async def get_patient_details(id: str):
    """
    Retourne le profil complet et anonymisé d'un patient.
    """
    # Mock data pour la démo
    return {
        "id": id,
        "patient": {
            "nom": "Patient_A3F2",
            "age_range": "55-60 ans",
            "sexe": "Masculin",
            "ville": "Région Casablanca-Settat",
            "couverture": "CNSS"
        },
        "pathologies": ["Diabète type 2", "Hypertension artérielle"],
        "medicaments": [
            {"nom": "Metformine", "dose": "850mg", "frequence": "2x/jour"},
            {"nom": "Amlodipine", "dose": "5mg", "frequence": "1x/jour"}
        ],
        "alertes": [
            {
                "type": "interaction",
                "message": "Associer Metformine et AINS majore le risque d'IR aiguë.",
                "severite": "moyenne"
            }
        ],
        "timeline": [
            {"date": "2024-06", "evenement": "Consultation Diabétologie", "type": "consultation"},
            {"date": "2024-11", "evenement": "Renouvellement ordonnance", "type": "prescription"}
        ],
        "privacy_score": 100
    }

@app.get("/api/alerts/supply", summary="Alertes de stock épidémiologique par région")
async def get_supply_alerts():
    """
    Retourne les alertes de stock calculées par le Module 3.
    """
    return [
        {
            "region": "Région Casablanca-Settat",
            "urgence": "critique",
            "pathologie": "Grippe saisonnière",
            "medicament": "Oseltamivir (Tamiflu)",
            "message": "Risque de rupture sous 7 jours. +35% de cas détectés.",
            "resolved": False,
            "created_at": "2025-03-15T09:00:00Z"
        },
        {
            "region": "Région Marrakech-Safi",
            "urgence": "modéré",
            "pathologie": "Diabète type 2",
            "medicament": "Insuline Glargine",
            "message": "Baisse anormale du stock constatée (-40% en 15j).",
            "resolved": False,
            "created_at": "2025-03-14T16:45:00Z"
        }
    ]

if __name__ == "__main__":
    import uvicorn
    # Mode dev avec hot reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
