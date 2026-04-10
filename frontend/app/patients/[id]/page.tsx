import React from 'react'
import Link from 'next/link'
import MedicalTimeline from '@/components/MedicalTimeline'
import AlertBadge from '@/components/AlertBadge'
import PrivacyScore from '@/components/PrivacyScore'
import { fetchPatientData } from '@/lib/api'
import { ArrowLeft, User, ShieldCheck, MapPin, Activity, Pill } from 'lucide-react'

export default async function PatientProfilePage({ params }: { params: { id: string } }) {
  
  let patientData = null
  try {
    patientData = await fetchPatientData(params.id)
  } catch (error) {
    console.warn("API patient failed, fallback to mock")
    patientData = {
      id: "mock",
      patient: {
        nom: "Patient_A3F2", age_range: "55-60 ans", sexe: "Masculin", 
        ville: "Région Casablanca-Settat", couverture: "CNSS"
      },
      pathologies: ["Diabète type 2", "Hypertension artérielle"],
      medicaments: [
        { nom: "Metformine", dose: "850mg", frequence: "2x/jour" },
        { nom: "Amlodipine", dose: "5mg", frequence: "1x/jour" }
      ],
      alertes: [
        { type: "interaction", message: "Risque IR avec AINS", severite: "moyenne" as const }
      ],
      timeline: [
        { date: "2024-06", evenement: "Consultation Diabétologie", type: "consultation" }
      ],
      privacy_score: 100
    }
  }

  if (!patientData) return <div>Introuvable</div>

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/patients" className="p-2 bg-slate-200 text-slate-600 rounded-full hover:bg-slate-300">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight flex items-center gap-3">
              {patientData.patient.nom}
            </h1>
            <p className="text-slate-500 mt-1 flex items-center gap-2">
              <ShieldCheck size={16} className="text-green-500" /> Profil Anonymisé • Loi 09-08
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column (Info) */}
        <div className="space-y-6">
          <PrivacyScore score={patientData.privacy_score || 90} />
          
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold border-b border-slate-100 pb-3 mb-4 text-slate-800">Identité & Démographie</h3>
            <ul className="space-y-4 text-sm">
              <li className="flex justify-between"><span className="text-slate-500 flex items-center gap-2"><User size={16}/> Sexe</span> <span className="font-semibold text-slate-800">{patientData.patient.sexe}</span></li>
              <li className="flex justify-between"><span className="text-slate-500 flex items-center gap-2"><Activity size={16}/> Tranche d'Âge</span> <span className="font-semibold text-slate-800">{patientData.patient.age_range || patientData.patient.age}</span></li>
              <li className="flex justify-between"><span className="text-slate-500 flex items-center gap-2"><MapPin size={16}/> Région</span> <span className="font-semibold text-slate-800 text-right">{patientData.patient.ville}</span></li>
              <li className="flex justify-between"><span className="text-slate-500 flex items-center gap-2"><ShieldCheck size={16}/> Couverture</span> <span className="font-semibold text-slate-800">{patientData.patient.couverture}</span></li>
            </ul>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold border-b border-slate-100 pb-3 mb-4 text-slate-800 flex items-center gap-2">
              <Pill size={18} className="text-blue-500" /> Traitement Actuel
            </h3>
            <div className="space-y-3">
              {patientData.medicaments.map((med: any, idx: number) => (
                <div key={idx} className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                  <div className="font-bold text-slate-800">{med.nom}</div>
                  <div className="text-xs text-slate-500 mt-1 flex justify-between">
                    <span>{med.dose}</span>
                    <span>{med.frequence}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column (Timeline & Alerts) */}
        <div className="lg:col-span-2 space-y-8">
          
          {patientData.alertes && patientData.alertes.length > 0 && (
            <div className="bg-red-50/50 p-6 rounded-2xl border border-red-100 shadow-sm">
              <h3 className="text-lg font-bold text-red-800 mb-4 tracking-tight">Détections IA (Risques Médicaux)</h3>
              <div className="space-y-3">
                {patientData.alertes.map((alerte: any, idx: number) => (
                  <AlertBadge 
                    key={idx}
                    type={alerte.type}
                    severite={alerte.severite}
                    message={alerte.message}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
              <h3 className="text-xl font-bold text-slate-800">Timeline Médicale</h3>
              <span className="text-xs font-semibold px-3 py-1 bg-slate-100 rounded-full text-slate-600">Reconstitué par IA</span>
            </div>
            <MedicalTimeline events={patientData.timeline} />
          </div>

        </div>

      </div>
    </div>
  )
}
