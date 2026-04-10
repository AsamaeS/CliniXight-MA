"""
CliniVIEW MA+ — Utilitaires d'anonymisation
Fonctions de support pour le Module 2 — Privacy Shield.
Conformité Loi 09-08 (Maroc) + RGPD (Europe).
"""

import hashlib
import re
from typing import Optional


def generer_code_patient(nom: str, seed: str = "") -> str:
    """
    Génère un code patient anonyme et déterministe.
    Le même nom produit toujours le même code (reproductible).
    
    Ex: "Rachid Amrani" → "Patient_A3F2"
    """
    texte = f"{nom.lower().strip()}{seed}"
    hash_hex = hashlib.sha256(texte.encode()).hexdigest()[:4].upper()
    return f"Patient_{hash_hex}"


def anonymiser_ville(ville: str) -> str:
    """
    Remplace la ville précise par sa région administrative.
    Mapping basé sur les 12 régions du Maroc (découpage 2015).
    """
    mapping_regions = {
        # Région Casablanca-Settat
        "casablanca": "Région Casablanca-Settat",
        "mohammedia": "Région Casablanca-Settat",
        "settat": "Région Casablanca-Settat",
        "berrechid": "Région Casablanca-Settat",
        "el jadida": "Région Casablanca-Settat",
        # Région Rabat-Salé-Kénitra
        "rabat": "Région Rabat-Salé-Kénitra",
        "salé": "Région Rabat-Salé-Kénitra",
        "kénitra": "Région Rabat-Salé-Kénitra",
        "témara": "Région Rabat-Salé-Kénitra",
        # Région Fès-Meknès
        "fès": "Région Fès-Meknès",
        "fes": "Région Fès-Meknès",
        "meknès": "Région Fès-Meknès",
        "meknes": "Région Fès-Meknès",
        "taza": "Région Fès-Meknès",
        # Région Marrakech-Safi
        "marrakech": "Région Marrakech-Safi",
        "safi": "Région Marrakech-Safi",
        "essaouira": "Région Marrakech-Safi",
        # Région Tanger-Tétouan-Al Hoceïma
        "tanger": "Région Tanger-Tétouan-Al Hoceïma",
        "tétouan": "Région Tanger-Tétouan-Al Hoceïma",
        "al hoceima": "Région Tanger-Tétouan-Al Hoceïma",
        # Région Souss-Massa
        "agadir": "Région Souss-Massa",
        "tiznit": "Région Souss-Massa",
        "taroudant": "Région Souss-Massa",
        # Région Oriental
        "oujda": "Région Oriental",
        "nador": "Région Oriental",
        "berkane": "Région Oriental",
        # Région Béni Mellal-Khénifra
        "béni mellal": "Région Béni Mellal-Khénifra",
        "khénifra": "Région Béni Mellal-Khénifra",
        "khouribga": "Région Béni Mellal-Khénifra",
        # Région Drâa-Tafilalet
        "errachidia": "Région Drâa-Tafilalet",
        "ouarzazate": "Région Drâa-Tafilalet",
        # Autres
        "laâyoune": "Région Laâyoune-Sakia El Hamra",
        "dakhla": "Région Dakhla-Oued Ed Dahab",
        "guelmim": "Région Guelmim-Oued Noun",
    }
    
    ville_norm = ville.lower().strip()
    return mapping_regions.get(ville_norm, "Région non identifiée")


def age_vers_tranche(age: int) -> str:
    """
    Convertit un âge précis en tranche d'âge pour anonymisation.
    Ex: 58 → "55-60 ans"
    """
    if age < 0:
        return "Âge inconnu"
    
    tranche_inf = (age // 5) * 5
    tranche_sup = tranche_inf + 5
    return f"{tranche_inf}-{tranche_sup} ans"


def masquer_identifiants(texte: str) -> str:
    """
    Détecte et masque les identifiants nationaux dans un texte libre.
    Gère : CNSS, CIN, RAMED, numéros de téléphone marocains.
    """
    # Numéros CNSS (9 chiffres)
    texte = re.sub(r'\b\d{9}\b', '[IDENTIFIANT_MASQUÉ]', texte)
    # CIN marocaine (lettres + chiffres, ex: BK123456)
    texte = re.sub(r'\b[A-Z]{1,2}\d{5,7}\b', '[IDENTIFIANT_MASQUÉ]', texte)
    # Numéros de téléphone marocains (06/07 + 8 chiffres)
    texte = re.sub(r'\b0[67]\d{8}\b', '[TEL_MASQUÉ]', texte)
    texte = re.sub(r'\b0[67]\d{2}[\s-]\d{2}[\s-]\d{2}[\s-]\d{2}\b', '[TEL_MASQUÉ]', texte)
    # Dates de naissance (format JJ/MM/AAAA)
    texte = re.sub(r'\b\d{2}/\d{2}/\d{4}\b', '[DATE_MASQUÉE]', texte)
    
    return texte


def calculer_score_confidentialite(donnees: dict) -> int:
    """
    Calcule le score de confidentialité (0 à 100).
    100 = aucune donnée personnelle identifiante détectable.
    -20 points par champ PHI encore présent.
    
    Conforme aux exigences de la Loi 09-08 (CNDP Maroc).
    """
    score = 100
    champs_sensibles = []
    
    patient = donnees.get("patient", {})
    
    # Vérification nom réel (pas un code anonyme)
    nom = patient.get("nom", "")
    if nom and not nom.startswith("Patient_"):
        score -= 20
        champs_sensibles.append("nom")
    
    # Vérification ville précise (pas une région)
    ville = patient.get("ville", "")
    if ville and not ville.startswith("Région"):
        score -= 20
        champs_sensibles.append("ville")
    
    # Vérification âge précis (pas une tranche)
    age = patient.get("age", 0)
    age_range = patient.get("age_range", "")
    if age and not age_range:
        score -= 20
        champs_sensibles.append("age_precis")
    
    # Vérification numéros d'identification
    texte_complet = str(donnees)
    if re.search(r'\b\d{9}\b', texte_complet):  # CNSS
        score -= 20
        champs_sensibles.append("numero_cnss")
    
    if re.search(r'\b0[67]\d{8}\b', texte_complet):  # Téléphone
        score -= 20
        champs_sensibles.append("telephone")
    
    return max(0, score), champs_sensibles
