import React from 'react'
import { AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react'

type AlertBadgeProps = {
  type?: 'interaction' | 'suivi_chronique' | 'incohérence' | string
  severite: 'haute' | 'moyenne' | 'faible' | 'critique'
  message: string
}

export default function AlertBadge({ type, severite, message }: AlertBadgeProps) {
  const isHigh = severite === 'haute' || severite === 'critique'
  const isMedium = severite === 'moyenne'

  const bgColor = isHigh ? 'bg-red-50 text-red-700 border-red-200' : 
                  isMedium ? 'bg-amber-50 text-amber-700 border-amber-200' : 
                  'bg-blue-50 text-blue-700 border-blue-200'
                  
  const iconColor = isHigh ? 'text-red-500' : isMedium ? 'text-amber-500' : 'text-blue-500'
  const Icon = isHigh ? AlertCircle : isMedium ? AlertTriangle : Info

  return (
    <div className={`flex items-start p-3 rounded-lg border ${bgColor} mb-3`}>
      <Icon className={`w-5 h-5 mr-3 mt-0.5 flex-shrink-0 ${iconColor}`} />
      <div>
        <div className="font-semibold text-sm capitalize">{type?.replace('_', ' ')} — Sévérité {severite}</div>
        <div className="text-sm mt-1 opacity-90">{message}</div>
      </div>
    </div>
  )
}
