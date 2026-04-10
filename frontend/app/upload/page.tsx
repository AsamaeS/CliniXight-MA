'use client'

import React, { useState } from 'react'
import { UploadCloud, CheckCircle2, ShieldAlert, FileText, Loader2, ArrowRight } from 'lucide-react'
import { uploadDocument, PatientProfile } from '@/lib/api'
import PrivacyScore from '@/components/PrivacyScore'
import AlertBadge from '@/components/AlertBadge'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ patient: PatientProfile, score: number, alerts: any[] } | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      // Appel réel vers FastAPI
      const response = await uploadDocument(file)
      setResult({
        patient: response.anonymized_profile,
        score: response.privacy_score,
        alerts: response.alertes_medicales,
      })
    } catch (err: any) {
      setError(err.message || "Erreur inconnue")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Numériser un Document</h1>
        <p className="text-slate-500 mt-1">Extraction IA et Anonymisation Loi 09-08</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Upload Zone */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 flex flex-col h-full">
          <form onSubmit={handleUpload} className="flex-1 flex flex-col justify-center">
            
            <label className="border-2 border-dashed border-slate-300 rounded-3xl p-12 text-center hover:bg-slate-50 transition-colors cursor-pointer group flex-1 flex items-center justify-center relative">
              <input type="file" accept=".pdf" className="hidden" onChange={(e) => setFile(e.target.files?.[0] || null)} />
              
              <div className="space-y-4">
                <div className="w-20 h-20 bg-blue-50 text-blue-500 rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                  <UploadCloud size={40} />
                </div>
                {file ? (
                  <div>
                    <h3 className="font-bold text-slate-800 text-lg">{file.name}</h3>
                    <p className="text-sm text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB — Prêt à traiter</p>
                  </div>
                ) : (
                  <div>
                    <h3 className="font-bold text-slate-800 text-lg">Glissez votre PDF ici</h3>
                    <p className="text-sm text-slate-500">Ordonnances, Comptes-Rendus (Max 10Mo)</p>
                  </div>
                )}
              </div>
            </label>

            <button 
              disabled={!file || loading}
              type="submit"
              className="mt-6 w-full py-4 rounded-xl font-bold tracking-wide transition-all bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/30 disabled:opacity-50 disabled:shadow-none disabled:cursor-not-allowed flex justify-center items-center gap-2"
            >
              {loading ? (
                <><Loader2 className="animate-spin" /> Traitement en cours (IA)...</>
              ) : (
                <><FileText /> Traiter le Document Sécurisé</>
              )}
            </button>
            <p className="text-center mt-4 text-xs font-semibold text-slate-400 flex justify-center items-center gap-1">
              <ShieldAlert size={14} /> Pipeline chiffré End-to-End
            </p>
          </form>
        </div>

        {/* Results Area */}
        <div className={`transition-all duration-700 ${result ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8 pointer-events-none'}`}>
          {result && (
            <div className="space-y-6">
              
              <div className="bg-emerald-50 text-emerald-800 p-4 rounded-xl border border-emerald-200 flex items-center gap-3">
                <CheckCircle2 size={24} className="text-emerald-500 shrink-0" />
                <p className="font-bold">Extraction terminée avec succès. Données anonymisées.</p>
              </div>

              <PrivacyScore score={result.score} />

              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 className="text-lg font-bold border-b pb-3 mb-4 text-slate-800">Résumé Structuré (Anonymisé)</h3>
                
                <div className="grid grid-cols-2 gap-4 text-sm mb-6 bg-slate-50 p-4 rounded-xl">
                  <div>
                    <div className="text-slate-500 font-medium text-xs uppercase tracking-wider">Identifiant</div>
                    <div className="font-bold text-slate-900">{result.patient.patient.nom}</div>
                  </div>
                  <div>
                     <div className="text-slate-500 font-medium text-xs uppercase tracking-wider">Tranche d'Âge</div>
                     <div className="font-bold text-slate-900">{result.patient.patient.age_range || result.patient.patient.age} ans</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <div className="text-xs font-bold uppercase text-slate-500 tracking-wider mb-2">Pathologies Extraites</div>
                    <div className="flex flex-wrap gap-2">
                       {result.patient.pathologies?.map((p: string, i: number) => (
                         <span key={i} className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded border border-indigo-100 font-medium text-sm">{p}</span>
                       ))}
                    </div>
                  </div>
                </div>
              </div>

              {result.alerts && result.alerts.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-sm font-bold uppercase text-slate-500 tracking-wider">Détection IA (Interactions)</h3>
                  {result.alerts.map((alert: any, i: number) => (
                    <AlertBadge key={i} type={alert.type} severite={alert.severite} message={alert.message} />
                  ))}
                </div>
              )}

            </div>
          )}
        </div>

      </div>
    </div>
  )
}
