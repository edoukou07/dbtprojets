"""
Script pour initialiser les seuils d'alerte et créer des alertes de test
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import AlertThreshold, Alert
from datetime import datetime

def init_alert_thresholds():
    """Créer les seuils d'alerte par défaut"""
    
    thresholds = [
        {
            'alert_type': 'taux_recouvrement',
            'threshold_value': 60.0,
            'threshold_operator': '<',
            'is_active': True,
            'check_interval': 60,
            'send_email': False,
        },
        {
            'alert_type': 'facture_impayee',
            'threshold_value': 90.0,  # 90 jours
            'threshold_operator': '>',
            'is_active': True,
            'check_interval': 1440,  # 24 heures
            'send_email': True,
            'email_recipients': 'admin@sigeti.ci',
        },
        {
            'alert_type': 'occupation_faible',
            'threshold_value': 30.0,  # 30%
            'threshold_operator': '<',
            'is_active': True,
            'check_interval': 720,  # 12 heures
            'send_email': False,
        },
        {
            'alert_type': 'client_inactif',
            'threshold_value': 180.0,  # 180 jours
            'threshold_operator': '>',
            'is_active': True,
            'check_interval': 1440,
            'send_email': False,
        },
    ]
    
    created_count = 0
    for threshold_data in thresholds:
        threshold, created = AlertThreshold.objects.get_or_create(
            alert_type=threshold_data['alert_type'],
            defaults=threshold_data
        )
        if created:
            created_count += 1
            print(f"✅ Seuil créé: {threshold.alert_type} {threshold.threshold_operator} {threshold.threshold_value}")
        else:
            print(f"ℹ️  Seuil existant: {threshold.alert_type}")
    
    print(f"\n✨ {created_count} nouveaux seuils créés sur {len(thresholds)} total")
    return AlertThreshold.objects.all()


def create_sample_alerts():
    """Créer des alertes de démonstration"""
    
    sample_alerts = [
        {
            'alert_type': 'taux_recouvrement',
            'severity': 'high',
            'status': 'active',
            'title': 'Taux de recouvrement critique: 45.0%',
            'message': 'Le taux de recouvrement moyen (45.0%) est en dessous du seuil de 60%. Action immédiate requise pour améliorer la collecte des créances.',
            'threshold_value': 60.0,
            'actual_value': 45.0,
            'context_data': {
                'annee': 2025,
                'mois': 11,
                'zone': 'Zone Industrielle de Yopougon',
                'trimestre': 4
            }
        },
        {
            'alert_type': 'facture_impayee',
            'severity': 'critical',
            'status': 'active',
            'title': '15 factures impayées anciennes détectées',
            'message': 'Il y a 15 factures avec un délai de paiement supérieur à 90 jours. Montant total impayé: 12,500,000 F CFA. Relances urgentes nécessaires.',
            'threshold_value': 90.0,
            'actual_value': 15.0,
            'context_data': {
                'count': 15,
                'total_impaye': 12500000,
                'plus_ancienne': '2025-06-15',
                'zones_concernees': ['Yopougon', 'Koumassi', 'Treichville']
            }
        },
        {
            'alert_type': 'occupation_faible',
            'severity': 'medium',
            'status': 'active',
            'title': 'Taux d\'occupation faible: Zone Industrielle de Vridi',
            'message': 'La zone Vridi a un taux d\'occupation de 28.5%, en dessous du seuil de 30%. Campagne de promotion recommandée.',
            'threshold_value': 30.0,
            'actual_value': 28.5,
            'context_data': {
                'zone_id': 4,
                'zone_nom': 'Zone Industrielle de Vridi',
                'lots_disponibles': 45,
                'lots_totaux': 63,
                'surface_disponible': 125000
            }
        },
        {
            'alert_type': 'taux_recouvrement',
            'severity': 'medium',
            'status': 'acknowledged',
            'title': 'Taux de recouvrement en amélioration',
            'message': 'Le taux de recouvrement est passé de 52% à 58%. Continuer les efforts de relance.',
            'threshold_value': 60.0,
            'actual_value': 58.0,
            'context_data': {
                'annee': 2025,
                'mois': 10,
                'evolution': '+6%',
                'zone': 'Zone Industrielle de Koumassi'
            },
            'acknowledged_at': datetime.now(),
            'acknowledged_by': 'admin'
        },
        {
            'alert_type': 'client_inactif',
            'severity': 'low',
            'status': 'resolved',
            'title': '8 clients inactifs depuis plus de 6 mois',
            'message': 'Plusieurs clients n\'ont pas eu de nouvelles factures depuis 6 mois. Contactez-les pour vérifier leur situation.',
            'threshold_value': 180.0,
            'actual_value': 8.0,
            'context_data': {
                'clients': ['ENT-001', 'ENT-015', 'ENT-028', 'ENT-042', 'ENT-056', 'ENT-071', 'ENT-089', 'ENT-095'],
                'dernier_contact': '2025-05-10'
            },
            'resolved_at': datetime.now()
        },
    ]
    
    created_count = 0
    for alert_data in sample_alerts:
        # Vérifier si une alerte similaire existe déjà
        existing = Alert.objects.filter(
            alert_type=alert_data['alert_type'],
            title=alert_data['title']
        ).first()
        
        if not existing:
            alert = Alert.objects.create(**alert_data)
            created_count += 1
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🔵'
            }
            status_emoji = {
                'active': '⚠️',
                'acknowledged': '👁️',
                'resolved': '✅',
                'dismissed': '🚫'
            }
            print(f"{severity_emoji[alert.severity]} {status_emoji[alert.status]} Alerte créée: {alert.title}")
        else:
            print(f"ℹ️  Alerte existante: {alert_data['title']}")
    
    print(f"\n✨ {created_count} nouvelles alertes créées sur {len(sample_alerts)} total")
    return Alert.objects.all()


if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Initialisation des Alertes SIGETI BI")
    print("=" * 80)
    print()
    
    print("📋 Étape 1: Création des seuils d'alerte")
    print("-" * 80)
    thresholds = init_alert_thresholds()
    print()
    
    print("📋 Étape 2: Création des alertes de démonstration")
    print("-" * 80)
    alerts = create_sample_alerts()
    print()
    
    print("=" * 80)
    print("✅ Initialisation terminée avec succès!")
    print("=" * 80)
    print()
    print(f"📊 Statistiques:")
    print(f"   - Seuils d'alerte: {thresholds.count()}")
    print(f"   - Alertes actives: {alerts.filter(status='active').count()}")
    print(f"   - Alertes acquittées: {alerts.filter(status='acknowledged').count()}")
    print(f"   - Alertes résolues: {alerts.filter(status='resolved').count()}")
    print(f"   - Total alertes: {alerts.count()}")
    print()
    print("🌐 Accédez au dashboard: http://localhost:5173")
    print("🔗 API Alertes: http://localhost:8000/api/alerts/")
    print()
