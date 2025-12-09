import React from 'react';
import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';
import AreaChartPDF from './AreaChartPDF';
import GaugeChartPDF from './GaugeChartPDF';
import BulletChartPDF from './BulletChartPDF';
import HeatmapCellPDF from './HeatmapCellPDF';

// Styles pour le document PDF
const styles = StyleSheet.create({
  page: {
    padding: 30,
    fontSize: 10,
    fontFamily: 'Helvetica',
    backgroundColor: '#f9fafb',
  },
  header: {
    marginBottom: 20,
    paddingBottom: 15,
    borderBottom: '2 solid #e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 12,
    color: '#4b5563',
  },
  section: {
    marginBottom: 20,
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 15,
    border: '1 solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 8,
    paddingBottom: 8,
    borderBottom: '1 solid #e5e7eb',
  },
  sectionDescription: {
    fontSize: 9,
    color: '#6b7280',
    marginBottom: 12,
    lineHeight: 1.4,
  },
  heatmapGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 12,
  },
  heatmapCell: {
    width: '23%',
  },
  legend: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 12,
    marginTop: 8,
    flexWrap: 'wrap',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  legendColor: {
    width: 12,
    height: 12,
    borderRadius: 2,
  },
  legendText: {
    fontSize: 8,
    color: '#6b7280',
  },
  twoColumn: {
    flexDirection: 'row',
    gap: 15,
  },
  column: {
    flex: 1,
  },
  gaugeGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 15,
  },
  table: {
    marginTop: 10,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#f3f4f6',
    padding: 8,
    borderRadius: 4,
    marginBottom: 5,
  },
  tableRow: {
    flexDirection: 'row',
    padding: 8,
    borderBottom: '1 solid #e5e7eb',
  },
  tableCell: {
    fontSize: 9,
    color: '#374151',
    paddingHorizontal: 4,
  },
  tableHeaderCell: {
    fontSize: 9,
    fontWeight: 'bold',
    color: '#111827',
    paddingHorizontal: 4,
  },
  badge: {
    padding: '4 8',
    borderRadius: 4,
    fontSize: 8,
  },
  emptyState: {
    textAlign: 'center',
    padding: 20,
    color: '#6b7280',
  },
  chartContainer: {
    marginTop: 10,
  },
});

// Fonction pour calculer le niveau de risque basé sur l'occupation
const calculateRiskScore = (occupation) => {
  if (occupation < 30) return 85;  // Sous-occupation critique
  if (occupation > 95) return 90;  // Saturation critique
  if (occupation < 50) return 65;  // Sous-occupation modérée
  if (occupation > 90) return 70;  // Proche saturation
  if (occupation < 60) return 45;  // Légèrement sous-occupée
  if (occupation > 85) return 50;  // Occupation élevée
  return 20; // Zone optimale: 60-85%
};

export default function AlertsAnalyticsPDF({ 
  alerts = [],
  occupationData = [],
  occupationSummary = {},
  financialData = {},
  timeRange = '30'
}) {
  // Calculer le taux d'occupation moyen depuis le summary (calcul correct: lots_attribues / total_lots * 100)
  const tauxOccupationMoyen = React.useMemo(() => {
    // Utiliser le taux d'occupation moyen du summary si disponible (calculé correctement par le backend)
    if (occupationSummary?.taux_occupation_moyen !== undefined && occupationSummary?.taux_occupation_moyen !== null) {
      return parseFloat(occupationSummary.taux_occupation_moyen) || 0;
    }
    
    // Fallback: calculer depuis les données par zone si le summary n'est pas disponible
    const zonesData = occupationData?.results || occupationData?.data || occupationData || [];
    
    if (!Array.isArray(zonesData) || zonesData.length === 0) {
      return 0;
    }
    
    // Calculer correctement: somme des lots attribués / somme des lots totaux * 100
    const totals = zonesData.reduce((acc, zone) => {
      const lotsAttribues = parseFloat(zone.lots_attribues || zone.nombre_lots_attribues || 0);
      const totalLots = parseFloat(zone.nombre_total_lots || zone.total_lots || 0);
      return {
        lotsAttribues: acc.lotsAttribues + lotsAttribues,
        totalLots: acc.totalLots + totalLots
      };
    }, { lotsAttribues: 0, totalLots: 0 });
    
    if (totals.totalLots > 0) {
      return (totals.lotsAttribues / totals.totalLots) * 100;
    }
    
    return 0;
  }, [occupationData, occupationSummary]);

  // Calculer les métriques financières
  const financialMetrics = React.useMemo(() => {
    if (!financialData) {
      return { tauxImpaye: 0, delaiMoyen: 0, tauxRecouvrement: 0 };
    }
    
    // Le backend retourne taux_paiement_pct ou taux_paiement_moyen selon la version
    const tauxPaiement = financialData.taux_paiement_pct || financialData.taux_paiement_moyen || 0;
    const delai = financialData.delai_moyen_paiement || 0;
    
    // Calculer le taux de recouvrement: utiliser la valeur du summary ou calculer depuis les montants
    let tauxRecouvrement = financialData.taux_recouvrement || financialData.taux_recouvrement_moyen || 0;
    
    // Si le taux n'est pas disponible, le calculer depuis les montants
    if (!tauxRecouvrement && financialData.montant_a_recouvrer) {
      const montantRecouvre = parseFloat(financialData.montant_recouvre || 0);
      const montantARecouvrer = parseFloat(financialData.montant_a_recouvrer || 0);
      if (montantARecouvrer > 0) {
        tauxRecouvrement = (montantRecouvre / montantARecouvrer) * 100;
      }
    }
    
    return {
      tauxImpaye: 100 - tauxPaiement,
      delaiMoyen: parseFloat(delai) || 0,
      tauxRecouvrement: parseFloat(tauxRecouvrement) || 0
    };
  }, [financialData]);

  // Données pour les gauges
  const gaugesData = {
    impaye: {
      value: financialMetrics.tauxImpaye,
      max: 100,
      threshold: 40,
      warning: 25
    },
    occupation: {
      value: tauxOccupationMoyen,
      max: 100,
      threshold: 95,
      warning: 80
    },
    delai: {
      value: financialMetrics.delaiMoyen,
      max: 120,
      threshold: 90,
      warning: 60
    }
  };

  // Données pour la timeline
  const timelineData = React.useMemo(() => {
    if (!alerts || !Array.isArray(alerts)) return [];
    
    return alerts.reduce((acc, alert) => {
      const date = new Date(alert.created_at).toLocaleDateString('fr-FR');
      const existing = acc.find(item => item.date === date);
      if (existing) {
        existing.count++;
        if (alert.severity === 'critical') existing.critical++;
        if (alert.severity === 'high') existing.warning++;
      } else {
        acc.push({
          date,
          count: 1,
          critical: alert.severity === 'critical' ? 1 : 0,
          warning: alert.severity === 'high' ? 1 : 0
        });
      }
      return acc;
    }, []).slice(-30);
  }, [alerts]);

  // Données heatmap par zone
  const heatmapData = React.useMemo(() => {
    const zonesData = occupationData?.results || occupationData?.data || occupationData || [];
    
    if (!Array.isArray(zonesData) || zonesData.length === 0) {
      return [];
    }
    
    return zonesData.slice(0, 12).map(zone => ({
      zone: zone.nom_zone || zone.name || zone.zone_name || 'Zone inconnue',
      occupation: zone.taux_occupation_pct || zone.occupation || zone.taux_occupation || 0,
      risk: calculateRiskScore(zone.taux_occupation_pct || zone.occupation || zone.taux_occupation || 0)
    }));
  }, [occupationData]);

  // Fonction pour obtenir la couleur de sévérité
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return { bg: '#fee2e2', text: '#dc2626' };
      case 'high': return { bg: '#fed7aa', text: '#ea580c' };
      case 'medium': return { bg: '#fef3c7', text: '#d97706' };
      case 'warning': return { bg: '#fef3c7', text: '#d97706' };
      default: return { bg: '#dbeafe', text: '#2563eb' };
    }
  };

  // Fonction pour obtenir la couleur de statut
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return { bg: '#fee2e2', text: '#dc2626' };
      case 'acknowledged': return { bg: '#fef3c7', text: '#d97706' };
      default: return { bg: '#d1fae5', text: '#059669' };
    }
  };

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Analytics des Alertes</Text>
          <Text style={styles.subtitle}>
            Visualisation avancée et analyse des alertes du système
          </Text>
          <Text style={[styles.subtitle, { marginTop: 5, fontSize: 9, color: '#6b7280' }]}>
            Généré le {new Date().toLocaleDateString('fr-FR', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })} • Période: {timeRange} derniers jours
          </Text>
        </View>

        {/* Section Heatmap des Zones */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Carte de Chaleur - Zones à Risque</Text>
          <Text style={styles.sectionDescription}>
            Score de risque basé sur le taux d'occupation des zones. 
            Zone optimale: 60-85% | 
            Critique si &lt;30% (sous-occupation) ou &gt;95% (saturation)
          </Text>
          
          {heatmapData.length === 0 ? (
            <View style={styles.emptyState}>
              <Text>Aucune donnée d'occupation disponible</Text>
            </View>
          ) : (
            <>
              <View style={styles.heatmapGrid}>
                {heatmapData.map((item, index) => (
                  <View key={index} style={styles.heatmapCell}>
                    <HeatmapCellPDF
                      zone={item.zone}
                      occupation={item.occupation}
                      value={item.risk}
                    />
                  </View>
                ))}
              </View>
              
              <View style={styles.legend}>
                <View style={styles.legendItem}>
                  <View style={[styles.legendColor, { backgroundColor: '#10b981' }]} />
                  <Text style={styles.legendText}>Faible risque (&lt;40%)</Text>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendColor, { backgroundColor: '#eab308' }]} />
                  <Text style={styles.legendText}>Risque modéré (40-60%)</Text>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendColor, { backgroundColor: '#f59e0b' }]} />
                  <Text style={styles.legendText}>Risque élevé (60-80%)</Text>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendColor, { backgroundColor: '#ef4444' }]} />
                  <Text style={styles.legendText}>Risque critique (&gt;80%)</Text>
                </View>
              </View>
            </>
          )}
        </View>

        {/* Bullet Charts - KPIs */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Indicateurs Clés de Performance</Text>
          <Text style={styles.sectionDescription}>
            Comparaison des indicateurs actuels avec les seuils configurés. 
            Barre verte = zone sûre, orange = attention, rouge = alerte. 
            Le trait bleu indique la cible optimale.
          </Text>
          
          <View style={styles.twoColumn}>
            <View style={styles.column}>
              <BulletChartPDF
                label="Taux d'Impayés"
                value={gaugesData.impaye.value}
                threshold={40}
                warning={25}
                target={15}
                max={100}
              />
              <Text style={{ fontSize: 7, color: '#6b7280', marginTop: 4, marginLeft: 4 }}>
                📊 Pourcentage de factures non payées. Cible: &lt;15% | Critique si &gt;40%
              </Text>
              
              <BulletChartPDF
                label="Délai de Paiement"
                value={gaugesData.delai.value}
                threshold={90}
                warning={60}
                target={48}
                max={120}
                unit=" jours"
              />
              <Text style={{ fontSize: 7, color: '#6b7280', marginTop: 4, marginLeft: 4 }}>
                ⏱️ Temps moyen avant paiement. Cible: 48 jours | Critique si &gt;90 jours
              </Text>
            </View>
            
            <View style={styles.column}>
              <BulletChartPDF
                label="Taux d'Occupation"
                value={gaugesData.occupation.value}
                threshold={95}
                warning={80}
                target={85}
                max={100}
              />
              <Text style={{ fontSize: 7, color: '#6b7280', marginTop: 4, marginLeft: 4 }}>
                🏢 Taux moyen d'occupation des zones. Cible: 85% | Critique si &gt;95% (saturation)
              </Text>
              
              <BulletChartPDF
                label="Taux de Recouvrement"
                value={financialMetrics.tauxRecouvrement}
                threshold={60}
                warning={75}
                target={90}
                max={100}
              />
              <Text style={{ fontSize: 7, color: '#6b7280', marginTop: 4, marginLeft: 4 }}>
                💰 Taux moyen de recouvrement des factures. Cible: 90% | Critique si &lt;60%
              </Text>
            </View>
          </View>
        </View>
      </Page>

      {/* Page 2: Historique des Alertes et Tableau */}
      <Page size="A4" style={styles.page}>
        {/* Section Timeline */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Historique des Alertes (30 derniers jours)</Text>
          {timelineData.length === 0 ? (
            <View style={styles.emptyState}>
              <Text>Aucune donnée disponible</Text>
            </View>
          ) : (
            <View style={styles.chartContainer}>
              <AreaChartPDF
                data={timelineData}
                dataKeys={[
                  { key: 'critical', color: '#ef4444', name: 'Critiques' },
                  { key: 'warning', color: '#f59e0b', name: 'Warnings' }
                ]}
                labelKey="date"
                width={500}
                height={300}
              />
            </View>
          )}
        </View>

        {/* Tableau détaillé des alertes */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Liste Détaillée des Alertes</Text>
          
          {alerts && Array.isArray(alerts) && alerts.length > 0 ? (
            <View style={styles.table}>
              <View style={styles.tableHeader}>
                <Text style={[styles.tableHeaderCell, { width: '15%' }]}>Sévérité</Text>
                <Text style={[styles.tableHeaderCell, { width: '20%' }]}>Titre</Text>
                <Text style={[styles.tableHeaderCell, { width: '35%' }]}>Message</Text>
                <Text style={[styles.tableHeaderCell, { width: '15%' }]}>Date</Text>
                <Text style={[styles.tableHeaderCell, { width: '15%' }]}>Statut</Text>
              </View>
              
              {alerts.slice(0, 10).map((alert, index) => {
                const severityColors = getSeverityColor(alert.severity);
                const statusColors = getStatusColor(alert.status);
                
                return (
                  <View key={alert.id || index} style={styles.tableRow}>
                    <View style={{ width: '15%' }}>
                      <View style={[styles.badge, {
                        backgroundColor: severityColors.bg,
                      }]}>
                        <Text style={{ 
                          fontSize: 7, 
                          color: severityColors.text,
                          fontWeight: 'bold'
                        }}>
                          {alert.severity || 'N/A'}
                        </Text>
                      </View>
                    </View>
                    <Text style={[styles.tableCell, { width: '20%', fontWeight: 'bold' }]}>
                      {alert.title || 'N/A'}
                    </Text>
                    <Text style={[styles.tableCell, { width: '35%' }]}>
                      {alert.message ? String(alert.message).substring(0, 50) + '...' : 'N/A'}
                    </Text>
                    <Text style={[styles.tableCell, { width: '15%' }]}>
                      {alert.created_at 
                        ? new Date(alert.created_at).toLocaleDateString('fr-FR')
                        : 'N/A'}
                    </Text>
                    <View style={{ width: '15%' }}>
                      <View style={[styles.badge, {
                        backgroundColor: statusColors.bg,
                      }]}>
                        <Text style={{ 
                          fontSize: 7, 
                          color: statusColors.text,
                          fontWeight: 'bold'
                        }}>
                          {alert.status || 'N/A'}
                        </Text>
                      </View>
                    </View>
                  </View>
                );
              })}
            </View>
          ) : (
            <View style={styles.emptyState}>
              <Text>Aucune alerte pour le moment</Text>
            </View>
          )}
        </View>
      </Page>
    </Document>
  );
}

