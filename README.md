# CliniVIEW MA+

![CliniVIEW MA+](https://via.placeholder.com/1200x600/1B4F8A/FFFFFF?text=CliniVIEW+MA%2B+-+HackEurope+2025)

**Plateforme intelligente de santé numérique adaptée au contexte marocain.**
*Built for HackEurope 2025*

**CliniVIEW MA+** transforme les dossiers médicaux traditionnels (ordonnances papier, PDF) en une base de connaissances structurée, confidentielle et connectée. La plateforme détecte les interactions médicamenteuses dangereuses, anonymise les données pour se conformer à la Loi 09-08 marocaine, et anticipe les ruptures de stock nationales (ex: insuline, tamiflu).

## 🏛️ Architecture Technique

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        CliniVIEW MA+ Platform                       │
│                                                                     │
│  ┌──────────────┐   ┌──────────────────┐   ┌───────────────────┐  │
│  │  Module 1    │   │   Module 2       │   │   Module 3        │  │
│  │  Extracteur  │──▶│   Privacy Shield │──▶│   Supply Alerts   │  │
│  │  (Claude AI) │   │   (Anonymiseur)  │   │   (Epidémiologie) │  │
│  └──────────────┘   └──────────────────┘   └───────────────────┘  │
│         │                    │                       │             │
│         ▼                    ▼                       ▼             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  FastAPI Backend (Python)                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                   │
│  ┌─────────────────────────────┴───────────────────────────────┐   │
│  │                  Next.js Frontend (React)                   │   │
│  └─────────────────────────────┬───────────────────────────────┘   │
│                                ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Supabase PostgreSQL                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## 🛠️ Stack Technique

- **Frontend** : Next.js 14, React, Tailwind CSS, shadcn/ui
- **Backend** : FastAPI, Python, LangGraph
- **IA Modèle** : Claude claude-sonnet-4-20250514 via API Anthropic
- **Base de Données** : Supabase (PostgreSQL)

## 🚀 Installation & Lancement

**Prérequis :**
- Node.js 18+
- Python 3.10+
- Un compte Anthropic (clé API)
- Un compte Supabase (optionnel en mode Mock)

### Étape 1 : Cloner et configurer
```bash
git clone <url-du-repo>
cd cliniview-ma
```
Copiez `.env.example` en `.env` dans le dossier `backend` et ajoutez vos clés (Anthropic, Supabase).

### Étape 2 : Lancer le Backend (FastAPI + LangGraph)
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Le backend tourne sur `http://localhost:8000`.

### Étape 3 : Lancer le Frontend (Next.js)
Dans un nouveau terminal :
```bash
cd frontend
npm install
npm run dev
```
L'application web est accessible sur `http://localhost:3000`.

## 📜 Conformité et Spécificités Maroc
La plateforme a été fine-tunée pour :
1. **Loi 09-08 (CNDP)** : Anonymisation des PII, conservation cryptée, droit à l'oubli géré via l'agent Privacy.
2. **Pathologies locales** : Détection des suivis métaboliques (HTA, Diabète type 2), Tuberculose pulmonaire.
3. **Couvertures locales** : CNSS, RAMED, AMO.

---
*Ce projet est une preuve de concept (PoC) développée dans le cadre de HackEurope.*
