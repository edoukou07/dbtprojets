"""
Module d'analyse de tendances pour le chatbot BI
Détecte les tendances, calcule les variations, et génère des prévisions simples
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import statistics

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analyse les tendances dans les données temporelles"""
    
    # Seuils pour classification des tendances
    SEUILS_VARIATION = {
        'forte_hausse': 20.0,      # > +20%
        'hausse': 5.0,             # > +5%
        'stable': -5.0,            # entre -5% et +5%
        'baisse': -20.0,           # < -5%
        'forte_baisse': -100.0     # < -20%
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_time_series(self, data: List[Dict], 
                           time_field: str, 
                           value_field: str,
                           entity_field: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyse une série temporelle et détecte les tendances
        
        Args:
            data: Liste de dictionnaires avec les données
            time_field: Nom du champ temporel (mois, annee, date)
            value_field: Nom du champ de valeur à analyser
            entity_field: Nom du champ d'entité (zone, client, etc.) pour analyse groupée
            
        Returns:
            Dict avec tendance, variations, prévisions
        """
        if not data:
            return {'error': 'Aucune donnée à analyser'}
        
        try:
            # Grouper par entité si spécifié
            if entity_field:
                return self._analyze_grouped_trends(data, time_field, value_field, entity_field)
            else:
                return self._analyze_single_trend(data, time_field, value_field)
                
        except Exception as e:
            self.logger.error(f"Erreur analyse tendance: {e}")
            return {'error': str(e)}
    
    def _analyze_single_trend(self, data: List[Dict], 
                             time_field: str, 
                             value_field: str) -> Dict[str, Any]:
        """Analyse la tendance d'une série temporelle simple"""
        
        # Trier par période
        sorted_data = sorted(data, key=lambda x: x.get(time_field, 0))
        
        # Extraire les valeurs
        values = []
        periods = []
        for row in sorted_data:
            val = row.get(value_field)
            period = row.get(time_field)
            if val is not None and period is not None:
                values.append(float(val))
                periods.append(period)
        
        if len(values) < 2:
            return {'error': 'Pas assez de données pour analyser la tendance (minimum 2 points)'}
        
        # Calculs statistiques
        variation_totale = self._calculate_variation(values[0], values[-1])
        variation_moyenne = self._calculate_average_variation(values)
        tendance = self._classify_trend(variation_moyenne)
        
        # Détection de saisonnalité
        saisonnalite = self._detect_seasonality(values)
        
        # Points remarquables
        max_val = max(values)
        min_val = min(values)
        max_idx = values.index(max_val)
        min_idx = values.index(min_val)
        
        # Prévision simple (moyenne mobile)
        prevision = self._simple_forecast(values)
        
        result = {
            'tendance': tendance,
            'variation_totale_pct': round(variation_totale, 2),
            'variation_moyenne_pct': round(variation_moyenne, 2),
            'nb_periodes': len(values),
            'valeur_initiale': round(values[0], 2),
            'valeur_finale': round(values[-1], 2),
            'valeur_max': round(max_val, 2),
            'valeur_min': round(min_val, 2),
            'periode_max': periods[max_idx],
            'periode_min': periods[min_idx],
            'moyenne': round(statistics.mean(values), 2),
            'ecart_type': round(statistics.stdev(values), 2) if len(values) > 1 else 0,
            'saisonnalite': saisonnalite,
            'prevision_prochaine_periode': round(prevision, 2),
            'volatilite': self._calculate_volatility(values),
            'insights': self._generate_trend_insights(tendance, variation_totale, saisonnalite, values)
        }
        
        return result
    
    def _analyze_grouped_trends(self, data: List[Dict],
                                time_field: str,
                                value_field: str,
                                entity_field: str) -> Dict[str, Any]:
        """Analyse les tendances groupées par entité (zones, clients, etc.)"""
        
        # Grouper les données par entité
        grouped = defaultdict(list)
        for row in data:
            entity = row.get(entity_field)
            if entity:
                grouped[entity].append(row)
        
        # Analyser chaque groupe
        entity_trends = {}
        for entity, entity_data in grouped.items():
            trend_result = self._analyze_single_trend(entity_data, time_field, value_field)
            if 'error' not in trend_result:
                entity_trends[entity] = trend_result
        
        if not entity_trends:
            return {'error': 'Aucune tendance détectée'}
        
        # Identifier les meilleures et pires performances
        best_performers = sorted(
            entity_trends.items(),
            key=lambda x: x[1]['variation_totale_pct'],
            reverse=True
        )[:5]
        
        worst_performers = sorted(
            entity_trends.items(),
            key=lambda x: x[1]['variation_totale_pct']
        )[:5]
        
        # Statistiques globales
        all_variations = [t['variation_totale_pct'] for t in entity_trends.values()]
        
        return {
            'nb_entites': len(entity_trends),
            'tendances_par_entite': entity_trends,
            'top_5_hausse': [
                {
                    'entite': entity,
                    'variation_pct': trend['variation_totale_pct'],
                    'tendance': trend['tendance']
                }
                for entity, trend in best_performers
            ],
            'top_5_baisse': [
                {
                    'entite': entity,
                    'variation_pct': trend['variation_totale_pct'],
                    'tendance': trend['tendance']
                }
                for entity, trend in worst_performers
            ],
            'variation_moyenne_globale': round(statistics.mean(all_variations), 2),
            'insights': self._generate_comparative_insights(entity_trends, best_performers, worst_performers)
        }
    
    def _calculate_variation(self, val_init: float, val_final: float) -> float:
        """Calcule la variation en pourcentage"""
        if val_init == 0:
            return 0 if val_final == 0 else 100
        return ((val_final - val_init) / val_init) * 100
    
    def _calculate_average_variation(self, values: List[float]) -> float:
        """Calcule la variation moyenne entre périodes consécutives"""
        if len(values) < 2:
            return 0
        
        variations = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                var = ((values[i] - values[i-1]) / values[i-1]) * 100
                variations.append(var)
        
        return statistics.mean(variations) if variations else 0
    
    def _classify_trend(self, variation_avg: float) -> str:
        """Classifie la tendance selon les seuils"""
        if variation_avg >= self.SEUILS_VARIATION['forte_hausse']:
            return 'forte_hausse'
        elif variation_avg >= self.SEUILS_VARIATION['hausse']:
            return 'hausse'
        elif variation_avg >= self.SEUILS_VARIATION['stable']:
            return 'stable'
        elif variation_avg >= self.SEUILS_VARIATION['baisse']:
            return 'baisse'
        else:
            return 'forte_baisse'
    
    def _detect_seasonality(self, values: List[float]) -> Dict[str, Any]:
        """Détecte la saisonnalité basique dans les données"""
        if len(values) < 12:  # Besoin d'au moins 1 an de données
            return {
                'detectee': False,
                'message': 'Pas assez de données pour détecter la saisonnalité'
            }
        
        # Calculer la variance par position dans le cycle (ex: mois)
        cycle_length = 12  # Supposer un cycle annuel
        positions = defaultdict(list)
        
        for i, val in enumerate(values):
            pos = i % cycle_length
            positions[pos].append(val)
        
        # Si certaines positions ont des moyennes très différentes = saisonnalité
        position_means = {pos: statistics.mean(vals) for pos, vals in positions.items() if len(vals) > 1}
        
        if len(position_means) < 2:
            return {'detectee': False, 'message': 'Données insuffisantes'}
        
        mean_values = list(position_means.values())
        global_mean = statistics.mean(mean_values)
        
        # Coefficient de variation
        if global_mean != 0:
            cv = (statistics.stdev(mean_values) / global_mean) * 100
            
            if cv > 15:  # Seuil arbitraire pour détection saisonnalité
                max_month = max(position_means, key=position_means.get)
                min_month = min(position_means, key=position_means.get)
                
                return {
                    'detectee': True,
                    'coefficient_variation': round(cv, 2),
                    'mois_fort': max_month + 1,  # +1 car index commence à 0
                    'mois_faible': min_month + 1,
                    'message': f'Saisonnalité détectée (CV={cv:.1f}%)'
                }
        
        return {
            'detectee': False,
            'message': 'Pas de saisonnalité significative détectée'
        }
    
    def _simple_forecast(self, values: List[float], periods: int = 1) -> float:
        """Prévision simple basée sur moyenne mobile et tendance"""
        if len(values) < 3:
            return values[-1] if values else 0
        
        # Moyenne mobile des 3 dernières périodes
        recent_values = values[-3:]
        moving_avg = statistics.mean(recent_values)
        
        # Tendance récente
        recent_trend = self._calculate_average_variation(recent_values)
        
        # Prévision = moyenne mobile + tendance
        forecast = moving_avg * (1 + recent_trend / 100)
        
        return max(0, forecast)  # Pas de valeurs négatives
    
    def _calculate_volatility(self, values: List[float]) -> str:
        """Calcule la volatilité de la série"""
        if len(values) < 2:
            return 'indéterminée'
        
        mean_val = statistics.mean(values)
        if mean_val == 0:
            return 'indéterminée'
        
        cv = (statistics.stdev(values) / mean_val) * 100
        
        if cv < 10:
            return 'faible'
        elif cv < 25:
            return 'modérée'
        else:
            return 'élevée'
    
    def _generate_trend_insights(self, tendance: str, 
                                 variation: float,
                                 saisonnalite: Dict,
                                 values: List[float]) -> List[str]:
        """Génère des insights basés sur la tendance détectée"""
        insights = []
        
        # Insights sur la tendance
        trend_messages = {
            'forte_hausse': f'📈 Excellente performance ! Croissance de {variation:.1f}% détectée.',
            'hausse': f'📊 Tendance positive avec une progression de {variation:.1f}%.',
            'stable': f'➡️ Performance stable (variation de {variation:.1f}%).',
            'baisse': f'📉 Attention : baisse de {variation:.1f}% observée.',
            'forte_baisse': f'🔴 Alerte : forte baisse de {variation:.1f}% ! Action requise.'
        }
        insights.append(trend_messages.get(tendance, 'Tendance indéterminée'))
        
        # Insights sur la saisonnalité
        if saisonnalite.get('detectee'):
            mois_fort = saisonnalite.get('mois_fort')
            mois_faible = saisonnalite.get('mois_faible')
            insights.append(f'📅 Saisonnalité détectée : pic au mois {mois_fort}, creux au mois {mois_faible}')
        
        # Insights sur la volatilité
        volatilite = self._calculate_volatility(values)
        if volatilite == 'élevée':
            insights.append('⚠️ Forte volatilité détectée - Performance instable')
        elif volatilite == 'faible':
            insights.append('✅ Volatilité faible - Performance stable et prévisible')
        
        # Recommandations selon tendance
        if tendance in ['baisse', 'forte_baisse']:
            insights.append('💡 Recommandation : Analyser les causes et mettre en place des actions correctives')
        elif tendance == 'forte_hausse':
            insights.append('💡 Recommandation : Capitaliser sur cette dynamique positive')
        
        return insights
    
    def _generate_comparative_insights(self, all_trends: Dict,
                                      best: List[Tuple],
                                      worst: List[Tuple]) -> List[str]:
        """Génère des insights comparatifs entre entités"""
        insights = []
        
        if best:
            best_entity, best_trend = best[0]
            insights.append(
                f'🏆 Meilleure performance : {best_entity} '
                f'({best_trend["variation_totale_pct"]:+.1f}%)'
            )
        
        if worst:
            worst_entity, worst_trend = worst[0]
            insights.append(
                f'⚠️ Performance la plus faible : {worst_entity} '
                f'({worst_trend["variation_totale_pct"]:+.1f}%)'
            )
        
        # Écart entre meilleur et pire
        if best and worst:
            ecart = best[0][1]['variation_totale_pct'] - worst[0][1]['variation_totale_pct']
            insights.append(f'📊 Écart de performance : {ecart:.1f} points de pourcentage')
        
        # Distribution des tendances
        trend_counts = defaultdict(int)
        for trend in all_trends.values():
            trend_counts[trend['tendance']] += 1
        
        total = len(all_trends)
        for trend_type, count in trend_counts.items():
            pct = (count / total) * 100
            if pct >= 30:  # Mention si > 30%
                trend_labels = {
                    'forte_hausse': 'forte hausse',
                    'hausse': 'hausse',
                    'stable': 'stables',
                    'baisse': 'baisse',
                    'forte_baisse': 'forte baisse'
                }
                insights.append(
                    f'📈 {pct:.0f}% des entités sont en {trend_labels.get(trend_type, trend_type)}'
                )
        
        return insights
    
    def compare_periods(self, data: List[Dict],
                       period_field: str,
                       value_field: str,
                       period1: Any,
                       period2: Any) -> Dict[str, Any]:
        """Compare deux périodes spécifiques"""
        
        # Extraire les valeurs pour chaque période
        val1 = None
        val2 = None
        
        for row in data:
            if row.get(period_field) == period1:
                val1 = row.get(value_field)
            if row.get(period_field) == period2:
                val2 = row.get(value_field)
        
        if val1 is None or val2 is None:
            return {'error': 'Périodes non trouvées dans les données'}
        
        variation = self._calculate_variation(val1, val2)
        
        return {
            'periode_1': period1,
            'valeur_1': round(val1, 2),
            'periode_2': period2,
            'valeur_2': round(val2, 2),
            'variation_pct': round(variation, 2),
            'variation_absolue': round(val2 - val1, 2),
            'tendance': 'hausse' if variation > 0 else 'baisse' if variation < 0 else 'stable',
            'emoji': '📈' if variation > 0 else '📉' if variation < 0 else '➡️'
        }
