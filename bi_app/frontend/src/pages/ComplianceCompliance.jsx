import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Calendar, CheckCircle, AlertTriangle, Clock, TrendingUp, FileText, BarChart3, Filter, X, RefreshCw } from 'lucide-react';
import complianceComplianceAPI from '../services/complianceComplianceAPI';
import StatsCard from '../components/StatsCard';
import ExportButton from '../components/ExportButton';
import './ComplianceCompliance.css';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

const ComplianceCompliance = () => {
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear());
  const [loading, setLoading] = useState(false);
  
  // Filtres
  const [showFilters, setShowFilters] = useState(false);
  const [selectedMonth, setSelectedMonth] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [selectedEtape, setSelectedEtape] = useState('');
  
  // Filtres pour le tableau détaillé
  const [tableFilterStatus, setTableFilterStatus] = useState('');
  const [tableFilterEtape, setTableFilterEtape] = useState('');
  const [tableFilterDelayMin, setTableFilterDelayMin] = useState('');
  const [tableFilterDelayMax, setTableFilterDelayMax] = useState('');
  const [showTableFilters, setShowTableFilters] = useState(false);
  
  // Filtres pour le tableau des délais par étape
  const [showEtapeTableFilters, setShowEtapeTableFilters] = useState(false);
  const [etapeFilterEtape, setEtapeFilterEtape] = useState('');
  
  // Résumé du tableau de bord
  const [summary, setSummary] = useState({
    conventions_validation: {},
    approval_delays: {}
  });

  // Conventions
  const [conventionsSummary, setConventionsSummary] = useState({});
  const [conventionsTrends, setConventionsTrends] = useState([]);
  const [conventionsByStatus, setConventionsByStatus] = useState([]);

  // Conventions - Enterprise Dimensions (Phase 1)
  const [conventionsByDomaine, setConventionsByDomaine] = useState([]);
  const [conventionsByCategorie, setConventionsByCategorie] = useState([]);
  const [conventionsByFormeJuridique, setConventionsByFormeJuridique] = useState([]);
  const [conventionsByEntreprise, setConventionsByEntreprise] = useState([]);

  // Délais d'approbation
  const [delaysSummary, setDelaysSummary] = useState({});
  const [delaysTrends, setDelaysTrends] = useState([]);
  const [delaysByStatus, setDelaysByStatus] = useState([]);
  const [delaysByEtape, setDelaysByEtape] = useState([]);

  // Délais - Enterprise Dimensions (Phase 1)
  const [delaysByDomaine, setDelaysByDomaine] = useState([]);
  const [delaysByFormeJuridique, setDelaysByFormeJuridique] = useState([]);

  useEffect(() => {
    fetchAllData();
  }, [currentYear]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [
        summary, convSum, convTr, convStat,
        convDomaine, convCategorie, convForme, convEntreprise,
        delaySum, delayTr, delayStat, delayEtape,
        delayDomaine, delayForme
      ] = await Promise.all([
        complianceComplianceAPI.getDashboardSummary(currentYear),
        complianceComplianceAPI.getConventionsSummary(currentYear),
        complianceComplianceAPI.getConventionsTrends(),
        complianceComplianceAPI.getConventionsByStatus(),
        // Phase 1: Enterprise Dimensions - Conventions
        complianceComplianceAPI.getConventionsByDomaine(currentYear),
        complianceComplianceAPI.getConventionsByCategorieDomaine(currentYear),
        complianceComplianceAPI.getConventionsByFormeJuridique(currentYear),
        complianceComplianceAPI.getConventionsByEntreprise(currentYear, 20),
        // Approval Delays
        complianceComplianceAPI.getApprovalDelaysSummary(currentYear),
        complianceComplianceAPI.getApprovalDelaysTrends(),
        complianceComplianceAPI.getApprovalDelaysByStatus(),
        complianceComplianceAPI.getApprovalDelaysByEtape(),
        // Phase 1: Enterprise Dimensions - Delays
        complianceComplianceAPI.getApprovalDelaysByDomaine(currentYear),
        complianceComplianceAPI.getApprovalDelaysByFormeJuridique(currentYear),
      ]);

      setSummary(summary.data);
      setConventionsSummary(convSum.data);
      setConventionsTrends(convTr.data || []);
      setConventionsByStatus(convStat.data || []);
      
      // Phase 1: Set Enterprise Dimensions - Conventions
      setConventionsByDomaine(convDomaine.data || []);
      setConventionsByCategorie(convCategorie.data || []);
      setConventionsByFormeJuridique(convForme.data || []);
      setConventionsByEntreprise(convEntreprise.data || []);
      
      setDelaysSummary(delaySum.data);
      setDelaysTrends(delayTr.data || []);
      setDelaysByStatus(delayStat.data || []);
      setDelaysByEtape(delayEtape.data || []);
      
      // Phase 1: Set Enterprise Dimensions - Delays
      setDelaysByDomaine(delayDomaine.data || []);
      setDelaysByFormeJuridique(delayForme.data || []);
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatPercent = (value) => {
    if (!value && value !== 0) return '0%'
    return value.toFixed(1) + '%'
  }

  const formatNumber = (value) => {
    if (!value && value !== 0) return '0'
    return value.toLocaleString('fr-FR')
  }

  const formatDays = (value) => {
    if (!value && value !== 0) return '0'
    return value.toFixed(1)
  }

  const handleResetFilters = () => {
    setSelectedMonth('');
    setSelectedStatus('');
    setSelectedEtape('');
  };

  // Extraire les valeurs uniques pour les filtres
  const uniqueStatuses = [...new Set(conventionsByStatus?.map(item => item.statut) || [])];
  const uniqueEtapes = [...new Set(delaysByEtape?.map(item => item.etape) || [])];
  
  // Créer les options de mois à partir des tendances
  const months = [];
  if (conventionsTrends && conventionsTrends.length > 0) {
    conventionsTrends.forEach((item, index) => {
      if (item.mois) {
        months.push({
          value: item.mois,
          label: item.mois
        });
      }
    });
  }

  // Filtrer les données par statut
  const filteredConventionsByStatus = conventionsByStatus.filter(item => {
    if (selectedStatus && item.statut !== selectedStatus) return false;
    return true;
  });

  // Filtrer les données par étape
  const filteredDelaysByEtape = delaysByEtape.filter(item => {
    if (selectedEtape && item.etape !== selectedEtape) return false;
    return true;
  });

  // Filtrer les données par mois
  const filteredConventionsTrends = conventionsTrends.filter((item) => {
    if (selectedMonth !== '' && item.mois !== selectedMonth) return false;
    return true;
  });

  const filteredDelaysTrends = delaysTrends.filter((item) => {
    if (selectedMonth !== '' && item.mois !== selectedMonth) return false;
    return true;
  });

  // Filtrer les données du tableau détaillé
  const filteredDetailedTable = delaysByStatus.filter(item => {
    if (tableFilterStatus && item.statut !== tableFilterStatus) return false;
    if (tableFilterEtape && item.etape_actuelle !== tableFilterEtape) return false;
    if (tableFilterDelayMin && item.avg_approval_days < parseFloat(tableFilterDelayMin)) return false;
    if (tableFilterDelayMax && item.avg_approval_days > parseFloat(tableFilterDelayMax)) return false;
    return true;
  });

  const activeTableFilters = [tableFilterStatus, tableFilterEtape, tableFilterDelayMin, tableFilterDelayMax].filter(f => f).length;
  
  // Extraire les statuts et étapes uniques du tableau
  const tableUniqueStatuses = [...new Set(delaysByStatus?.map(item => item.statut) || [])];
  const tableUniqueEtapes = [...new Set(delaysByStatus?.map(item => item.etape_actuelle) || [])];

  // Filtrer les données du tableau délais par étape
  const filteredDelaysByEtapeTable = delaysByEtape.filter(item => {
    if (etapeFilterEtape && item.etape_actuelle !== etapeFilterEtape) return false;
    return true;
  });

  const activeEtapeTableFilters = [etapeFilterEtape].filter(f => f).length;
  const etapeTableUniqueEtapes = [...new Set(delaysByEtape?.map(item => item.etape_actuelle) || [])];

  // Calculer les données agrégées filtrées
  const calculateFilteredSummary = () => {
    let filteredData = {
      total_conventions: 0,
      conventions_approved: 0,
      conventions_rejected: 0,
      conventions_in_progress: 0,
      avg_validation_rate_pct: 0,
      avg_approval_days: 0,
      max_approval_days: 0
    };

    // Appliquer les filtres
    let tempConventions = [...conventionsByStatus];
    let tempDelays = [...delaysByStatus];

    if (selectedStatus) {
      tempConventions = tempConventions.filter(item => item.statut === selectedStatus);
    }

    if (selectedEtape) {
      tempDelays = tempDelays.filter(item => item.etape === selectedEtape);
    }

    // Si filtre mois est actif, utiliser les données de tendances
    if (selectedMonth !== '') {
      const monthData = filteredConventionsTrends.length > 0 ? filteredConventionsTrends[0] : null;
      const monthDelaysData = filteredDelaysTrends.length > 0 ? filteredDelaysTrends[0] : null;
      
      if (monthData) {
        filteredData.total_conventions = monthData.total_conventions || 0;
        filteredData.conventions_approved = monthData.conventions_approved || 0;
        filteredData.conventions_rejected = monthData.conventions_rejected || 0;
        filteredData.avg_validation_rate_pct = monthData.avg_validation_rate || 0;
      }
      
      if (monthDelaysData) {
        filteredData.conventions_in_progress = monthDelaysData.conventions_in_progress || 0;
        filteredData.avg_approval_days = monthDelaysData.avg_approval_days || 0;
        filteredData.max_approval_days = monthDelaysData.max_approval_days || 0;
      }
    } else {
      // Calculer les totaux
      if (tempConventions.length > 0) {
        filteredData.total_conventions = tempConventions.reduce((sum, item) => sum + (item.total_conventions || 0), 0);
        filteredData.conventions_approved = tempConventions.reduce((sum, item) => sum + (item.conventions_approved || 0), 0);
        filteredData.conventions_rejected = tempConventions.reduce((sum, item) => sum + (item.conventions_rejected || 0), 0);
        filteredData.avg_validation_rate_pct = tempConventions.length > 0 
          ? tempConventions.reduce((sum, item) => sum + (item.taux_validation_pct || 0), 0) / tempConventions.length 
          : 0;
      }

      if (tempDelays.length > 0) {
        filteredData.conventions_in_progress = tempDelays.reduce((sum, item) => sum + (item.conventions_in_progress || 0), 0);
        filteredData.avg_approval_days = tempDelays.length > 0 
          ? tempDelays.reduce((sum, item) => sum + (item.delai_moyen_traitement_jours || 0), 0) / tempDelays.length 
          : 0;
        filteredData.max_approval_days = Math.max(...tempDelays.map(item => item.delai_max_traitement_jours || 0), 0);
      }
    }

    return filteredData;
  };

  const filteredSummaryData = calculateFilteredSummary();
  const activeFilters = [selectedMonth, selectedStatus, selectedEtape].filter(f => f).length;

  // Préparer les données pour l'export
  const prepareExportData = () => {
    const exportData = [];
    
    // Ajouter le résumé
    exportData.push({
      Type: 'Résumé',
      'Total Conventions': filteredSummaryData.total_conventions || summary.conventions_validation?.total_conventions || 0,
      'Taux de Validation': filteredSummaryData.avg_validation_rate_pct || summary.conventions_validation?.avg_validation_rate_pct || 0,
      'Conventions Approuvées': filteredSummaryData.conventions_approved || summary.approval_delays?.conventions_approved || 0,
      'Délai Moyen (j)': filteredSummaryData.avg_approval_days || summary.approval_delays?.avg_approval_days || 0,
      'Délai Maximum (j)': filteredSummaryData.max_approval_days || summary.approval_delays?.max_approval_days || 0,
    });

    // Ajouter les conventions par statut
    if (filteredConventionsByStatus.length > 0) {
      filteredConventionsByStatus.forEach(item => {
        exportData.push({
          Type: 'Convention - Statut',
          Statut: item.statut || '',
          Total: item.total_conventions || 0,
          'Taux Validation': item.taux_validation_pct || 0,
        });
      });
    }

    // Ajouter les délais par étape
    if (filteredDelaysByEtape.length > 0) {
      filteredDelaysByEtape.forEach(item => {
        exportData.push({
          Type: 'Délai - Étape',
          Étape: item.etape || '',
          Total: item.total_conventions || 0,
          'Délai Moyen (j)': item.avg_approval_days || 0,
          'Délai Max (j)': item.max_approval_days || 0,
        });
      });
    }

    // Ajouter les tendances
    if (filteredConventionsTrends.length > 0) {
      filteredConventionsTrends.forEach(item => {
        exportData.push({
          Type: 'Tendance - Conventions',
          Mois: item.mois || '',
          Total: item.total_conventions || 0,
          Approuvées: item.conventions_approved || 0,
          Rejetées: item.conventions_rejected || 0,
        });
      });
    }

    return exportData.length > 0 ? exportData : [{ Type: 'Aucune donnée', Message: 'Aucune donnée disponible' }];
  };

  return (
    <div className="space-y-8">
      {/* Header Principal */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Tableau de Bord Conformité</h2>
        <ExportButton 
          data={prepareExportData()}
          filename="compliance_compliance"
          title="Tableau de Bord Conformité - Conventions et Délais"
        />
      </div>

      {/* Contrôles */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Calendar className="w-5 h-5 text-gray-400" />
          <select
            value={currentYear}
            onChange={(e) => setCurrentYear(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value={2024}>2024</option>
            <option value={2025}>2025</option>
            <option value={2026}>2026</option>
          </select>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Filter className="w-4 h-4" />
            <span>Filtres {activeFilters > 0 && `(${activeFilters})`}</span>
          </button>
          {activeFilters > 0 && (
            <button
              onClick={handleResetFilters}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-900 dark:text-white rounded-lg hover:bg-gray-400 dark:hover:bg-gray-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Réinitialiser</span>
            </button>
          )}
        </div>
      </div>

      {/* Panel des Filtres */}
      {showFilters && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700 relative z-50 overflow-visible">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Options de Filtrage</h3>
            <button
              onClick={() => setShowFilters(false)}
              className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pb-2">
            {/* Filtre par Mois */}
            <div className="flex flex-col">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Mois
              </label>
              <select
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white relative z-50"
              >
                <option value="">Tous les mois</option>
                {months.map((month) => (
                  <option key={month.value} value={month.value}>
                    {month.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Filtre par Statut */}
            <div className="flex flex-col">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Statut
              </label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white relative z-50"
              >
                <option value="">Tous les statuts</option>
                {uniqueStatuses.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </div>

            {/* Filtre par Étape */}
            <div className="flex flex-col">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Étape
              </label>
              <select
                value={selectedEtape}
                onChange={(e) => setSelectedEtape(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white relative z-50"
              >
                <option value="">Toutes les étapes</option>
                {uniqueEtapes.map((etape) => (
                  <option key={etape} value={etape}>
                    {etape}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-8 text-center">Chargement des données...</div>
      ) : (
        <>
          {/* KPIs Principaux - Résumé du Tableau de Bord */}
          <section>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <BarChart3 className="w-6 h-6 mr-2 text-blue-600" />
              Vue d'Ensemble Conformité
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
              <StatsCard
                title="Total Conventions"
                value={formatNumber(activeFilters > 0 ? filteredSummaryData.total_conventions : summary.conventions_validation?.total_conventions)}
                subtitle="Conventions enregistrées"
                icon={FileText}
                color="blue"
                loading={loading}
              />
              <StatsCard
                title="Taux de Validation"
                value={formatPercent(activeFilters > 0 ? filteredSummaryData.avg_validation_rate_pct : summary.conventions_validation?.avg_validation_rate_pct)}
                subtitle="Moyenne de validation"
                icon={CheckCircle}
                color="green"
                loading={loading}
              />
              <StatsCard
                title="Approuvées"
                value={formatNumber(activeFilters > 0 ? filteredSummaryData.conventions_approved : summary.approval_delays?.conventions_approved)}
                subtitle="Conventions acceptées"
                icon={CheckCircle}
                color="green"
                loading={loading}
              />
              <StatsCard
                title="Délai Moyen"
                value={formatDays(activeFilters > 0 ? filteredSummaryData.avg_approval_days : summary.approval_delays?.avg_approval_days) + ' j'}
                subtitle="Délai d'approbation"
                icon={Clock}
                color="orange"
                loading={loading}
              />
              <StatsCard
                title="Délai Maximum"
                value={formatDays(activeFilters > 0 ? filteredSummaryData.max_approval_days : summary.approval_delays?.max_approval_days) + ' j'}
                subtitle="Délai max. de traitement"
                icon={AlertTriangle}
                color="red"
                loading={loading}
              />
            </div>
          </section>


          {/* Conventions Validation Section */}
          <section>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <FileText className="w-6 h-6 mr-2 text-blue-600" />
              Analyse de la Validation des Conventions
            </h3>
            
            {/* Graphiques */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Distribution par Statut */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Distribution par Statut
                </h4>
                {filteredConventionsByStatus.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={filteredConventionsByStatus}
                        dataKey="total_conventions"
                        nameKey="statut"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        label
                      >
                        {filteredConventionsByStatus.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => value.toLocaleString('fr-FR')} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-500">Aucune donnée disponible</div>
                )}
              </div>

              {/* Tendances mensuelles */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Tendances Mensuelles
                </h4>
                {conventionsTrends.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={conventionsTrends}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="mois" />
                      <YAxis />
                      <Tooltip formatter={(value) => value.toLocaleString('fr-FR')} />
                      <Legend />
                      <Line type="monotone" dataKey="total_conventions" stroke="#3B82F6" name="Total Conventions" />
                      <Line type="monotone" dataKey="conventions_approved" stroke="#10B981" name="Approuvées" />
                      <Line type="monotone" dataKey="conventions_rejected" stroke="#EF4444" name="Rejetées" />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-500">Aucune donnée disponible</div>
                )}
              </div>
            </div>
          </section>

          {/* PHASE 1: Enterprise Dimensions - Conventions Section */}
          <section className="mt-8">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <BarChart3 className="w-6 h-6 mr-2 text-purple-600" />
              Analyse par Dimensions Entreprise (Phase 1)
            </h3>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Conventions par Catégorie de Domaine */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Conventions par Catégorie Sectorielle
                </h4>
                {conventionsByCategorie.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={conventionsByCategorie}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="categorie_domaine" />
                      <YAxis />
                      <Tooltip formatter={(value) => value.toLocaleString('fr-FR', {maximumFractionDigits: 1})} />
                      <Legend />
                      <Bar dataKey="total_conventions" fill="#8B5CF6" name="Total Conventions" />
                      <Bar dataKey="avg_validation_pct" fill="#10B981" name="Taux Valid. (%)" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-500">Aucune donnée disponible</div>
                )}
              </div>

              {/* Conventions par Forme Juridique */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Conventions par Forme Juridique
                </h4>
                {conventionsByFormeJuridique.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={conventionsByFormeJuridique}
                        dataKey="total_conventions"
                        nameKey="forme_juridique"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        label={({ forme_juridique, total_conventions }) => 
                          `${forme_juridique}: ${total_conventions}`
                        }
                      >
                        {conventionsByFormeJuridique.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => value.toLocaleString('fr-FR')} />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-500">Aucune donnée disponible</div>
                )}
              </div>

              {/* Top Entreprises */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 lg:col-span-2">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Top 10 Entreprises par Volume
                </h4>
                {conventionsByEntreprise.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={conventionsByEntreprise.slice(0, 10)} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="raison_sociale" type="category" width={200} />
                      <Tooltip formatter={(value) => value.toLocaleString('fr-FR', {maximumFractionDigits: 1})} />
                      <Legend />
                      <Bar dataKey="total_conventions" fill="#3B82F6" name="Conventions" />
                      <Bar dataKey="avg_processing_days" fill="#F59E0B" name="Délai Moy. (j)" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-500">Aucune donnée disponible</div>
                )}
              </div>

              {/* Délais par Domaine d'Activité */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 lg:col-span-2">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Délais d'Approbation par Secteur d'Activité
                </h4>
                {delaysByDomaine.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={delaysByDomaine.slice(0, 10)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="libelle_domaine" angle={-45} textAnchor="end" height={100} />
                      <YAxis />
                      <Tooltip formatter={(value) => value.toLocaleString('fr-FR', {maximumFractionDigits: 1})} />
                      <Legend />
                      <Bar dataKey="avg_approval_days" fill="#EF4444" name="Délai Moy. (j)" />
                      <Bar dataKey="median_approval_days" fill="#F59E0B" name="Délai Médian (j)" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-500">Aucune donnée disponible</div>
                )}
              </div>
            </div>
          </section>

          {/* Approval Delays Section */}
          <section>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <Clock className="w-6 h-6 mr-2 text-blue-600" />
              Analyse des Délais d'Approbation
            </h3>
            
            {/* Statistiques principales des délais */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <StatsCard
                title="Délai Moyen"
                value={formatDays(delaysSummary.avg_approval_days) + ' j'}
                subtitle="Durée moyenne de traitement"
                icon={Clock}
                color="blue"
              />
              <StatsCard
                title="Délai Médian"
                value={formatDays(delaysSummary.median_approval_days) + ' j'}
                subtitle="Valeur médiane"
                icon={TrendingUp}
                color="green"
              />
              <StatsCard
                title="Délai P95"
                value={formatDays(delaysSummary.p95_approval_days) + ' j'}
                subtitle="95e percentile"
                icon={AlertTriangle}
                color="orange"
              />
              <StatsCard
                title="Conventions Suivi"
                value={formatNumber(delaysSummary.total_conventions_tracked)}
                subtitle="Enregistrements suivis"
                icon={FileText}
                color="purple"
              />
            </div>

            {/* Graphiques des délais */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Délais par Étape */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Délais Moyens par Étape
                  </h4>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setShowEtapeTableFilters(!showEtapeTableFilters)}
                      className="flex items-center space-x-2 px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                    >
                      <Filter className="w-4 h-4" />
                      <span>Filtres {activeEtapeTableFilters > 0 && `(${activeEtapeTableFilters})`}</span>
                    </button>
                    {activeEtapeTableFilters > 0 && (
                      <button
                        onClick={() => {
                          setEtapeFilterEtape('');
                        }}
                        className="flex items-center space-x-2 px-3 py-1 bg-gray-300 dark:bg-gray-600 text-gray-900 dark:text-white rounded-lg hover:bg-gray-400 dark:hover:bg-gray-700 transition-colors text-sm"
                      >
                        <X className="w-4 h-4" />
                        <span>Réinitialiser</span>
                      </button>
                    )}
                  </div>
                </div>

                {/* Panel des filtres */}
                {showEtapeTableFilters && (
                  <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-4 border border-gray-200 dark:border-gray-600">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Étape
                      </label>
                      <select
                        value={etapeFilterEtape}
                        onChange={(e) => setEtapeFilterEtape(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                      >
                        <option value="">Toutes les étapes</option>
                        {etapeTableUniqueEtapes.map((etape) => (
                          <option key={etape} value={etape}>
                            {etape}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                )}

                {filteredDelaysByEtapeTable.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={filteredDelaysByEtapeTable}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="etape_actuelle" angle={-45} textAnchor="end" height={100} />
                      <YAxis />
                      <Tooltip formatter={(value) => formatDays(value) + ' j'} />
                      <Bar dataKey="avg_approval_days" fill="#F59E0B" name="Délai Moyen (j)" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-500">Aucune donnée disponible</div>
                )}
              </div>

              {/* Tendances des Délais */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Évolution des Délais
                </h4>
                {delaysTrends.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={delaysTrends}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="annee_mois" />
                      <YAxis />
                      <Tooltip formatter={(value) => formatDays(value) + ' j'} />
                      <Legend />
                      <Line type="monotone" dataKey="avg_approval_days" stroke="#F59E0B" name="Moyenne" strokeWidth={2} />
                      <Line type="monotone" dataKey="median_approval_days" stroke="#3B82F6" name="Médiane" strokeWidth={2} />
                      <Line type="monotone" dataKey="p95_approval_days" stroke="#EF4444" name="P95" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-64 text-gray-500">Aucune donnée disponible</div>
                )}
              </div>
            </div>

            {/* Tableau détaillé des délais par statut */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mt-6">
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Détail des Délais par Statut et Étape
                </h4>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setShowTableFilters(!showTableFilters)}
                    className="flex items-center space-x-2 px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    <Filter className="w-4 h-4" />
                    <span>Filtres {activeTableFilters > 0 && `(${activeTableFilters})`}</span>
                  </button>
                  {activeTableFilters > 0 && (
                    <button
                      onClick={() => {
                        setTableFilterStatus('');
                        setTableFilterEtape('');
                        setTableFilterDelayMin('');
                        setTableFilterDelayMax('');
                      }}
                      className="flex items-center space-x-2 px-3 py-1 bg-gray-300 dark:bg-gray-600 text-gray-900 dark:text-white rounded-lg hover:bg-gray-400 dark:hover:bg-gray-700 transition-colors text-sm"
                    >
                      <X className="w-4 h-4" />
                      <span>Réinitialiser</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Panel des filtres du tableau */}
              {showTableFilters && (
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-4 border border-gray-200 dark:border-gray-600">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {/* Filtre par Statut */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Statut
                      </label>
                      <select
                        value={tableFilterStatus}
                        onChange={(e) => setTableFilterStatus(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                      >
                        <option value="">Tous les statuts</option>
                        {tableUniqueStatuses.map((status) => (
                          <option key={status} value={status}>
                            {status}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Filtre par Étape */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Étape
                      </label>
                      <select
                        value={tableFilterEtape}
                        onChange={(e) => setTableFilterEtape(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                      >
                        <option value="">Toutes les étapes</option>
                        {tableUniqueEtapes.map((etape) => (
                          <option key={etape} value={etape}>
                            {etape}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Filtre Délai Moyen Min */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Délai Moy. Min (j)
                      </label>
                      <input
                        type="number"
                        value={tableFilterDelayMin}
                        onChange={(e) => setTableFilterDelayMin(e.target.value)}
                        placeholder="Min"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                      />
                    </div>

                    {/* Filtre Délai Moyen Max */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Délai Moy. Max (j)
                      </label>
                      <input
                        type="number"
                        value={tableFilterDelayMax}
                        onChange={(e) => setTableFilterDelayMax(e.target.value)}
                        placeholder="Max"
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
                      />
                    </div>
                  </div>
                </div>
              )}

              {filteredDetailedTable.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase">Statut</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-gray-700 dark:text-gray-300 uppercase">Étape</th>
                        <th className="px-4 py-2 text-center text-xs font-medium text-gray-700 dark:text-gray-300 uppercase">Enreg.</th>
                        <th className="px-4 py-2 text-center text-xs font-medium text-gray-700 dark:text-gray-300 uppercase">Conventions</th>
                        <th className="px-4 py-2 text-center text-xs font-medium text-gray-700 dark:text-gray-300 uppercase">Délai Moy (j)</th>
                        <th className="px-4 py-2 text-center text-xs font-medium text-gray-700 dark:text-gray-300 uppercase">Médian (j)</th>
                        <th className="px-4 py-2 text-center text-xs font-medium text-gray-700 dark:text-gray-300 uppercase">P95 (j)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredDetailedTable.map((row, idx) => (
                        <tr key={idx} className="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                          <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{row.statut}</td>
                          <td className="px-4 py-3 text-sm text-gray-700 dark:text-gray-300">{row.etape_actuelle}</td>
                          <td className="px-4 py-3 text-sm text-center text-gray-700 dark:text-gray-300">{row.records_count}</td>
                          <td className="px-4 py-3 text-sm text-center text-gray-700 dark:text-gray-300">{formatNumber(row.total_conventions)}</td>
                          <td className="px-4 py-3 text-sm text-center text-gray-700 dark:text-gray-300 font-semibold">{formatDays(row.avg_approval_days)}</td>
                          <td className="px-4 py-3 text-sm text-center text-gray-700 dark:text-gray-300">{formatDays(row.median_approval_days)}</td>
                          <td className="px-4 py-3 text-sm text-center text-gray-700 dark:text-gray-300 font-semibold text-orange-600 dark:text-orange-400">{formatDays(row.p95_approval_days)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="flex items-center justify-center h-32 text-gray-500">Aucune donnée disponible</div>
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
};

export default ComplianceCompliance;
