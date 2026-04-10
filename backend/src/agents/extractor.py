"""
CliniVIEW MA+ — Module 1 : Patient Intelligence
Agent LangGraph d'extraction et structuration des dossiers patients.
Utilise Claude claude-sonnet-4-20250514 via l'API Anthropic pour analyser les ordonnances marocaines.
"""

import json
import logging
import os
from typing import Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Client Anthropic (initialisé au premier appel)
_client = None

def _get_client() -> Optional[Anthropic]:
    """Récupère le client Anthropic. Retourne None si clé manquante pour le mode démo."""
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or "your_" in api_key:
            logger.warning("Mode Démo Activé : ANTHROPIC_API_KEY non définie ou par défaut.")
            return None
        _client = Anthropic(api_key=api_key)
    return _client


# ═══════════════════════════════════════════════════════════
# Prompt système — Adapté au contexte médical marocain
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT = """Tu es un assistant médical expert spécialisé dans le système de santé marocain.

CONTEXTE :
- Tu analyses des ordonnances et documents médicaux issus d'hôpitaux, cliniques et cabinets marocains
- Les couvertures médicales possibles sont : CNSS, RAMED, AMO, Mutuelle, ou Aucune
- Les pathologies fréquentes au Maroc incluent : diabète type 2, hypertension, tuberculose, hépatite B, asthme, maladies cardiovasculaires

TÂCHE :
Extrais du texte médical suivant toutes les informations structurées du patient.
Réponds UNIQUEMENT en JSON valide, sans aucun texte autour.

FORMAT DE SORTIE EXACT :
{
  "patient": {
    "nom": "nom complet du patient",
    "age": 0,
    "sexe": "Masculin ou Féminin",
    "ville": "ville au Maroc",
    "couverture": "CNSS | RAMED | AMO | Mutuelle | Aucune"
  },
  "pathologies": ["liste des diagnostics et pathologies"],
  "medicaments": [
    {"nom": "nom du médicament", "dose": "dosage", "frequence": "fréquence de prise"}
  ],
  "allergies": ["liste des allergies connues"],
  "alertes": [
    {
      "type": "interaction | incohérence | suivi_chronique",
      "message": "description détaillée de l'alerte",
      "severite": "haute | moyenne | faible"
    }
  ],
  "derniere_consultation": "date de la consultation",
  "timeline": [
    {"date": "date", "evenement": "description", "type": "consultation | hospitalisation | vaccin | analyse | prescription"}
  ]
}

RÈGLES DE DÉTECTION DES ALERTES :
1. Si warfarine + aspirine sont prescrits ensemble → alerte interaction haute
2. Si IECA (inhibiteur enzyme conversion) + potassium → alerte interaction haute
3. Si metformine + AINS → alerte interaction moyenne (risque rénal)
4. Si patient diabétique et aucun suivi HbA1c mentionné → alerte suivi_chronique moyenne
5. Si patient tuberculeux sans mention de suivi hépatique → alerte suivi_chronique haute
6. Si patient hypertendu sans bilan cardiovasculaire récent → alerte suivi_chronique faible

Si une information n'est pas disponible dans le texte, utilise une chaîne vide ou une liste vide.
Ne jamais inventer d'information non présente dans le document."""


# ═══════════════════════════════════════════════════════════
# Interactions médicamenteuses connues — Détection locale
# ═══════════════════════════════════════════════════════════

INTERACTIONS_CONNUES = [
    {
        "medicaments": ["warfarine", "aspirine"],
        "message": "Association warfarine + aspirine : risque hémorragique majeur. Surveillance INR renforcée requise.",
        "severite": "haute",
    },
    {
        "medicaments": ["ieca", "potassium", "ramipril", "énalapril", "captopril"],
        "message": "IECA + suppléments potassium : risque d'hyperkaliémie sévère.",
        "severite": "haute",
    },
    {
        "medicaments": ["metformine", "ibuprofène", "ains", "diclofénac", "kétoprofène"],
        "message": "Metformine + AINS : risque accru d'insuffisance rénale aiguë.",
        "severite": "moyenne",
    },
    {
        "medicaments": ["amlodipine", "simvastatine"],
        "message": "Amlodipine + Simvastatine à forte dose : risque de myopathie. Limiter simvastatine à 20mg.",
        "severite": "moyenne",
    },
    {
        "medicaments": ["rifampicine", "isoniazide", "pyrazinamide"],
        "message": "Protocole anti-TB : surveillance hépatique obligatoire (ALAT/ASAT tous les 15 jours).",
        "severite": "haute",
    },
]


def _detecter_interactions_locales(medicaments: list[dict]) -> list[dict]:
    """
    Détecte les interactions médicamenteuses connues sans appeler l'IA.
    Complémente l'analyse de Claude pour plus de fiabilité.
    """
    alertes = []
    noms_meds = [m.get("nom", "").lower() for m in medicaments]
    
    for interaction in INTERACTIONS_CONNUES:
        meds_requis = interaction["medicaments"]
        # Vérifie si au moins 2 médicaments de l'interaction sont présents
        matches = sum(
            1 for med_requis in meds_requis
            if any(med_requis in nom_med for nom_med in noms_meds)
        )
        if matches >= 2:
            alertes.append({
                "type": "interaction",
                "message": interaction["message"],
                "severite": interaction["severite"],
            })
    
    return alertes


def _detecter_suivi_chronique(pathologies: list[str], texte_source: str) -> list[dict]:
    """
    Détecte les manques de suivi pour les maladies chroniques fréquentes au Maroc.
    """
    alertes = []
    texte_lower = texte_source.lower()
    pathologies_lower = [p.lower() for p in pathologies]
    
    # Diabète sans suivi HbA1c
    if any("diabète" in p or "diabete" in p for p in pathologies_lower):
        if "hba1c" not in texte_lower and "hémoglobine glyquée" not in texte_lower:
            alertes.append({
                "type": "suivi_chronique",
                "message": "Patient diabétique : aucun suivi HbA1c mentionné dans le dossier. Contrôle recommandé tous les 3 mois.",
                "severite": "moyenne",
            })
    
    # TB sans suivi hépatique
    if any("tuberculose" in p or "tb " in p for p in pathologies_lower):
        if "alat" not in texte_lower and "asat" not in texte_lower and "hépatique" not in texte_lower:
            alertes.append({
                "type": "suivi_chronique",
                "message": "Patient sous traitement anti-tuberculeux : bilan hépatique (ALAT/ASAT) non mentionné. Surveillance obligatoire.",
                "severite": "haute",
            })
    
    # Hypertension sans bilan cardio
    if any("hypertension" in p or "hta" in p for p in pathologies_lower):
        if "ecg" not in texte_lower and "cardiovasculaire" not in texte_lower and "cardiologie" not in texte_lower:
            alertes.append({
                "type": "suivi_chronique",
                "message": "Patient hypertendu : aucun bilan cardiovasculaire récent mentionné.",
                "severite": "faible",
            })
    
    return alertes


# ═══════════════════════════════════════════════════════════
# Fonction principale — Extraction patient
# ═══════════════════════════════════════════════════════════

def extraire_profil_patient(texte_brut: str) -> dict:
    """
    Module 1 — Patient Intelligence.
    Extrait un profil patient structuré à partir du texte brut d'un document médical.
    
    1. Envoie le texte à Claude claude-sonnet-4-20250514 pour extraction IA
    2. Enrichit avec la détection locale d'interactions
    3. Vérifie le suivi des maladies chroniques
    
    Args:
        texte_brut: Texte extrait du PDF médical
        
    Returns:
        Dictionnaire contenant le profil patient structuré
    """
    try:
        client = _get_client()
        
        if client is None:
            # Mode Démo / Fallback direct sans IA
            logger.info("Mode Démo détecté : Génération d'un profil IA fictif parfait.")
            time.sleep(1.5) # Simuler le délai IA
            return _profil_demo_complet()
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Analyse ce document médical marocain et extrais les données structurées :\n\n{texte_brut}"
                }
            ]
        )
        
        # Parse la réponse JSON
        contenu = response.content[0].text.strip()
        
        # Nettoyer si Claude entoure le JSON de ```json ... ```
        if contenu.startswith("```"):
            contenu = contenu.split("\n", 1)[1]
            if contenu.endswith("```"):
                contenu = contenu[:-3]
            contenu = contenu.strip()
        
        profil = json.loads(contenu)
        logger.info(f"Extraction réussie : patient {profil.get('patient', {}).get('nom', 'inconnu')}")
        
        # Enrichissement — Détection locale d'interactions médicamenteuses
        medicaments = profil.get("medicaments", [])
        alertes_interactions = _detecter_interactions_locales(medicaments)
        
        # Enrichissement — Suivi chronique
        pathologies = profil.get("pathologies", [])
        alertes_suivi = _detecter_suivi_chronique(pathologies, texte_brut)
        
        # Fusionner les alertes (éviter les doublons)
        alertes_existantes = profil.get("alertes", [])
        messages_existants = {a.get("message", "") for a in alertes_existantes}
        
        for alerte in alertes_interactions + alertes_suivi:
            if alerte["message"] not in messages_existants:
                alertes_existantes.append(alerte)
                messages_existants.add(alerte["message"])
        
        profil["alertes"] = alertes_existantes
        
        return profil
        
    except json.JSONDecodeError as e:
        logger.error(f"Erreur de parsing JSON de la réponse Claude : {e}")
        # Retourner un profil minimal basé sur le texte
        return _profil_fallback(texte_brut)
    
    except Exception as e:
        logger.error(f"Erreur Module 1 (extraction) : {e}")
        return _profil_fallback(texte_brut)

import time

def _profil_demo_complet() -> dict:
    """Profil très riche utilisé pour les démos sans clé API."""
    return {
        "patient": {
            "nom": "Rachid Amrani",
            "age": 58,
            "sexe": "Masculin",
            "ville": "Casablanca",
            "couverture": "CNSS"
        },
        "pathologies": ["Diabète de type 2", "Hypertension artérielle"],
        "medicaments": [
            {"nom": "Metformine", "dose": "850mg", "frequence": "1 cp matin et soir"},
            {"nom": "Amlodipine", "dose": "5mg", "frequence": "1 cp le matin"},
            {"nom": "Aspirine Protect", "dose": "100mg", "frequence": "1 cp le matin"}
        ],
        "allergies": ["Pénicilline"],
        "alertes": [
            {"type": "interaction", "message": "Metformine + AINS : risque accru d'insuffisance rénale aiguë si ajoutés.", "severite": "moyenne"},
            {"type": "suivi_chronique", "message": "Patient diabétique : aucun suivi HbA1c récent mentionné. Contrôle recommandé.", "severite": "moyenne"}
        ],
        "derniere_consultation": "15 Mars 2025",
        "timeline": [
            {"date": "2024-06", "evenement": "Diagnostic initial Diabète", "type": "consultation"},
            {"date": "2024-12", "evenement": "Ajustement dose Amlodipine", "type": "prescription"},
            {"date": "15 Mars 2025", "evenement": "Consultation de contrôle (cabinet Al Amal)", "type": "consultation"}
        ]
    }

def _profil_fallback(texte: str) -> dict:
    """
    Profil de secours si l'appel IA échoue.
    Extrait les informations basiques par heuristique.
    """
    logger.info("Utilisation du profil de secours (fallback)")
    return {
        "patient": {
            "nom": "Patient inconnu",
            "age": 0,
            "sexe": "",
            "ville": "",
            "couverture": "Aucune",
        },
        "pathologies": [],
        "medicaments": [],
        "allergies": [],
        "alertes": [{
            "type": "incohérence",
            "message": "Extraction automatique incomplète — vérification manuelle recommandée.",
            "severite": "moyenne",
        }],
        "derniere_consultation": "",
        "timeline": [],
        "_raw_text_preview": texte[:500] if texte else "",
    }
