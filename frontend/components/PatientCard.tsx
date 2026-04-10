import React from 'react'
import Link from 'next/link'
import { ShieldAlert, User, MapPin, Pill, Activity } from 'lucide-react'
import { PatientListItem } from '@/lib/api' // using any or creating type

export default function PatientCard({ patient }: { patient: any }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="p-5 border-b border-slate-100 flex justify-between items-start">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-500">
            <User size={20} />
          </div>
          <div>
            <h3 className="font-bold text-slate-900">{patient.patient_code}</h3>
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-green-100 text-green-700 inline-flex items-center gap-1 mt-1">
              <ShieldAlert size={12} /> Loi 09-08 ✓
            </span>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-sm font-semibold text-slate-700">{patient.age_range}</div>
          <div className="text-xs text-slate-500">{patient.couverture || 'Aucune'}</div>
        </div>
      </div>
      
      <div className="p-5 space-y-3">
        <div className="flex items-start gap-2 text-sm text-slate-600">
          <MapPin size={16} className="text-slate-400 mt-0.5 shrink-0" />
          <span>{patient.region}</span>
        </div>
        
        <div className="flex items-start gap-2 text-sm text-slate-600">
          <Activity size={16} className="text-indigo-400 mt-0.5 shrink-0" />
          <div className="flex flex-wrap gap-1">
            {patient.pathologies?.map((patho: string, idx: number) => (
              <span key={idx} className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded text-xs border border-indigo-100">
                {patho}
              </span>
            ))}
          </div>
        </div>
      </div>
      
      <div className="bg-slate-50 p-4 border-t border-slate-100 flex justify-end">
        <Link 
          href={`/patients/${patient.id}`}
          className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors"
        >
          Voir le dossier clinique →
        </Link>
      </div>
    </div>
  )
}
