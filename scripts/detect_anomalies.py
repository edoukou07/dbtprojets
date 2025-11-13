"""
Script de détection d'anomalies dans le DWH
Surveille les métriques critiques et envoie des alertes
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': os.getenv('DWH_DB_NAME', 'sigeti_node_db'),
    'user': os.getenv('DWH_DB_USER', 'postgres'),
    'password': os.getenv('DBT_PASSWORD', 'postgres')
}

class AnomalyDetector:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.anomalies = []
    
    def check_data_freshness(self):
        """Vérifie que les données ont été rafraîchies récemment"""
        cursor = self.conn.cursor()
        
        # Vérifier la fraîcheur de fait_attributions
        cursor.execute("""
            SELECT MAX(created_at) as derniere_maj
            FROM dwh_facts.fait_attributions;
        """)
        
        last_update = cursor.fetchone()[0]
        if last_update:
            days_old = (datetime.now().date() - last_update).days
            if days_old > 7:
                self.anomalies.append({
                    'type': 'FRESHNESS',
                    'severity': 'WARNING',
                    'message': f'Données fait_attributions non rafraîchies depuis {days_old} jours'
                })
        
        cursor.close()
    
    def check_null_rates(self):
        """Vérifie les taux de valeurs nulles anormaux"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(montant_total) as non_null_montant,
                COUNT(entreprise_key) as non_null_entreprise
            FROM dwh_facts.fait_attributions;
        """)
        
        total, non_null_montant, non_null_entreprise = cursor.fetchone()
        
        if total > 0:
            null_rate_montant = (total - non_null_montant) / total
            null_rate_entreprise = (total - non_null_entreprise) / total
            
            if null_rate_montant > 0.1:  # Plus de 10% de nulls
                self.anomalies.append({
                    'type': 'DATA_QUALITY',
                    'severity': 'ERROR',
                    'message': f'Taux de nulls élevé pour montant_total: {null_rate_montant:.1%}'
                })
            
            if null_rate_entreprise > 0.05:
                self.anomalies.append({
                    'type': 'DATA_QUALITY',
                    'severity': 'ERROR',
                    'message': f'Taux de nulls élevé pour entreprise_key: {null_rate_entreprise:.1%}'
                })
        
        cursor.close()
    
    def check_duplicates(self):
        """Détecte les doublons potentiels"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as nb_duplicates
            FROM (
                SELECT reference, COUNT(*) as cnt
                FROM dwh_facts.fait_attributions
                GROUP BY reference
                HAVING COUNT(*) > 1
            ) duplicates;
        """)
        
        nb_duplicates = cursor.fetchone()[0]
        if nb_duplicates > 0:
            self.anomalies.append({
                'type': 'DATA_INTEGRITY',
                'severity': 'WARNING',
                'message': f'{nb_duplicates} références dupliquées détectées dans fait_attributions'
            })
        
        cursor.close()
    
    def check_row_count_changes(self):
        """Vérifie les variations importantes de volumétrie"""
        # Cette fonctionnalité nécessiterait un historique des comptages
        # À implémenter avec une table de métriques historiques
        pass
    
    def run_all_checks(self):
        """Exécute tous les contrôles"""
        print("🔍 Détection d'anomalies en cours...\n")
        
        self.check_data_freshness()
        self.check_null_rates()
        self.check_duplicates()
        
        # Afficher les résultats
        if not self.anomalies:
            print("✅ Aucune anomalie détectée!")
        else:
            print(f"⚠️  {len(self.anomalies)} anomalie(s) détectée(s):\n")
            for anomaly in self.anomalies:
                icon = "🔴" if anomaly['severity'] == 'ERROR' else "🟡"
                print(f"{icon} [{anomaly['type']}] {anomaly['message']}")
        
        self.conn.close()
        return self.anomalies

if __name__ == "__main__":
    detector = AnomalyDetector()
    anomalies = detector.run_all_checks()
    
    # Ici vous pouvez ajouter l'envoi d'emails/notifications si anomalies détectées
    if anomalies:
        print("\n📧 TODO: Envoyer une notification aux administrateurs")
