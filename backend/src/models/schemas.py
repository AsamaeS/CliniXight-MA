"""
CliniVIEW MA+ — Modèles Pydantic
Schémas de données pour les 3 modules de la plateforme.
Adapté au contexte médical marocain (CNSS, RAMED, pathologies locales).
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ═══════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════

class Couverture(str, Enum):
    """Types de couverture médicale au Maroc"""
    CNSS = "CNSS"
    RAMED = "RAMED"
    MUTUELLE = "Mutuelle"
    AMO = "AMO"
    AUCUNE = "Aucune"


class SeveriteAlerte(str, Enum):
    """Niveaux de sévérité des alertes médicales"""
    HAUTE = "haute"
    MOYENNE = "moyenne"
    FAIBLE = "faible"


class TypeAlerte(str, Enum):
    """Types d'alertes détectables par le Module 1"""
    INTERACTION = "interaction"
    INCOHERENCE = "incohérence"
    SUIVI_CHRONIQUE = "suivi_chronique"


class TypeEvenement(str, Enum):
    """Types d'événements dans la timeline médicale"""
    CONSULTATION = "consultation"
    HOSPITALISATION = "hospitalisation"
    VACCIN = "vaccin"
    ANALYSE = "analyse"
    PRESCRIPTION = "prescription"
    URGENCE = "urgence"


class UrgenceStock(str, Enum):
    """Niveaux d'urgence pour les alertes de stock"""
    CRITIQUE = "critique"
    MODERE = "modéré"
    FAIBLE = "faible"
    STABLE = "stable"


# ═══════════════════════════════════════════════════════════
# Module 1 — Patient Intelligence
# ═══════════════════════════════════════════════════════════

class Medicament(BaseModel):
    """Médicament prescrit au patient"""
    nom: str = Field(..., description="Nom commercial ou DCI du médicament")
    dose: str = Field("", description="Dosage (ex: 850mg)")
    frequence: str = Field("", description="Fréquence de prise (ex: 2x/jour)")


class AlerteMedicale(BaseModel):
    """Alerte détectée par l'analyse IA du dossier"""
    type: TypeAlerte
    message: str = Field(..., description="Description détaillée de l'alerte")
    severite: SeveriteAlerte = SeveriteAlerte.MOYENNE


class EvenementTimeline(BaseModel):
    """Événement dans la timeline médicale du patient"""
    date: str = Field(..., description="Date de l'événement (format libre)")
    evenement: str = Field(..., description="Description de l'événement")
    type: TypeEvenement = TypeEvenement.CONSULTATION


class PatientInfo(BaseModel):
    """Informations d'identité du patient (avant anonymisation)"""
    nom: str = ""
    age: int = 0
    sexe: str = ""
    ville: str = Field("", description="Ville au Maroc (Casablanca, Rabat, etc.)")
    couverture: str = Field("Aucune", description="Type de couverture médicale")


class ProfilPatient(BaseModel):
    """Profil patient complet extrait par le Module 1"""
    patient: PatientInfo
    pathologies: list[str] = []
    medicaments: list[Medicament] = []
    allergies: list[str] = []
    alertes: list[AlerteMedicale] = []
    derniere_consultation: str = ""
    timeline: list[EvenementTimeline] = []


# ═══════════════════════════════════════════════════════════
# Module 2 — Privacy Shield
# ═══════════════════════════════════════════════════════════

class ResultatAnonymisation(BaseModel):
    """Résultat du processus d'anonymisation (Module 2)"""
    anonymized_data: dict = Field(..., description="Données patient anonymisées")
    privacy_score: int = Field(..., ge=0, le=100, description="Score de confidentialité 0-100")
    fields_redacted: list[str] = Field(default_factory=list, description="Champs anonymisés")
    conformite_loi_09_08: bool = Field(True, description="Conformité Loi 09-08 Maroc")


# ═══════════════════════════════════════════════════════════
# Module 3 — Smart Supply Alerts
# ═══════════════════════════════════════════════════════════

class MedicamentStock(BaseModel):
    """État du stock d'un médicament dans une région"""
    nom: str
    stock_actuel: int
    besoin_estime_7j: int
    urgence: UrgenceStock


class AlerteSupply(BaseModel):
    """Alerte de stock générée par le Module 3"""
    region: str
    alerte_epidemique: bool = False
    pathologie_dominante: str = ""
    medicaments_a_risque: list[MedicamentStock] = []
    recommandation: str = ""
    pharmacies_alertees: list[str] = []


# ═══════════════════════════════════════════════════════════
# Pipeline — État global LangGraph
# ═══════════════════════════════════════════════════════════

class CliniViewState(BaseModel):
    """État global du pipeline LangGraph — circule entre les 3 agents"""
    raw_text: str = ""
    patient_profile: dict = {}
    anonymized_profile: dict = {}
    privacy_score: int = 0
    supply_alerts: list = []
    processing_status: str = "pending"


# ═══════════════════════════════════════════════════════════
# API — Réponses
# ═══════════════════════════════════════════════════════════

class UploadResponse(BaseModel):
    """Réponse complète après traitement d'un document"""
    success: bool
    patient_code: str = ""
    anonymized_profile: dict = {}
    privacy_score: int = 0
    alertes_medicales: list[AlerteMedicale] = []
    supply_alerts: list[dict] = []
    processing_time_ms: int = 0


class PatientListItem(BaseModel):
    """Élément de la liste des patients (vue anonymisée)"""
    id: str
    patient_code: str
    region: str
    age_range: str
    couverture: str
    pathologies: list[str]
    privacy_score: int
    created_at: str


class HealthResponse(BaseModel):
    """Réponse du healthcheck"""
    status: str = "ok"
    version: str = "1.0.0"
    modules: dict = {
        "extractor": "ready",
        "redactor": "ready",
        "supply_agent": "ready",
    }
