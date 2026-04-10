"""
CliniVIEW MA+ — Module 2 : Privacy Shield
Agent LangGraph d'anonymisation intelligente des données patients.
Conformité Loi 09-08 (CNDP Maroc) + RGPD (Europe).
Utilise Claude claude-sonnet-4-20250514 pour une anonymisation contextuelle (pas juste [MASQUÉ]).
"""

import json
import logging
import os
from typing import Optional
from anthropic import Anthropic
from src.utils.anonymizer import (
    generer_code_patient,
    anonymiser_ville,
    age_vers_tranche,
    calculer_score_confidentialite,
)

logger = logging.getLogger(__name__)

_client = None

def _get_client() -> Optional[Anthropic]:
    """Récupère ou initialise le client Anthropic."""
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or "your_" in api_key:
            return None
        _client = Anthropic(api_key=api_key)
    return _client


# ═══════════════════════════════════════════════════════════
# Prompt système — Anonymisation contextuelle
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT = """Tu es un expert en conformité des données de santé, spécialisé dans :
- La Loi 09-08 relative à la protection des données personnelles au Maroc (CNDP)
- Le RGPD européen (articles applicables aux données de santé)

TÂCHE :
Anonymise les données personnelles du profil patient ci-dessous en respectant ces règles :

RÈGLES D'ANONYMISATION :
1. Nom réel → code anonyme au format "Patient_XXXX" (4 caractères hexadécimaux)
2. Ville précise → nom de la région administrative (ex: "Casablanca" → "Région Casablanca-Settat")
3. Âge précis → tranche d'âge de 5 ans (ex: 58 → "55-60 ans")
4. N° CNSS / RAMED / CIN → "[IDENTIFIANT_MASQUÉ]"
5. Nom de médecin → "Médecin_[SPÉCIALITÉ]" (ex: "Dr. Bennani" → "Médecin_Généraliste")
6. Dates précises → mois/année uniquement (ex: "15 Mars 2025" → "Mars 2025")

NE PAS ANONYMISER :
- Les pathologies et diagnostics (données médicales essentielles)
- Les noms de médicaments et posologies
- Les résultats d'analyses (HbA1c, glycémie, etc.)
- Les types de couverture (CNSS, RAMED, etc.)

IMPORTANT : Préserve le sens clinique du dossier. Un médecin doit pouvoir lire
le profil anonymisé et comprendre l'historique médical du patient.

Réponds UNIQUEMENT en JSON avec ce format :
{
  "anonymized_data": { ... le profil anonymisé ... },
  "privacy_score": 85,
  "fields_redacted": ["nom", "ville", "age", ...]
}"""


# ═══════════════════════════════════════════════════════════
# Anonymisation locale (sans IA) — Rapide et déterministe
# ═══════════════════════════════════════════════════════════

def _anonymiser_localement(profil: dict) -> dict:
    """
    Effectue une anonymisation déterministe des champs principaux.
    Utilisé en complément ou en fallback de l'anonymisation IA.
    """
    profil_anon = json.loads(json.dumps(profil))  # Deep copy
    patient = profil_anon.get("patient", {})
    champs_rediges = []
    
    # Anonymiser le nom
    nom_original = patient.get("nom", "")
    if nom_original and not nom_original.startswith("Patient_"):
        patient["nom"] = generer_code_patient(nom_original)
        champs_rediges.append("nom")
    
    # Anonymiser la ville → région
    ville = patient.get("ville", "")
    if ville and not ville.startswith("Région"):
        patient["ville"] = anonymiser_ville(ville)
        champs_rediges.append("ville")
    
    # Anonymiser l'âge → tranche
    age = patient.get("age", 0)
    if age > 0:
        patient["age_range"] = age_vers_tranche(age)
        patient["age"] = 0  # Supprimer l'âge précis
        champs_rediges.append("age")
    
    # Masquer les identifiants dans la timeline
    timeline = profil_anon.get("timeline", [])
    for event in timeline:
        evenement_text = event.get("evenement", "")
        # Supprimer les noms de médecins détectés
        if "Dr." in evenement_text or "Docteur" in evenement_text:
            import re
            evenement_text = re.sub(
                r'Dr\.?\s+[A-Za-zÀ-ÿ]+',
                'Médecin_Traitant',
                evenement_text
            )
            event["evenement"] = evenement_text
            if "medecin" not in champs_rediges:
                champs_rediges.append("medecin")
    
    profil_anon["patient"] = patient
    return profil_anon, champs_rediges


# ═══════════════════════════════════════════════════════════
# Fonction principale — Anonymisation
# ═══════════════════════════════════════════════════════════

def anonymiser_profil(profil_patient: dict) -> dict:
    """
    Module 2 — Privacy Shield.
    Anonymise un profil patient en préservant les données médicales.
    
    Processus :
    1. Anonymisation locale déterministe (rapide)
    2. Enrichissement IA via Claude (contextuel)
    3. Calcul du score de confidentialité
    4. Vérification conformité Loi 09-08
    
    Args:
        profil_patient: Profil brut issu du Module 1
        
    Returns:
        Dictionnaire avec données anonymisées, score et champs traités
    """
    try:
        # Étape 1 — Anonymisation locale (toujours exécutée)
        profil_anon, champs_locaux = _anonymiser_localement(profil_patient)
        logger.info(f"Anonymisation locale : {len(champs_locaux)} champs traités")
        
        # Étape 2 — Enrichissement IA (si API disponible)
        try:
            client = _get_client()
            if client is None:
                raise ValueError("Mode Démo / Clé manquante: passage direct à l'anonymisation statique (Loi 09-08).")
            
            logger.info("Appel à Claude claude-sonnet-4-20250514 — Module 2 : Anonymisation contextuelle")
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"Anonymise ce profil patient marocain :\n\n{json.dumps(profil_anon, ensure_ascii=False, indent=2)}"
                    }
                ]
            )
            
            contenu = response.content[0].text.strip()
            
            # Nettoyer le JSON si nécessaire
            if contenu.startswith("```"):
                contenu = contenu.split("\n", 1)[1]
                if contenu.endswith("```"):
                    contenu = contenu[:-3]
                contenu = contenu.strip()
            
            resultat_ia = json.loads(contenu)
            
            # Fusionner les résultats IA avec l'anonymisation locale
            anonymized_data = resultat_ia.get("anonymized_data", profil_anon)
            fields_from_ia = resultat_ia.get("fields_redacted", [])
            
            # Combiner les champs anonymisés
            tous_champs = list(set(champs_locaux + fields_from_ia))
            
            logger.info(f"Anonymisation IA réussie — {len(tous_champs)} champs au total")
            
        except Exception as e:
            logger.warning(f"Enrichissement IA indisponible : {e}. Utilisation locale seule.")
            anonymized_data = profil_anon
            tous_champs = champs_locaux
        
        # Étape 3 — Calcul du score de confidentialité
        score, champs_restants = calculer_score_confidentialite(anonymized_data)
        
        if champs_restants:
            logger.warning(f"Champs PHI résiduels détectés : {champs_restants}")
        
        # Étape 4 — Assemblage du résultat final
        resultat = {
            "anonymized_data": anonymized_data,
            "privacy_score": score,
            "fields_redacted": tous_champs,
            "conformite_loi_09_08": score >= 80,
            "conformite_rgpd": score >= 85,
        }
        
        logger.info(
            f"Privacy Shield — Score : {score}/100 | "
            f"Loi 09-08 : {'✓' if score >= 80 else '✗'} | "
            f"RGPD : {'✓' if score >= 85 else '✗'}"
        )
        
        return resultat
        
    except Exception as e:
        logger.error(f"Erreur Module 2 (anonymisation) : {e}")
        # Retourner l'anonymisation locale minimale
        profil_anon, champs = _anonymiser_localement(profil_patient)
        return {
            "anonymized_data": profil_anon,
            "privacy_score": 60,
            "fields_redacted": champs,
            "conformite_loi_09_08": False,
            "conformite_rgpd": False,
            "_error": str(e),
        }
