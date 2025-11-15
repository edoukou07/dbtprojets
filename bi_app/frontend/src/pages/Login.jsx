import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { 
  Building2, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  AlertCircle,
  TrendingUp,
  BarChart3,
  PieChart
} from 'lucide-react';

export default function Login() {
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await login(formData.email, formData.password);
      
      if (!result.success) {
        setError(result.error || 'Email ou mot de passe incorrect');
      }
      // Si succès, la redirection est gérée par le contexte AuthContext
    } catch (err) {
      console.error('Login error:', err);
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex">
      {/* Panneau gauche - Informations */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-purple-700 p-12 flex-col justify-between relative overflow-hidden">
        {/* Motif de fond décoratif */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-72 h-72 bg-white rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 right-20 w-96 h-96 bg-white rounded-full blur-3xl"></div>
        </div>

        <div className="relative z-10">
          {/* Logo et titre */}
          <div className="flex items-center space-x-3 mb-12">
            <div className="bg-white/20 backdrop-blur-sm p-3 rounded-xl">
              <Building2 className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">SIGETI BI</h1>
              <p className="text-blue-100 text-sm">Business Intelligence Platform</p>
            </div>
          </div>

          {/* Message d'accueil */}
          <div className="space-y-6">
            <h2 className="text-4xl font-bold text-white leading-tight">
              Pilotez votre<br />
              activité en temps réel
            </h2>
            <p className="text-blue-100 text-lg">
              Accédez à tous vos indicateurs de performance dans une interface moderne et intuitive.
            </p>
          </div>

          {/* Statistiques */}
          <div className="grid grid-cols-3 gap-6 mt-12">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
              <TrendingUp className="w-8 h-8 text-white mb-2" />
              <div className="text-2xl font-bold text-white">54</div>
              <div className="text-blue-100 text-sm">Indicateurs</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
              <BarChart3 className="w-8 h-8 text-white mb-2" />
              <div className="text-2xl font-bold text-white">4</div>
              <div className="text-blue-100 text-sm">Dashboards</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
              <PieChart className="w-8 h-8 text-white mb-2" />
              <div className="text-2xl font-bold text-white">100%</div>
              <div className="text-blue-100 text-sm">Temps réel</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="relative z-10">
          <p className="text-blue-100 text-sm">
            © 2025 SIGETI. Tous droits réservés.
          </p>
        </div>
      </div>

      {/* Panneau droit - Formulaire de connexion */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Logo mobile */}
          <div className="lg:hidden flex items-center justify-center mb-8">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-3 rounded-xl">
              <Building2 className="w-8 h-8 text-white" />
            </div>
          </div>

          {/* Titre du formulaire */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Bon retour !
            </h2>
            <p className="text-gray-600">
              Connectez-vous pour accéder à vos dashboards
            </p>
          </div>

          {/* Alerte d'erreur */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-red-800 font-medium">Erreur de connexion</p>
                <p className="text-sm text-red-600 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Formulaire */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Adresse email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="votre.email@sigeti.ci"
                />
              </div>
            </div>

            {/* Mot de passe */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Mot de passe
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Options */}
            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-600">Se souvenir de moi</span>
              </label>
              <a href="#" className="text-sm font-medium text-blue-600 hover:text-blue-500">
                Mot de passe oublié ?
              </a>
            </div>

            {/* Bouton de connexion */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Connexion en cours...</span>
                </div>
              ) : (
                'Se connecter'
              )}
            </button>
          </form>

          {/* Comptes de test */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
            <p className="text-sm font-medium text-blue-900 mb-2">🔐 Comptes de démonstration :</p>
            <div className="space-y-2 text-sm text-blue-700">
              <div>
                <span className="font-medium">Admin:</span> admin@sigeti.ci / admin123
              </div>
              <div>
                <span className="font-medium">Finance:</span> finance@sigeti.ci / finance123
              </div>
              <div>
                <span className="font-medium">Opérations:</span> ops@sigeti.ci / ops123
              </div>
            </div>
          </div>

          {/* Liens */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Besoin d'aide ?{' '}
              <a href="#" className="font-medium text-blue-600 hover:text-blue-500">
                Contactez le support
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
