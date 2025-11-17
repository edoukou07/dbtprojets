import React, { useState, useEffect } from 'react'
import { reportsAPI } from '../services/api'
import { Calendar, Mail, FileText, Clock, Send, Edit2, Trash2, CheckCircle, Clock8, AlertCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const ReportConfig = () => {
  const { user } = useAuth()
  const [name, setName] = useState('Rapport automatisé')
  const [dashboard, setDashboard] = useState('financier')
  const [datetime, setDatetime] = useState('')
  const [recipients, setRecipients] = useState('')
  const [message, setMessage] = useState(null)
  const [reports, setReports] = useState([])
  const [editingReport, setEditingReport] = useState(null)
  const [loading, setLoading] = useState(false)
  const [deletingId, setDeletingId] = useState(null)

  const dashboards = [
    { value: 'dashboard', label: 'Tableau de bord', icon: '📊', color: 'bg-blue-50 border-blue-200' },
    { value: 'financier', label: 'Performance Financière', icon: '💰', color: 'bg-green-50 border-green-200' },
    { value: 'occupation', label: 'Occupation Zones', icon: '📍', color: 'bg-purple-50 border-purple-200' },
    { value: 'clients', label: 'Portefeuille Clients', icon: '👥', color: 'bg-orange-50 border-orange-200' },
    { value: 'operationnel', label: 'KPI Opérationnels', icon: '⚙️', color: 'bg-indigo-50 border-indigo-200' },
    { value: 'alerts', label: 'Alerts Analytics', icon: '🔔', color: 'bg-red-50 border-red-200' },
  ]

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true)
        const res = await reportsAPI.list()
        setReports(res.data.results || [])
      } catch (e) {
        console.error('Erreur lors du chargement des rapports:', e)
        setReports([])
      } finally {
        setLoading(false)
      }
    }
    fetchReports()
  }, [])

  const handleEdit = (report) => {
    setEditingReport(report)
    setName(report.name)
    setDashboard(report.dashboard)
    setDatetime(new Date(report.scheduled_at).toISOString().slice(0, 16))
    setRecipients(report.recipients || '')
    setMessage(null)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleCancel = () => {
    setEditingReport(null)
    setName('Rapport automatisé')
    setDashboard('financier')
    setDatetime('')
    setRecipients('')
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

  const handleSchedule = async (sendNow = false) => {
    setMessage(null)
    if (!name.trim() || !dashboard || !recipients.trim()) {
      setMessage({ type: 'error', text: 'Veuillez remplir tous les champs' })
      return
    }

    try {
      setLoading(true)
      const payload = {
        name,
        dashboard,
        scheduled_at: datetime || new Date().toISOString(),
        recipients,
      }

      let res
      if (editingReport) {
        res = await reportsAPI.update(editingReport.id, payload)
        setMessage({ type: 'success', text: '✓ Planification mise à jour avec succès' })
      } else {
        res = await reportsAPI.create(payload)

        if (sendNow && res?.data?.id) {
          await reportsAPI.sendNow(res.data.id)
          setMessage({ type: 'success', text: '✓ Rapport envoyé immédiatement' })
        } else {
          setMessage({ type: 'success', text: '✓ Planification enregistrée' })
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
      setMessage({ 
        type: 'error', 
        text: 'Erreur: ' + (e?.response?.data?.detail || e.message) 
      })
    } finally {
      setLoading(false)
    }
  }

  const getDashboardInfo = (dashboardValue) => {
    return dashboards.find(d => d.value === dashboardValue)
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

              {/* Sélection du Dashboard */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-3">Dashboard</label>
                <div className="grid grid-cols-2 gap-2">
                  {dashboards.map(d => (
                    <button
                      key={d.value}
                      onClick={() => setDashboard(d.value)}
                      className={`p-3 rounded-lg border-2 transition-all cursor-pointer ${
                        dashboard === d.value
                          ? `border-blue-600 ${d.color} bg-opacity-100`
                          : `border-gray-200 bg-gray-50 hover:border-gray-300`
                      }`}
                    >
                      <div className="text-xl mb-1">{d.icon}</div>
                      <div className="text-xs font-medium text-gray-700 line-clamp-2">{d.label}</div>
                    </button>
                  ))}
                </div>
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
                  Date & Heure
                </label>
                <input 
                  type="datetime-local" 
                  value={datetime} 
                  onChange={(e) => setDatetime(e.target.value)} 
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {!datetime && <p className="text-xs text-gray-500 mt-1">Laissez vide pour un envoi immédiat</p>}
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
                            {getDashboardInfo(report.dashboard)?.icon}
                            {report.name}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            {getDashboardInfo(report.dashboard)?.label}
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

                      <div className="grid grid-cols-2 gap-3 text-sm mb-4 pb-4 border-b border-gray-100">
                        <div className="flex items-center gap-2 text-gray-700">
                          <Calendar size={16} className="text-gray-400" />
                          {new Date(report.scheduled_at).toLocaleString('fr-FR')}
                        </div>
                        <div className="flex items-center gap-2 text-gray-700">
                          <Mail size={16} className="text-gray-400" />
                          {report.recipients?.split(',').length || 0} destinataire(s)
                        </div>
                      </div>

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
