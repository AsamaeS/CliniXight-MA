import React from 'react'
import StockAlertMap from '@/components/StockAlertMap'
import { fetchSupplyAlerts } from '@/lib/api'
import { AlertCircle, FileWarning } from 'lucide-react'

export default async function AlertsPage() {
  
  let alerts = []
  try {
    alerts = await fetchSupplyAlerts()
  } catch (error) {
    alerts = [
      {
        region: "Région Casablanca-Settat",
        urgence: "critique", pathologie: "Grippe", medicament: "Oseltamivir", message: "Critique sous 7 jours"
      }
    ]
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 h-full flex flex-col">
      
      <header className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Smart Supply Alerts</h1>
          <p className="text-slate-500 mt-1">Surveillance épidémiologique et ruptures de stock</p>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 flex-1">
        
        {/* Table/List */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
          <div className="p-5 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
            <h3 className="font-bold tracking-tight text-slate-800">Alertes Actives</h3>
            <span className="bg-red-100 text-red-700 font-bold px-3 py-1 rounded-full text-xs">
              {alerts.length} en cours
            </span>
          </div>
          <div className="p-5 space-y-4 overflow-y-auto max-h-[600px]">
            {alerts.length === 0 ? (
               <div className="text-center p-8 text-slate-500">Aucune alerte à afficher.</div>
            ) : alerts.map((alert: any, i: number) => (
              <div key={i} className={`p-4 rounded-xl border-l-4 ${alert.urgence === 'critique' ? 'border-red-500 bg-red-50 text-red-900 border' : 'border-amber-500 bg-amber-50 text-amber-900 border'}`}>
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-lg">{alert.medicament}</h4>
                  <span className={`text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded ${alert.urgence === 'critique' ? 'bg-red-200 text-red-800' : 'bg-amber-200 text-amber-800'}`}>
                    {alert.urgence}
                  </span>
                </div>
                <div className="text-sm font-semibold opacity-80 mb-1">{alert.region}</div>
                <div className="text-sm opacity-90 leading-tight">
                  <FileWarning size={14} className="inline mr-1 -mt-0.5" />
                  {alert.message}
                </div>
                
                <div className="mt-4 pt-4 border-t border-black/10 text-right">
                  <button className="text-sm font-bold opacity-80 hover:opacity-100 transition-opacity">
                    Notifier Pharmacies →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Map */}
        <div className="rounded-2xl shadow-sm overflow-hidden h-full min-h-[500px]">
          <StockAlertMap alerts={alerts} />
        </div>

      </div>

    </div>
  )
}
