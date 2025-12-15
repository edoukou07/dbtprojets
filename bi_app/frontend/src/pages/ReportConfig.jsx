import React, { useState, useEffect } from 'react'
import { reportsAPI, financierAPI, occupationAPI, clientsAPI, operationnelAPI } from '../services/api'
import api from '../services/api'
import { Calendar, Mail, FileText, Clock, Send, Edit2, Trash2, CheckCircle, Clock8, AlertCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { pdf } from '@react-pdf/renderer'
import DashboardPDF from '../components/pdf/DashboardPDF'
import FinancierPDF from '../components/pdf/FinancierPDF'
import OccupationPDF from '../components/pdf/OccupationPDF'
import PortefeuillePDF from '../components/pdf/PortefeuillePDF'
import OperationnelPDF from '../components/pdf/OperationnelPDF'
import AlertsAnalyticsPDF from '../components/pdf/AlertsAnalyticsPDF'

const ReportConfig = () => {
  const { user } = useAuth()
  const [name, setName] = useState('Rapport automatisé')
  const [dashboard, setDashboard] = useState('financier') // Deprecated, kept for backward compatibility
  const [dashboards, setDashboards] = useState(['financier']) // Nouveau: liste de dashboards
  const [datetime, setDatetime] = useState('')
  const [recipients, setRecipients] = useState('')
  const [message, setMessage] = useState(null)
  const [reports, setReports] = useState([])
  const [editingReport, setEditingReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [deletingId, setDeletingId] = useState(null)
  
  // Recurrence state
  const [isRecurring, setIsRecurring] = useState(false)
  const [recurrenceType, setRecurrenceType] = useState('none')
  const [recurrenceInterval, setRecurrenceInterval] = useState(1)
  const [recurrenceMinute, setRecurrenceMinute] = useState(null)
  const [recurrenceHour, setRecurrenceHour] = useState(null)
  const [recurrenceDaysOfWeek, setRecurrenceDaysOfWeek] = useState([])
  const [recurrenceDayOfMonth, setRecurrenceDayOfMonth] = useState(null)
  const [recurrenceWeekOfMonth, setRecurrenceWeekOfMonth] = useState(null)
  const [recurrenceMonth, setRecurrenceMonth] = useState(null)
  const [recurrenceWorkdaysOnly, setRecurrenceWorkdaysOnly] = useState(false)
  const [recurrenceHourRangeStart, setRecurrenceHourRangeStart] = useState('')
  const [recurrenceHourRangeEnd, setRecurrenceHourRangeEnd] = useState('')
  const [recurrenceHourRangeInterval, setRecurrenceHourRangeInterval] = useState(60)
  const [recurrenceEndDate, setRecurrenceEndDate] = useState('')

  const availableDashboards = [
    { value: 'dashboard', label: 'Tableau de bord', icon: '📊', color: 'bg-blue-50 border-blue-200' },
    { value: 'financier', label: 'Performance Financière', icon: '💰', color: 'bg-green-50 border-green-200' },
    { value: 'occupation', label: 'Occupation Zones', icon: '📍', color: 'bg-purple-50 border-purple-200' },
    { value: 'clients', label: 'Portefeuille Clients', icon: '👥', color: 'bg-orange-50 border-orange-200' },
    { value: 'operationnel', label: 'KPI Opérationnels', icon: '⚙️', color: 'bg-indigo-50 border-indigo-200' },
    { value: 'alerts', label: 'Alerts Analytics', icon: '🔔', color: 'bg-red-50 border-red-200' },
  ]

  useEffect(() => {
    const fetchReports = async (showLoading = true) => {
      try {
        if (showLoading) {
          setLoading(true)
        }
        const res = await reportsAPI.list()
        setReports(res.data.results || [])
      } catch (e) {
        console.error('Erreur lors du chargement des rapports:', e)
        setReports([])
      } finally {
        if (showLoading) {
          setLoading(false)
        }
      }
    }
    
    // Chargement initial avec indicateur de chargement
    fetchReports(true)
    
    // Rafraîchir la liste toutes les 30 secondes pour voir les statuts mis à jour
    // (les envois sont maintenant gérés par le management command backend)
    const refreshInterval = setInterval(() => fetchReports(false), 30000)
    
    return () => {
      clearInterval(refreshInterval)
    }
  }, [])

  const handleEdit = (report) => {
    setEditingReport(report)
    setName(report.name)
    setDashboard(report.dashboard)
    setDatetime(new Date(report.scheduled_at).toISOString().slice(0, 16))
    setRecipients(report.recipients || '')
    // Recurrence fields
    setIsRecurring(report.is_recurring || false)
    setRecurrenceType(report.recurrence_type || 'none')
    setRecurrenceInterval(report.recurrence_interval || 1)
    setRecurrenceMinute(report.recurrence_minute)
    setRecurrenceHour(report.recurrence_hour)
    setRecurrenceDaysOfWeek(report.recurrence_days_of_week || [])
    setRecurrenceDayOfMonth(report.recurrence_day_of_month)
    setRecurrenceWeekOfMonth(report.recurrence_week_of_month)
    setRecurrenceMonth(report.recurrence_month)
    setRecurrenceWorkdaysOnly(report.recurrence_workdays_only || false)
    setRecurrenceHourRangeStart(report.recurrence_hour_range_start || '')
    setRecurrenceHourRangeEnd(report.recurrence_hour_range_end || '')
    setRecurrenceHourRangeInterval(report.recurrence_hour_range_interval || 60)
    setRecurrenceEndDate(report.recurrence_end_date ? new Date(report.recurrence_end_date).toISOString().slice(0, 16) : '')
    setMessage(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleCancel = () => {
    setEditingReport(null)
    setName('Rapport automatisé')
    setDashboard('financier')
    setDashboards(['financier'])
    setDatetime('')
    setRecipients('')
    // Reset recurrence fields
    setIsRecurring(false)
    setRecurrenceType('none')
    setRecurrenceInterval(1)
    setRecurrenceMinute(null)
    setRecurrenceHour(null)
    setRecurrenceDaysOfWeek([])
    setRecurrenceDayOfMonth(null)
    setRecurrenceWeekOfMonth(null)
    setRecurrenceMonth(null)
    setRecurrenceWorkdaysOnly(false)
    setRecurrenceHourRangeStart('')
    setRecurrenceHourRangeEnd('')
    setRecurrenceHourRangeInterval(60)
    setRecurrenceEndDate('')
    setMessage(null)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette programmation ?')) {
      return
    }

    try {
      setDeletingId(id)
      await reportsAPI.delete(id)
      setMessage({ type: 'success', text: '✓ Programmation supprimée' })
      
      // Refresh the list
      const listRes = await reportsAPI.list()
      setReports(listRes.data.results || [])
    } catch (e) {
      setMessage({ 
        type: 'error', 
        text: 'Erreur: ' + (e?.response?.data?.detail || e.message) 
      })
    } finally {
      setDeletingId(null)
    }
  }

  // Fonction pour générer un PDF pour un dashboard spécifique
  const generateDashboardPDF = async (dashboardName) => {
    try {
      switch (dashboardName) {
        case 'dashboard': {
          // Charger les données pour le dashboard général
          const [financierRes, occupationRes, clientsRes, operationnelRes] = await Promise.all([
            financierAPI.getSummary(),
            occupationAPI.getSummary(),
            clientsAPI.getSummary(),
            operationnelAPI.getSummary(),
          ])
          
          const blob = await pdf(
            <DashboardPDF
              financierData={financierRes.data}
              occupationData={occupationRes.data}
              clientsData={clientsRes.data}
              operationnelData={operationnelRes.data}
            />
          ).toBlob()
          return blob
        }
        
        case 'financier': {
          const selectedYear = new Date().getFullYear()
          const [summaryRes, tendancesMensuellesRes, tendancesTrimestriellesRes, topZonesRes, comparaisonRes] = await Promise.all([
            financierAPI.getSummary({ annee: selectedYear }),
            financierAPI.getTendancesMensuelles(selectedYear),
            financierAPI.getTendancesTrimestrielles(selectedYear),
            financierAPI.getTopZonesPerformance(selectedYear, 5),
            financierAPI.getComparaisonAnnuelle(selectedYear),
          ])
          
          const blob = await pdf(
            <FinancierPDF
              summary={summaryRes.data}
              tendancesMensuelles={tendancesMensuellesRes.data}
              tendancesTrimestrielles={tendancesTrimestriellesRes.data}
              topZones={topZonesRes.data}
              comparaison={comparaisonRes.data}
              selectedYear={selectedYear}
            />
          ).toBlob()
          return blob
        }
        
        case 'occupation': {
          const [summaryRes, byZoneRes, disponibiliteRes, topZonesRes] = await Promise.all([
            occupationAPI.getSummary(),
            occupationAPI.getByZone(),
            occupationAPI.getDisponibilite(),
            occupationAPI.getTopZones(5),
          ])
          
          const blob = await pdf(
            <OccupationPDF
              summary={summaryRes.data}
              allZonesData={byZoneRes.data}
              disponibilite={disponibiliteRes.data}
              topZones={topZonesRes.data}
            />
          ).toBlob()
          return blob
        }
        
        case 'clients': {
          const [summaryRes, segmentationRes, topClientsRes, atRiskRes, occupationRes] = await Promise.all([
            clientsAPI.getSummary(),
            clientsAPI.getSegmentation(),
            clientsAPI.getTopClients(10),
            clientsAPI.getAtRisk(),
            clientsAPI.getAnalyseOccupation(),
          ])
          
          // Essayer de récupérer analyse_comportement, mais ne pas échouer si ça échoue
          let comportementData = null
          try {
            const comportementRes = await clientsAPI.getAnalyseComportement()
            comportementData = comportementRes.data
          } catch (error) {
            console.warn('Erreur lors de la récupération de analyse_comportement, continuation sans ces données:', error)
            // Continuer sans ces données
          }
          
          const blob = await pdf(
            <PortefeuillePDF
              summary={summaryRes.data}
              segmentation={segmentationRes.data}
              topClients={topClientsRes.data}
              atRisk={atRiskRes.data}
              comportement={comportementData}
              occupation={occupationRes.data}
            />
          ).toBlob()
          return blob
        }
        
        case 'operationnel': {
          const [summaryRes, indicateursClesRes, performanceCollectesRes, performanceAttributionsRes, performanceFacturationRes] = await Promise.all([
            operationnelAPI.getSummary(),
            operationnelAPI.getIndicateursCles(),
            operationnelAPI.getPerformanceCollectes(),
            operationnelAPI.getPerformanceAttributions(),
            operationnelAPI.getPerformanceFacturation(),
          ])
          
          const blob = await pdf(
            <OperationnelPDF
              summary={summaryRes.data}
              indicateursCles={indicateursClesRes.data}
              performanceCollectes={performanceCollectesRes.data}
              performanceAttributions={performanceAttributionsRes.data}
              performanceFacturation={performanceFacturationRes.data}
            />
          ).toBlob()
          return blob
        }
        
        case 'alerts': {
          // Pour les alertes, on a besoin de charger les données depuis l'API
          const alertsRes = await api.get('/alerts/')
          
          const [occupationByZoneRes, occupationSummaryRes, financierRes] = await Promise.all([
            occupationAPI.getByZone(), // Pour la heatmap (données par zone)
            occupationAPI.getSummary(), // Pour le taux d'occupation moyen correct
            financierAPI.getSummary(),
          ])
          
          const blob = await pdf(
            <AlertsAnalyticsPDF
              alerts={alertsRes.data.results || alertsRes.data || []}
              occupationData={occupationByZoneRes.data} // Données par zone pour la heatmap
              occupationSummary={occupationSummaryRes.data} // Summary pour le taux moyen
              financialData={financierRes.data}
              timeRange="30"
            />
          ).toBlob()
          return blob
        }
        
        default:
          throw new Error(`Dashboard inconnu: ${dashboardName}`)
      }
    } catch (error) {
      console.error(`Erreur lors de la génération du PDF pour ${dashboardName}:`, error)
      throw error
    }
  }

  // Fonction pour envoyer les PDFs au backend
  const sendPDFsToBackend = async (reportId, dashboardList) => {
    const formData = new FormData()
    
    // Générer un PDF pour chaque dashboard
    for (const dashboard of dashboardList) {
      try {
        console.log(`Génération du PDF pour ${dashboard}...`)
        const blob = await generateDashboardPDF(dashboard)
        const file = new File([blob], `${dashboard}.pdf`, { type: 'application/pdf' })
        formData.append(`pdf_${dashboard}`, file)
        console.log(`PDF généré avec succès pour ${dashboard}`)
      } catch (error) {
        console.error(`Erreur lors de la génération du PDF pour ${dashboard}:`, error)
        // Ne pas échouer complètement, continuer avec les autres dashboards
        // mais loguer l'erreur
        throw new Error(`Impossible de générer le PDF pour ${dashboard}: ${error.message}`)
      }
    }
    
    // Envoyer les PDFs au backend
    try {
      console.log(`Envoi des PDFs au backend pour le rapport ${reportId}...`)
      const response = await api.post(
        `/reports/${reportId}/send_now/`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      console.log('PDFs envoyés avec succès')
      return response.data
    } catch (error) {
      console.error('Erreur lors de l\'envoi des PDFs au backend:', error)
      throw error
    }
  }

  const handleSchedule = async (sendNow = false) => {
    setMessage(null)
    if (!name.trim() || dashboards.length === 0 || !recipients.trim()) {
      setMessage({ type: 'error', text: 'Veuillez remplir tous les champs et sélectionner au moins un dashboard' })
      return
    }

    try {
      setLoading(true)
      
      // Toujours générer les PDFs avec react-pdf lors de la planification
      console.log('Génération des PDFs pour la planification...')
      const formData = new FormData()
      
      // Ajouter les données du rapport au FormData
      formData.append('name', name)
      formData.append('dashboards', JSON.stringify(dashboards))
      formData.append('scheduled_at', datetime || new Date().toISOString())
      formData.append('recipients', recipients)
      
      // Ajouter les champs de récurrence
      formData.append('is_recurring', isRecurring.toString())
      formData.append('recurrence_type', recurrenceType)
      if (isRecurring && recurrenceType !== 'none') {
        if (recurrenceInterval) formData.append('recurrence_interval', recurrenceInterval.toString())
        if (recurrenceMinute !== null && recurrenceMinute !== '') formData.append('recurrence_minute', recurrenceMinute.toString())
        if (recurrenceHour !== null && recurrenceHour !== '') formData.append('recurrence_hour', recurrenceHour.toString())
        if (recurrenceDaysOfWeek.length > 0) formData.append('recurrence_days_of_week', JSON.stringify(recurrenceDaysOfWeek))
        if (recurrenceDayOfMonth !== null && recurrenceDayOfMonth !== '') formData.append('recurrence_day_of_month', recurrenceDayOfMonth.toString())
        if (recurrenceWeekOfMonth !== null && recurrenceWeekOfMonth !== '') formData.append('recurrence_week_of_month', recurrenceWeekOfMonth.toString())
        if (recurrenceMonth !== null && recurrenceMonth !== '') formData.append('recurrence_month', recurrenceMonth.toString())
        formData.append('recurrence_workdays_only', recurrenceWorkdaysOnly.toString())
        if (recurrenceHourRangeStart) formData.append('recurrence_hour_range_start', recurrenceHourRangeStart)
        if (recurrenceHourRangeEnd) formData.append('recurrence_hour_range_end', recurrenceHourRangeEnd)
        if (recurrenceHourRangeInterval) formData.append('recurrence_hour_range_interval', recurrenceHourRangeInterval.toString())
        if (recurrenceEndDate) formData.append('recurrence_end_date', new Date(recurrenceEndDate).toISOString())
      }
      
      // Générer un PDF pour chaque dashboard
      for (const dashboard of dashboards) {
        try {
          console.log(`Génération du PDF pour ${dashboard}...`)
          const blob = await generateDashboardPDF(dashboard)
          const file = new File([blob], `${dashboard}.pdf`, { type: 'application/pdf' })
          formData.append(`pdf_${dashboard}`, file)
          console.log(`PDF généré avec succès pour ${dashboard}`)
        } catch (error) {
          console.error(`Erreur lors de la génération du PDF pour ${dashboard}:`, error)
          throw new Error(`Impossible de générer le PDF pour ${dashboard}: ${error.message}`)
        }
      }

      let res
      if (editingReport) {
        // Mise à jour avec PDFs
        res = await api.put(
          `/reports/${editingReport.id}/`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        )
        setMessage({ type: 'success', text: '✓ Planification mise à jour avec succès' })
      } else {
        // Création avec PDFs
        res = await api.post(
          '/reports/',
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        )

        if (sendNow && res?.data?.id) {
          // Envoyer immédiatement avec les PDFs générés par react-pdf
          try {
            await sendPDFsToBackend(res.data.id, dashboards)
            setMessage({ type: 'success', text: '✓ Rapport envoyé immédiatement' })
          } catch (error) {
            console.error('Erreur lors de l\'envoi immédiat:', error)
            setMessage({ 
              type: 'error', 
              text: 'Erreur lors de l\'envoi: ' + (error?.response?.data?.detail || error.message) 
            })
          }
        } else {
          setMessage({ type: 'success', text: '✓ Planification enregistrée avec PDFs générés' })
        }
      }

      // Refresh the list
      const listRes = await reportsAPI.list()
      setReports(listRes.data.results || [])

      if (!editingReport) {
        handleCancel() // Reset form
      } else {
        handleCancel()
      }
    } catch (e) {
      console.error('Erreur lors de la planification:', e)
      setMessage({ 
        type: 'error', 
        text: 'Erreur: ' + (e?.response?.data?.detail || e.message) 
      })
    } finally {
      setLoading(false)
    }
  }

  const getDashboardInfo = (dashboardValue) => {
    return availableDashboards.find(d => d.value === dashboardValue)
  }

  const getDashboardsDisplay = (report) => {
    // Gérer l'affichage pour les anciens rapports (dashboard) et les nouveaux (dashboards)
    if (report.dashboards && report.dashboards.length > 0) {
      return report.dashboards.map(db => {
        const info = getDashboardInfo(db)
        return info ? info.label : db
      }).join(', ')
    } else if (report.dashboard) {
      const info = getDashboardInfo(report.dashboard)
      return info ? info.label : report.dashboard
    }
    return 'Aucun'
  }

  const getDashboardsIcons = (report) => {
    // Retourner les icônes des dashboards sélectionnés
    if (report.dashboards && report.dashboards.length > 0) {
      return report.dashboards.map(db => {
        const info = getDashboardInfo(db)
        return info ? info.icon : '📊'
      }).join(' ')
    } else if (report.dashboard) {
      const info = getDashboardInfo(report.dashboard)
      return info ? info.icon : '📊'
    }
    return '📊'
  }

  // Vérifier si l'utilisateur est admin
  if (!user?.is_staff || user?.username !== 'admin') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 flex items-start space-x-4">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h2 className="text-lg font-bold text-red-900">Accès refusé</h2>
              <p className="text-red-700 mt-2">
                Seul l'administrateur SIGETI peut accéder à cette page.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="flex items-center gap-3 mb-2">
            <FileText size={32} />
            <h1 className="text-3xl font-bold">Générateur de Rapports</h1>
          </div>
          <p className="text-blue-100 text-lg">Créez et programmez des rapports automatisés pour vos tableaux de bord</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
            message.type === 'success' 
              ? 'bg-green-100 border border-green-300 text-green-800' 
              : 'bg-red-100 border border-red-300 text-red-800'
          }`}>
            {message.type === 'success' ? <CheckCircle size={20} /> : <Mail size={20} />}
            {message.text}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Formulaire */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6 sticky top-6">
              <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <Send size={22} className="text-blue-600" />
                {editingReport ? 'Modifier la programmation' : 'Créer un nouveau rapport'}
              </h2>

              {/* Sélection du Dashboard (multiple) */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Dashboards {dashboards.length > 0 && <span className="text-xs font-normal text-gray-500">({dashboards.length} sélectionné{dashboards.length > 1 ? 's' : ''})</span>}
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {availableDashboards.map(d => (
                    <button
                      key={d.value}
                      type="button"
                      onClick={() => {
                        const value = d.value
                        if (dashboards.includes(value)) {
                          // Désélectionner si déjà sélectionné (mais garder au moins un)
                          if (dashboards.length > 1) {
                            const newDashboards = dashboards.filter(db => db !== value)
                            setDashboards(newDashboards)
                            setDashboard(newDashboards[0]) // Pour compatibilité
                          }
                        } else {
                          // Ajouter à la sélection
                          const newDashboards = [...dashboards, value]
                          setDashboards(newDashboards)
                          setDashboard(newDashboards[0]) // Pour compatibilité
                        }
                      }}
                      className={`p-3 rounded-lg border-2 transition-all cursor-pointer ${
                        dashboards.includes(d.value)
                          ? `border-blue-600 ${d.color} bg-opacity-100`
                          : `border-gray-200 bg-gray-50 hover:border-gray-300`
                      }`}
                    >
                      <div className="text-xl mb-1">{d.icon}</div>
                      <div className="text-xs font-medium text-gray-700 line-clamp-2">{d.label}</div>
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-2">Cliquez sur un dashboard pour le sélectionner/désélectionner</p>
              </div>

              {/* Nom du rapport */}
              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2">Nom du rapport</label>
                <input 
                  type="text" 
                  value={name} 
                  onChange={(e) => setName(e.target.value)} 
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Rapport Financier Mensuel"
                />
              </div>

              {/* Date et Heure */}
              <div className="mb-4">
                <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                  <Calendar size={16} />
                  Date & Heure (Première occurrence)
                </label>
                <input 
                  type="datetime-local" 
                  value={datetime} 
                  onChange={(e) => setDatetime(e.target.value)} 
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {!datetime && <p className="text-xs text-gray-500 mt-1">Laissez vide pour un envoi immédiat</p>}
              </div>

              {/* Récurrence */}
              <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-sm font-semibold text-gray-700 flex items-center gap-2">
                    <Clock size={16} />
                    Envoie récurrent
                  </label>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={isRecurring}
                      onChange={(e) => {
                        setIsRecurring(e.target.checked)
                        if (!e.target.checked) {
                          setRecurrenceType('none')
                        }
                      }}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                {isRecurring && (
                  <div className="space-y-4 mt-4">
                    {/* Type de récurrence */}
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-2">Type de récurrence</label>
                      <select
                        value={recurrenceType}
                        onChange={(e) => setRecurrenceType(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="minute">Par minute</option>
                        <option value="hour">Par heure</option>
                        <option value="daily">Quotidien</option>
                        <option value="weekly">Hebdomadaire</option>
                        <option value="monthly">Mensuel</option>
                        <option value="yearly">Annuel</option>
                        <option value="custom">Personnalisé</option>
                      </select>
                    </div>

                    {/* Configuration selon le type */}
                    {recurrenceType === 'minute' && (
                      <div className="space-y-2">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Toutes les X minutes</label>
                          <input
                            type="number"
                            min="1"
                            value={recurrenceInterval}
                            onChange={(e) => setRecurrenceInterval(parseInt(e.target.value) || 1)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            placeholder="1"
                          />
                        </div>
                      </div>
                    )}

                    {recurrenceType === 'hour' && (
                      <div className="space-y-2">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Toutes les X heures</label>
                          <input
                            type="number"
                            min="1"
                            value={recurrenceInterval}
                            onChange={(e) => setRecurrenceInterval(parseInt(e.target.value) || 1)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                          />
                        </div>
                        <div className="border-t pt-2">
                          <label className="block text-xs font-medium text-gray-700 mb-2">Plage horaire</label>
                          <div className="grid grid-cols-2 gap-2 mb-2">
                            <input
                              type="time"
                              value={recurrenceHourRangeStart}
                              onChange={(e) => setRecurrenceHourRangeStart(e.target.value)}
                              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                              placeholder="Début"
                            />
                            <input
                              type="time"
                              value={recurrenceHourRangeEnd}
                              onChange={(e) => setRecurrenceHourRangeEnd(e.target.value)}
                              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                              placeholder="Fin"
                            />
                          </div>
                          <input
                            type="number"
                            min="1"
                            value={recurrenceHourRangeInterval}
                            onChange={(e) => setRecurrenceHourRangeInterval(parseInt(e.target.value) || 60)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            placeholder="Intervalle (minutes)"
                          />
                        </div>
                      </div>
                    )}

                    {recurrenceType === 'daily' && (
                      <div className="space-y-2">
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Heure (0-23)</label>
                            <input
                              type="number"
                              min="0"
                              max="23"
                              value={recurrenceHour || ''}
                              onChange={(e) => setRecurrenceHour(e.target.value ? parseInt(e.target.value) : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Minute (0-59)</label>
                            <input
                              type="number"
                              min="0"
                              max="59"
                              value={recurrenceMinute || ''}
                              onChange={(e) => setRecurrenceMinute(e.target.value ? parseInt(e.target.value) : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            />
                          </div>
                        </div>
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={recurrenceWorkdaysOnly}
                            onChange={(e) => setRecurrenceWorkdaysOnly(e.target.checked)}
                            className="rounded border-gray-300"
                          />
                          <span className="text-xs text-gray-700">Uniquement jours ouvrables (lundi-vendredi)</span>
                        </label>
                      </div>
                    )}

                    {recurrenceType === 'weekly' && (
                      <div className="space-y-2">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-2">Jours de la semaine</label>
                          <div className="grid grid-cols-7 gap-1">
                            {['L', 'M', 'M', 'J', 'V', 'S', 'D'].map((day, idx) => (
                              <button
                                key={idx}
                                type="button"
                                onClick={() => {
                                  const newDays = recurrenceDaysOfWeek.includes(idx)
                                    ? recurrenceDaysOfWeek.filter(d => d !== idx)
                                    : [...recurrenceDaysOfWeek, idx]
                                  setRecurrenceDaysOfWeek(newDays.sort())
                                }}
                                className={`px-2 py-1 text-xs rounded border ${
                                  recurrenceDaysOfWeek.includes(idx)
                                    ? 'bg-blue-600 text-white border-blue-600'
                                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                                }`}
                              >
                                {day}
                              </button>
                            ))}
                          </div>
                          <div className="flex gap-2 mt-2">
                            <button
                              type="button"
                              onClick={() => setRecurrenceDaysOfWeek([0, 1, 2, 3, 4])}
                              className="text-xs px-2 py-1 bg-gray-100 rounded hover:bg-gray-200"
                            >
                              Jours ouvrables
                            </button>
                            <button
                              type="button"
                              onClick={() => setRecurrenceDaysOfWeek([5, 6])}
                              className="text-xs px-2 py-1 bg-gray-100 rounded hover:bg-gray-200"
                            >
                              Week-end
                            </button>
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Heure (0-23)</label>
                            <input
                              type="number"
                              min="0"
                              max="23"
                              value={recurrenceHour || ''}
                              onChange={(e) => setRecurrenceHour(e.target.value ? parseInt(e.target.value) : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Minute (0-59)</label>
                            <input
                              type="number"
                              min="0"
                              max="59"
                              value={recurrenceMinute || ''}
                              onChange={(e) => setRecurrenceMinute(e.target.value ? parseInt(e.target.value) : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            />
                          </div>
                        </div>
                      </div>
                    )}

                    {recurrenceType === 'monthly' && (
                      <div className="space-y-2">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-2">Type</label>
                          <select
                            value={recurrenceWeekOfMonth ? 'relative' : recurrenceDayOfMonth === -1 ? 'last' : 'fixed'}
                            onChange={(e) => {
                              if (e.target.value === 'relative') {
                                setRecurrenceDayOfMonth(null)
                                setRecurrenceWeekOfMonth(1)
                                setRecurrenceDaysOfWeek([0])
                              } else if (e.target.value === 'last') {
                                setRecurrenceDayOfMonth(-1)
                                setRecurrenceWeekOfMonth(null)
                              } else {
                                setRecurrenceDayOfMonth(1)
                                setRecurrenceWeekOfMonth(null)
                              }
                            }}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                          >
                            <option value="fixed">Jour fixe du mois</option>
                            <option value="relative">Jour relatif (ex: 1er lundi)</option>
                            <option value="last">Dernier jour du mois</option>
                          </select>
                        </div>
                        {recurrenceWeekOfMonth ? (
                          <div className="space-y-2">
                            <div>
                              <label className="block text-xs font-medium text-gray-700 mb-1">Semaine (1-4)</label>
                              <input
                                type="number"
                                min="1"
                                max="4"
                                value={recurrenceWeekOfMonth || 1}
                                onChange={(e) => setRecurrenceWeekOfMonth(parseInt(e.target.value) || 1)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-medium text-gray-700 mb-1">Jour de la semaine</label>
                              <select
                                value={recurrenceDaysOfWeek[0] ?? 0}
                                onChange={(e) => setRecurrenceDaysOfWeek([parseInt(e.target.value)])}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                              >
                                <option value="0">Lundi</option>
                                <option value="1">Mardi</option>
                                <option value="2">Mercredi</option>
                                <option value="3">Jeudi</option>
                                <option value="4">Vendredi</option>
                                <option value="5">Samedi</option>
                                <option value="6">Dimanche</option>
                              </select>
                            </div>
                          </div>
                        ) : recurrenceDayOfMonth !== -1 ? (
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Jour du mois (1-31)</label>
                            <input
                              type="number"
                              min="1"
                              max="31"
                              value={recurrenceDayOfMonth || ''}
                              onChange={(e) => setRecurrenceDayOfMonth(e.target.value ? parseInt(e.target.value) : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            />
                          </div>
                        ) : null}
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Heure (0-23)</label>
                            <input
                              type="number"
                              min="0"
                              max="23"
                              value={recurrenceHour || ''}
                              onChange={(e) => setRecurrenceHour(e.target.value ? parseInt(e.target.value) : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Minute (0-59)</label>
                            <input
                              type="number"
                              min="0"
                              max="59"
                              value={recurrenceMinute || ''}
                              onChange={(e) => setRecurrenceMinute(e.target.value ? parseInt(e.target.value) : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            />
                          </div>
                        </div>
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={recurrenceWorkdaysOnly}
                            onChange={(e) => setRecurrenceWorkdaysOnly(e.target.checked)}
                            className="rounded border-gray-300"
                          />
                          <span className="text-xs text-gray-700">Premier jour ouvrable du mois</span>
                        </label>
                      </div>
                    )}

                    {recurrenceType === 'yearly' && (
                      <div className="space-y-2">
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Mois (1-12)</label>
                            <input
                              type="number"
                              min="1"
                              max="12"
                              value={recurrenceMonth || ''}
                              onChange={(e) => setRecurrenceMonth(e.target.value ? parseInt(e.target.value) : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Jour (1-31)</label>
                            <input
                              type="number"
                              min="1"
                              max="31"
                              value={recurrenceDayOfMonth || ''}
                              onChange={(e) => setRecurrenceDayOfMonth(e.target.value ? parseInt(e.target.value) : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Heure (0-23)</label>
                            <input
                              type="number"
                              min="0"
                              max="23"
                              value={recurrenceHour || ''}
                              onChange={(e) => setRecurrenceHour(e.target.value ? parseInt(e.target.value) : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            />
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">Minute (0-59)</label>
                            <input
                              type="number"
                              min="0"
                              max="59"
                              value={recurrenceMinute || ''}
                              onChange={(e) => setRecurrenceMinute(e.target.value ? parseInt(e.target.value) : null)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                            />
                          </div>
                        </div>
                      </div>
                    )}

                    {recurrenceType === 'custom' && (
                      <div className="space-y-2">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">Tous les X jours</label>
                          <input
                            type="number"
                            min="1"
                            value={recurrenceInterval}
                            onChange={(e) => setRecurrenceInterval(parseInt(e.target.value) || 1)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                          />
                        </div>
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={recurrenceWorkdaysOnly}
                            onChange={(e) => setRecurrenceWorkdaysOnly(e.target.checked)}
                            className="rounded border-gray-300"
                          />
                          <span className="text-xs text-gray-700">Uniquement jours ouvrables</span>
                        </label>
                      </div>
                    )}

                    {/* Date de fin optionnelle */}
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Date de fin (optionnelle)</label>
                      <input
                        type="datetime-local"
                        value={recurrenceEndDate}
                        onChange={(e) => setRecurrenceEndDate(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Destinataires */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
                  <Mail size={16} />
                  Destinataires
                </label>
                <textarea 
                  value={recipients} 
                  onChange={(e) => setRecipients(e.target.value)} 
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  rows={3}
                  placeholder="email1@example.com, email2@example.com"
                />
                <p className="text-xs text-gray-500 mt-1">Séparés par des virgules</p>
              </div>

              {/* Actions */}
              <div className="flex flex-col gap-2">
                <button 
                  onClick={() => handleSchedule(false)} 
                  disabled={loading}
                  className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <Clock8 size={18} />
                  {editingReport ? 'Mettre à jour' : 'Planifier'}
                </button>
                {!editingReport && (
                  <button 
                    onClick={() => handleSchedule(true)} 
                    disabled={loading}
                    className="w-full px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 font-medium transition-colors flex items-center justify-center gap-2"
                  >
                    <Send size={18} />
                    Envoyer maintenant
                  </button>
                )}
                {editingReport && (
                  <button 
                    onClick={handleCancel}
                    className="w-full px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium transition-colors"
                  >
                    Annuler
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Liste des programmations */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                <FileText size={22} className="text-blue-600" />
                Programmations actives
                {reports.length > 0 && <span className="ml-auto text-sm font-normal text-gray-500">({reports.length})</span>}
              </h2>

              {loading ? (
                <div className="flex justify-center items-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                </div>
              ) : reports.length === 0 ? (
                <div className="text-center py-12 bg-gray-50 rounded-lg">
                  <FileText size={48} className="mx-auto text-gray-300 mb-4" />
                  <p className="text-gray-500 text-lg">Aucune programmation pour le moment</p>
                  <p className="text-gray-400 text-sm mt-2">Créez votre premier rapport à gauche</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {reports.map(report => (
                    <div key={report.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-800 text-lg flex items-center gap-2">
                            {getDashboardsIcons(report)}
                            {report.name}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            {getDashboardsDisplay(report)}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          report.sent 
                            ? 'bg-green-100 text-green-800 flex items-center gap-1' 
                            : 'bg-yellow-100 text-yellow-800 flex items-center gap-1'
                        }`}>
                          {report.sent ? <CheckCircle size={14} /> : <Clock8 size={14} />}
                          {report.sent ? 'Envoyé' : 'En attente'}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-3 text-sm mb-3 pb-3 border-b border-gray-100">
                        <div className="flex items-center gap-2 text-gray-700">
                          <Calendar size={16} className="text-gray-400" />
                          <div>
                            <div>{new Date(report.scheduled_at).toLocaleString('fr-FR')}</div>
                            {report.is_recurring && report.recurrence_type !== 'none' && (
                              <div className="text-xs text-blue-600 mt-1 flex items-center gap-1">
                                <Clock size={12} />
                                {report.parent_schedule ? `Occurrence #${report.occurrence_number}` : 'Récurrent'}
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2 text-gray-700">
                          <Mail size={16} className="text-gray-400" />
                          {report.recipients?.split(',').length || 0} destinataire(s)
                        </div>
                      </div>

                      {/* Informations de récurrence */}
                      {report.is_recurring && report.recurrence_type !== 'none' && (
                        <div className="mb-3 pb-3 border-b border-gray-100">
                          <div className="flex items-center gap-2 text-xs text-gray-600 mb-1">
                            <Clock size={12} />
                            <span className="font-medium">Récurrence:</span>
                            <span>
                              {report.recurrence_type === 'minute' && `Toutes les ${report.recurrence_interval || 1} minute(s)`}
                              {report.recurrence_type === 'hour' && `Toutes les ${report.recurrence_interval || 1} heure(s)`}
                              {report.recurrence_type === 'daily' && `Tous les jours${report.recurrence_workdays_only ? ' (jours ouvrables)' : ''}`}
                              {report.recurrence_type === 'weekly' && `Hebdomadaire`}
                              {report.recurrence_type === 'monthly' && `Mensuel`}
                              {report.recurrence_type === 'yearly' && `Annuel`}
                              {report.recurrence_type === 'custom' && `Tous les ${report.recurrence_interval || 1} jour(s)`}
                            </span>
                          </div>
                          {report.recurrence_end_date && (
                            <div className="text-xs text-gray-500">
                              Fin le {new Date(report.recurrence_end_date).toLocaleString('fr-FR', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                                second: '2-digit'
                              })}
                            </div>
                          )}
                          {!report.parent_schedule && (
                            <div className="text-xs text-gray-500 mt-1">
                              Occurrence #{report.occurrence_number || 1}
                            </div>
                          )}
                        </div>
                      )}

                      {report.sent && report.sent_at && (
                        <div className="text-xs text-gray-500 mb-3 pb-3 border-b border-gray-100">
                          Envoyé le {new Date(report.sent_at).toLocaleString('fr-FR')}
                        </div>
                      )}

                      <div className="flex gap-2">
                        <button 
                          onClick={() => handleEdit(report)}
                          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors font-medium text-sm"
                        >
                          <Edit2 size={16} />
                          Modifier
                        </button>
                        <button 
                          onClick={() => handleDelete(report.id)}
                          disabled={deletingId === report.id || loading}
                          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <Trash2 size={16} />
                          {deletingId === report.id ? 'Suppression...' : 'Supprimer'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReportConfig
