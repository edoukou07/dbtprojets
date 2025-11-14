import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Polygon, Marker, Popup, Tooltip, useMap } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import domtoimage from 'dom-to-image-more';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Search, Maximize2, RotateCcw, TrendingUp, MapPin, DollarSign, SlidersHorizontal, X, Flame, Download, Share2 } from 'lucide-react';

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Composant pour la heatmap d'occupation
function HeatmapLayer({ zones, show }) {
  const map = useMap();
  const heatLayerRef = useRef(null);

  useEffect(() => {
    if (!show) {
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current);
        heatLayerRef.current = null;
      }
      return;
    }

    // Créer les données de la heatmap basées sur le taux d'occupation
    const heatData = zones
      .filter(z => z.latitude && z.longitude && z.taux_occupation_pct !== null)
      .map(z => [
        z.latitude,
        z.longitude,
        z.taux_occupation_pct / 100 // Normaliser entre 0 et 1
      ]);

    if (heatData.length === 0) return;

    // Créer la heatmap
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
    }

    heatLayerRef.current = L.heatLayer(heatData, {
      radius: 50,
      blur: 35,
      maxZoom: 17,
      max: 1.0,
      gradient: {
        0.0: '#10B981',  // Vert - faible occupation
        0.3: '#FBBF24',  // Jaune
        0.6: '#F59E0B',  // Orange
        0.8: '#EF4444',  // Rouge - forte occupation
        1.0: '#991B1B'   // Rouge foncé
      }
    }).addTo(map);

    return () => {
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current);
        heatLayerRef.current = null;
      }
    };
  }, [map, zones, show]);

  return null;
}

// Composant pour gérer les tuiles avec dark mode
function DynamicTileLayer() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    // Détecter le mode dark initial
    const checkDarkMode = () => {
      setIsDark(document.documentElement.classList.contains('dark'));
    };
    
    checkDarkMode();
    
    // Observer les changements de classe sur l'élément HTML
    const observer = new MutationObserver(checkDarkMode);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    });
    
    return () => observer.disconnect();
  }, []);

  // URLs des tuiles selon le mode
  const lightTiles = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  const darkTiles = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png";
  
  return (
    <TileLayer
      attribution={isDark 
        ? '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
        : '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      }
      url={isDark ? darkTiles : lightTiles}
      key={isDark ? 'dark' : 'light'} // Force le rechargement des tuiles
    />
  );
}

// Composant pour contrôles personnalisés de la carte
function MapControls({ onReset, onFullscreen }) {
  const map = useMap();
  
  const handleFullscreen = () => {
    const container = map.getContainer();
    if (!document.fullscreenElement) {
      container.requestFullscreen?.() || container.webkitRequestFullscreen?.();
    } else {
      document.exitFullscreen?.() || document.webkitExitFullscreen?.();
    }
    onFullscreen?.();
  };
  
  return (
    <div className="leaflet-top leaflet-right" style={{ marginTop: '80px', marginRight: '10px' }}>
      <div className="leaflet-control bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
        <button
          onClick={() => map.setView([5.35, -4.00], 11)}
          className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 border-b border-gray-200 dark:border-gray-700 flex items-center gap-2 text-sm"
          title="Réinitialiser la vue"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <button
          onClick={handleFullscreen}
          className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 text-sm"
          title="Plein écran"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

// Composant pour recentrer la carte (préserve le niveau de zoom)
function MapRecenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      const currentZoom = map.getZoom(); // Préserver le zoom actuel
      map.flyTo(center, currentZoom, { duration: 1.5 }); // Animation fluide
    }
  }, [center, map]);
  return null;
}

// Fonction pour obtenir la couleur selon le taux d'occupation
function getOccupationColor(taux) {
  if (taux === null || taux === undefined) return '#9CA3AF'; // Gris si pas de données
  if (taux >= 80) return '#EF4444'; // Rouge - forte occupation
  if (taux >= 60) return '#F59E0B'; // Orange
  if (taux >= 40) return '#FBBF24'; // Jaune
  if (taux >= 20) return '#84CC16'; // Vert clair
  return '#10B981'; // Vert - faible occupation (beaucoup de disponibilité)
}

function ZonesMap({ height = '600px' }) {
  const [zones, setZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedZone, setSelectedZone] = useState(null);
  const [filterType, setFilterType] = useState('all'); // all, high, medium, low
  const [searchTerm, setSearchTerm] = useState('');
  const [superficieRange, setSuperficieRange] = useState([0, 1000]);
  const [selectedViabilite, setSelectedViabilite] = useState([]);
  const [selectedStatut, setSelectedStatut] = useState([]);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [hoveredZone, setHoveredZone] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [shareUrl, setShareUrl] = useState('');
  const [showShareDialog, setShowShareDialog] = useState(false);
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const mapRef = useRef(null);
  const mapContainerRef = useRef(null);

  // Options pour les filtres multi-select
  const viabiliteOptions = [
    { value: 'COMPLETE', label: 'Complète (≥80%)', color: 'green', min: 80, max: 100 },
    { value: 'PARTIELLE', label: 'Partielle (20-80%)', color: 'yellow', min: 20, max: 80 },
    { value: 'AUCUNE', label: 'Faible (<20%)', color: 'red', min: 0, max: 20 },
  ];

  const statutOptions = [
    { value: 'actif', label: 'Actif', color: 'green' },
    { value: 'inactif', label: 'Inactif', color: 'gray' },
    { value: 'en_construction', label: 'En construction', color: 'yellow' },
  ];

  // Centre sur Abidjan par défaut
  const defaultCenter = [5.35, -4.00];
  const defaultZoom = 11;

  useEffect(() => {
    fetchZonesData();
  }, []);

  const fetchZonesData = async () => {
    try {
      setLoading(true);
      console.log('🗺️ Fetching zones data...');
      const response = await fetch('http://127.0.0.1:8000/api/zones/map/');
      const data = await response.json();
      console.log('📡 API Response:', data);
      
      if (data.success) {
        // Filtrer uniquement les zones avec des polygones valides
        const validZones = data.zones.filter(z => 
          z.polygon && 
          z.polygon.coordinates && 
          z.polygon.coordinates.length > 0 &&
          z.latitude && 
          z.longitude
        );
        console.log(`✅ Valid zones: ${validZones.length}/${data.zones.length}`);
        console.log('📍 First zone:', validZones[0]);
        console.log('📍 First zone superficie:', validZones[0]?.superficie, 'type:', typeof validZones[0]?.superficie);
        console.log('📍 First zone viabilite:', validZones[0]?.viabilite);
        console.log('📍 First zone statut:', validZones[0]?.statut);
        setZones(validZones);
      } else {
        console.error('❌ API Error:', data.error);
        setError(data.error);
      }
    } catch (err) {
      console.error('❌ Fetch Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Export de la carte en PNG
  const handleExportPNG = async () => {
    if (!mapContainerRef.current || exporting) return;
    
    try {
      setExporting(true);
      const mapElement = mapContainerRef.current;
      
      // Générer l'image
      const dataUrl = await domtoimage.toPng(mapElement, {
        quality: 0.95,
        bgcolor: '#ffffff',
        style: {
          transform: 'scale(1)',
          transformOrigin: 'top left'
        }
      });
      
      // Créer un lien de téléchargement
      const link = document.createElement('a');
      link.download = `carte-zones-industrielles-${new Date().toISOString().split('T')[0]}.png`;
      link.href = dataUrl;
      link.click();
    } catch (error) {
      console.error('❌ Erreur export PNG:', error);
      alert('Erreur lors de l\'export. Veuillez réessayer.');
    } finally {
      setExporting(false);
    }
  };

  // Générer URL partageable avec filtres
  const handleShare = () => {
    const params = new URLSearchParams();
    
    if (filterType !== 'all') params.set('filter', filterType);
    if (searchTerm) params.set('search', searchTerm);
    if (superficieRange[0] !== 0) params.set('minSuperficie', superficieRange[0]);
    if (superficieRange[1] !== 1000) params.set('maxSuperficie', superficieRange[1]);
    if (selectedViabilite.length > 0) params.set('viabilite', selectedViabilite.join(','));
    if (selectedStatut.length > 0) params.set('statut', selectedStatut.join(','));
    if (showHeatmap) params.set('heatmap', 'true');
    
    const shareableUrl = `${window.location.origin}${window.location.pathname}?${params.toString()}`;
    setShareUrl(shareableUrl);
    setShowShareDialog(true);
    
    // Copier dans le presse-papier
    navigator.clipboard.writeText(shareableUrl).then(() => {
      console.log('✅ URL copiée dans le presse-papier');
    });
  };

  // Restaurer les filtres depuis l'URL au chargement
  useEffect(() => {
    const filter = searchParams.get('filter');
    const search = searchParams.get('search');
    const minSuperficie = searchParams.get('minSuperficie');
    const maxSuperficie = searchParams.get('maxSuperficie');
    const viabilite = searchParams.get('viabilite');
    const statut = searchParams.get('statut');
    const heatmap = searchParams.get('heatmap');
    
    if (filter) setFilterType(filter);
    if (search) setSearchTerm(search);
    if (minSuperficie) setSuperficieRange(prev => [parseInt(minSuperficie), prev[1]]);
    if (maxSuperficie) setSuperficieRange(prev => [prev[0], parseInt(maxSuperficie)]);
    if (viabilite) setSelectedViabilite(viabilite.split(','));
    if (statut) setSelectedStatut(statut.split(','));
    if (heatmap === 'true') setShowHeatmap(true);
  }, [searchParams]);

  // Filtrer les zones selon tous les filtres
  const getFilteredZones = () => {
    let filtered = zones;
    
    console.log('🔍 Filtering - Total zones:', zones.length);
    console.log('🔍 Filters:', { filterType, searchTerm, superficieRange, selectedViabilite, selectedStatut });
    
    // Filtre par taux d'occupation
    if (filterType !== 'all') {
      filtered = filtered.filter(zone => {
        const taux = zone.taux_occupation_pct || 0;
        if (filterType === 'high') return taux >= 60;
        if (filterType === 'medium') return taux >= 30 && taux < 60;
        if (filterType === 'low') return taux < 30;
        return true;
      });
      console.log('🔍 After occupation filter:', filtered.length);
    }
    
    // Filtre par recherche
    if (searchTerm) {
      filtered = filtered.filter(zone =>
        zone.nom?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      console.log('🔍 After search filter:', filtered.length, 'search term:', searchTerm);
    }
    
    // Filtre par superficie
    const beforeSuperficie = filtered.length;
    filtered = filtered.filter(zone => {
      const superficie = parseFloat(zone.superficie) || 0;
      return superficie >= superficieRange[0] && superficie <= superficieRange[1];
    });
    console.log('🔍 After superficie filter:', filtered.length, 'range:', superficieRange, '(removed:', beforeSuperficie - filtered.length, ')');
    
    // Filtre par viabilité (basé sur taux_viabilisation_pct)
    if (selectedViabilite.length > 0) {
      filtered = filtered.filter(zone => {
        const taux = zone.taux_viabilisation_pct || 0;
        return selectedViabilite.some(viab => {
          const option = viabiliteOptions.find(opt => opt.value === viab);
          return option && taux >= option.min && taux < option.max;
        });
      });
      console.log('🔍 After viabilite filter:', filtered.length);
    }
    
    // Filtre par statut
    if (selectedStatut.length > 0) {
      filtered = filtered.filter(zone =>
        selectedStatut.includes(zone.statut)
      );
      console.log('🔍 After statut filter:', filtered.length);
    }
    
    console.log('✅ Final filtered zones:', filtered.length);
    return filtered;
  };

  const filteredZones = getFilteredZones();

  // Convertir les coordonnées GeoJSON en format Leaflet
  const convertPolygonCoords = (coords) => {
    // coords est un tableau de [[[lon, lat], [lon, lat], ...]]
    if (!coords || !coords[0]) {
      console.warn('⚠️ Invalid coordinates:', coords);
      return [];
    }
    
    // Inverser lon,lat en lat,lon pour Leaflet
    const converted = coords[0].map(coord => [coord[1], coord[0]]);
    console.log('🔄 Converted coords:', { original: coords[0].length, converted: converted.length });
    return converted;
  };

  const handleZoneClick = (zone) => {
    setSelectedZone(zone);
    // Navigation vers les détails de la zone
    // navigate(`/occupation/zones/${zone.id}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 bg-white dark:bg-gray-800 rounded-lg">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Chargement de la carte...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-800 dark:text-red-200">Erreur de chargement: {error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Barre de recherche */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher une zone par nom..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              Effacer
            </button>
          )}
          <button
            onClick={handleExportPNG}
            disabled={exporting}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              exporting
                ? 'bg-gray-300 dark:bg-gray-600 cursor-not-allowed'
                : 'bg-purple-600 hover:bg-purple-700 text-white'
            }`}
            title="Exporter la carte en PNG"
          >
            <Download className="w-4 h-4" />
            <span className="text-sm font-medium">{exporting ? 'Export...' : 'Export'}</span>
          </button>
          <button
            onClick={handleShare}
            className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors bg-indigo-600 hover:bg-indigo-700 text-white"
            title="Partager avec filtres"
          >
            <Share2 className="w-4 h-4" />
            <span className="text-sm font-medium">Partager</span>
          </button>
          <button
            onClick={() => setShowHeatmap(!showHeatmap)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              showHeatmap
                ? 'bg-orange-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            }`}
            title="Afficher/masquer la heatmap d'occupation"
          >
            <Flame className="w-4 h-4" />
            <span className="text-sm font-medium">Heatmap</span>
          </button>
          <button
            onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              showAdvancedFilters
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            }`}
          >
            <SlidersHorizontal className="w-4 h-4" />
            <span className="text-sm font-medium">Filtres avancés</span>
          </button>
        </div>
      </div>

      {/* Dialog de partage */}
      {showShareDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-lg w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Partager la carte</h3>
              <button
                onClick={() => setShowShareDialog(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Lien copié dans le presse-papier ! Cette URL conserve tous vos filtres actifs.
            </p>
            <div className="bg-gray-100 dark:bg-gray-700 rounded p-3 break-all text-sm font-mono">
              {shareUrl}
            </div>
            <button
              onClick={() => {
                navigator.clipboard.writeText(shareUrl);
                alert('URL copiée !');
              }}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Copier à nouveau
            </button>
          </div>
        </div>
      )}

      {/* Filtres avancés (affichage conditionnel) */}
      {showAdvancedFilters && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-6">
          {/* Slider de superficie */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Superficie (hectares)
              </label>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                {superficieRange[0]} - {superficieRange[1]} ha
              </span>
            </div>
            <div className="space-y-2">
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="text-xs text-gray-500 dark:text-gray-400 mb-1 block">Min</label>
                  <input
                    type="range"
                    min="0"
                    max="1000"
                    value={superficieRange[0]}
                    onChange={(e) => setSuperficieRange([parseInt(e.target.value), superficieRange[1]])}
                    className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                </div>
                <div className="flex-1">
                  <label className="text-xs text-gray-500 dark:text-gray-400 mb-1 block">Max</label>
                  <input
                    type="range"
                    min="0"
                    max="1000"
                    value={superficieRange[1]}
                    onChange={(e) => setSuperficieRange([superficieRange[0], parseInt(e.target.value)])}
                    className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Multi-select Viabilité */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Viabilité
            </label>
            <div className="flex flex-wrap gap-2">
              {viabiliteOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => {
                    setSelectedViabilite(prev =>
                      prev.includes(option.value)
                        ? prev.filter(v => v !== option.value)
                        : [...prev, option.value]
                    );
                  }}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    selectedViabilite.includes(option.value)
                      ? `bg-${option.color}-600 text-white shadow-md`
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {option.label}
                  {selectedViabilite.includes(option.value) && (
                    <span className="ml-2">✓</span>
                  )}
                </button>
              ))}
              {selectedViabilite.length > 0 && (
                <button
                  onClick={() => setSelectedViabilite([])}
                  className="px-3 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Multi-select Statut */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Statut
            </label>
            <div className="flex flex-wrap gap-2">
              {statutOptions.map(option => (
                <button
                  key={option.value}
                  onClick={() => {
                    setSelectedStatut(prev =>
                      prev.includes(option.value)
                        ? prev.filter(s => s !== option.value)
                        : [...prev, option.value]
                    );
                  }}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    selectedStatut.includes(option.value)
                      ? `bg-${option.color}-600 text-white shadow-md`
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {option.label}
                  {selectedStatut.includes(option.value) && (
                    <span className="ml-2">✓</span>
                  )}
                </button>
              ))}
              {selectedStatut.length > 0 && (
                <button
                  onClick={() => setSelectedStatut([])}
                  className="px-3 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Bouton reset tous les filtres avancés */}
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={() => {
                setSuperficieRange([0, 1000]);
                setSelectedViabilite([]);
                setSelectedStatut([]);
              }}
              className="w-full px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm font-medium"
            >
              Réinitialiser les filtres avancés
            </button>
          </div>
        </div>
      )}
      
      {/* Filtres */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex flex-wrap items-center gap-4">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Filtrer par occupation:
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setFilterType('all')}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                filterType === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              Toutes ({zones.length})
            </button>
            <button
              onClick={() => setFilterType('high')}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                filterType === 'high'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              Haute ≥60% ({zones.filter(z => (z.taux_occupation_pct || 0) >= 60).length})
            </button>
            <button
              onClick={() => setFilterType('medium')}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                filterType === 'medium'
                  ? 'bg-yellow-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              Moyenne 30-60% ({zones.filter(z => {
                const t = z.taux_occupation_pct || 0;
                return t >= 30 && t < 60;
              }).length})
            </button>
            <button
              onClick={() => setFilterType('low')}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                filterType === 'low'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              Faible &lt;30% ({zones.filter(z => (z.taux_occupation_pct || 0) < 30).length})
            </button>
          </div>
          <span className="text-sm text-gray-500 dark:text-gray-400 ml-auto">
            Affichage: {filteredZones.length} zone(s)
          </span>
        </div>
      </div>

      {/* Carte */}
      <div ref={mapContainerRef} className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <MapContainer
          center={defaultCenter}
          zoom={defaultZoom}
          style={{ height, width: '100%' }}
          className="z-0"
        >
          <DynamicTileLayer />
          
          {/* Polygones des zones */}
          {filteredZones.map((zone) => {
            const polygonCoords = convertPolygonCoords(zone.polygon?.coordinates);
            const color = getOccupationColor(zone.taux_occupation_pct);
            
            return (
              polygonCoords.length > 0 && (
                <Polygon
                  key={`polygon-${zone.id}`}
                  positions={polygonCoords}
                  pathOptions={{
                    color: color,
                    fillColor: color,
                    fillOpacity: hoveredZone === zone.id ? 0.6 : 0.4,
                    weight: hoveredZone === zone.id ? 3 : 2,
                  }}
                  eventHandlers={{
                    click: () => handleZoneClick(zone),
                    mouseover: () => setHoveredZone(zone.id),
                    mouseout: () => setHoveredZone(null),
                  }}
                >
                  {/* Tooltip au survol */}
                  <Tooltip direction="top" offset={[0, -10]} opacity={0.9}>
                    <div className="text-center">
                      <div className="font-bold">{zone.nom}</div>
                      <div className="text-sm" style={{ color }}>
                        {zone.taux_occupation_pct?.toFixed(1) || 0}% occupé
                      </div>
                    </div>
                  </Tooltip>
                </Polygon>
              )
            );
          })}
          
          {/* Marqueurs avec clustering */}
          <MarkerClusterGroup
            chunkedLoading
            maxClusterRadius={80}
            spiderfyOnMaxZoom={true}
            showCoverageOnHover={false}
            zoomToBoundsOnClick={true}
            iconCreateFunction={(cluster) => {
              const count = cluster.getChildCount();
              let size = 'small';
              if (count > 10) size = 'large';
              else if (count > 5) size = 'medium';
              
              return L.divIcon({
                html: `<div class="cluster-icon cluster-${size}"><span>${count}</span></div>`,
                className: 'custom-cluster-icon',
                iconSize: L.point(40, 40),
              });
            }}
          >
            {filteredZones.map((zone) => {
              const color = getOccupationColor(zone.taux_occupation_pct);
              
              return (
                zone.latitude && zone.longitude && (
                  <Marker
                    key={`marker-${zone.id}`}
                    position={[zone.latitude, zone.longitude]}
                    eventHandlers={{
                      click: () => handleZoneClick(zone),
                    }}
                  >
                    {/* Popup amélioré */}
                    <Popup maxWidth={350} className="custom-popup">
                      <div className="min-w-[320px] p-2">
                        {/* En-tête */}
                        <div className="border-b pb-3 mb-3">
                          <h3 className="font-bold text-xl text-gray-900 mb-1">{zone.nom}</h3>
                          <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4 text-gray-500" />
                            <span className="text-sm text-gray-600">
                              Zone industrielle - {zone.superficie} ha
                            </span>
                          </div>
                        </div>
                        
                        {/* Jauge d'occupation */}
                        <div className="mb-4">
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-sm font-medium text-gray-700">Taux d'occupation</span>
                            <span className="text-lg font-bold" style={{ color }}>
                              {zone.taux_occupation_pct?.toFixed(1) || 0}%
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all duration-500"
                              style={{
                                width: `${zone.taux_occupation_pct || 0}%`,
                                backgroundColor: color
                              }}
                            ></div>
                          </div>
                        </div>
                        
                        {/* Statistiques en grille */}
                        <div className="grid grid-cols-2 gap-3 mb-4">
                          <div className="bg-green-50 rounded-lg p-3">
                            <div className="text-xs text-green-600 font-medium mb-1">Disponibles</div>
                            <div className="text-2xl font-bold text-green-700">
                              {zone.lots_disponibles || 0}
                            </div>
                            <div className="text-xs text-gray-500">lots</div>
                          </div>
                          
                          <div className="bg-blue-50 rounded-lg p-3">
                            <div className="text-xs text-blue-600 font-medium mb-1">Attribués</div>
                            <div className="text-2xl font-bold text-blue-700">
                              {zone.lots_attribues || 0}
                            </div>
                            <div className="text-xs text-gray-500">lots</div>
                          </div>
                          
                          <div className="bg-orange-50 rounded-lg p-3">
                            <div className="text-xs text-orange-600 font-medium mb-1">Réservés</div>
                            <div className="text-2xl font-bold text-orange-700">
                              {zone.lots_reserves || 0}
                            </div>
                            <div className="text-xs text-gray-500">lots</div>
                          </div>
                          
                          <div className="bg-purple-50 rounded-lg p-3">
                            <div className="text-xs text-purple-600 font-medium mb-1">Superficie</div>
                            <div className="text-2xl font-bold text-purple-700">
                              {zone.superficie_disponible?.toFixed(0) || 0}
                            </div>
                            <div className="text-xs text-gray-500">m² dispo</div>
                          </div>
                        </div>
                        
                        {/* Informations supplémentaires */}
                        <div className="space-y-2 text-sm border-t pt-3">
                          {zone.taux_viabilisation_pct !== null && zone.taux_viabilisation_pct !== undefined && (
                            <div className="flex justify-between">
                              <span className="text-gray-600">Viabilisation:</span>
                              <span className={`font-medium px-2 py-1 rounded ${
                                zone.taux_viabilisation_pct >= 80
                                  ? 'bg-green-100 text-green-700'
                                  : zone.taux_viabilisation_pct >= 20
                                  ? 'bg-yellow-100 text-yellow-700'
                                  : 'bg-red-100 text-red-700'
                              }`}>
                                {zone.taux_viabilisation_pct?.toFixed(1)}%
                              </span>
                            </div>
                          )}
                          
                          {zone.statut && (
                            <div className="flex justify-between">
                              <span className="text-gray-600">Statut:</span>
                              <span className={`font-medium px-2 py-1 rounded ${
                                zone.statut === 'actif'
                                  ? 'bg-green-100 text-green-700'
                                  : zone.statut === 'en_construction'
                                  ? 'bg-yellow-100 text-yellow-700'
                                  : 'bg-gray-100 text-gray-700'
                              }`}>
                                {zone.statut}
                              </span>
                            </div>
                          )}
                          
                          {zone.lots_viabilises !== null && zone.lots_viabilises !== undefined && (
                            <div className="flex justify-between">
                              <span className="text-gray-600">Lots viabilisés:</span>
                              <span className="font-medium">{zone.lots_viabilises} / {zone.nombre_total_lots || 0}</span>
                            </div>
                          )}
                        </div>
                        
                        {/* Bouton d'action */}
                        <button
                          onClick={() => navigate(`/occupation/zone/${encodeURIComponent(zone.nom)}`)}
                          className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                        >
                          <TrendingUp className="w-4 h-4" />
                          Voir les détails complets
                        </button>
                      </div>
                    </Popup>
                  </Marker>
                )
              );
            })}
          </MarkerClusterGroup>
          
          {/* Heatmap layer */}
          <HeatmapLayer zones={zones} show={showHeatmap} />
          
          {/* Contrôles personnalisés */}
          <MapControls />
          
          {selectedZone && (
            <MapRecenter center={[selectedZone.latitude, selectedZone.longitude]} />
          )}
        </MapContainer>
      </div>

      {/* Légende */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <h4 className="font-semibold text-gray-900 dark:text-white mb-3">
          Légende - Taux d'occupation
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded border-2" style={{ backgroundColor: '#10B981', borderColor: '#10B981' }}></div>
            <span className="text-sm text-gray-700 dark:text-gray-300">0-20%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded border-2" style={{ backgroundColor: '#84CC16', borderColor: '#84CC16' }}></div>
            <span className="text-sm text-gray-700 dark:text-gray-300">20-40%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded border-2" style={{ backgroundColor: '#FBBF24', borderColor: '#FBBF24' }}></div>
            <span className="text-sm text-gray-700 dark:text-gray-300">40-60%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded border-2" style={{ backgroundColor: '#F59E0B', borderColor: '#F59E0B' }}></div>
            <span className="text-sm text-gray-700 dark:text-gray-300">60-80%</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded border-2" style={{ backgroundColor: '#EF4444', borderColor: '#EF4444' }}></div>
            <span className="text-sm text-gray-700 dark:text-gray-300">80-100%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ZonesMap;
