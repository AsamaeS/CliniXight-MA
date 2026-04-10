"""
CliniVIEW MA+ — Module 3 : Smart Supply Alerts
Agent d'analyse épidémiologique et de prédiction des ruptures de stock.
Analyse les données anonymisées agrégées par région pour le Maroc.
"""

import json
import logging
import os
from typing import Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)

_client = None

def _get_client() -> Optional[Anthropic]:
    global _client
    if _client is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key or "your_" in api_key:
            return None
        _client = Anthropic(api_key=api_key)
    return _client


# ═══════════════════════════════════════════════════════════
# Mapping pathologies → médicaments essentiels au Maroc
# ═══════════════════════════════════════════════════════════

PATHOLOGIE_MEDICAMENTS = {
    "grippe": ["Oseltamivir (Tamiflu)", "Paracétamol", "Amoxicilline"],
    "covid": ["Paracétamol", "Dexaméthasone", "Azithromycine"],
    "diabète": ["Metformine", "Insuline Glargine", "Glibenclamide", "Bandelettes glycémie"],
    "hypertension": ["Amlodipine", "Losartan", "Hydrochlorothiazide"],
    "tuberculose": ["Rifampicine", "Isoniazide", "Pyrazinamide", "Éthambutol"],
    "hépatite b": ["Ténofovir", "Lamivudine", "Entécavir"],
    "asthme": ["Salbutamol inhalateur", "Fluticasone inhalateur", "Budésonide"],
    "infection orl": ["Amoxicilline sirop", "Ibuprofène sirop", "Paracétamol sirop"],
}

# Stock de démo par région (simulé — en production viendrait de Supabase)
STOCK_DEMO = {
    "Région Casablanca-Settat": {
        "Oseltamivir (Tamiflu)": {"stock": 120, "seuil": 200},
        "Metformine": {"stock": 5000, "seuil": 2000},
        "Insuline Glargine": {"stock": 300, "seuil": 500},
        "Amoxicilline": {"stock": 800, "seuil": 400},
        "Paracétamol": {"stock": 10000, "seuil": 3000},
    },
    "Région Marrakech-Safi": {
        "Insuline Glargine": {"stock": 80, "seuil": 200},
        "Metformine": {"stock": 2000, "seuil": 1500},
        "Amlodipine": {"stock": 1200, "seuil": 800},
    },
    "Région Fès-Meknès": {
        "Rifampicine": {"stock": 150, "seuil": 100},
        "Isoniazide": {"stock": 200, "seuil": 100},
        "Amoxicilline sirop": {"stock": 50, "seuil": 200},
    },
    "Région Souss-Massa": {
        "Salbutamol inhalateur": {"stock": 100, "seuil": 150},
        "Amoxicilline sirop": {"stock": 80, "seuil": 300},
    },
    "Région Rabat-Salé-Kénitra": {
        "Ténofovir": {"stock": 500, "seuil": 200},
        "Paracétamol": {"stock": 8000, "seuil": 2000},
    },
}

# Pharmacies de démonstration par région
PHARMACIES_DEMO = {
    "Région Casablanca-Settat": [
        "Pharmacie Al Amal — Casablanca",
        "Pharmacie Ibn Sina — Mohammedia",
        "Pharmacie Centrale — Settat",
    ],
    "Région Marrakech-Safi": [
        "Pharmacie Koutoubia — Marrakech",
        "Pharmacie Atlas — Safi",
    ],
    "Région Fès-Meknès": [
        "Pharmacie Qaraouiyine — Fès",
        "Pharmacie Ismaïlia — Meknès",
    ],
    "Région Souss-Massa": [
        "Pharmacie Souss — Agadir",
        "Pharmacie Littoral — Tiznit",
    ],
    "Région Rabat-Salé-Kénitra": [
        "Pharmacie Capitale — Rabat",
        "Pharmacie Bouregreg — Salé",
    ],
}


# ═══════════════════════════════════════════════════════════
# Prompt système — Analyse épidémiologique
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT = """Tu es un expert en épidémiologie et gestion des stocks pharmaceutiques au Maroc.

CONTEXTE :
- Tu analyses les données agrégées et anonymisées de patients marocains
- Tu dois détecter les tendances épidémiologiques par région
- Tu dois anticiper les ruptures de stock de médicaments

TÂCHE :
Analyse les données patients anonymisées ci-dessous et génère un rapport d'alertes.

RÈGLES :
1. Si >15% des patients récents d'une région ont grippe/COVID → alerte épidémique
2. Si un médicament essentiel est en dessous du seuil de stock → alerte stock
3. Croise la tendance des pathologies avec les stocks pour anticiper

Réponds UNIQUEMENT en JSON avec ce format :
{
  "region": "nom de la région",
  "alerte_epidemique": true/false,
  "pathologie_dominante": "nom de la pathologie principale",
  "medicaments_a_risque": [
    {
      "nom": "nom du médicament",
      "stock_actuel": 120,
      "besoin_estime_7j": 450,
      "urgence": "critique | modéré | faible"
    }
  ],
  "recommandation": "texte de recommandation",
  "pharmacies_alertees": ["liste des pharmacies"]
}"""


# ═══════════════════════════════════════════════════════════
# Analyse locale — Sans IA (rapide)
# ═══════════════════════════════════════════════════════════

def _analyser_localement(patients_anonymises: list[dict]) -> list[dict]:
    """
    Analyse épidémiologique locale sans appel IA.
    Agrège les pathologies par région et détecte les tensions de stock.
    """
    alertes = []
    
    # Agréger les pathologies par région
    regions_data = {}
    for patient in patients_anonymises:
        patient_info = patient.get("patient", patient.get("anonymized_data", {}).get("patient", {}))
        region = patient_info.get("ville", "Région inconnue")
        if not region.startswith("Région"):
            region = f"Région {region}"
        
        pathologies = patient.get("pathologies",
            patient.get("anonymized_data", {}).get("pathologies", []))
        
        if region not in regions_data:
            regions_data[region] = {"total": 0, "pathologies": {}}
        
        regions_data[region]["total"] += 1
        
        for pathologie in pathologies:
            path_lower = pathologie.lower()
            for key in PATHOLOGIE_MEDICAMENTS.keys():
                if key in path_lower:
                    regions_data[region]["pathologies"][key] = \
                        regions_data[region]["pathologies"].get(key, 0) + 1
    
    # Générer les alertes par région
    for region, data in regions_data.items():
        total = data["total"]
        if total == 0:
            continue
        
        medicaments_risque = []
        alerte_epidemique = False
        pathologie_dominante = ""
        
        # Trouver la pathologie dominante
        if data["pathologies"]:
            pathologie_dominante = max(data["pathologies"], key=data["pathologies"].get)
            ratio = data["pathologies"][pathologie_dominante] / total
            
            # Seuil épidémique : >15%
            if ratio > 0.15 and pathologie_dominante in ["grippe", "covid"]:
                alerte_epidemique = True
        
        # Vérifier les stocks de la région
        stocks_region = STOCK_DEMO.get(region, {})
        for pathologie, count in data["pathologies"].items():
            meds = PATHOLOGIE_MEDICAMENTS.get(pathologie, [])
            for med in meds:
                stock_info = stocks_region.get(med)
                if stock_info:
                    besoin = max(count * 10, stock_info["seuil"])  # Estimation basique
                    if stock_info["stock"] < stock_info["seuil"]:
                        urgence = "critique" if stock_info["stock"] < stock_info["seuil"] * 0.3 else "modéré"
                        medicaments_risque.append({
                            "nom": med,
                            "stock_actuel": stock_info["stock"],
                            "besoin_estime_7j": besoin,
                            "urgence": urgence,
                        })
        
        # Créer l'alerte si pertinent
        if alerte_epidemique or medicaments_risque:
            recommandation = ""
            if alerte_epidemique:
                recommandation = f"Alerte épidémique {pathologie_dominante} dans {region}. Renforcement des stocks recommandé sous 48h."
            elif medicaments_risque:
                meds_critiques = [m["nom"] for m in medicaments_risque if m["urgence"] == "critique"]
                if meds_critiques:
                    recommandation = f"Commande urgente recommandée pour : {', '.join(meds_critiques)}"
                else:
                    recommandation = "Surveillance renforcée des stocks recommandée."
            
            alertes.append({
                "region": region,
                "alerte_epidemique": alerte_epidemique,
                "pathologie_dominante": pathologie_dominante.capitalize() if pathologie_dominante else "",
                "medicaments_a_risque": medicaments_risque,
                "recommandation": recommandation,
                "pharmacies_alertees": PHARMACIES_DEMO.get(region, []),
            })
    
    return alertes


# ═══════════════════════════════════════════════════════════
# Fonction principale — Analyse Supply
# ═══════════════════════════════════════════════════════════

def analyser_supply(patients_anonymises: list[dict]) -> list[dict]:
    """
    Module 3 — Smart Supply Alerts.
    Analyse les données agrégées pour détecter les tendances épidémiologiques
    et anticiper les ruptures de stock de médicaments au Maroc.
    
    Args:
        patients_anonymises: Liste des profils patients anonymisés
        
    Returns:
        Liste d'alertes de stock par région
    """
    try:
        # Étape 1 — Analyse locale (toujours exécutée)
        alertes_locales = _analyser_localement(patients_anonymises)
        logger.info(f"Analyse locale : {len(alertes_locales)} alertes générées")
        
        # Étape 2 — Enrichissement IA (optionnel)
        try:
            client = _get_client()
            if not client:
                logger.info("Mode Démo détecté : conservation des alertes épidémiologiques locales.")
                return alertes_locales
            
            # Préparer un résumé pour Claude (pas toutes les données brutes)
            resume = {
                "nombre_patients": len(patients_anonymises),
                "alertes_detectees": len(alertes_locales),
                "regions_concernees": [a["region"] for a in alertes_locales],
                "alertes": alertes_locales,
            }
            
            logger.info("Appel à Claude claude-sonnet-4-20250514 — Module 3 : Analyse épidémiologique")
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Analyse ces données épidémiologiques marocaines "
                            f"et enrichis les alertes :\n\n"
                            f"{json.dumps(resume, ensure_ascii=False, indent=2)}"
                        )
                    }
                ]
            )
            
            contenu = response.content[0].text.strip()
            if contenu.startswith("```"):
                contenu = contenu.split("\n", 1)[1]
                if contenu.endswith("```"):
                    contenu = contenu[:-3]
                contenu = contenu.strip()
            
            alerte_ia = json.loads(contenu)
            
            # Si Claude retourne une seule alerte, en faire une liste
            if isinstance(alerte_ia, dict):
                alerte_ia = [alerte_ia]
            
            # Fusionner alertes locales et IA
            regions_locales = {a["region"] for a in alertes_locales}
            for alerte in alerte_ia:
                if alerte.get("region") not in regions_locales:
                    alertes_locales.append(alerte)
            
            logger.info(f"Enrichissement IA réussi — Total alertes : {len(alertes_locales)}")
            
        except Exception as e:
            logger.warning(f"Enrichissement IA supply indisponible : {e}")
        
        return alertes_locales
        
    except Exception as e:
        logger.error(f"Erreur Module 3 (supply) : {e}")
        return _alertes_demo()


def _alertes_demo() -> list[dict]:
    """Alertes de démonstration si l'analyse échoue."""
    return [
        {
            "region": "Région Casablanca-Settat",
            "alerte_epidemique": True,
            "pathologie_dominante": "Grippe saisonnière",
            "medicaments_a_risque": [
                {
                    "nom": "Oseltamivir (Tamiflu)",
                    "stock_actuel": 120,
                    "besoin_estime_7j": 450,
                    "urgence": "critique",
                }
            ],
            "recommandation": "Commande urgente recommandée sous 48h pour Oseltamivir.",
            "pharmacies_alertees": [
                "Pharmacie Al Amal — Casablanca",
                "Pharmacie Ibn Sina — Mohammedia",
            ],
        },
        {
            "region": "Région Marrakech-Safi",
            "alerte_epidemique": False,
            "pathologie_dominante": "Diabète T2 décompensé",
            "medicaments_a_risque": [
                {
                    "nom": "Insuline Glargine",
                    "stock_actuel": 80,
                    "besoin_estime_7j": 200,
                    "urgence": "critique",
                }
            ],
            "recommandation": "Stock insuline critique. Coordination avec grossistes recommandée.",
            "pharmacies_alertees": [
                "Pharmacie Koutoubia — Marrakech",
            ],
        },
    ]
