"""
CliniVIEW MA+ — Pipeline LangGraph
Workflow orchestrant les 3 modules dans l'ordre :
  PDF → Extraction → Anonymisation → Sauvegarde → Analyse Supply

Utilise LangGraph StateGraph pour un pipeline séquentiel robuste.
"""

import logging
import time
from typing import TypedDict, Any
from langgraph.graph import StateGraph, END

from src.utils.pdf_parser import extraire_texte_depuis_bytes, _texte_demo
from src.agents.extractor import extraire_profil_patient
from src.agents.redactor import anonymiser_profil
from src.agents.supply_agent import analyser_supply

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# État global du pipeline — Circule entre les nœuds
# ═══════════════════════════════════════════════════════════

class CliniViewState(TypedDict):
    """
    État partagé entre tous les nœuds du pipeline LangGraph.
    Chaque nœud lit et écrit dans cet état.
    """
    # Entrée
    raw_text: str
    pdf_bytes: bytes
    filename: str
    
    # Module 1 — Extraction
    patient_profile: dict
    
    # Module 2 — Anonymisation
    anonymized_profile: dict
    privacy_score: int
    fields_redacted: list
    
    # Module 3 — Supply
    supply_alerts: list
    
    # Méta
    processing_status: str
    processing_time_ms: int
    errors: list


# ═══════════════════════════════════════════════════════════
# Nœuds du pipeline
# ═══════════════════════════════════════════════════════════

def noeud_extraction_pdf(state: CliniViewState) -> dict:
    """
    Nœud 1 — Extraction du texte brut depuis le PDF.
    Utilise PyMuPDF. Fallback vers le texte de démo si le PDF est vide.
    """
    logger.info("📄 Pipeline — Étape 1 : Extraction PDF")
    
    try:
        pdf_bytes = state.get("pdf_bytes", b"")
        filename = state.get("filename", "document.pdf")
        
        if pdf_bytes:
            texte = extraire_texte_depuis_bytes(pdf_bytes, filename)
        else:
            # Utiliser le texte de démo si aucun PDF fourni
            logger.info("Aucun PDF fourni — utilisation du texte de démonstration")
            texte = _texte_demo()
        
        return {
            "raw_text": texte,
            "processing_status": "extraction_done",
        }
        
    except Exception as e:
        logger.error(f"Erreur extraction PDF : {e}")
        return {
            "raw_text": _texte_demo(),
            "processing_status": "extraction_fallback",
            "errors": state.get("errors", []) + [f"Extraction PDF : {str(e)}"],
        }


def noeud_extraction_patient(state: CliniViewState) -> dict:
    """
    Nœud 2 — Module 1 : Patient Intelligence.
    Appelle Claude claude-sonnet-4-20250514 pour extraire le profil structuré du patient.
    """
    logger.info("🧠 Pipeline — Étape 2 : Extraction profil patient (Module 1)")
    
    try:
        texte = state.get("raw_text", "")
        profil = extraire_profil_patient(texte)
        
        return {
            "patient_profile": profil,
            "processing_status": "extraction_patient_done",
        }
        
    except Exception as e:
        logger.error(f"Erreur extraction patient : {e}")
        return {
            "patient_profile": {},
            "processing_status": "extraction_patient_error",
            "errors": state.get("errors", []) + [f"Module 1 : {str(e)}"],
        }


def noeud_anonymisation(state: CliniViewState) -> dict:
    """
    Nœud 3 — Module 2 : Privacy Shield.
    Anonymise le profil patient (conformité Loi 09-08 + RGPD).
    """
    logger.info("🔐 Pipeline — Étape 3 : Anonymisation (Module 2)")
    
    try:
        profil = state.get("patient_profile", {})
        resultat = anonymiser_profil(profil)
        
        return {
            "anonymized_profile": resultat.get("anonymized_data", {}),
            "privacy_score": resultat.get("privacy_score", 0),
            "fields_redacted": resultat.get("fields_redacted", []),
            "processing_status": "anonymisation_done",
        }
        
    except Exception as e:
        logger.error(f"Erreur anonymisation : {e}")
        return {
            "anonymized_profile": state.get("patient_profile", {}),
            "privacy_score": 0,
            "fields_redacted": [],
            "processing_status": "anonymisation_error",
            "errors": state.get("errors", []) + [f"Module 2 : {str(e)}"],
        }


def noeud_analyse_supply(state: CliniViewState) -> dict:
    """
    Nœud 4 — Module 3 : Smart Supply Alerts.
    Analyse épidémiologique et prédiction de stock.
    """
    logger.info("📊 Pipeline — Étape 4 : Analyse supply (Module 3)")
    
    try:
        # On passe le profil anonymisé dans une liste (simulation d'agrégation)
        profil_anon = state.get("anonymized_profile", {})
        patients = [profil_anon] if profil_anon else []
        
        # En production : récupérer les patients récents depuis Supabase
        alertes = analyser_supply(patients)
        
        return {
            "supply_alerts": alertes,
            "processing_status": "complete",
        }
        
    except Exception as e:
        logger.error(f"Erreur analyse supply : {e}")
        return {
            "supply_alerts": [],
            "processing_status": "supply_error",
            "errors": state.get("errors", []) + [f"Module 3 : {str(e)}"],
        }


# ═══════════════════════════════════════════════════════════
# Construction du graphe LangGraph
# ═══════════════════════════════════════════════════════════

def construire_pipeline() -> StateGraph:
    """
    Construit le pipeline LangGraph complet :
    PDF → Extraction → Anonymisation → Supply Alerts
    """
    workflow = StateGraph(CliniViewState)
    
    # Ajouter les nœuds
    workflow.add_node("extraction_pdf", noeud_extraction_pdf)
    workflow.add_node("extraction_patient", noeud_extraction_patient)
    workflow.add_node("anonymisation", noeud_anonymisation)
    workflow.add_node("analyse_supply", noeud_analyse_supply)
    
    # Définir les transitions (séquentielles)
    workflow.set_entry_point("extraction_pdf")
    workflow.add_edge("extraction_pdf", "extraction_patient")
    workflow.add_edge("extraction_patient", "anonymisation")
    workflow.add_edge("anonymisation", "analyse_supply")
    workflow.add_edge("analyse_supply", END)
    
    return workflow.compile()


# Instance globale du pipeline compilé
pipeline = construire_pipeline()


async def executer_pipeline(
    pdf_bytes: bytes = b"",
    filename: str = "document.pdf",
    texte_brut: str = "",
) -> dict:
    """
    Exécute le pipeline complet de traitement d'un document médical.
    
    Args:
        pdf_bytes: Contenu binaire du PDF (optionnel)
        filename: Nom du fichier PDF
        texte_brut: Texte brut alternatif (si pas de PDF)
        
    Returns:
        Résultat complet avec profil anonymisé, score, et alertes
    """
    start = time.time()
    
    # État initial
    initial_state = {
        "raw_text": texte_brut,
        "pdf_bytes": pdf_bytes,
        "filename": filename,
        "patient_profile": {},
        "anonymized_profile": {},
        "privacy_score": 0,
        "fields_redacted": [],
        "supply_alerts": [],
        "processing_status": "started",
        "processing_time_ms": 0,
        "errors": [],
    }
    
    logger.info(f"🚀 Démarrage pipeline CliniVIEW MA+ — Fichier : {filename}")
    
    # Exécution du pipeline
    result = pipeline.invoke(initial_state)
    
    # Calcul du temps de traitement
    elapsed_ms = int((time.time() - start) * 1000)
    result["processing_time_ms"] = elapsed_ms
    
    logger.info(
        f"✅ Pipeline terminé en {elapsed_ms}ms — "
        f"Status : {result.get('processing_status')} — "
        f"Privacy Score : {result.get('privacy_score')}/100"
    )
    
    return result
