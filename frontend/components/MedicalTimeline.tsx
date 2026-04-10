import React from 'react'
import { Activity, Stethoscope, Syringe, FileText, AlertTriangle } from 'lucide-react'

type TimelineEvent = {
  date: string
  evenement: string
  type: string
}

export default function MedicalTimeline({ events }: { events: TimelineEvent[] }) {
  const getIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'consultation': return <Stethoscope size={16} className="text-blue-500" />
      case 'analyse': return <FileText size={16} className="text-purple-500" />
      case 'prescription': return <Activity size={16} className="text-green-500" />
      case 'vaccin': return <Syringe size={16} className="text-amber-500" />
      case 'urgence': return <AlertTriangle size={16} className="text-red-500" />
      default: return <Activity size={16} className="text-slate-400" />
    }
  }

  const getBgColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'consultation': return 'bg-blue-100 border-blue-200'
      case 'analyse': return 'bg-purple-100 border-purple-200'
      case 'prescription': return 'bg-green-100 border-green-200'
      case 'vaccin': return 'bg-amber-100 border-amber-200'
      case 'urgence': return 'bg-red-100 border-red-200'
      default: return 'bg-slate-100 border-slate-200'
    }
  }

  if (!events || events.length === 0) {
    return <div className="text-gray-500 italic text-sm p-4">Aucun antécédent répertorié.</div>
  }

  return (
    <div className="relative border-l-2 border-slate-200 ml-4 py-2">
      {events.map((event, idx) => (
        <div key={idx} className="mb-6 ml-6 relative">
          <div className={`absolute -left-9 mt-1 w-6 h-6 rounded-full border flex items-center justify-center bg-white ${getBgColor(event.type)}`}>
            {getIcon(event.type)}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="font-semibold text-sm text-slate-800">{event.date}</h4>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-2 py-0.5 bg-slate-50 rounded-full border border-slate-100">
                {event.type}
              </span>
            </div>
            <p className="text-sm text-slate-600 mt-1 leading-relaxed">
              {event.evenement}
            </p>
          </div>
        </div>
      ))}
    </div>
  )
}
