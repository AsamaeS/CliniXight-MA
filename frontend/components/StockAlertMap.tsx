import React from 'react'
import { Map, AlertTriangle, BatteryWarning, CheckCircle2 } from 'lucide-react'

// Simple map visualization for demo purposes
// In a real app, this would use leaflet or mapbox
export default function StockAlertMap({ alerts = [] }: { alerts: any[] }) {
  
  const regions = [
    { id: 'casa', name: 'Région Casablanca-Settat', x: 45, y: 35 },
    { id: 'rabat', name: 'Région Rabat-Salé-Kénitra', x: 50, y: 25 },
    { id: 'marrakech', name: 'Région Marrakech-Safi', x: 35, y: 50 },
    { id: 'agadir', name: 'Région Souss-Massa', x: 25, y: 65 },
    { id: 'fes', name: 'Région Fès-Meknès', x: 60, y: 30 },
  ]

  const getUrgencyColor = (regionName: string) => {
    const alert = alerts.find(a => a.region === regionName)
    if (!alert) return 'bg-emerald-500 shadow-emerald-500/50'
    if (alert.urgence === 'critique') return 'bg-red-500 shadow-red-500/50 animate-pulse'
    if (alert.urgence === 'modéré') return 'bg-amber-500 shadow-amber-500/50'
    return 'bg-emerald-500 shadow-emerald-500/50'
  }

  const getUrgencyIcon = (regionName: string) => {
    const alert = alerts.find(a => a.region === regionName)
    if (!alert) return <CheckCircle2 size={12} className="text-white" />
    if (alert.urgence === 'critique') return <AlertTriangle size={12} className="text-white" />
    return <BatteryWarning size={12} className="text-white" />
  }

  return (
    <div className="bg-slate-900 rounded-xl p-6 h-full relative overflow-hidden flex flex-col items-center justify-center min-h-[400px]">
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2 text-slate-300 pointer-events-none">
        <Map size={20} className="text-blue-400" />
        <span className="font-semibold tracking-wide text-sm">Vue Territoriale</span>
      </div>
      
      {/* Abstract Morocco Map Representation */}
      <div className="relative w-full max-w-sm aspect-[3/4] border-2 border-slate-800 rounded-3xl bg-slate-800/50 p-4">
        
        {regions.map((region) => {
          const alert = alerts.find(a => a.region === region.name)
          
          return (
            <div 
              key={region.id}
              className="absolute transform -translate-x-1/2 -translate-y-1/2 group cursor-pointer"
              style={{ left: `${region.x}%`, top: `${region.y}%` }}
              title={region.name}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shadow-lg transition-transform hover:scale-110 ${getUrgencyColor(region.name)}`}>
                {getUrgencyIcon(region.name)}
              </div>
              
              {/* Tooltip */}
              <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-max max-w-[200px] bg-white rounded-lg p-3 text-slate-800 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity z-20 pointer-events-none">
                <p className="font-bold text-xs border-b pb-1 mb-1">{region.name}</p>
                {alert ? (
                  <div className="text-xs">
                    <span className="text-red-500 font-semibold">{alert.medicament}</span>
                    <p className="mt-1 text-slate-600 leading-tight">{alert.message}</p>
                  </div>
                ) : (
                  <p className="text-xs text-emerald-600 font-semibold">Stock stable. Aucune alerte.</p>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
