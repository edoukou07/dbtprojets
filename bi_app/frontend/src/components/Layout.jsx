import { Outlet } from 'react-router-dom'
import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import Sidebar from './Sidebar'
import Header from './Header'

export default function Layout() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar Desktop */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar Mobile */}
      <div className={`
        fixed inset-y-0 left-0 z-50 lg:hidden transition-transform duration-300 ease-in-out
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <Sidebar />
      </div>

      {/* Main Content Area */}
      <div className="lg:ml-72 transition-all duration-300">
        {/* Mobile Header with Menu Button */}
        <div className="lg:hidden bg-gray-900 border-b border-gray-700 px-4 py-3 flex items-center justify-between sticky top-0 z-30">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="text-white p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            {isMobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">S</span>
            </div>
            <span className="text-white font-bold">SIGETI BI</span>
          </div>
          <div className="w-10"></div> {/* Spacer for alignment */}
        </div>

        {/* Header */}
        <Header />

        {/* Main Content */}
        <main className="p-6">
          <Outlet />
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12 py-6">
          <div className="px-6">
            <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
              <p className="text-sm text-gray-500">
                © 2025 SIGETI - Système Intégré de Gestion des Terres Industrielles
              </p>
              <div className="flex space-x-6 text-sm text-gray-500">
                <a href="#" className="hover:text-gray-900 transition-colors">Documentation</a>
                <a href="#" className="hover:text-gray-900 transition-colors">Support</a>
                <a href="#" className="hover:text-gray-900 transition-colors">Confidentialité</a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  )
}
