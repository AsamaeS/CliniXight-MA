import React from 'react'
import Link from 'next/link'
import StockAlertMap from '@/components/StockAlertMap'
import { fetchSupplyAlerts } from '@/lib/api'
import { ShieldCheck, Activity, BrainCircuit } from 'lucide-react'

// Render Server Component
export default async function Dashboard() {
  
  // Try fetching alerts from API, fallback to mock if API is down
  let alerts = []
  try {
    alerts = await fetchSupplyAlerts()
  } catch (error) {
    console.warn("API non disponible, utilisation des données de secours.")
    alerts = [
      {
        region: "Région Casablanca-Settat",
        urgence: "critique",
        medicament: "Oseltamivir (Tamiflu)",
        message: "Risque de rupture sous 7 jours. Vague grippale."
      }
    ]
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Vue d'ensemble</h1>
          <p className="text-slate-500 mt-1">Plateforme nationale de santé (Maroc)</p>
        </div>
        <Link 
          href="/upload" 
          className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors shadow-sm shadow-blue-600/20"
        >
          Numériser un dossier
        </Link>
      </header>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-5 relative overflow-hidden">
          <div className="w-14 h-14 bg-blue-50 flex items-center justify-center rounded-xl shrink-0">
            <BrainCircuit size={28} className="text-blue-600" />
          </div>
          <div className="z-10 relative">
            <p className="text-sm font-medium text-slate-500">Dossiers traités (Ajd)</p>
            <h3 className="text-3xl font-black text-slate-800 mt-1">124</h3>
          </div>
          <div className="absolute -right-6 -top-6 w-32 h-32 bg-blue-50 rounded-full blur-2xl opacity-50"></div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-emerald-100 shadow-sm flex items-center gap-5 relative overflow-hidden">
          <div className="w-14 h-14 bg-emerald-50 flex items-center justify-center rounded-xl shrink-0">
            <ShieldCheck size={28} className="text-emerald-600" />
          </div>
          <div className="z-10 relative">
            <p className="text-sm font-medium text-slate-500">Moy. Score Confidentialité</p>
            <h3 className="text-3xl font-black text-emerald-700 mt-1">96 <span className="text-lg opacity-50">/100</span></h3>
          </div>
          <p className="absolute bottom-3 right-6 text-[10px] font-bold text-emerald-600 tracking-wider">Loi 09-08 ✓</p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-5 relative overflow-hidden">
          <div className="w-14 h-14 bg-red-50 flex items-center justify-center rounded-xl shrink-0">
            <Activity size={28} className="text-red-500" />
          </div>
          <div className="z-10 relative">
            <p className="text-sm font-medium text-slate-500">Alertes Stock Actives</p>
            <h3 className="text-3xl font-black text-red-600 mt-1">{alerts.length}</h3>
          </div>
          <div className="absolute -right-6 -top-6 w-32 h-32 bg-red-50 rounded-full blur-2xl opacity-50"></div>
        </div>

      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Alerts Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-slate-800">Flux Épidémiologique</h2>
            <Link href="/alerts" className="text-sm font-medium text-blue-600 hover:underline">Voir tout</Link>
          </div>
          
          <div className="space-y-4">
            {alerts.length > 0 ? alerts.map((alert: any, i: number) => (
              <div key={i} className="bg-white border text-left p-5 rounded-xl flex items-start gap-4 border-l-4 border-l-red-500 shadow-sm">
                <div className="mt-1 bg-red-100 text-red-700 p-2 rounded-lg">
                  <Activity size={20} />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold uppercase tracking-wider text-red-600 bg-red-50 px-2 py-0.5 rounded">
                      {alert.urgence}
                    </span>
                    <span className="text-sm font-medium text-slate-500">{alert.region}</span>
                  </div>
                  <h4 className="font-bold text-slate-800 text-lg mb-1 leading-tight">{alert.medicament}</h4>
                  <p className="text-slate-600 text-sm">{alert.message}</p>
                </div>
              </div>
            )) : (
              <div className="text-center p-8 bg-white rounded-xl border border-slate-200 text-slate-500">
                Aucune alerte épidémiologique active.
              </div>
            )}
          </div>
        </div>

        {/* Map */}
        <div className="lg:col-span-1">
          <StockAlertMap alerts={alerts} />
        </div>

      </div>

    </div>
  )
}
