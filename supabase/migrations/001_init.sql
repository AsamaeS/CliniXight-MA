-- Migration 001: Initialisation du schéma CliniVIEW MA+
-- Contexte : HackEurope 2025 / Système de santé marocain

-- Table principale des patients (anonymisés)
CREATE TABLE patients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_code VARCHAR(10) NOT NULL,     -- ex: Patient_A3F2
  region VARCHAR(100),                   -- ex: Région Casablanca-Settat
  age_range VARCHAR(20),                 -- ex: "45-50 ans"
  couverture VARCHAR(50),                -- ex: CNSS, RAMED
  pathologies JSONB,                     -- liste de chaînes
  medicaments JSONB,                     -- array d'objets (nom, dose, frequence)
  alertes JSONB,                         -- array d'objets (type, message, severite)
  timeline JSONB,                        -- array d'objets (date, evenement, type)
  privacy_score INTEGER,                 -- de 0 à 100
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index pour la recherche par région et couverture
CREATE INDEX idx_patients_region ON patients(region);
CREATE INDEX idx_patients_couverture ON patients(couverture);

-- Table des stocks de médicaments par région et pharmacie
CREATE TABLE medicaments_stock (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nom VARCHAR(200) NOT NULL,
  region VARCHAR(100) NOT NULL,
  pharmacie VARCHAR(200) NOT NULL,
  stock_actuel INTEGER NOT NULL DEFAULT 0,
  seuil_alerte INTEGER NOT NULL DEFAULT 50,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index sur les noms de médicaments et régions
CREATE INDEX idx_medicaments_nom ON medicaments_stock(nom);
CREATE INDEX idx_medicaments_region ON medicaments_stock(region);

-- Table des alertes épidémiologiques et ruptures de stock
CREATE TABLE supply_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region VARCHAR(100) NOT NULL,
  pathologie VARCHAR(200),
  medicament VARCHAR(200),
  urgence VARCHAR(20),                   -- critique, modéré, faible
  message TEXT,
  resolved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index sur le statut de résolution
CREATE INDEX idx_supply_alerts_resolved ON supply_alerts(resolved);

-- Jeu de données initial factice (Démonstration)
INSERT INTO medicaments_stock (nom, region, pharmacie, stock_actuel, seuil_alerte) VALUES
('Oseltamivir (Tamiflu)', 'Région Casablanca-Settat', 'Pharmacie Principale', 120, 200),
('Metformine 850mg', 'Région Casablanca-Settat', 'Pharmacie Al Amal', 500, 1000),
('Insuline Glargine', 'Région Marrakech-Safi', 'Pharmacie Koutoubia', 30, 100),
('Rifampicine', 'Région Fès-Meknès', 'Pharmacie Qaraouiyine', 40, 150),
('Losartan 50mg', 'Région Rabat-Salé-Kénitra', 'Pharmacie Capitale', 1200, 500);
