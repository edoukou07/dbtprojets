import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  AlertCircle, 
  TrendingDown, 
  TrendingUp, 
  Users, 
  Calendar,
  Save,
  RotateCcw,
  CheckCircle,
  XCircle
} from 'lucide-react';

const AlertsConfig = () => {
  const [thresholds, setThresholds] = useState({
    financier: {
      taux_impaye_critique: 40.0,
      taux_impaye_warning: 25.0,
      ca_baisse_critique: -30.0,
      ca_baisse_warning: -15.0,
      delai_paiement_critique: 90,
      delai_paiement_warning: 60
    },
    occupation: {
      occupation_critique_basse: 30.0,
      occupation_warning_basse: 50.0,
      occupation_saturee: 95.0
    },
    operationnel: {
      taux_cloture_faible: 60.0
    }
  });

  const [originalThresholds, setOriginalThresholds] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null); // 'success' | 'error' | null
  const [isLoading, setIsLoading] = useState(false);

  // Charger les seuils depuis l'API
  useEffect(() => {
    fetchThresholds();
  }, []);

  // Détecter les changements
  useEffect(() => {
    if (originalThresholds) {
      const changed = JSON.stringify(thresholds) !== JSON.stringify(originalThresholds);
      setHasChanges(changed);
    }
  }, [thresholds, originalThresholds]);

  const fetchThresholds = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/alerts/thresholds/');
      if (response.ok) {
        const data = await response.json();
        setThresholds(data);
        setOriginalThresholds(JSON.parse(JSON.stringify(data)));
      }
    } catch (error) {
      console.error('Erreur chargement seuils:', error);
      // Utiliser les valeurs par défaut
      setOriginalThresholds(JSON.parse(JSON.stringify(thresholds)));
    }
  };

  const handleChange = (category, key, value) => {
    setThresholds(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: parseFloat(value) || 0
      }
    }));
    setSaveStatus(null);
  };

  const handleSave = async () => {
    setIsLoading(true);
    setSaveStatus(null);

    try {
      const response = await fetch('http://localhost:8000/api/alerts/thresholds/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(thresholds)
      });

      if (response.ok) {
        const data = await response.json();
        setOriginalThresholds(JSON.parse(JSON.stringify(data)));
        setSaveStatus('success');
        setTimeout(() => setSaveStatus(null), 3000);
      } else {
        setSaveStatus('error');
      }
    } catch (error) {
      console.error('Erreur sauvegarde:', error);
      setSaveStatus('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setThresholds(JSON.parse(JSON.stringify(originalThresholds)));
    setSaveStatus(null);
  };

  const handleResetToDefaults = () => {
    const defaults = {
      financier: {
        taux_impaye_critique: 40.0,
        taux_impaye_warning: 25.0,
        ca_baisse_critique: -30.0,
        ca_baisse_warning: -15.0,
        delai_paiement_critique: 90,
        delai_paiement_warning: 60
      },
      occupation: {
        occupation_critique_basse: 30.0,
        occupation_warning_basse: 50.0,
        occupation_saturee: 95.0
      },
      operationnel: {
        taux_cloture_faible: 60.0
      }
    };
    setThresholds(defaults);
    setSaveStatus(null);
  };

  const ThresholdInput = ({ label, value, onChange, suffix = '%', description, icon: Icon }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        {Icon && (
          <div className="mt-1">
            <Icon className="w-5 h-5 text-gray-400" />
          </div>
        )}
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {label}
          </label>
          {description && (
            <p className="text-xs text-gray-500 mb-2">{description}</p>
          )}
          <div className="flex items-center gap-2">
            <input
              type="number"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              step={suffix === '%' ? '0.1' : '1'}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <span className="text-sm text-gray-600 min-w-fit">{suffix}</span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Settings className="w-6 h-6 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Configuration des Alertes
                </h1>
                <p className="text-sm text-gray-600 mt-1">
                  Définissez les seuils déclenchant les alertes intelligentes
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Statut sauvegarde */}
              {saveStatus === 'success' && (
                <div className="flex items-center gap-2 text-green-600 bg-green-50 px-3 py-2 rounded-md">
                  <CheckCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">Sauvegardé</span>
                </div>
              )}
              {saveStatus === 'error' && (
                <div className="flex items-center gap-2 text-red-600 bg-red-50 px-3 py-2 rounded-md">
                  <XCircle className="w-4 h-4" />
                  <span className="text-sm font-medium">Erreur</span>
                </div>
              )}

              {/* Boutons d'action */}
              <button
                onClick={handleResetToDefaults}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors flex items-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                Valeurs par défaut
              </button>

              {hasChanges && (
                <>
                  <button
                    onClick={handleReset}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                  >
                    Annuler
                  </button>
                  <button
                    onClick={handleSave}
                    disabled={isLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50"
                  >
                    <Save className="w-4 h-4" />
                    {isLoading ? 'Enregistrement...' : 'Enregistrer'}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Section Financière */}
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-red-500 to-orange-500 px-6 py-4">
              <div className="flex items-center gap-3 text-white">
                <TrendingDown className="w-6 h-6" />
                <div>
                  <h2 className="text-xl font-bold">Alertes Financières</h2>
                  <p className="text-sm text-red-100">Seuils pour impayés, CA et délais de paiement</p>
                </div>
              </div>
            </div>

            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <ThresholdInput
                label="Taux d'impayé critique"
                value={thresholds.financier.taux_impaye_critique}
                onChange={(v) => handleChange('financier', 'taux_impaye_critique', v)}
                description="Alerte rouge si le taux d'impayés dépasse ce seuil"
                icon={AlertCircle}
              />

              <ThresholdInput
                label="Taux d'impayé warning"
                value={thresholds.financier.taux_impaye_warning}
                onChange={(v) => handleChange('financier', 'taux_impaye_warning', v)}
                description="Alerte orange pour surveillance"
                icon={AlertCircle}
              />

              <ThresholdInput
                label="Baisse CA critique"
                value={thresholds.financier.ca_baisse_critique}
                onChange={(v) => handleChange('financier', 'ca_baisse_critique', v)}
                description="Baisse du CA déclenchant une alerte critique (négatif)"
                icon={TrendingDown}
              />

              <ThresholdInput
                label="Baisse CA warning"
                value={thresholds.financier.ca_baisse_warning}
                onChange={(v) => handleChange('financier', 'ca_baisse_warning', v)}
                description="Baisse modérée nécessitant attention"
                icon={TrendingDown}
              />

              <ThresholdInput
                label="Délai paiement critique"
                value={thresholds.financier.delai_paiement_critique}
                onChange={(v) => handleChange('financier', 'delai_paiement_critique', v)}
                suffix="jours"
                description="Délai de paiement moyen critique"
                icon={Calendar}
              />

              <ThresholdInput
                label="Délai paiement warning"
                value={thresholds.financier.delai_paiement_warning}
                onChange={(v) => handleChange('financier', 'delai_paiement_warning', v)}
                suffix="jours"
                description="Délai nécessitant surveillance"
                icon={Calendar}
              />
            </div>
          </section>

          {/* Section Occupation */}
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-cyan-500 px-6 py-4">
              <div className="flex items-center gap-3 text-white">
                <TrendingUp className="w-6 h-6" />
                <div>
                  <h2 className="text-xl font-bold">Alertes d'Occupation</h2>
                  <p className="text-sm text-blue-100">Seuils pour taux d'occupation des zones</p>
                </div>
              </div>
            </div>

            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <ThresholdInput
                label="Occupation critique basse"
                value={thresholds.occupation.occupation_critique_basse}
                onChange={(v) => handleChange('occupation', 'occupation_critique_basse', v)}
                description="Sous-utilisation critique de la zone"
                icon={TrendingDown}
              />

              <ThresholdInput
                label="Occupation warning basse"
                value={thresholds.occupation.occupation_warning_basse}
                onChange={(v) => handleChange('occupation', 'occupation_warning_basse', v)}
                description="Occupation faible nécessitant attention"
                icon={AlertCircle}
              />

              <ThresholdInput
                label="Occupation saturée"
                value={thresholds.occupation.occupation_saturee}
                onChange={(v) => handleChange('occupation', 'occupation_saturee', v)}
                description="Zone proche de la saturation"
                icon={TrendingUp}
              />
            </div>
          </section>

          {/* Section Opérationnelle */}
          <section className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 px-6 py-4">
              <div className="flex items-center gap-3 text-white">
                <Users className="w-6 h-6" />
                <div>
                  <h2 className="text-xl font-bold">Alertes Opérationnelles</h2>
                  <p className="text-sm text-purple-100">Seuils pour processus et collectes</p>
                </div>
              </div>
            </div>

            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              <ThresholdInput
                label="Taux clôture faible"
                value={thresholds.operationnel.taux_cloture_faible}
                onChange={(v) => handleChange('operationnel', 'taux_cloture_faible', v)}
                description="Pourcentage minimal de collectes clôturées"
                icon={AlertCircle}
              />
            </div>
          </section>

          {/* Info Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">💡 Comment ça fonctionne ?</p>
                <ul className="space-y-1 ml-4 list-disc">
                  <li>Les seuils sont utilisés par le système d'alertes intelligentes</li>
                  <li>Les alertes critiques (🔴) nécessitent une action immédiate</li>
                  <li>Les alertes warning (⚠️) demandent une surveillance</li>
                  <li>Les modifications sont appliquées immédiatement après sauvegarde</li>
                  <li>Utilisez "Valeurs par défaut" pour restaurer les paramètres recommandés</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlertsConfig;
