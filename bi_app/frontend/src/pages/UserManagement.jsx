import { useState, useEffect } from 'react'
import { Shield, Plus, Edit2, Trash2, Search, Eye, EyeOff, Check, X, AlertCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

export default function UserManagement() {
  const { user } = useAuth()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [selectedDashboards, setSelectedDashboards] = useState({})
  const [showPassword, setShowPassword] = useState(false)
  const [message, setMessage] = useState(null)

  const dashboards = [
    { id: 'financier', name: 'Performance Financière', color: 'blue' },
    { id: 'occupation', name: 'Occupation Zones', color: 'green' },
    { id: 'portefeuille', name: 'Portefeuille Clients', color: 'purple' },
    { id: 'operationnel', name: 'KPI Opérationnels', color: 'orange' },
    { id: 'chatbot', name: 'Assistant IA', color: 'indigo' },
  ]

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    is_staff: false,
    dashboards: [],
  })

  // Charger les utilisateurs
  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const response = await api.get('/auth/users/')
      // Gérer la réponse paginée ou directe
      const data = Array.isArray(response.data) ? response.data : response.data.results || []
      setUsers(data)
      setMessage(null)
    } catch (error) {
      setMessage({
        type: 'error',
        text: 'Erreur lors du chargement des utilisateurs',
      })
      console.error('Error fetching users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddUser = () => {
    setFormData({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      is_staff: false,
      dashboards: [],
    })
    // Par défaut: tous les dashboards sont sélectionnés
    const allDashboardsSelected = {}
    dashboards.forEach((d) => {
      allDashboardsSelected[d.id] = true
    })
    setSelectedDashboards(allDashboardsSelected)
    setShowPassword(false)
    setEditingId(null)
    setShowForm(true)
  }

  const handleEditUser = (user) => {
    setFormData({
      username: user.username,
      email: user.email,
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      password: '',
      is_staff: user.is_staff || false,
      dashboards: user.dashboards || [],
    })
    // Initialiser les dashboards sélectionnés
    const dashboardMap = {}
    dashboards.forEach((d) => {
      dashboardMap[d.id] = (user.dashboards || []).includes(d.id)
    })
    setSelectedDashboards(dashboardMap)
    setShowPassword(false)
    setEditingId(user.id)
    setShowForm(true)
  }

  const handleSaveUser = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const selectedDashboardList = Object.keys(selectedDashboards).filter(
        (key) => selectedDashboards[key]
      )

      const payload = {
        username: formData.username,
        email: formData.email,
        first_name: formData.first_name,
        last_name: formData.last_name,
        is_staff: formData.is_staff,
        dashboards_write: selectedDashboardList,
      }

      if (formData.password) {
        payload.password = formData.password
      }

      if (editingId) {
        // Mise à jour
        await api.put(`/auth/users/${editingId}/`, payload)
        setMessage({ type: 'success', text: 'Utilisateur mis à jour' })
      } else {
        // Création
        await api.post('/auth/users/', payload)
        setMessage({ type: 'success', text: 'Utilisateur créé' })
      }

      setShowForm(false)
      fetchUsers()
    } catch (error) {
      const errorMsg =
        error.response?.data?.detail || 'Erreur lors de la sauvegarde'
      setMessage({ type: 'error', text: errorMsg })
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteUser = async (userId, username) => {
    // Empêcher la suppression de l'admin SIGETI
    if (username === 'admin') {
      setMessage({
        type: 'error',
        text: 'Impossible de supprimer l\'administrateur SIGETI',
      })
      return
    }

    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?'))
      return

    setLoading(true)
    try {
      await api.delete(`/auth/users/${userId}/`)
      setMessage({ type: 'success', text: 'Utilisateur supprimé' })
      fetchUsers()
    } catch (error) {
      setMessage({ type: 'error', text: 'Erreur lors de la suppression' })
    } finally {
      setLoading(false)
    }
  }

  const filteredUsers = users.filter(
    (user) =>
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  // Vérifier si l'utilisateur est admin
  if (!user?.is_staff || user?.username !== 'admin') {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
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
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <span>Gestion des Utilisateurs</span>
            </h1>
            <p className="text-gray-600 mt-2">
              Gérez les utilisateurs et leurs droits d'accès aux dashboards
            </p>
          </div>
          <button
            onClick={handleAddUser}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition"
          >
            <Plus className="w-5 h-5" />
            <span>Ajouter Utilisateur</span>
          </button>
        </div>
      </div>

      {/* Messages */}
      {message && (
        <div
          className={`max-w-7xl mx-auto mb-6 p-4 rounded-lg flex items-center space-x-3 ${
            message.type === 'success'
              ? 'bg-green-100 text-green-800 border border-green-300'
              : 'bg-red-100 text-red-800 border border-red-300'
          }`}
        >
          {message.type === 'success' ? (
            <Check className="w-5 h-5" />
          ) : (
            <X className="w-5 h-5" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* Search */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="relative">
          <Search className="absolute left-4 top-3 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher par nom d'utilisateur ou email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
              <h2 className="text-xl font-bold text-gray-900">
                {editingId ? 'Modifier Utilisateur' : 'Ajouter Utilisateur'}
              </h2>
              <button
                onClick={() => setShowForm(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSaveUser} className="p-6 space-y-4">
              {/* Identité */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom d'utilisateur
                  </label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) =>
                      setFormData({ ...formData, username: e.target.value })
                    }
                    disabled={!!editingId}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              {/* Nom et prénom */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Prénom
                  </label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) =>
                      setFormData({ ...formData, first_name: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom
                  </label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) =>
                      setFormData({ ...formData, last_name: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Mot de passe */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mot de passe {editingId && '(laisser vide pour ne pas changer)'}
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) =>
                      setFormData({ ...formData, password: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 pr-12"
                    required={!editingId}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-2.5 text-gray-500 hover:text-gray-700"
                  >
                    {showPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Admin */}
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="is_staff"
                  checked={formData.is_staff}
                  onChange={(e) =>
                    setFormData({ ...formData, is_staff: e.target.checked })
                  }
                  className="w-4 h-4 text-blue-600"
                />
                <label
                  htmlFor="is_staff"
                  className="text-sm font-medium text-gray-700"
                >
                  Administrateur
                </label>
              </div>

              {/* Dashboards */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Accès aux Dashboards
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {dashboards.map((dashboard) => (
                    <label
                      key={dashboard.id}
                      className="flex items-center space-x-3 p-3 border border-gray-300 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedDashboards[dashboard.id] || false}
                        onChange={(e) =>
                          setSelectedDashboards({
                            ...selectedDashboards,
                            [dashboard.id]: e.target.checked,
                          })
                        }
                        className="w-4 h-4 text-blue-600"
                      />
                      <span className="text-sm font-medium text-gray-700">
                        {dashboard.name}
                      </span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Buttons */}
              <div className="flex space-x-3 pt-4 border-t border-gray-200">
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Enregistrement...' : 'Enregistrer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Users Table */}
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {filteredUsers.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              {loading ? 'Chargement...' : 'Aucun utilisateur trouvé'}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Utilisateur
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Dashboards
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Rôle
                    </th>
                    <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredUsers.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900">
                            {user.first_name} {user.last_name}
                          </p>
                          <p className="text-sm text-gray-500">
                            @{user.username}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {user.email}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-2">
                          {user.dashboards?.map((dash) => {
                            const dashboard = dashboards.find(
                              (d) => d.id === dash
                            )
                            return (
                              <span
                                key={dash}
                                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${dashboard?.color}-100 text-${dashboard?.color}-800`}
                              >
                                {dashboard?.name}
                              </span>
                            )
                          })}
                          {!user.dashboards?.length && (
                            <span className="text-gray-400 text-sm">
                              Aucun accès
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                            user.is_staff
                              ? 'bg-purple-100 text-purple-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {user.is_staff ? 'Admin' : 'Utilisateur'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex justify-end space-x-3">
                          <button
                            onClick={() => handleEditUser(user)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            <Edit2 className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleDeleteUser(user.id, user.username)}
                            disabled={user.username === 'admin'}
                            className={`${
                              user.username === 'admin'
                                ? 'text-gray-400 cursor-not-allowed'
                                : 'text-red-600 hover:text-red-900'
                            }`}
                            title={
                              user.username === 'admin'
                                ? 'Admin SIGETI ne peut pas être supprimé'
                                : 'Supprimer'
                            }
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
