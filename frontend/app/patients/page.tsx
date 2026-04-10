import React from 'react'
import PatientCard from '@/components/PatientCard'
import { fetchPatients } from '@/lib/api'
import { Search, Filter } from 'lucide-react'

export default async function PatientsPage() {
  
  // Try fetching patients from API, fallback to mock if API is down
  let patients = []
  try {
    patients = await fetchPatients()
  } catch (error) {
    console.warn("API non disponible, utilisation des données de secours.")
    patients = [
      {
        id: "mock1", patient_code: "Patient_A3F2", region: "Région Casablanca-Settat", 
        age_range: "55-60 ans", couverture: "CNSS", pathologies: ["Diabète", "Hypertension"], privacy_score: 100
      },
      {
        id: "mock2", patient_code: "Patient_B9E1", region: "Région Marrakech-Safi", 
        age_range: "30-35 ans", couverture: "RAMED", pathologies: ["Tuberculose"], privacy_score: 85
      }
    ]
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Dossiers Cliniques</h1>
          <p className="text-slate-500 mt-1">Données anonymes (Loi 09-08)</p>
        </div>
      </header>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search size={20} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" />
          <input 
            type="text" 
            placeholder="Rechercher par Code Patient..." 
            className="w-full pl-12 pr-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
          />
        </div>
        <button className="bg-white border text-sm font-semibold border-slate-200 text-slate-700 px-6 py-3 rounded-xl hover:bg-slate-50 flexItems-center gap-2 shadow-sm transition-colors">
          <Filter size={18} /> Filtrer
        </button>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {patients.map((patient: any) => (
          <PatientCard key={patient.id} patient={patient} />
        ))}
      </div>

    </div>
  )
}
