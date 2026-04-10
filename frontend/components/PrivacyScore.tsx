import React from 'react'
import { ShieldCheck } from 'lucide-react'

export default function PrivacyScore({ score }: { score: number }) {
  const isExcellent = score >= 90
  const isGood = score >= 80 && score < 90
  
  const colorClass = isExcellent ? 'text-green-500' : isGood ? 'text-amber-500' : 'text-red-500'
  const bgClass = isExcellent ? 'bg-green-50 border-green-200' : isGood ? 'bg-amber-50 border-amber-200' : 'bg-red-50 border-red-200'
  const progressColor = isExcellent ? 'bg-green-500' : isGood ? 'bg-amber-500' : 'bg-red-500'

  return (
    <div className={`p-4 rounded-xl border ${bgClass}`}>
      <div className="flex justify-between items-center mb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className={colorClass} size={20} />
          <h3 className="font-bold text-slate-800 text-sm">Score de Confidentialité</h3>
        </div>
        <div className={`font-black text-xl ${colorClass}`}>
          {score}/100
        </div>
      </div>
      
      <div className="h-2 w-full bg-black/5 rounded-full overflow-hidden">
        <div 
          className={`h-full ${progressColor} transition-all duration-1000 ease-out`}
          style={{ width: `${score}%` }}
        />
      </div>
      
      <p className="text-xs text-slate-500 mt-3 flex items-center gap-1">
        ✓ Conforme Loi 09-08 (CNDP Maroc)
      </p>
    </div>
  )
}
