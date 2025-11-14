# Plan d'Amélioration - Visualisations de Données

## 2. Visualisations Avancées avec Recharts

### 2.1 Installation et Configuration

```bash
cd bi_app/frontend
npm install recharts
```

### 2.2 Composant Chart Réutilisable

```jsx
// bi_app/frontend/src/components/charts/BaseChart.jsx
import { ResponsiveContainer } from 'recharts'

export function ChartContainer({ 
  children, 
  height = 300, 
  className = '',
  loading = false 
}) {
  if (loading) {
    return (
      <div className={`w-full animate-pulse ${className}`} style={{ height }}>
        <div className="bg-gray-200 rounded-lg h-full"></div>
      </div>
    )
  }

  return (
    <div className={className}>
      <ResponsiveContainer width="100%" height={height}>
        {children}
      </ResponsiveContainer>
    </div>
  )
}
```

### 2.3 Graphique d'Évolution Temporelle

```jsx
// bi_app/frontend/src/components/charts/TrendChart.jsx
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  Area,
  ComposedChart
} from 'recharts'
import { ChartContainer } from './BaseChart'

export default function TrendChart({ data, metrics, title }) {
  // data format: [{ date: '2024-01', occupation: 75, disponibilite: 25 }, ...]
  
  const colors = {
    occupation: '#3b82f6', // blue
    disponibilite: '#10b981', // green
    factures: '#f59e0b', // orange
    paiements: '#8b5cf6', // purple
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      
      <ChartContainer height={350}>
        <ComposedChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <defs>
            {metrics.map(metric => (
              <linearGradient key={metric.key} id={`gradient-${metric.key}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors[metric.key]} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={colors[metric.key]} stopOpacity={0}/>
              </linearGradient>
            ))}
          </defs>
          
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          
          <XAxis 
            dataKey="date" 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          
          <YAxis 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          
          <Tooltip 
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}
            formatter={(value, name) => [
              `${value}${metrics.find(m => m.key === name)?.unit || ''}`,
              metrics.find(m => m.key === name)?.label || name
            ]}
          />
          
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            formatter={(value) => metrics.find(m => m.key === value)?.label || value}
          />
          
          {metrics.map((metric, index) => (
            <React.Fragment key={metric.key}>
              {metric.type === 'area' ? (
                <Area
                  type="monotone"
                  dataKey={metric.key}
                  stroke={colors[metric.key]}
                  strokeWidth={2}
                  fill={`url(#gradient-${metric.key})`}
                />
              ) : (
                <Line
                  type="monotone"
                  dataKey={metric.key}
                  stroke={colors[metric.key]}
                  strokeWidth={2}
                  dot={{ r: 4, fill: colors[metric.key] }}
                  activeDot={{ r: 6 }}
                />
              )}
            </React.Fragment>
          ))}
        </ComposedChart>
      </ChartContainer>
    </div>
  )
}
```

```jsx
// Utilisation
export default function OccupationTrends() {
  const { data } = useQuery({
    queryKey: ['occupation-trends'],
    queryFn: () => occupationAPI.getTrends({ period: '12months' })
  })

  const metrics = [
    { key: 'taux_occupation', label: 'Taux d\'Occupation', unit: '%', type: 'area' },
    { key: 'lots_attribues', label: 'Lots Attribués', unit: '', type: 'line' },
    { key: 'lots_disponibles', label: 'Lots Disponibles', unit: '', type: 'line' },
  ]

  return (
    <TrendChart 
      data={data?.trends || []}
      metrics={metrics}
      title="Évolution de l'Occupation (12 derniers mois)"
    />
  )
}
```

### 2.4 Heatmap - Calendrier d'Occupation

```jsx
// bi_app/frontend/src/components/charts/HeatmapCalendar.jsx
import { useState } from 'react'
import { Tooltip } from 'recharts'

export default function HeatmapCalendar({ data, year }) {
  // data format: [{ date: '2024-01-15', value: 75 }, ...]
  const [hoveredCell, setHoveredCell] = useState(null)

  const months = [
    'Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
    'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'
  ]

  const getColorForValue = (value) => {
    if (value >= 90) return 'bg-red-600'
    if (value >= 70) return 'bg-orange-500'
    if (value >= 50) return 'bg-yellow-400'
    if (value >= 30) return 'bg-green-400'
    return 'bg-blue-300'
  }

  const getIntensity = (value) => {
    // Retourne l'opacité basée sur la valeur
    return Math.min(100, Math.max(10, value)) / 100
  }

  // Grouper les données par mois
  const dataByMonth = data.reduce((acc, item) => {
    const date = new Date(item.date)
    const month = date.getMonth()
    const day = date.getDate()
    
    if (!acc[month]) acc[month] = {}
    acc[month][day] = item.value
    
    return acc
  }, {})

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Calendrier d'Occupation {year}
        </h3>
        
        {/* Légende */}
        <div className="flex items-center gap-4 text-xs text-gray-600">
          <span>Moins occupé</span>
          <div className="flex gap-1">
            <div className="w-4 h-4 bg-blue-300 rounded"></div>
            <div className="w-4 h-4 bg-green-400 rounded"></div>
            <div className="w-4 h-4 bg-yellow-400 rounded"></div>
            <div className="w-4 h-4 bg-orange-500 rounded"></div>
            <div className="w-4 h-4 bg-red-600 rounded"></div>
          </div>
          <span>Plus occupé</span>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-2">
        {months.map((month, monthIndex) => (
          <div key={monthIndex} className="space-y-1">
            <div className="text-xs font-medium text-gray-600 text-center mb-2">
              {month}
            </div>
            
            {/* Grille des jours du mois */}
            <div className="grid grid-rows-5 gap-1">
              {Array.from({ length: 31 }, (_, i) => i + 1).map(day => {
                const value = dataByMonth[monthIndex]?.[day]
                const hasData = value !== undefined

                return (
                  <div
                    key={day}
                    className={`
                      w-3 h-3 rounded-sm cursor-pointer transition-all
                      ${hasData ? getColorForValue(value) : 'bg-gray-100'}
                    `}
                    style={{ opacity: hasData ? getIntensity(value) : 0.3 }}
                    onMouseEnter={() => hasData && setHoveredCell({ month, day, value })}
                    onMouseLeave={() => setHoveredCell(null)}
                    title={hasData ? `${day} ${month}: ${value}%` : ''}
                  />
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Tooltip personnalisé */}
      {hoveredCell && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg text-sm">
          <span className="font-medium">{hoveredCell.day} {hoveredCell.month} {year}</span>
          <span className="ml-2 text-gray-600">
            Taux d'occupation: <span className="font-semibold">{hoveredCell.value}%</span>
          </span>
        </div>
      )}
    </div>
  )
}
```

### 2.5 Treemap - Répartition Hiérarchique

```jsx
// bi_app/frontend/src/components/charts/OccupationTreemap.jsx
import { Treemap, ResponsiveContainer, Tooltip } from 'recharts'

export default function OccupationTreemap({ data }) {
  // data format: [
  //   { name: 'Zone A', size: 150000, occupation: 85, children: [...] },
  //   ...
  // ]

  const COLORS = {
    low: '#3b82f6',    // blue
    medium: '#10b981', // green
    high: '#f59e0b',   // orange
    critical: '#ef4444' // red
  }

  const getColorByOccupation = (occupation) => {
    if (occupation >= 90) return COLORS.critical
    if (occupation >= 70) return COLORS.high
    if (occupation >= 50) return COLORS.medium
    return COLORS.low
  }

  const CustomizedContent = (props) => {
    const { x, y, width, height, name, occupation, size } = props

    if (width < 50 || height < 50) return null

    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          style={{
            fill: getColorByOccupation(occupation),
            stroke: '#fff',
            strokeWidth: 2,
            strokeOpacity: 1,
          }}
        />
        
        {width > 100 && height > 60 && (
          <>
            <text
              x={x + width / 2}
              y={y + height / 2 - 10}
              textAnchor="middle"
              fill="#fff"
              fontSize={14}
              fontWeight="bold"
            >
              {name}
            </text>
            <text
              x={x + width / 2}
              y={y + height / 2 + 10}
              textAnchor="middle"
              fill="#fff"
              fontSize={12}
            >
              {occupation}%
            </text>
            <text
              x={x + width / 2}
              y={y + height / 2 + 25}
              textAnchor="middle"
              fill="rgba(255,255,255,0.8)"
              fontSize={10}
            >
              {(size / 1000).toFixed(0)}k m²
            </text>
          </>
        )}
      </g>
    )
  }

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null

    const data = payload[0].payload

    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border">
        <p className="font-semibold text-gray-900">{data.name}</p>
        <p className="text-sm text-gray-600 mt-1">
          Occupation: <span className="font-medium">{data.occupation}%</span>
        </p>
        <p className="text-sm text-gray-600">
          Superficie: <span className="font-medium">{data.size.toLocaleString()} m²</span>
        </p>
        {data.lots && (
          <p className="text-sm text-gray-600">
            Lots: <span className="font-medium">{data.lots}</span>
          </p>
        )}
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Répartition des Zones par Superficie
      </h3>

      <ResponsiveContainer width="100%" height={400}>
        <Treemap
          data={data}
          dataKey="size"
          stroke="#fff"
          fill="#8884d8"
          content={<CustomizedContent />}
        >
          <Tooltip content={<CustomTooltip />} />
        </Treemap>
      </ResponsiveContainer>

      {/* Légende */}
      <div className="flex items-center justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: COLORS.low }}></div>
          <span className="text-gray-600">&lt; 50%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: COLORS.medium }}></div>
          <span className="text-gray-600">50-69%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: COLORS.high }}></div>
          <span className="text-gray-600">70-89%</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded" style={{ backgroundColor: COLORS.critical }}></div>
          <span className="text-gray-600">≥ 90%</span>
        </div>
      </div>
    </div>
  )
}
```

### 2.6 Graphique en Barres Comparatif

```jsx
// bi_app/frontend/src/components/charts/ComparativeBarChart.jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell } from 'recharts'
import { ChartContainer } from './BaseChart'

export default function ComparativeBarChart({ 
  data, 
  title,
  xKey = 'name',
  bars = [],
  height = 300
}) {
  // bars format: [
  //   { key: 'current', label: 'Actuel', color: '#3b82f6' },
  //   { key: 'previous', label: 'Précédent', color: '#94a3b8' }
  // ]

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload) return null

    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border">
        <p className="font-semibold text-gray-900 mb-2">{payload[0]?.payload[xKey]}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center justify-between gap-4 text-sm">
            <span className="text-gray-600">{entry.name}:</span>
            <span className="font-medium" style={{ color: entry.color }}>
              {entry.value.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>

      <ChartContainer height={height}>
        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis 
            dataKey={xKey} 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
          />
          
          {bars.map(bar => (
            <Bar 
              key={bar.key}
              dataKey={bar.key} 
              name={bar.label}
              fill={bar.color}
              radius={[8, 8, 0, 0]}
            />
          ))}
        </BarChart>
      </ChartContainer>
    </div>
  )
}
```

```jsx
// Utilisation
export default function ZoneComparison() {
  const { data } = useQuery({
    queryKey: ['zone-comparison'],
    queryFn: occupationAPI.getComparison
  })

  const bars = [
    { key: 'attribues_2024', label: '2024', color: '#3b82f6' },
    { key: 'attribues_2023', label: '2023', color: '#94a3b8' }
  ]

  return (
    <ComparativeBarChart
      data={data?.zones || []}
      title="Comparaison Lots Attribués 2024 vs 2023"
      xKey="nom_zone"
      bars={bars}
      height={350}
    />
  )
}
```

### 2.7 Graphique Radar - Profil Multi-critères

```jsx
// bi_app/frontend/src/components/charts/RadarProfile.jsx
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Tooltip, Legend } from 'recharts'
import { ChartContainer } from './BaseChart'

export default function RadarProfile({ zones, title = "Profil des Zones" }) {
  // Normaliser les données pour le radar (échelle 0-100)
  const normalizeData = (zones) => {
    return [
      { 
        metric: 'Occupation',
        ...zones.reduce((acc, zone) => ({
          ...acc,
          [zone.name]: zone.taux_occupation_pct
        }), {})
      },
      { 
        metric: 'Disponibilité',
        ...zones.reduce((acc, zone) => ({
          ...acc,
          [zone.name]: 100 - zone.taux_occupation_pct
        }), {})
      },
      { 
        metric: 'Attractivité',
        ...zones.reduce((acc, zone) => ({
          ...acc,
          [zone.name]: (zone.demandes / zone.lots_total) * 100
        }), {})
      },
      { 
        metric: 'Performance',
        ...zones.reduce((acc, zone) => ({
          ...acc,
          [zone.name]: zone.taux_paiement
        }), {})
      },
      { 
        metric: 'Développement',
        ...zones.reduce((acc, zone) => ({
          ...acc,
          [zone.name]: (zone.lots_attribues / zone.lots_total) * 100
        }), {})
      },
    ]
  }

  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444']

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>

      <ChartContainer height={400}>
        <RadarChart data={normalizeData(zones)}>
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis 
            dataKey="metric" 
            style={{ fontSize: '12px', fill: '#6b7280' }}
          />
          <PolarRadiusAxis 
            angle={90} 
            domain={[0, 100]}
            style={{ fontSize: '10px', fill: '#9ca3af' }}
          />
          
          {zones.map((zone, index) => (
            <Radar
              key={zone.name}
              name={zone.name}
              dataKey={zone.name}
              stroke={colors[index % colors.length]}
              fill={colors[index % colors.length]}
              fillOpacity={0.3}
              strokeWidth={2}
            />
          ))}
          
          <Tooltip 
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #e5e7eb',
              borderRadius: '8px'
            }}
          />
          <Legend wrapperStyle={{ paddingTop: '20px' }} />
        </RadarChart>
      </ChartContainer>
    </div>
  )
}
```

### 2.8 Dashboard avec Graphiques Combinés

```jsx
// bi_app/frontend/src/pages/Analytics.jsx
import TrendChart from '../components/charts/TrendChart'
import HeatmapCalendar from '../components/charts/HeatmapCalendar'
import OccupationTreemap from '../components/charts/OccupationTreemap'
import ComparativeBarChart from '../components/charts/ComparativeBarChart'
import RadarProfile from '../components/charts/RadarProfile'

export default function Analytics() {
  const { data: trends } = useQuery(['occupation-trends'], occupationAPI.getTrends)
  const { data: heatmap } = useQuery(['occupation-heatmap'], occupationAPI.getHeatmap)
  const { data: zones } = useQuery(['zones-treemap'], occupationAPI.getZonesTreemap)

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Analytique Avancée</h1>

      {/* Section 1: Évolutions temporelles */}
      <div className="grid grid-cols-1 gap-6">
        <TrendChart 
          data={trends?.monthly || []}
          metrics={[
            { key: 'occupation', label: 'Occupation', unit: '%', type: 'area' },
            { key: 'disponibilite', label: 'Disponibilité', unit: '%', type: 'line' }
          ]}
          title="Évolution Mensuelle"
        />
      </div>

      {/* Section 2: Calendrier + Treemap */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <HeatmapCalendar data={heatmap?.daily || []} year={2024} />
        <OccupationTreemap data={zones?.hierarchy || []} />
      </div>

      {/* Section 3: Comparaisons */}
      <div className="grid grid-cols-1 gap-6">
        <ComparativeBarChart
          data={zones?.top10 || []}
          title="Top 10 Zones - Évolution Annuelle"
          bars={[
            { key: 'current', label: '2024', color: '#3b82f6' },
            { key: 'previous', label: '2023', color: '#94a3b8' }
          ]}
        />
      </div>

      {/* Section 4: Profils radar */}
      <div className="grid grid-cols-1 gap-6">
        <RadarProfile 
          zones={zones?.top5 || []}
          title="Profil Comparatif - Top 5 Zones"
        />
      </div>
    </div>
  )
}
```

---

**Suite dans le prochain fichier: AMELIORATIONS_FONCTIONNALITES.md**
