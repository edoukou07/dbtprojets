import React from 'react';
import { Document, Page, Text, View, StyleSheet, Svg, Path } from '@react-pdf/renderer';

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
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 12,
    paddingBottom: 8,
    borderBottom: '1 solid #e5e7eb',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 15,
    justifyContent: 'space-between',
  },
  kpiCard: {
    width: '23.5%',
    marginBottom: 15,
    backgroundColor: '#ffffff',
    padding: 12,
    borderRadius: 8,
    border: '1 solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  kpiTitle: {
    fontSize: 9,
    color: '#6b7280',
    marginBottom: 5,
  },
  kpiValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 3,
  },
  kpiSubtitle: {
    fontSize: 8,
    color: '#9ca3af',
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    border: '1 solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  gaugeContainer: {
    alignItems: 'center',
    marginBottom: 15,
  },
  gaugeTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 15,
    textAlign: 'center',
  },
  alertCard: {
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
    border: '1 solid',
  },
  alertTitle: {
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  alertValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  alertSubtitle: {
    fontSize: 9,
    color: '#6b7280',
  },
  legend: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 10,
    marginTop: 10,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 8,
  },
  legendDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 4,
  },
  legendText: {
    fontSize: 8,
    color: '#374151',
  },
  histogramContainer: {
    marginTop: 10,
  },
  histogramItem: {
    marginBottom: 12,
  },
  histogramHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  histogramBar: {
    height: 20,
    borderRadius: 4,
    marginBottom: 4,
    border: '1 solid',
  },
  histogramInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    fontSize: 8,
    color: '#6b7280',
  },
  topZonesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginTop: 10,
  },
  topZoneCard: {
    width: '18%',
    backgroundColor: '#ffffff',
    padding: 10,
    borderRadius: 6,
    border: '1 solid #e5e7eb',
    boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
  },
  topZoneRank: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#3b82f6',
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 6,
  },
  topZoneName: {
    fontSize: 9,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4,
  },
  topZoneValue: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#3b82f6',
    marginBottom: 4,
  },
  topZoneDetails: {
    fontSize: 7,
    color: '#6b7280',
    marginBottom: 4,
  },
  topZoneProgress: {
    height: 4,
    backgroundColor: '#e5e7eb',
    borderRadius: 2,
    marginTop: 4,
  },
  table: {
    marginTop: 10,
  },
  tableHeader: {
    flexDirection: 'row',
    backgroundColor: '#3b82f6',
    padding: 8,
    borderRadius: 4,
    marginBottom: 5,
  },
  tableRow: {
    flexDirection: 'row',
    padding: 8,
    borderBottom: '1 solid #e5e7eb',
    backgroundColor: '#ffffff',
  },
  tableCell: {
    fontSize: 8,
    color: '#374151',
    paddingHorizontal: 4,
  },
  tableHeaderCell: {
    fontSize: 9,
    fontWeight: 'bold',
    color: '#ffffff',
    paddingHorizontal: 4,
  },
  badge: {
    padding: '3 8',
    borderRadius: 12,
    fontSize: 7,
    fontWeight: 'bold',
  },
  progressBar: {
    height: 6,
    backgroundColor: '#e5e7eb',
    borderRadius: 3,
    marginTop: 4,
  },
  progressFill: {
    height: 6,
    borderRadius: 3,
  },
});

const formatNumber = (value) => {
  if (!value && value !== 0) return '0';
  // Convertir en nombre si c'est une chaîne
  const numValue = typeof value === 'string' ? parseFloat(value.replace(/\//g, '').replace(/\s/g, '')) : value;
  if (isNaN(numValue)) return '0';
  // Formater avec des espaces normaux comme séparateurs de milliers
  return new Intl.NumberFormat('fr-FR', {
    useGrouping: true,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(numValue).replace(/\u202F/g, ' ').replace(/,/g, ' ').replace(/\//g, '');
};

const formatPercent = (value) => {
  if (!value && value !== 0) return '0%';
  const numValue = typeof value === 'string' ? parseFloat(value.toString().replace(/\//g, '')) : value;
  if (isNaN(numValue)) return '0%';
  return numValue.toFixed(1) + '%';
};

const formatSuperficie = (value) => {
  if (!value && value !== 0) return '0 m²';
  // Nettoyer la valeur en retirant les "/" et autres caractères indésirables
  const numValue = typeof value === 'string' ? parseFloat(value.toString().replace(/\//g, '').replace(/\s/g, '')) : value;
  if (isNaN(numValue)) return '0 m²';
  // Formater avec des espaces normaux
  const formatted = new Intl.NumberFormat('fr-FR', {
    useGrouping: true,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(numValue).replace(/\u202F/g, ' ').replace(/,/g, ' ').replace(/\//g, '');
  return formatted + ' m²';
};

const getOccupationColor = (rate) => {
  if (rate >= 90) return { bg: '#fee2e2', border: '#ef4444', text: '#991b1b', bar: '#ef4444' };
  if (rate >= 70) return { bg: '#fef3c7', border: '#f59e0b', text: '#92400e', bar: '#f59e0b' };
  if (rate >= 50) return { bg: '#d1fae5', border: '#10b981', text: '#065f46', bar: '#10b981' };
  return { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af', bar: '#3b82f6' };
};

const getOccupationStatus = (rate) => {
  if (rate >= 90) return { label: 'Saturée', color: 'red' };
  if (rate >= 70) return { label: 'Élevée', color: 'orange' };
  if (rate >= 50) return { label: 'Normale', color: 'green' };
  return { label: 'Faible', color: 'blue' };
};

// Composant pour la jauge SVG
const GaugeChart = ({ rate = 0 }) => {
  const angle = (rate / 100) * 180 - 180;
  const radians = (angle * Math.PI) / 180;
  const x = 150 + 110 * Math.cos(radians);
  const y = 150 + 110 * Math.sin(radians);
  const largeArc = rate > 50 ? 1 : 0;
  
  let strokeColor = '#3b82f6';
  if (rate >= 90) strokeColor = '#ef4444';
  else if (rate >= 70) strokeColor = '#f59e0b';
  else if (rate >= 50) strokeColor = '#10b981';

  return (
    <View style={{ alignItems: 'center', marginBottom: 15, position: 'relative', height: 180 }}>
      <Svg width="300" height="180" viewBox="0 0 300 180" style={{ position: 'absolute', top: 0, left: '50%', marginLeft: -150 }}>
        {/* Background arc */}
        <Path
          d="M 40 150 A 110 110 0 0 1 260 150"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="30"
          strokeLinecap="round"
        />
        {/* Active arc */}
        <Path
          d={`M 40 150 A 110 110 0 ${largeArc} 1 ${x} ${y}`}
          fill="none"
          stroke={strokeColor}
          strokeWidth="30"
          strokeLinecap="round"
        />
      </Svg>
      {/* Center text - percentage */}
      <View style={{ position: 'absolute', top: 100, left: 0, right: 0, alignItems: 'center' }}>
        <Text style={{ fontSize: 36, fontWeight: 'bold', color: '#111827', textAlign: 'center' }}>
          {formatPercent(rate)}
        </Text>
        <Text style={{ fontSize: 10, color: '#6b7280', textAlign: 'center', marginTop: 5 }}>
          {rate >= 90 ? 'Critique' : rate >= 70 ? 'Élevée' : rate >= 50 ? 'Normale' : 'Faible'}
        </Text>
      </View>
    </View>
  );
};

export default function OccupationPDF({ 
  summary,
  allZonesData = [],
  topZones
}) {
  // Trier les zones par taux d'occupation pour le tableau
  const sortedZones = [...(allZonesData || [])].sort((a, b) => {
    const aRate = parseFloat(a.taux_occupation_pct) || 0;
    const bRate = parseFloat(b.taux_occupation_pct) || 0;
    return bRate - aRate;
  });

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* En-tête */}
        <View style={styles.header}>
          <Text style={styles.title}>Occupation des Zones</Text>
          <Text style={styles.subtitle}>Analyse de l'occupation des zones industrielles</Text>
          <Text style={[styles.subtitle, { marginTop: 5, fontSize: 9, color: '#6b7280' }]}>
            Généré le {new Date().toLocaleDateString('fr-FR', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })}
          </Text>
        </View>

        {/* KPIs Principaux */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Vue d'Ensemble</Text>
          <View style={styles.grid}>
            <View style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>Zones Industrielles</Text>
              <Text style={styles.kpiValue}>
                {formatNumber(summary?.nombre_zones)}
              </Text>
              <Text style={styles.kpiSubtitle}>Zones actives</Text>
            </View>
            <View style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>Total Lots</Text>
              <Text style={styles.kpiValue}>
                {formatNumber(summary?.total_lots)}
              </Text>
              <Text style={styles.kpiSubtitle}>Capacité totale</Text>
            </View>
            <View style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>Lots Attribués</Text>
              <Text style={styles.kpiValue}>
                {formatNumber(summary?.lots_attribues)}
              </Text>
              <Text style={styles.kpiSubtitle}>
                {formatPercent(summary?.taux_occupation_moyen)} occupés
              </Text>
            </View>
            <View style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>Lots Disponibles</Text>
              <Text style={styles.kpiValue}>
                {formatNumber(summary?.lots_disponibles)}
              </Text>
              <Text style={styles.kpiSubtitle}>Prêts à l'attribution</Text>
            </View>
          </View>
        </View>

        {/* Statistiques de Surface */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Superficies</Text>
          <View style={styles.grid}>
            <View style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>Superficie Totale</Text>
              <Text style={styles.kpiValue}>
                {formatSuperficie(summary?.superficie_totale)}
              </Text>
              <Text style={styles.kpiSubtitle}>Surface industrielle</Text>
            </View>
            <View style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>Surface Attribuée</Text>
              <Text style={styles.kpiValue}>
                {formatSuperficie(summary?.superficie_attribuee)}
              </Text>
              <Text style={styles.kpiSubtitle}>En exploitation</Text>
            </View>
            <View style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>Surface Disponible</Text>
              <Text style={styles.kpiValue}>
                {formatSuperficie(summary?.superficie_disponible)}
              </Text>
              <Text style={styles.kpiSubtitle}>Disponible</Text>
            </View>
          </View>
        </View>

        {/* Alertes et Zones Critiques */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Alertes d'Occupation</Text>

          {/* Jauge du Taux d'Occupation Moyen */}
          <View style={styles.card}>
            <Text style={styles.gaugeTitle}>Taux d'Occupation Moyen</Text>
            <GaugeChart rate={summary?.taux_occupation_moyen || 0} />
            
            {/* Légende */}
            <View style={styles.legend}>
              <View style={styles.legendItem}>
                <View style={[styles.legendDot, { backgroundColor: '#3b82f6' }]} />
                <Text style={styles.legendText}>Faible (&lt; 50%)</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendDot, { backgroundColor: '#10b981' }]} />
                <Text style={styles.legendText}>Normale (50-70%)</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendDot, { backgroundColor: '#f59e0b' }]} />
                <Text style={styles.legendText}>Élevée (70-90%)</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendDot, { backgroundColor: '#ef4444' }]} />
                <Text style={styles.legendText}>Critique (&gt; 90%)</Text>
              </View>
            </View>
          </View>
        </View>
      </Page>

      {/* Page 2: Top Zones et Tableau */}
      <Page size="A4" style={styles.page}>
        {/* Cards - Zones Saturées et Sous-Occupées */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Alertes d'Occupation</Text>
          <View style={styles.grid}>
            <View style={[styles.alertCard, { 
              backgroundColor: '#fee2e2', 
              borderColor: '#ef4444',
              width: '48%'
            }]}>
              <Text style={[styles.alertTitle, { color: '#991b1b' }]}>Zones Saturées</Text>
              <Text style={[styles.alertValue, { color: '#991b1b' }]}>
                {formatNumber(summary?.zones_saturees)}
              </Text>
              <Text style={[styles.alertSubtitle, { color: '#991b1b' }]}>Occupation &gt; 90%</Text>
            </View>

            <View style={[styles.alertCard, { 
              backgroundColor: '#dbeafe', 
              borderColor: '#3b82f6',
              width: '48%'
            }]}>
              <Text style={[styles.alertTitle, { color: '#1e40af' }]}>Zones Sous-Occupées</Text>
              <Text style={[styles.alertValue, { color: '#1e40af' }]}>
                {formatNumber(summary?.zones_faible_occupation)}
              </Text>
              <Text style={[styles.alertSubtitle, { color: '#1e40af' }]}>Occupation &lt; 50%</Text>
            </View>
          </View>
        </View>
        {/* Top 5 des Zones les Plus Occupées */}
        {topZones?.plus_occupees && topZones.plus_occupees.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Top 5 des Zones les Plus Occupées</Text>
            <View style={styles.topZonesGrid}>
              {topZones.plus_occupees.slice(0, 5).map((zone, index) => {
                const percentage = parseFloat(zone.taux_occupation_pct) || 0;
                return (
                  <View key={index} style={styles.topZoneCard}>
                    <View style={styles.topZoneRank}>{index + 1}</View>
                    <Text style={styles.topZoneName} numberOfLines={2}>
                      {zone.nom_zone || 'N/A'}
                    </Text>
                    <Text style={styles.topZoneValue}>
                      {formatPercent(percentage)}
                    </Text>
                    <Text style={styles.topZoneDetails}>
                      {formatNumber(zone.lots_attribues)} / {formatNumber(zone.nombre_total_lots)} lots
                    </Text>
                    <View style={styles.topZoneProgress}>
                      <View style={[styles.progressFill, {
                        width: `${Math.min(percentage, 100)}%`,
                        backgroundColor: '#3b82f6'
                      }]} />
                    </View>
                  </View>
                );
              })}
            </View>
          </View>
        )}

        {/* Zones les Moins Occupées - Histogramme */}
        {topZones?.moins_occupees && topZones.moins_occupees.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Zones les Moins Occupées</Text>
            <View style={styles.card}>
              <View style={styles.histogramContainer}>
                {topZones.moins_occupees.slice(0, 5).map((zone, index) => {
                  const percentage = parseFloat(zone.taux_occupation_pct) || 0;
                  const colors = [
                    { bg: '#3b82f6', border: '#2563eb' },
                    { bg: '#60a5fa', border: '#3b82f6' },
                    { bg: '#93c5fd', border: '#60a5fa' },
                    { bg: '#bfdbfe', border: '#93c5fd' },
                    { bg: '#dbeafe', border: '#bfdbfe' }
                  ];
                  
                  return (
                    <View key={index} style={styles.histogramItem}>
                      <View style={styles.histogramHeader}>
                        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                          <View style={{
                            width: 20,
                            height: 20,
                            borderRadius: 10,
                            backgroundColor: '#dbeafe',
                            justifyContent: 'center',
                            alignItems: 'center',
                            marginRight: 6
                          }}>
                            <Text style={{ fontSize: 8, fontWeight: 'bold', color: '#1e40af' }}>
                              {index + 1}
                            </Text>
                          </View>
                          <Text style={{ fontSize: 9, fontWeight: 'bold', color: '#111827' }}>
                            {zone.nom_zone || 'N/A'}
                          </Text>
                        </View>
                        <Text style={{ fontSize: 9, fontWeight: 'bold', color: '#3b82f6' }}>
                          {formatPercent(percentage)}
                        </Text>
                      </View>
                      <View style={[styles.histogramBar, {
                        backgroundColor: colors[index].bg,
                        borderColor: colors[index].border,
                        width: `${percentage}%`
                      }]} />
                      <View style={styles.histogramInfo}>
                        <Text>{formatNumber(zone.lots_attribues || 0)} lots attribués</Text>
                        <Text>{formatNumber(zone.lots_disponibles || 0)} lots disponibles</Text>
                      </View>
                    </View>
                  );
                })}
              </View>
            </View>
          </View>
        )}

        {/* Tableau des Zones */}
        {sortedZones.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Détails par Zone</Text>
            <View style={styles.table}>
              <View style={styles.tableHeader}>
                <Text style={[styles.tableHeaderCell, { width: '20%' }]}>Zone</Text>
                <Text style={[styles.tableHeaderCell, { width: '12%' }]}>Taux Occupation</Text>
                <Text style={[styles.tableHeaderCell, { width: '10%' }]}>Lots Total</Text>
                <Text style={[styles.tableHeaderCell, { width: '10%' }]}>Attribués</Text>
                <Text style={[styles.tableHeaderCell, { width: '10%' }]}>Disponibles</Text>
                <Text style={[styles.tableHeaderCell, { width: '10%' }]}>Réservés</Text>
                <Text style={[styles.tableHeaderCell, { width: '13%' }]}>Superficie</Text>
                <Text style={[styles.tableHeaderCell, { width: '15%' }]}>Statut</Text>
              </View>
              {sortedZones.slice(0, 15).map((zone, index) => {
                const status = getOccupationStatus(zone.taux_occupation_pct);
                const colors = getOccupationColor(zone.taux_occupation_pct);
                return (
                  <View key={index} style={styles.tableRow}>
                    <Text style={[styles.tableCell, { width: '20%', fontWeight: 'bold' }]}>
                      {zone.nom_zone || 'N/A'}
                    </Text>
                    <View style={{ width: '12%', flexDirection: 'row', alignItems: 'center' }}>
                      <View style={[styles.progressBar, { width: 40, marginRight: 4 }]}>
                        <View style={[styles.progressFill, {
                          width: `${Math.min(zone.taux_occupation_pct || 0, 100)}%`,
                          backgroundColor: colors.bar
                        }]} />
                      </View>
                      <Text style={[styles.tableCell, { fontSize: 7 }]}>
                        {formatPercent(zone.taux_occupation_pct)}
                      </Text>
                    </View>
                    <Text style={[styles.tableCell, { width: '10%' }]}>
                      {formatNumber(zone.nombre_total_lots)}
                    </Text>
                    <Text style={[styles.tableCell, { width: '10%', color: '#10b981' }]}>
                      {formatNumber(zone.lots_attribues)}
                    </Text>
                    <Text style={[styles.tableCell, { width: '10%', color: '#3b82f6' }]}>
                      {formatNumber(zone.lots_disponibles)}
                    </Text>
                    <Text style={[styles.tableCell, { width: '10%', color: '#f59e0b' }]}>
                      {formatNumber(zone.lots_reserves)}
                    </Text>
                    <Text style={[styles.tableCell, { width: '13%' }]}>
                      {formatSuperficie(zone.superficie_totale)}
                    </Text>
                    <View style={{ width: '15%' }}>
                      <View style={[styles.badge, {
                        backgroundColor: colors.bg,
                        color: colors.text
                      }]}>
                        <Text style={{ fontSize: 7, color: colors.text }}>
                          {status.label}
                        </Text>
                      </View>
                    </View>
                  </View>
                );
              })}
            </View>
            {sortedZones.length > 15 && (
              <Text style={{ fontSize: 8, color: '#6b7280', marginTop: 8, textAlign: 'center' }}>
                ... et {sortedZones.length - 15} autres zones
              </Text>
            )}
          </View>
        )}
      </Page>
    </Document>
  );
}

