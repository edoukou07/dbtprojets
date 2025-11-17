"""
API Views pour la configuration des alertes
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
import json
import logging

logger = logging.getLogger(__name__)


class AlertThresholdsView(APIView):
    """
    GET: Récupère les seuils d'alertes actuels
    PUT: Met à jour les seuils d'alertes
    """
    
    CACHE_KEY = 'alert_thresholds'
    
    DEFAULT_THRESHOLDS = {
        'financier': {
            'taux_impaye_critique': 40.0,
            'taux_impaye_warning': 25.0,
            'ca_baisse_critique': -30.0,
            'ca_baisse_warning': -15.0,
            'delai_paiement_critique': 90,
            'delai_paiement_warning': 60
        },
        'occupation': {
            'occupation_critique_basse': 30.0,
            'occupation_warning_basse': 50.0,
            'occupation_saturee': 95.0
        },
        'operationnel': {
            'taux_cloture_faible': 60.0
        }
    }
    
    def get(self, request):
        """Récupère les seuils depuis le cache ou retourne les valeurs par défaut"""
        try:
            # Essayer de récupérer depuis le cache
            thresholds = cache.get(self.CACHE_KEY)
            
            if thresholds is None:
                # Utiliser les valeurs par défaut
                thresholds = self.DEFAULT_THRESHOLDS
                # Sauvegarder dans le cache
                cache.set(self.CACHE_KEY, thresholds, timeout=None)
            
            return Response(thresholds, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur récupération seuils: {e}")
            return Response(
                {'error': 'Erreur lors de la récupération des seuils'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        """Met à jour les seuils d'alertes"""
        try:
            data = request.data
            
            # Valider la structure
            if not self._validate_thresholds(data):
                return Response(
                    {'error': 'Structure de données invalide'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Sauvegarder dans le cache
            cache.set(self.CACHE_KEY, data, timeout=None)
            
            # Mettre à jour AlertSystem avec les nouveaux seuils
            self._update_alert_system(data)
            
            logger.info("Seuils d'alertes mis à jour avec succès")
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Erreur mise à jour seuils: {e}")
            return Response(
                {'error': 'Erreur lors de la mise à jour des seuils'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _validate_thresholds(self, data):
        """Valide la structure des seuils"""
        try:
            # Vérifier que toutes les catégories sont présentes
            required_categories = ['financier', 'occupation', 'operationnel']
            if not all(cat in data for cat in required_categories):
                return False
            
            # Vérifier les champs financiers
            financier_fields = [
                'taux_impaye_critique', 'taux_impaye_warning',
                'ca_baisse_critique', 'ca_baisse_warning',
                'delai_paiement_critique', 'delai_paiement_warning'
            ]
            if not all(field in data['financier'] for field in financier_fields):
                return False
            
            # Vérifier les champs occupation
            occupation_fields = [
                'occupation_critique_basse', 'occupation_warning_basse', 'occupation_saturee'
            ]
            if not all(field in data['occupation'] for field in occupation_fields):
                return False
            
            # Vérifier les champs opérationnels
            if 'taux_cloture_faible' not in data['operationnel']:
                return False
            
            # Vérifier que toutes les valeurs sont numériques
            for category in data.values():
                for value in category.values():
                    if not isinstance(value, (int, float)):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur validation: {e}")
            return False
    
    def _update_alert_system(self, thresholds):
        """Met à jour les seuils dans AlertSystem"""
        try:
            from ai_chat.alert_system import AlertSystem
            
            # Convertir la structure pour AlertSystem
            alert_thresholds = {
                'taux_impaye_critique': thresholds['financier']['taux_impaye_critique'],
                'taux_impaye_warning': thresholds['financier']['taux_impaye_warning'],
                'ca_baisse_critique': thresholds['financier']['ca_baisse_critique'],
                'ca_baisse_warning': thresholds['financier']['ca_baisse_warning'],
                'occupation_critique_basse': thresholds['occupation']['occupation_critique_basse'],
                'occupation_warning_basse': thresholds['occupation']['occupation_warning_basse'],
                'occupation_saturee': thresholds['occupation']['occupation_saturee'],
                'delai_paiement_critique': thresholds['financier']['delai_paiement_critique'],
                'delai_paiement_warning': thresholds['financier']['delai_paiement_warning'],
                'taux_cloture_faible': thresholds['operationnel']['taux_cloture_faible']
            }
            
            # Mettre à jour les seuils de la classe
            AlertSystem.ALERT_THRESHOLDS = alert_thresholds
            
            logger.info("AlertSystem mis à jour avec les nouveaux seuils")
            
        except Exception as e:
            logger.error(f"Erreur mise à jour AlertSystem: {e}")


class AlertThresholdsResetView(APIView):
    """
    POST: Réinitialise les seuils aux valeurs par défaut
    """
    
    def post(self, request):
        """Réinitialise aux valeurs par défaut"""
        try:
            thresholds_view = AlertThresholdsView()
            
            # Sauvegarder les valeurs par défaut
            cache.set(
                AlertThresholdsView.CACHE_KEY, 
                AlertThresholdsView.DEFAULT_THRESHOLDS, 
                timeout=None
            )
            
            # Mettre à jour AlertSystem
            thresholds_view._update_alert_system(AlertThresholdsView.DEFAULT_THRESHOLDS)
            
            logger.info("Seuils réinitialisés aux valeurs par défaut")
            
            return Response(
                AlertThresholdsView.DEFAULT_THRESHOLDS, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Erreur réinitialisation: {e}")
            return Response(
                {'error': 'Erreur lors de la réinitialisation'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
