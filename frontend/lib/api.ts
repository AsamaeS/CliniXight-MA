// API Utilities pour interagir avec le backend FastAPI

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export type AlerteMedicale = {
  type: string
  message: string
  severite: 'haute' | 'moyenne' | 'faible'
}

export type PatientProfile = {
  id: string
  patient: {
    nom: string
    age: number
    sexe: string
    ville: string
    couverture: string
    age_range?: string
  }
  pathologies: string[]
  medicaments: { nom: string; dose: string; frequence: string }[]
  alertes: AlerteMedicale[]
  timeline: { date: string; evenement: string; type: string }[]
  privacy_score?: number
}

export const fetchPatients = async () => {
  const response = await fetch(`${API_BASE_URL}/api/patients`)
  if (!response.ok) throw new Error("Erreur de récupération des patients")
  return response.json()
}

export const fetchPatientData = async (id: string): Promise<PatientProfile> => {
  const response = await fetch(`${API_BASE_URL}/api/patients/${id}`)
  if (!response.ok) throw new Error("Erreur de récupération du patient")
  return response.json()
}

export const fetchSupplyAlerts = async () => {
  const response = await fetch(`${API_BASE_URL}/api/alerts/supply`)
  if (!response.ok) throw new Error("Erreur de récupération des alertes")
  return response.json()
}

export const uploadDocument = async (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  })
  
  if (!response.ok) throw new Error("Erreur lors de l'upload")
  return response.json()
}
