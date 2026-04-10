import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import { LayoutDashboard, Users, Upload, BellRing } from 'lucide-react'
import '../app/globals.css' // Import correct tailwind css

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CliniVIEW MA+ | HackEurope',
  description: 'Plateforme de santé intelligente pour le Maroc',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr" className="bg-slate-50">
      <body className={inter.className}>
        <div className="flex h-screen overflow-hidden">
          
          {/* Sidebar */}
          <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col border-r border-slate-800 shadow-xl z-20">
            <div className="h-16 flex items-center px-6 border-b border-slate-800">
              <span className="text-blue-500 font-black text-xl mr-1">CliniVIEW</span>
              <span className="text-white font-bold text-xl">MA+</span>
            </div>
            
            <div className="p-4 flex-1">
              <p className="px-3 text-xs font-bold text-slate-500 tracking-wider mb-4 mt-2">PLATEFORME</p>
              <nav className="space-y-1">
                <Link href="/" className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 hover:text-white transition-colors">
                  <LayoutDashboard size={18} className="text-blue-400" /> Dashboard
                </Link>
                <Link href="/patients" className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 hover:text-white transition-colors">
                  <Users size={18} className="text-blue-400" /> Dossiers Patients
                </Link>
                <Link href="/upload" className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 hover:text-white transition-colors">
                  <Upload size={18} className="text-blue-400" /> Numérisation
                </Link>
                <Link href="/alerts" className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-slate-800 hover:text-white transition-colors">
                  <BellRing size={18} className="text-blue-400" /> Alertes Stock
                </Link>
              </nav>
            </div>
            
            <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
              CliniVIEW MA+ © 2026<br/>
              Plateforme Santé Maroc
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-y-auto bg-slate-50/50">
            {children}
          </main>
          
        </div>
      </body>
    </html>
  )
}
