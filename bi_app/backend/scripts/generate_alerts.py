"""
Script pour générer automatiquement des alertes basées sur les données actuelles
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from analytics.models import (
    MartPerformanceFinanciere,
    MartOccupationZones,
    MartPortefeuilleClients,
    Alert
)
from ai_chat.alert_system import AlertSystem
from datetime import datetime
from django.core.cache import cache


def get_alert_thresholds():
    """Récupère les seuils depuis le cache ou utilise les valeurs par défaut"""
    thresholds = cache.get('alert_thresholds')
    if not thresholds:
        return AlertSystem.ALERT_THRESHOLDS
    
    # Convertir le format du cache au format AlertSystem
    return {
        'taux_impaye_critique': thresholds['financier']['taux_impaye_critique'],
        'taux_impaye_warning': thresholds['financier']['taux_impaye_warning'],
        'ca_baisse_critique': thresholds['financier']['ca_baisse_critique'],
        'ca_baisse_warning': thresholds['financier']['ca_baisse_warning'],
        'delai_paiement_critique': thresholds['financier']['delai_paiement_critique'],
        'delai_paiement_warning': thresholds['financier']['delai_paiement_warning'],
        'occupation_critique_basse': thresholds['occupation']['occupation_critique_basse'],
        'occupation_warning_basse': thresholds['occupation']['occupation_warning_basse'],
        'occupation_saturee': thresholds['occupation']['occupation_saturee'],
        'taux_cloture_faible': thresholds['operationnel']['taux_cloture_faible'],
    }


def generate_financial_alerts(alert_system, thresholds):
    """Génère les alertes financières"""
    print("\n🔍 Analyse des données financières...")
    
    # Récupérer les données financières de l'année en cours
    current_year = datetime.now().year
    financial_data = MartPerformanceFinanciere.objects.filter(
        annee=current_year
    ).values(
        'nom_zone',
        'taux_paiement_pct',
        'montant_impaye',
        'delai_moyen_paiement'
    )
    
    alerts_data = []
    for row in financial_data:
        # Convertir en dict pour AlertSystem
        delai = row['delai_moyen_paiement']
        delai_jours = delai.days if delai else None
        
        data = {
            'nom_zone': row['nom_zone'],
            'taux_paiement_pct': float(row['taux_paiement_pct']) if row['taux_paiement_pct'] else None,
            'ca_impaye': float(row['montant_impaye']) if row['montant_impaye'] else 0,
            'delai_moyen_paiement_jours': delai_jours,
        }
        alerts_data.append(data)
    
    if alerts_data:
        alerts = alert_system.analyze_all_zones(alerts_data)
        print(f"  ✅ {len(alerts)} alertes financières détectées")
        return alerts
    
    print("  ⚠️ Aucune donnée financière trouvée")
    return []


def generate_occupation_alerts(alert_system, thresholds):
    """Génère les alertes d'occupation"""
    print("\n🔍 Analyse des données d'occupation...")
    
    occupation_data = MartOccupationZones.objects.all().values(
        'nom_zone',
        'taux_occupation_pct',
        'lots_disponibles',
        'nombre_total_lots'
    )
    
    alerts_data = []
    for row in occupation_data:
        data = {
            'nom_zone': row['nom_zone'],
            'taux_occupation_pct': float(row['taux_occupation_pct']) if row['taux_occupation_pct'] else None,
            'lots_disponibles': row['lots_disponibles'],
            'nombre_total_lots': row['nombre_total_lots'],
        }
        alerts_data.append(data)
    
    if alerts_data:
        alerts = alert_system.analyze_all_zones(alerts_data)
        print(f"  ✅ {len(alerts)} alertes d'occupation détectées")
        return alerts
    
    print("  ⚠️ Aucune donnée d'occupation trouvée")
    return []


def generate_client_alerts(alert_system, thresholds):
    """Génère les alertes clients"""
    print("\n🔍 Analyse des clients à risque...")
    
    client_data = MartPortefeuilleClients.objects.filter(
        niveau_risque__in=['Élevé', 'Critique']
    ).values(
        'raison_sociale',
        'niveau_risque',
        'taux_paiement_pct',
        'ca_impaye',
        'nombre_factures_retard'
    )[:20]  # Limiter aux 20 clients les plus à risque
    
    alerts_data = []
    for row in client_data:
        data = {
            'raison_sociale': row['raison_sociale'],
            'niveau_risque': row['niveau_risque'],
            'taux_paiement_pct': float(row['taux_paiement_pct']) if row['taux_paiement_pct'] else None,
            'ca_impaye': float(row['ca_impaye']) if row['ca_impaye'] else 0,
            'nombre_factures_retard': row['nombre_factures_retard'],
        }
        alerts_data.append(data)
    
    if alerts_data:
        alerts = alert_system.analyze_all_zones(alerts_data)
        print(f"  ✅ {len(alerts)} alertes clients détectées")
        return alerts
    
    print("  ⚠️ Aucun client à risque trouvé")
    return []


def save_alerts_to_db(alerts):
    """Sauvegarde les alertes dans la base de données"""
    print(f"\n💾 Sauvegarde de {len(alerts)} alertes...")
    
    # Marquer toutes les anciennes alertes actives comme résolues
    from django.utils import timezone
    old_active_alerts = Alert.objects.filter(status='active')
    old_count = old_active_alerts.count()
    old_active_alerts.update(status='resolved', resolved_at=timezone.now())
    print(f"  📝 {old_count} anciennes alertes marquées comme résolues")
    
    created_count = 0
    for alert_data in alerts:
        try:
            # Mapper le type d'alerte
            alert_type = alert_data.get('type', '').lower()
            if 'impaye' in alert_type or 'paiement' in alert_type:
                alert_type_db = 'facture_impayee'
            elif 'occupation' in alert_type:
                alert_type_db = 'occupation_faible'
            elif 'client' in alert_type:
                alert_type_db = 'client_inactif'
            else:
                alert_type_db = 'objectif_non_atteint'
            
            # Mapper les champs de AlertSystem vers le modèle Alert
            alert = Alert(
                alert_type=alert_type_db,
                severity=alert_data.get('severity', 'low'),
                title=alert_data.get('title', alert_data.get('message', 'Alerte')),
                message=alert_data.get('message', ''),
                threshold_value=alert_data.get('threshold'),
                actual_value=alert_data.get('value'),
                status='active',
                context_data={
                    'entity': alert_data.get('entity', 'Système'),
                    'details': alert_data.get('details'),
                    'recommendations': alert_data.get('recommendations', []),
                    'category': alert_data.get('category'),
                    'icon': alert_data.get('icon'),
                    'impact_score': alert_data.get('impact_score', 0),
                }
            )
            alert.save()
            created_count += 1
        except Exception as e:
            print(f"  ❌ Erreur lors de la création de l'alerte: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"  ✅ {created_count} nouvelles alertes créées")
    return created_count


def main():
    """Fonction principale"""
    print("=" * 60)
    print("🚨 GÉNÉRATION AUTOMATIQUE DES ALERTES")
    print("=" * 60)
    
    # Récupérer les seuils configurés
    thresholds = get_alert_thresholds()
    print(f"\n📊 Seuils utilisés:")
    print(f"  - Taux impayé critique: {thresholds['taux_impaye_critique']}%")
    print(f"  - Occupation critique basse: {thresholds['occupation_critique_basse']}%")
    print(f"  - Délai paiement critique: {thresholds['delai_paiement_critique']} jours")
    
    # Initialiser le système d'alertes
    alert_system = AlertSystem()
    alert_system.ALERT_THRESHOLDS = thresholds
    
    # Générer les alertes
    all_alerts = []
    
    # 1. Alertes financières
    financial_alerts = generate_financial_alerts(alert_system, thresholds)
    all_alerts.extend(financial_alerts)
    
    # 2. Alertes d'occupation
    occupation_alerts = generate_occupation_alerts(alert_system, thresholds)
    all_alerts.extend(occupation_alerts)
    
    # 3. Alertes clients
    client_alerts = generate_client_alerts(alert_system, thresholds)
    all_alerts.extend(client_alerts)
    
    # Sauvegarder en base
    if all_alerts:
        created = save_alerts_to_db(all_alerts)
        
        # Afficher un résumé
        print("\n" + "=" * 60)
        print("📈 RÉSUMÉ")
        print("=" * 60)
        print(f"  Total alertes générées: {len(all_alerts)}")
        print(f"  Alertes sauvegardées: {created}")
        
        # Compter par sévérité
        critical = len([a for a in all_alerts if a['severity'] == 'critical'])
        warning = len([a for a in all_alerts if a['severity'] == 'warning'])
        info = len([a for a in all_alerts if a['severity'] == 'info'])
        
        print(f"\n  Par sévérité:")
        print(f"    🔴 Critique: {critical}")
        print(f"    🟠 Warning: {warning}")
        print(f"    🔵 Info: {info}")
        
        print("\n✅ Génération terminée avec succès!")
        print("=" * 60)
    else:
        print("\n⚠️ Aucune alerte à générer (toutes les métriques sont dans les normes)")
        print("=" * 60)


if __name__ == '__main__':
    main()
