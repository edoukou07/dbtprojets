"""
Système d'alertes intelligentes pour le chatbot BI
Détecte automatiquement les problèmes et génère des alertes prioritaires
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class AlertSystem:
    """Système de détection et gestion d'alertes intelligentes"""
    
    # Seuils critiques pour alertes
    ALERT_THRESHOLDS = {
        # Financier
        'taux_impaye_critique': 40.0,       # > 40% impayés = alerte rouge
        'taux_impaye_warning': 25.0,        # > 25% = alerte orange
        'ca_baisse_critique': -30.0,        # Baisse > 30% = critique
        'ca_baisse_warning': -15.0,         # Baisse > 15% = warning
        
        # Occupation
        'occupation_critique_basse': 30.0,  # < 30% = sous-utilisation critique
        'occupation_warning_basse': 50.0,   # < 50% = warning
        'occupation_saturee': 95.0,         # > 95% = saturation
        
        # Opérationnel
        'delai_paiement_critique': 90,      # > 90 jours = critique
        'delai_paiement_warning': 60,       # > 60 jours = warning
        'taux_cloture_faible': 60.0,        # < 60% collectes clôturées = problème
    }
    
    # Types d'alertes
    ALERT_TYPES = {
        'IMPAYE_CRITIQUE': {
            'icon': '🔴',
            'severity': 'critical',
            'category': 'financier',
            'title': 'Impayés critiques'
        },
        'OCCUPATION_FAIBLE': {
            'icon': '⚠️',
            'severity': 'warning',
            'category': 'occupation',
            'title': 'Sous-utilisation'
        },
        'OCCUPATION_SATUREE': {
            'icon': '🔴',
            'severity': 'critical',
            'category': 'occupation',
            'title': 'Saturation'
        },
        'DELAI_PAIEMENT': {
            'icon': '⏰',
            'severity': 'warning',
            'category': 'financier',
            'title': 'Délais de paiement'
        },
        'BAISSE_CA': {
            'icon': '📉',
            'severity': 'warning',
            'category': 'financier',
            'title': 'Baisse CA'
        },
        'COLLECTES_NON_CLOTUREES': {
            'icon': '⚠️',
            'severity': 'warning',
            'category': 'operationnel',
            'title': 'Collectes en retard'
        },
        'DEMANDES_EN_ATTENTE': {
            'icon': '📋',
            'severity': 'info',
            'category': 'operationnel',
            'title': 'Demandes en attente'
        },
        'CLIENT_RISQUE': {
            'icon': '🚨',
            'severity': 'critical',
            'category': 'clients',
            'title': 'Client à risque'
        }
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_all_zones(self, data: List[Dict]) -> List[Dict]:
        """
        Analyse toutes les zones et génère des alertes
        
        Returns:
            Liste d'alertes triées par priorité (critical > warning > info)
        """
        if not data:
            return []
        
        alerts = []
        
        # Analyser chaque zone/entité
        for row in data:
            zone_name = row.get('nom_zone') or row.get('raison_sociale') or row.get('zone') or 'Zone inconnue'
            
            # Alertes financières
            alerts.extend(self._check_financial_alerts(row, zone_name))
            
            # Alertes occupation
            alerts.extend(self._check_occupation_alerts(row, zone_name))
            
            # Alertes opérationnelles
            alerts.extend(self._check_operational_alerts(row, zone_name))
            
            # Alertes clients
            alerts.extend(self._check_client_alerts(row, zone_name))
        
        # Trier par priorité
        priority_order = {'critical': 0, 'warning': 1, 'info': 2}
        alerts.sort(key=lambda x: (priority_order.get(x['severity'], 3), -x.get('impact_score', 0)))
        
        return alerts
    
    def _check_financial_alerts(self, row: Dict, entity_name: str) -> List[Dict]:
        """Vérifie les alertes financières"""
        alerts = []
        
        # Alerte impayés critiques
        taux_impaye = row.get('taux_impaye_pct') or row.get('taux_paiement_pct')
        if taux_impaye is not None:
            # Si c'est un taux de paiement, calculer l'impayé
            if 'taux_paiement_pct' in row:
                taux_impaye = 100 - taux_impaye
            
            ca_impaye = row.get('ca_impaye') or row.get('montant_impaye') or 0
            
            if taux_impaye >= self.ALERT_THRESHOLDS['taux_impaye_critique']:
                alerts.append({
                    'type': 'IMPAYE_CRITIQUE',
                    'severity': 'critical',
                    'entity': entity_name,
                    'message': f"{entity_name} : Taux d'impayés critique à {taux_impaye:.1f}%",
                    'details': f"Montant impayé : {ca_impaye:,.0f} FCFA",
                    'value': taux_impaye,
                    'threshold': self.ALERT_THRESHOLDS['taux_impaye_critique'],
                    'impact_score': taux_impaye * (ca_impaye / 1_000_000),  # Score basé sur % et montant
                    'recommendations': [
                        "Relance immédiate des clients en retard",
                        "Analyse des créances anciennes",
                        "Mise en place d'un plan de recouvrement"
                    ],
                    **self.ALERT_TYPES['IMPAYE_CRITIQUE']
                })
            elif taux_impaye >= self.ALERT_THRESHOLDS['taux_impaye_warning']:
                alerts.append({
                    'type': 'IMPAYE_CRITIQUE',
                    'severity': 'warning',
                    'entity': entity_name,
                    'message': f"{entity_name} : Taux d'impayés élevé à {taux_impaye:.1f}%",
                    'details': f"Montant impayé : {ca_impaye:,.0f} FCFA",
                    'value': taux_impaye,
                    'threshold': self.ALERT_THRESHOLDS['taux_impaye_warning'],
                    'impact_score': taux_impaye * (ca_impaye / 1_000_000) * 0.7,
                    'recommendations': [
                        "Surveiller de près l'évolution",
                        "Relance préventive des clients"
                    ],
                    **self.ALERT_TYPES['IMPAYE_CRITIQUE']
                })
        
        # Alerte délais de paiement
        delai_moyen = row.get('delai_moyen_paiement_jours') or row.get('delai_moyen_paiement')
        if delai_moyen and delai_moyen >= self.ALERT_THRESHOLDS['delai_paiement_warning']:
            severity = 'critical' if delai_moyen >= self.ALERT_THRESHOLDS['delai_paiement_critique'] else 'warning'
            alerts.append({
                'type': 'DELAI_PAIEMENT',
                'severity': severity,
                'entity': entity_name,
                'message': f"{entity_name} : Délai de paiement de {delai_moyen:.0f} jours",
                'details': f"Seuil normal : {self.ALERT_THRESHOLDS['delai_paiement_warning']} jours",
                'value': delai_moyen,
                'threshold': self.ALERT_THRESHOLDS['delai_paiement_warning'],
                'impact_score': delai_moyen / 10,
                'recommendations': [
                    "Réviser les conditions de paiement",
                    "Identifier les causes de retard",
                    "Mettre en place des pénalités de retard"
                ],
                **self.ALERT_TYPES['DELAI_PAIEMENT']
            })
        
        return alerts
    
    def _check_occupation_alerts(self, row: Dict, entity_name: str) -> List[Dict]:
        """Vérifie les alertes d'occupation"""
        alerts = []
        
        taux_occupation = row.get('taux_occupation_pct') or row.get('taux_occupation')
        if taux_occupation is None:
            return alerts
        
        lots_disponibles = row.get('lots_disponibles') or 0
        lots_total = row.get('nombre_total_lots') or 0
        
        # Alerte sous-utilisation
        if taux_occupation < self.ALERT_THRESHOLDS['occupation_critique_basse']:
            alerts.append({
                'type': 'OCCUPATION_FAIBLE',
                'severity': 'critical',
                'entity': entity_name,
                'message': f"{entity_name} : Occupation très faible à {taux_occupation:.1f}%",
                'details': f"{lots_disponibles} lots disponibles sur {lots_total}",
                'value': taux_occupation,
                'threshold': self.ALERT_THRESHOLDS['occupation_critique_basse'],
                'impact_score': (100 - taux_occupation) * (lots_disponibles / 10),
                'recommendations': [
                    "Campagne de commercialisation urgente",
                    "Analyse des prix et attractivité",
                    "Étude de la concurrence locale"
                ],
                **self.ALERT_TYPES['OCCUPATION_FAIBLE']
            })
        elif taux_occupation < self.ALERT_THRESHOLDS['occupation_warning_basse']:
            alerts.append({
                'type': 'OCCUPATION_FAIBLE',
                'severity': 'warning',
                'entity': entity_name,
                'message': f"{entity_name} : Occupation faible à {taux_occupation:.1f}%",
                'details': f"{lots_disponibles} lots disponibles sur {lots_total}",
                'value': taux_occupation,
                'threshold': self.ALERT_THRESHOLDS['occupation_warning_basse'],
                'impact_score': (100 - taux_occupation) * (lots_disponibles / 10) * 0.6,
                'recommendations': [
                    "Intensifier la prospection",
                    "Proposer des offres promotionnelles"
                ],
                **self.ALERT_TYPES['OCCUPATION_FAIBLE']
            })
        
        # Alerte saturation
        elif taux_occupation >= self.ALERT_THRESHOLDS['occupation_saturee']:
            alerts.append({
                'type': 'OCCUPATION_SATUREE',
                'severity': 'critical',
                'entity': entity_name,
                'message': f"{entity_name} : Saturation à {taux_occupation:.1f}%",
                'details': f"Seulement {lots_disponibles} lots restants",
                'value': taux_occupation,
                'threshold': self.ALERT_THRESHOLDS['occupation_saturee'],
                'impact_score': taux_occupation * 1.5,
                'recommendations': [
                    "Planifier l'extension de la zone",
                    "Optimiser l'utilisation actuelle",
                    "Préparer une nouvelle zone"
                ],
                **self.ALERT_TYPES['OCCUPATION_SATUREE']
            })
        
        # Alerte demandes en attente
        demandes_attente = row.get('demandes_en_attente') or 0
        if demandes_attente > 10:
            alerts.append({
                'type': 'DEMANDES_EN_ATTENTE',
                'severity': 'info' if demandes_attente < 20 else 'warning',
                'entity': entity_name,
                'message': f"{entity_name} : {demandes_attente} demandes en attente",
                'details': "Traitement requis pour fluidifier le processus",
                'value': demandes_attente,
                'threshold': 10,
                'impact_score': demandes_attente / 5,
                'recommendations': [
                    "Accélérer le traitement des demandes",
                    "Vérifier les ressources allouées",
                    "Identifier les blocages éventuels"
                ],
                **self.ALERT_TYPES['DEMANDES_EN_ATTENTE']
            })
        
        return alerts
    
    def _check_operational_alerts(self, row: Dict, entity_name: str) -> List[Dict]:
        """Vérifie les alertes opérationnelles"""
        alerts = []
        
        # Alerte collectes non clôturées
        taux_cloture = row.get('taux_cloture_pct')
        if taux_cloture is not None and taux_cloture < self.ALERT_THRESHOLDS['taux_cloture_faible']:
            collectes_ouvertes = row.get('collectes_ouvertes') or 0
            alerts.append({
                'type': 'COLLECTES_NON_CLOTUREES',
                'severity': 'warning',
                'entity': entity_name,
                'message': f"{entity_name} : {collectes_ouvertes} collectes non clôturées ({taux_cloture:.1f}%)",
                'details': "Impact sur le recouvrement et la trésorerie",
                'value': 100 - taux_cloture,
                'threshold': 100 - self.ALERT_THRESHOLDS['taux_cloture_faible'],
                'impact_score': collectes_ouvertes * 2,
                'recommendations': [
                    "Clôturer les collectes en retard",
                    "Analyser les causes de blocage",
                    "Former les équipes au processus"
                ],
                **self.ALERT_TYPES['COLLECTES_NON_CLOTUREES']
            })
        
        return alerts
    
    def _check_client_alerts(self, row: Dict, entity_name: str) -> List[Dict]:
        """Vérifie les alertes clients"""
        alerts = []
        
        # Alerte client à risque
        niveau_risque = row.get('niveau_risque')
        if niveau_risque in ['Élevé', 'Critique']:
            nb_factures_retard = row.get('nombre_factures_retard') or 0
            ca_impaye_client = row.get('ca_impaye') or 0
            
            severity = 'critical' if niveau_risque == 'Critique' else 'warning'
            alerts.append({
                'type': 'CLIENT_RISQUE',
                'severity': severity,
                'entity': entity_name,
                'message': f"{entity_name} : Client à risque {niveau_risque.lower()}",
                'details': f"{nb_factures_retard} factures en retard, {ca_impaye_client:,.0f} FCFA impayés",
                'value': nb_factures_retard,
                'threshold': 0,
                'impact_score': (ca_impaye_client / 1_000_000) * 2,
                'recommendations': [
                    "Suspendre toute nouvelle attribution",
                    "Planifier un rendez-vous urgent",
                    "Évaluer la solvabilité du client",
                    "Envisager des actions en recouvrement"
                ],
                **self.ALERT_TYPES['CLIENT_RISQUE']
            })
        
        return alerts
    
    def get_alerts_summary(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Génère un résumé des alertes"""
        if not alerts:
            return {
                'total': 0,
                'by_severity': {},
                'by_category': {},
                'top_critical': [],
                'message': '✅ Aucune alerte détectée - Tout fonctionne normalement'
            }
        
        # Compter par sévérité
        by_severity = defaultdict(int)
        by_category = defaultdict(int)
        
        for alert in alerts:
            by_severity[alert['severity']] += 1
            by_category[alert.get('category', 'other')] += 1
        
        # Top 5 alertes critiques
        critical_alerts = [a for a in alerts if a['severity'] == 'critical']
        top_critical = sorted(critical_alerts, key=lambda x: -x.get('impact_score', 0))[:5]
        
        return {
            'total': len(alerts),
            'by_severity': dict(by_severity),
            'by_category': dict(by_category),
            'top_critical': top_critical,
            'critical_count': len(critical_alerts),
            'warning_count': by_severity.get('warning', 0),
            'info_count': by_severity.get('info', 0),
            'message': self._generate_summary_message(by_severity, len(alerts))
        }
    
    def _generate_summary_message(self, by_severity: Dict, total: int) -> str:
        """Génère un message de résumé"""
        critical = by_severity.get('critical', 0)
        warning = by_severity.get('warning', 0)
        info = by_severity.get('info', 0)
        
        if critical > 0:
            return f"🔴 {critical} alerte(s) critique(s) détectée(s) - Action immédiate requise !"
        elif warning > 0:
            return f"⚠️ {warning} alerte(s) nécessitant une attention"
        elif info > 0:
            return f"ℹ️ {info} point(s) d'information"
        else:
            return "✅ Situation normale"
    
    def filter_alerts(self, alerts: List[Dict], 
                     severity: Optional[str] = None,
                     category: Optional[str] = None,
                     min_impact: float = 0) -> List[Dict]:
        """Filtre les alertes selon des critères"""
        filtered = alerts
        
        if severity:
            filtered = [a for a in filtered if a['severity'] == severity]
        
        if category:
            filtered = [a for a in filtered if a.get('category') == category]
        
        if min_impact > 0:
            filtered = [a for a in filtered if a.get('impact_score', 0) >= min_impact]
        
        return filtered
