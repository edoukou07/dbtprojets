"""
Règles métier pour le chatbot BI
Contient les validations, seuils d'alerte et logique business
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BusinessRules:
    """Ensemble de règles métier pour valider et enrichir les requêtes"""
    
    # Seuils d'alerte métier
    SEUILS = {
        'taux_impaye_critique': 30.0,  # > 30% d'impayés = critique
        'taux_impaye_warning': 15.0,   # > 15% = warning
        'occupation_faible': 50.0,      # < 50% = sous-utilisé
        'occupation_optimale': 80.0,    # 80-95% = optimal
        'occupation_saturee': 95.0,     # > 95% = saturé
        'ca_minimum_client': 10_000_000,  # 10M FCFA minimum pour "gros client"
        'delai_paiement_normal': 30,   # 30 jours = délai normal
        'delai_paiement_long': 60,     # > 60 jours = retard important
    }
    
    # Années valides (évite les erreurs de saisie)
    ANNEES_VALIDES = range(2020, 2026)
    
    @staticmethod
    def validate_year(year: int) -> tuple[bool, Optional[str]]:
        """Valide qu'une année est cohérente"""
        if year not in BusinessRules.ANNEES_VALIDES:
            return False, f"Année {year} non valide. Années disponibles: {min(BusinessRules.ANNEES_VALIDES)}-{max(BusinessRules.ANNEES_VALIDES)}"
        return True, None
    
    @staticmethod
    def validate_threshold(value: float, min_val: float = 0, max_val: float = 100) -> tuple[bool, Optional[str]]:
        """Valide qu'un seuil est dans les limites acceptables"""
        if value < min_val or value > max_val:
            return False, f"Valeur {value} hors limites ({min_val}-{max_val})"
        return True, None
    
    @staticmethod
    def validate_top_limit(limit: int) -> tuple[bool, Optional[str]]:
        """Valide un limit pour TOP N requêtes"""
        if limit < 1:
            return False, "La limite doit être >= 1"
        if limit > 100:
            return False, "Limite maximale: 100 résultats"
        return True, None
    
    @staticmethod
    def analyze_taux_impaye(taux: float) -> Dict[str, Any]:
        """Analyse un taux d'impayé et retourne un diagnostic"""
        if taux >= BusinessRules.SEUILS['taux_impaye_critique']:
            return {
                'niveau': 'critique',
                'emoji': '🔴',
                'message': f"Taux d'impayé critique ({taux:.1f}%) ! Action urgente requise.",
                'recommandations': [
                    "Relance immédiate des clients",
                    "Analyse des créances anciennes",
                    "Révision des conditions de paiement"
                ]
            }
        elif taux >= BusinessRules.SEUILS['taux_impaye_warning']:
            return {
                'niveau': 'warning',
                'emoji': '⚠️',
                'message': f"Taux d'impayé élevé ({taux:.1f}%). Surveillance nécessaire.",
                'recommandations': [
                    "Relance préventive",
                    "Suivi hebdomadaire des paiements"
                ]
            }
        else:
            return {
                'niveau': 'ok',
                'emoji': '✅',
                'message': f"Taux d'impayé acceptable ({taux:.1f}%).",
                'recommandations': []
            }
    
    @staticmethod
    def analyze_occupation(taux: float) -> Dict[str, Any]:
        """Analyse un taux d'occupation et retourne un diagnostic"""
        if taux < BusinessRules.SEUILS['occupation_faible']:
            return {
                'niveau': 'faible',
                'emoji': '📉',
                'message': f"Occupation faible ({taux:.1f}%). Potentiel inexploité.",
                'recommandations': [
                    "Campagne de commercialisation",
                    "Révision de la stratégie tarifaire",
                    "Analyse de la concurrence"
                ]
            }
        elif taux >= BusinessRules.SEUILS['occupation_saturee']:
            return {
                'niveau': 'saturé',
                'emoji': '🔴',
                'message': f"Occupation saturée ({taux:.1f}%). Capacité maximale atteinte.",
                'recommandations': [
                    "Planifier extension de capacité",
                    "Prioriser les clients stratégiques",
                    "Augmentation tarifaire possible"
                ]
            }
        elif taux >= BusinessRules.SEUILS['occupation_optimale']:
            return {
                'niveau': 'optimal',
                'emoji': '✅',
                'message': f"Occupation optimale ({taux:.1f}%).",
                'recommandations': []
            }
        else:
            return {
                'niveau': 'correct',
                'emoji': '📊',
                'message': f"Occupation correcte ({taux:.1f}%).",
                'recommandations': ["Continuer le suivi régulier"]
            }
    
    @staticmethod
    def analyze_delai_paiement(delai: float) -> Dict[str, Any]:
        """Analyse un délai de paiement moyen"""
        if delai > BusinessRules.SEUILS['delai_paiement_long']:
            return {
                'niveau': 'long',
                'emoji': '⏰',
                'message': f"Délai de paiement long ({delai:.0f} jours).",
                'recommandations': [
                    "Renforcer les relances",
                    "Réviser les conditions de crédit",
                    "Mettre en place des pénalités de retard"
                ]
            }
        elif delai > BusinessRules.SEUILS['delai_paiement_normal']:
            return {
                'niveau': 'acceptable',
                'emoji': '📅',
                'message': f"Délai de paiement acceptable ({delai:.0f} jours).",
                'recommandations': ["Surveiller l'évolution"]
            }
        else:
            return {
                'niveau': 'excellent',
                'emoji': '⚡',
                'message': f"Excellent délai de paiement ({delai:.0f} jours).",
                'recommandations': []
            }
    
    @staticmethod
    def classify_client(ca: float) -> Dict[str, Any]:
        """Classifie un client selon son CA"""
        if ca >= BusinessRules.SEUILS['ca_minimum_client']:
            return {
                'categorie': 'premium',
                'emoji': '💎',
                'message': 'Client premium',
                'priorite': 'haute'
            }
        elif ca >= BusinessRules.SEUILS['ca_minimum_client'] / 2:
            return {
                'categorie': 'standard',
                'emoji': '⭐',
                'message': 'Client standard',
                'priorite': 'moyenne'
            }
        else:
            return {
                'categorie': 'petit',
                'emoji': '📌',
                'message': 'Petit client',
                'priorite': 'normale'
            }
    
    @staticmethod
    def detect_anomalies(data: List[Dict], category: str = None) -> List[Dict[str, Any]]:
        """Détecte des anomalies dans les données selon le contexte"""
        anomalies = []
        
        if not data:
            return anomalies
        
        # Détecter les colonnes présentes dans les données
        all_columns = set()
        for row in data:
            all_columns.update(row.keys())
        
        for idx, row in enumerate(data):
            # Anomalies financières (seulement si colonnes financières présentes)
            if 'montant_total_facture' in all_columns or 'ca_total' in all_columns:
                # Vérifier les valeurs nulles sur champs critiques financiers
                if row.get('montant_total_facture') is None and row.get('ca_total') is None:
                    anomalies.append({
                        'type': 'valeur_nulle',
                        'row': idx,
                        'field': 'montant',
                        'severity': 'warning',
                        'message': 'Montant manquant'
                    })
                
                # Vérifier les valeurs négatives (anormal pour CA)
                ca = row.get('montant_total_facture') or row.get('ca_total') or 0
                if ca < 0:
                    anomalies.append({
                        'type': 'valeur_negative',
                        'row': idx,
                        'field': 'ca',
                        'severity': 'error',
                        'message': f'CA négatif détecté: {ca}'
                    })
                
                # Vérifier impayés > CA (impossible)
                ca_total = row.get('montant_total_facture') or 0
                impaye = row.get('montant_impaye') or 0
                if ca_total > 0 and impaye > ca_total:
                    anomalies.append({
                        'type': 'incoherence',
                        'row': idx,
                        'field': 'impaye',
                        'severity': 'error',
                        'message': f'Impayé ({impaye}) > CA total ({ca_total})'
                    })
            
            # Anomalies d'occupation (seulement si colonnes occupation présentes)
            if 'taux_occupation_pct' in all_columns:
                taux_occupation = row.get('taux_occupation_pct')
                if taux_occupation and taux_occupation > 100:
                    anomalies.append({
                        'type': 'valeur_aberrante',
                        'row': idx,
                        'field': 'taux_occupation',
                        'severity': 'error',
                        'message': f'Taux > 100%: {taux_occupation:.1f}%'
                    })
                
                # Vérifier incohérence lots occupés vs total
                lots_occupes = row.get('nombre_lots_occupes')
                lots_total = row.get('nombre_lots_total')
                if lots_occupes and lots_total and lots_occupes > lots_total:
                    anomalies.append({
                        'type': 'incoherence',
                        'row': idx,
                        'field': 'lots',
                        'severity': 'error',
                        'message': f'Lots occupés ({lots_occupes}) > Total ({lots_total})'
                    })
        
        return anomalies
    
    @staticmethod
    def generate_insights(data: List[Dict], category: str) -> List[str]:
        """Génère des insights métier à partir des données"""
        insights = []
        
        if not data:
            return insights
        
        if category == 'financier':
            # Calculer moyennes et totaux
            total_ca = sum(row.get('montant_total_facture', 0) or 0 for row in data)
            total_impaye = sum(row.get('montant_impaye', 0) or 0 for row in data)
            
            if total_ca > 0:
                taux_impaye_global = (total_impaye / total_ca) * 100
                analysis = BusinessRules.analyze_taux_impaye(taux_impaye_global)
                insights.append(f"{analysis['emoji']} {analysis['message']}")
                insights.extend(analysis['recommandations'])
        
        elif category == 'occupation':
            # Analyser occupation moyenne
            taux_list = [row.get('taux_occupation_pct', 0) or 0 for row in data if row.get('taux_occupation_pct')]
            if taux_list:
                taux_moyen = sum(taux_list) / len(taux_list)
                analysis = BusinessRules.analyze_occupation(taux_moyen)
                insights.append(f"{analysis['emoji']} {analysis['message']}")
                insights.extend(analysis['recommandations'])
        
        elif category == 'clients':
            # Classifier les clients
            nb_premium = sum(1 for row in data if (row.get('chiffre_affaires_total') or 0) >= BusinessRules.SEUILS['ca_minimum_client'])
            nb_total = len(data)
            if nb_total > 0:
                pct_premium = (nb_premium / nb_total) * 100
                insights.append(f"💎 {nb_premium} clients premium ({pct_premium:.1f}% du portefeuille)")
                
                if pct_premium < 20:
                    insights.append("📈 Opportunité de développement des clients premium")
        
        return insights
