import React from 'react';
import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';
import AreaChartPDF from './AreaChartPDF';
import MultiBarChartPDF from './MultiBarChartPDF';

// Styles pour le document PDF
const styles = StyleSheet.create({
  page: {
    padding: 20,
    fontSize: 10,
    fontFamily: 'Helvetica',
    backgroundColor: '#f9fafb',
  },
  header: {
    marginBottom: 15,
    paddingBottom: 10,
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
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 8,
    paddingBottom: 6,
    borderBottom: '1 solid #e5e7eb',
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 10,
    marginBottom: 10,
    border: '1 solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 10,
    justifyContent: 'space-between',
  },
  kpiCard: {
    width: '23.5%',
    marginBottom: 10,
    backgroundColor: '#ffffff',
    padding: 10,
    borderRadius: 8,
    border: '1 solid #e5e7eb',
  },
  kpiTitle: {
    fontSize: 9,
    color: '#6b7280',
    marginBottom: 5,
  },
  kpiValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 3,
    flexWrap: 'wrap',
  },
  kpiSubtitle: {
    fontSize: 8,
    color: '#9ca3af',
  },
  twoColumn: {
    flexDirection: 'row',
    gap: 10,
    justifyContent: 'space-between',
  },
  threeColumn: {
    flexDirection: 'row',
    gap: 15,
  },
  column: {
    flex: 1,
    minWidth: 0, // Permet au flex de fonctionner correctement
  },
  zoneItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 10,
    backgroundColor: '#f9fafb',
    borderRadius: 6,
    marginBottom: 8,
  },
  zoneRank: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#eff6ff',
    color: '#3b82f6',
    fontSize: 10,
    fontWeight: 'bold',
    textAlign: 'center',
    paddingTop: 5,
    marginRight: 10,
  },
  zoneRankGreen: {
    backgroundColor: '#ecfdf5',
    color: '#10b981',
  },
  zoneRankRed: {
    backgroundColor: '#fef2f2',
    color: '#dc2626',
  },
  zoneInfo: {
    flex: 1,
  },
  zoneName: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 2,
  },
  zoneSubtitle: {
    fontSize: 8,
    color: '#6b7280',
  },
  zoneValue: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#3b82f6',
  },
  zoneValueGreen: {
    color: '#10b981',
  },
  zoneValueRed: {
    color: '#dc2626',
  },
  emptyState: {
    padding: 20,
    textAlign: 'center',
    color: '#6b7280',
    fontSize: 10,
  },
  comparisonBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  comparisonValue: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  comparisonValuePositive: {
    color: '#10b981',
  },
  comparisonValueNegative: {
    color: '#dc2626',
  },
});

const formatCurrency = (value) => {
  if (!value && value !== 0) return '0 FCFA';
  return new Intl.NumberFormat('fr-FR', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value) + ' FCFA';
};

const formatCurrencyShort = (value) => {
  if (!value && value !== 0) return '0';
  return new Intl.NumberFormat('fr-FR', { 
    notation: 'compact',
    compactDisplay: 'short'
  }).format(value);
};

const formatPercent = (value) => {
  if (!value && value !== 0) return '0%';
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return '0%';
  return numValue.toFixed(1) + '%';
};

// Composant pour une carte KPI
const KPICard = ({ title, value, subtitle, color = 'blue' }) => {
  return (
    <View style={styles.kpiCard}>
      <Text style={styles.kpiTitle}>{title}</Text>
      <Text style={[styles.kpiValue, { flexWrap: 'wrap' }]}>{value}</Text>
      {subtitle && (
        <Text style={styles.kpiSubtitle} wrap>
          {subtitle}
        </Text>
      )}
    </View>
  );
};

// Composant pour un élément de zone
const ZoneItem = ({ zone, index, type = 'ca' }) => {
  const rankStyle = type === 'ca' 
    ? styles.zoneRank 
    : type === 'payeurs' 
    ? [styles.zoneRank, styles.zoneRankGreen]
    : [styles.zoneRank, styles.zoneRankRed];
  
  const valueStyle = type === 'ca'
    ? styles.zoneValue
    : type === 'payeurs'
    ? [styles.zoneValue, styles.zoneValueGreen]
    : [styles.zoneValue, styles.zoneValueRed];

  const subtitle = type === 'ca'
    ? `Taux: ${formatPercent(zone.taux_paiement)}`
    : type === 'payeurs'
    ? `CA: ${formatCurrencyShort(zone.ca_total)}`
    : `Impayé: ${formatCurrencyShort(zone.ca_impaye)}`;

  const value = type === 'ca'
    ? formatCurrencyShort(zone.ca_total)
    : formatPercent(zone.taux_paiement);

  return (
    <View style={styles.zoneItem}>
      <View style={rankStyle}>
        <Text>{index + 1}</Text>
      </View>
      <View style={styles.zoneInfo}>
        <Text style={styles.zoneName}>{zone.nom_zone}</Text>
        <Text style={styles.zoneSubtitle}>{subtitle}</Text>
      </View>
      <Text style={valueStyle}>{value}</Text>
    </View>
  );
};

export default function FinancierPDF({ 
  summary,
  tendancesMensuelles,
  tendancesTrimestrielles,
  topZones,
  comparaison,
  selectedYear
}) {
  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* En-tête */}
        <View style={styles.header}>
          <Text style={styles.title}>Performance Financière</Text>
          <Text style={styles.subtitle}>Analyse financière et recouvrement</Text>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 5 }}>
            <Text style={[styles.subtitle, { fontSize: 9, color: '#6b7280' }]}>
              Année: {selectedYear || new Date().getFullYear()}
            </Text>
            {comparaison && comparaison.variations && (
              <View style={styles.comparisonBadge}>
                <Text style={[styles.subtitle, { fontSize: 9, color: '#6b7280', marginRight: 4 }]}>
                  vs {comparaison.annee_precedente}:
                </Text>
                <Text style={[
                  styles.comparisonValue,
                  comparaison.variations.ca_total >= 0 
                    ? styles.comparisonValuePositive 
                    : styles.comparisonValueNegative
                ]}>
                  {Math.abs(comparaison.variations.ca_total || 0).toFixed(1)}%
                </Text>
              </View>
            )}
          </View>
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
          <Text style={styles.sectionTitle}>Vue d'Ensemble Financière</Text>
          <View style={styles.grid}>
            <KPICard
              title="CA Facturé"
              value={formatCurrencyShort(summary?.ca_total) + ' FCFA'}
              subtitle={formatCurrency(summary?.ca_total)}
              color="blue"
            />
            <KPICard
              title="CA Payé"
              value={formatCurrencyShort(summary?.ca_paye) + ' FCFA'}
              subtitle={formatPercent(summary?.taux_paiement_moyen)}
              color="green"
            />
            <KPICard
              title="Créances"
              value={formatCurrencyShort(summary?.ca_impaye) + ' FCFA'}
              subtitle={formatPercent(summary?.taux_impaye_pct) + ' du CA'}
              color="orange"
            />
            <KPICard
              title="Nombre Factures"
              value={summary?.total_factures?.toLocaleString('fr-FR') || '0'}
              subtitle="Factures émises"
              color="purple"
            />
          </View>
        </View>

        {/* Analyse du Recouvrement */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Analyse du Recouvrement</Text>
          <View style={styles.grid}>
            <KPICard
              title="Montant Recouvré"
              value={formatCurrencyShort(summary?.montant_recouvre) + ' FCFA'}
              subtitle={`${summary?.total_collectes || 0} collectes`}
              color="green"
            />
            <KPICard
              title="Taux Recouvrement"
              value={formatPercent(summary?.taux_recouvrement_moyen)}
              subtitle="Sur créances totales"
              color="blue"
            />
            <KPICard
              title="Montant À Recouvrer"
              value={formatCurrencyShort(summary?.montant_a_recouvrer) + ' FCFA'}
              subtitle="Objectif collecte"
              color="red"
            />
          </View>
        </View>

        {/* Graphiques de Tendances */}
        <View style={[styles.section, { marginBottom: 10 }]}>
          <Text style={styles.sectionTitle}>Graphiques de Tendances</Text>
          <View style={styles.twoColumn}>
            {/* Évolution Mensuelle */}
            <View style={[styles.column, styles.card]}>
              <Text style={{ fontSize: 10, fontWeight: 'bold', marginBottom: 8, color: '#111827' }}>
                Évolution Mensuelle {selectedYear || new Date().getFullYear()}
              </Text>
              {tendancesMensuelles && tendancesMensuelles.length > 0 ? (
                <AreaChartPDF
                  data={tendancesMensuelles}
                  dataKeys={[
                    { key: 'ca_facture', color: '#0ea5e9', name: 'CA Facturé' },
                    { key: 'ca_paye', color: '#10b981', name: 'CA Payé' }
                  ]}
                  labelKey="nom_mois"
                  width={220}
                  height={180}
                />
              ) : (
                <View style={styles.emptyState}>
                  <Text>Aucune donnée disponible</Text>
                </View>
              )}
            </View>

            {/* Performance Trimestrielle */}
            <View style={[styles.column, styles.card]}>
              <Text style={{ fontSize: 10, fontWeight: 'bold', marginBottom: 8, color: '#111827' }}>
                Performance Trimestrielle
              </Text>
              {tendancesTrimestrielles && tendancesTrimestrielles.length > 0 ? (
                <MultiBarChartPDF
                  data={tendancesTrimestrielles}
                  dataKeys={[
                    { key: 'ca_facture', color: '#0ea5e9', name: 'CA Facturé' },
                    { key: 'ca_paye', color: '#10b981', name: 'CA Payé' },
                    { key: 'ca_impaye', color: '#f59e0b', name: 'Créances' }
                  ]}
                  labelKey="nom_trimestre"
                  width={220}
                  height={180}
                />
              ) : (
                <View style={styles.emptyState}>
                  <Text>Aucune donnée disponible</Text>
                </View>
              )}
            </View>
          </View>
        </View>
      </Page>

      {/* Page 2: Top Zones */}
      <Page size="A4" style={styles.page}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Analyse par Zone</Text>
          
          <View style={styles.threeColumn}>
            {/* Top Zones par CA */}
            <View style={[styles.column, styles.card]}>
              <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10, color: '#111827' }}>
                Top Zones par CA
              </Text>
              {topZones?.top_chiffre_affaires && topZones.top_chiffre_affaires.length > 0 ? (
                <View>
                  {topZones.top_chiffre_affaires.map((zone, index) => (
                    <ZoneItem
                      key={index}
                      zone={zone}
                      index={index}
                      type="ca"
                    />
                  ))}
                </View>
              ) : (
                <View style={styles.emptyState}>
                  <Text>Aucune donnée disponible</Text>
                </View>
              )}
            </View>

            {/* Meilleurs Payeurs */}
            <View style={[styles.column, styles.card]}>
              <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10, color: '#111827' }}>
                Meilleurs Payeurs
              </Text>
              {topZones?.meilleurs_payeurs && topZones.meilleurs_payeurs.length > 0 ? (
                <View>
                  {topZones.meilleurs_payeurs.map((zone, index) => (
                    <ZoneItem
                      key={index}
                      zone={zone}
                      index={index}
                      type="payeurs"
                    />
                  ))}
                </View>
              ) : (
                <View style={styles.emptyState}>
                  <Text>Aucune donnée disponible</Text>
                </View>
              )}
            </View>

            {/* Zones à Risque */}
            <View style={[styles.column, styles.card]}>
              <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10, color: '#111827' }}>
                Zones à Risque
              </Text>
              {topZones?.zones_a_risque && topZones.zones_a_risque.length > 0 ? (
                <View>
                  {topZones.zones_a_risque.map((zone, index) => (
                    <ZoneItem
                      key={index}
                      zone={zone}
                      index={index}
                      type="risque"
                    />
                  ))}
                </View>
              ) : (
                <View style={styles.emptyState}>
                  <Text style={{ fontSize: 9 }}>Aucune zone à risque</Text>
                </View>
              )}
            </View>
          </View>
        </View>
      </Page>
    </Document>
  );
}

