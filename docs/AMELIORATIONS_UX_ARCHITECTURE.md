# Plan d'Amélioration - UX/UI et Architecture

## 4. UX/UI Améliorations

### 4.1 Dark Mode

```jsx
// bi_app/frontend/src/contexts/ThemeContext.jsx
import { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light'
  })

  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light')
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => useContext(ThemeContext)
```

```js
// tailwind.config.js - Activer le dark mode
module.exports = {
  darkMode: 'class', // ou 'media' pour mode automatique
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // Couleurs personnalisées pour dark mode
        dark: {
          bg: '#0f172a',
          card: '#1e293b',
          border: '#334155',
          text: '#e2e8f0',
        }
      }
    },
  },
  plugins: [],
}
```

```jsx
// Composants avec support dark mode
export default function StatsCard({ title, value, subtitle, icon: Icon }) {
  return (
    <div className="bg-white dark:bg-dark-card rounded-xl shadow-sm border border-gray-200 dark:border-dark-border p-6 transition-colors">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </p>
          <p className="text-3xl font-bold text-gray-900 dark:text-dark-text mt-2">
            {value}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {subtitle}
          </p>
        </div>
        <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
          <Icon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
        </div>
      </div>
    </div>
  )
}

// Bouton de toggle dans la navbar
import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-card transition-colors"
      aria-label="Toggle theme"
    >
      {theme === 'light' ? (
        <Moon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
      ) : (
        <Sun className="w-5 h-5 text-gray-400" />
      )}
    </button>
  )
}
```

### 4.2 Skeleton Loaders

```jsx
// bi_app/frontend/src/components/skeletons/TableSkeleton.jsx
export function TableSkeleton({ rows = 5, columns = 6 }) {
  return (
    <div className="bg-white dark:bg-dark-card rounded-xl shadow-sm border border-gray-200 dark:border-dark-border overflow-hidden">
      {/* Header skeleton */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-800 dark:to-blue-900 p-4">
        <div className="grid" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {Array.from({ length: columns }).map((_, i) => (
            <div key={i} className="h-4 bg-blue-500 dark:bg-blue-700 rounded animate-pulse" />
          ))}
        </div>
      </div>

      {/* Rows skeleton */}
      <div className="divide-y divide-gray-200 dark:divide-dark-border">
        {Array.from({ length: rows }).map((_, rowIndex) => (
          <div key={rowIndex} className="p-4">
            <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <div
                  key={colIndex}
                  className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"
                  style={{ animationDelay: `${(rowIndex * columns + colIndex) * 0.05}s` }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// Card skeleton
export function CardSkeleton() {
  return (
    <div className="bg-white dark:bg-dark-card rounded-xl shadow-sm border border-gray-200 dark:border-dark-border p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1 space-y-3">
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3 animate-pulse" />
          <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded w-1/2 animate-pulse" />
          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded w-2/3 animate-pulse" />
        </div>
        <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" />
      </div>
    </div>
  )
}

// Chart skeleton
export function ChartSkeleton({ height = 300 }) {
  return (
    <div className="bg-white dark:bg-dark-card rounded-xl shadow-sm border border-gray-200 dark:border-dark-border p-6">
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-6 animate-pulse" />
      <div className="space-y-3" style={{ height }}>
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="flex items-end gap-2"
            style={{ height: `${100 / 5}%` }}
          >
            {Array.from({ length: 12 }).map((_, j) => (
              <div
                key={j}
                className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-t animate-pulse"
                style={{
                  height: `${Math.random() * 100}%`,
                  animationDelay: `${j * 0.1}s`
                }}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
```

```jsx
// Utilisation
import { TableSkeleton, CardSkeleton, ChartSkeleton } from '../components/skeletons'

export default function Occupation() {
  const { data, isLoading } = useQuery(['zones'], occupationAPI.getZones)

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
        <ChartSkeleton height={300} />
        <TableSkeleton rows={10} columns={6} />
      </div>
    )
  }

  return (
    // Contenu normal
  )
}
```

### 4.3 Raccourcis Clavier

```jsx
// bi_app/frontend/src/hooks/useKeyboardShortcuts.js
import { useEffect } from 'react'

export function useKeyboardShortcuts(shortcuts) {
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Ignorer si dans un input
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
        return
      }

      const key = event.key.toLowerCase()
      const combo = [
        event.ctrlKey && 'ctrl',
        event.shiftKey && 'shift',
        event.altKey && 'alt',
        key
      ].filter(Boolean).join('+')

      const shortcut = shortcuts[combo]
      if (shortcut) {
        event.preventDefault()
        shortcut()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [shortcuts])
}

// Hook pour shortcuts globaux
export function useGlobalShortcuts(navigate) {
  useKeyboardShortcuts({
    'ctrl+k': () => {
      // Ouvrir recherche globale
      document.getElementById('global-search')?.focus()
    },
    'ctrl+h': () => navigate('/'),
    'ctrl+o': () => navigate('/occupation'),
    'ctrl+c': () => navigate('/clients'),
    'ctrl+f': () => navigate('/financier'),
    'ctrl+shift+d': () => {
      // Toggle dark mode
      document.dispatchEvent(new Event('toggle-theme'))
    },
    'ctrl+shift+e': () => {
      // Trigger export
      document.dispatchEvent(new Event('trigger-export'))
    }
  })
}
```

```jsx
// bi_app/frontend/src/components/ShortcutsModal.jsx
import { useState, useEffect } from 'react'
import { Keyboard, X } from 'lucide-react'

export function ShortcutsModal() {
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === '?' && e.shiftKey) {
        setIsOpen(true)
      }
      if (e.key === 'Escape') {
        setIsOpen(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const shortcuts = [
    { category: 'Navigation', items: [
      { keys: ['Ctrl', 'H'], description: 'Accueil' },
      { keys: ['Ctrl', 'O'], description: 'Occupation' },
      { keys: ['Ctrl', 'C'], description: 'Clients' },
      { keys: ['Ctrl', 'F'], description: 'Financier' },
    ]},
    { category: 'Actions', items: [
      { keys: ['Ctrl', 'K'], description: 'Recherche globale' },
      { keys: ['Ctrl', 'Shift', 'E'], description: 'Exporter' },
      { keys: ['Ctrl', 'Shift', 'D'], description: 'Toggle Dark Mode' },
    ]},
    { category: 'Interface', items: [
      { keys: ['?'], description: 'Afficher les raccourcis' },
      { keys: ['Esc'], description: 'Fermer modal' },
    ]}
  ]

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 p-3 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-colors"
        title="Raccourcis clavier (Shift + ?)"
      >
        <Keyboard className="w-5 h-5" />
      </button>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-dark-card rounded-xl shadow-xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-dark-text flex items-center gap-2">
            <Keyboard className="w-6 h-6" />
            Raccourcis Clavier
          </h2>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-6">
          {shortcuts.map(category => (
            <div key={category.category}>
              <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase mb-3">
                {category.category}
              </h3>
              <div className="space-y-2">
                {category.items.map((shortcut, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
                  >
                    <span className="text-gray-700 dark:text-gray-300">
                      {shortcut.description}
                    </span>
                    <div className="flex items-center gap-1">
                      {shortcut.keys.map((key, i) => (
                        <span key={i} className="flex items-center gap-1">
                          <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded text-sm font-mono">
                            {key}
                          </kbd>
                          {i < shortcut.keys.length - 1 && (
                            <span className="text-gray-400">+</span>
                          )}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-dark-border text-center text-sm text-gray-500 dark:text-gray-400">
          Appuyez sur <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 border rounded">?</kbd> pour afficher/masquer ce panneau
        </div>
      </div>
    </div>
  )
}
```

### 4.4 Recherche Globale

```jsx
// bi_app/frontend/src/components/GlobalSearch.jsx
import { useState, useEffect, useRef } from 'react'
import { Search, X, TrendingUp, Users, FileText } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { searchAPI } from '../services/api'

export function GlobalSearch() {
  const [isOpen, setIsOpen] = useState(false)
  const [query, setQuery] = useState('')
  const inputRef = useRef(null)
  const navigate = useNavigate()

  const { data: results, isLoading } = useQuery({
    queryKey: ['global-search', query],
    queryFn: () => searchAPI.search(query),
    enabled: query.length >= 2
  })

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'k' && e.ctrlKey) {
        e.preventDefault()
        setIsOpen(true)
      }
      if (e.key === 'Escape') {
        setIsOpen(false)
        setQuery('')
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus()
    }
  }, [isOpen])

  const getIcon = (type) => {
    switch (type) {
      case 'zone': return <TrendingUp className="w-4 h-4" />
      case 'client': return <Users className="w-4 h-4" />
      case 'document': return <FileText className="w-4 h-4" />
      default: return <Search className="w-4 h-4" />
    }
  }

  const handleSelect = (item) => {
    setIsOpen(false)
    setQuery('')
    navigate(item.url)
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center pt-20 z-50">
      <div className="bg-white dark:bg-dark-card rounded-xl shadow-2xl w-full max-w-2xl mx-4">
        {/* Input */}
        <div className="flex items-center gap-3 p-4 border-b border-gray-200 dark:border-dark-border">
          <Search className="w-5 h-5 text-gray-400" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Rechercher zones, clients, documents... (Ctrl+K)"
            className="flex-1 bg-transparent outline-none text-gray-900 dark:text-dark-text"
          />
          {query && (
            <button
              onClick={() => setQuery('')}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          )}
        </div>

        {/* Résultats */}
        <div className="max-h-96 overflow-y-auto">
          {isLoading && (
            <div className="p-8 text-center text-gray-500">
              Recherche en cours...
            </div>
          )}

          {!isLoading && query.length >= 2 && results?.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              Aucun résultat trouvé pour "{query}"
            </div>
          )}

          {!isLoading && results && results.length > 0 && (
            <div className="divide-y divide-gray-200 dark:divide-dark-border">
              {results.map((item, index) => (
                <button
                  key={index}
                  onClick={() => handleSelect(item)}
                  className="w-full p-4 flex items-center gap-3 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-left"
                >
                  <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg text-blue-600 dark:text-blue-400">
                    {getIcon(item.type)}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-gray-900 dark:text-dark-text">
                      {item.title}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {item.description}
                    </div>
                  </div>
                  <div className="text-xs text-gray-400 uppercase">
                    {item.type}
                  </div>
                </button>
              ))}
            </div>
          )}

          {query.length < 2 && (
            <div className="p-8">
              <p className="text-center text-gray-500 mb-4">
                Suggestions rapides
              </p>
              <div className="space-y-2">
                {['Zones industrielles', 'Top clients', 'Factures en retard'].map((suggestion, i) => (
                  <button
                    key={i}
                    onClick={() => setQuery(suggestion)}
                    className="w-full p-2 text-left hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg text-gray-700 dark:text-gray-300 text-sm"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-dark-border flex items-center justify-between text-xs text-gray-500 rounded-b-xl">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-white dark:bg-gray-700 border rounded">↑</kbd>
              <kbd className="px-1.5 py-0.5 bg-white dark:bg-gray-700 border rounded">↓</kbd>
              pour naviguer
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-white dark:bg-gray-700 border rounded">Enter</kbd>
              pour sélectionner
            </span>
          </div>
          <span className="flex items-center gap-1">
            <kbd className="px-1.5 py-0.5 bg-white dark:bg-gray-700 border rounded">Esc</kbd>
            pour fermer
          </span>
        </div>
      </div>
    </div>
  )
}
```

---

## 5. Architecture Backend

### 5.1 Celery pour Tâches Asynchrones

```bash
pip install celery redis
```

```python
# bi_app/backend/sigeti_bi/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')

app = Celery('sigeti_bi')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configuration des tâches périodiques
app.conf.beat_schedule = {
    'refresh-cache-every-15-minutes': {
        'task': 'analytics.tasks.refresh_all_caches',
        'schedule': crontab(minute='*/15'),
    },
    'check-alerts-every-hour': {
        'task': 'analytics.tasks.check_all_alerts',
        'schedule': crontab(minute=0),
    },
    'generate-daily-report': {
        'task': 'analytics.tasks.generate_daily_report',
        'schedule': crontab(hour=7, minute=0),
    },
}

# bi_app/backend/sigeti_bi/__init__.py
from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app

__all__ = ('celery_app',)

# bi_app/backend/sigeti_bi/settings.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Abidjan'
```

```python
# bi_app/backend/analytics/tasks.py
from celery import shared_task
from django.core.cache import cache
from .models import MartOccupationZones, Alert
from .alerts import AlertManager
from .predictions import OccupationPredictor
import logging

logger = logging.getLogger(__name__)

@shared_task
def refresh_all_caches():
    """Rafraîchir tous les caches importants"""
    logger.info("Starting cache refresh...")
    
    try:
        # Rafraîchir les données d'occupation
        zones = MartOccupationZones.objects.all()
        cache.set('all_zones', list(zones.values()), 900)
        
        # Rafraîchir les statistiques
        stats = calculate_occupation_summary()
        cache.set('occupation_summary', stats, 900)
        
        logger.info("Cache refresh completed successfully")
        return {'status': 'success', 'zones_count': len(zones)}
    except Exception as e:
        logger.error(f"Cache refresh failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}

@shared_task
def check_all_alerts():
    """Vérifier toutes les zones pour les alertes"""
    logger.info("Checking alerts...")
    
    zones = MartOccupationZones.objects.all()
    alerts_created = 0
    
    for zone in zones:
        zone_data = {
            'nom_zone': zone.nom_zone,
            'taux_occupation_pct': zone.taux_occupation_pct
        }
        alerts = AlertManager.check_occupation_alerts(zone_data)
        alerts_created += len(alerts)
    
    logger.info(f"Alert check completed. {alerts_created} new alerts created.")
    return {'status': 'success', 'alerts_created': alerts_created}

@shared_task
def generate_daily_report():
    """Générer le rapport quotidien"""
    logger.info("Generating daily report...")
    
    from django.core.mail import send_mail
    from django.conf import settings
    
    # Collecter les données
    zones = MartOccupationZones.objects.all()
    alerts = Alert.objects.filter(status='active').count()
    
    report = f"""
    Rapport Quotidien SIGETI BI
    Date: {datetime.now().strftime('%d/%m/%Y')}
    
    Occupation:
    - Zones totales: {zones.count()}
    - Taux moyen: {zones.aggregate(Avg('taux_occupation_pct'))['taux_occupation_pct__avg']:.1f}%
    
    Alertes:
    - Alertes actives: {alerts}
    
    Consultez le tableau de bord pour plus de détails.
    """
    
    send_mail(
        'Rapport Quotidien SIGETI BI',
        report,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
    )
    
    logger.info("Daily report sent successfully")
    return {'status': 'success'}

@shared_task
def export_data_async(export_type, filters, user_email):
    """Export asynchrone de grandes quantités de données"""
    logger.info(f"Starting async export: {export_type}")
    
    try:
        # Générer l'export (Excel, CSV, etc.)
        file_path = generate_export(export_type, filters)
        
        # Envoyer par email
        from django.core.mail import EmailMessage
        
        email = EmailMessage(
            subject=f'Export {export_type} - SIGETI BI',
            body='Votre export est prêt. Veuillez trouver le fichier en pièce jointe.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        email.attach_file(file_path)
        email.send()
        
        logger.info(f"Export {export_type} completed and sent to {user_email}")
        return {'status': 'success', 'file': file_path}
    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        return {'status': 'error', 'message': str(e)}
```

```bash
# Démarrer Celery worker
cd bi_app/backend
celery -A sigeti_bi worker -l info

# Démarrer Celery beat (pour les tâches périodiques)
celery -A sigeti_bi beat -l info
```

---

Suite dans AMELIORATIONS_SECURITE_TESTS.md
