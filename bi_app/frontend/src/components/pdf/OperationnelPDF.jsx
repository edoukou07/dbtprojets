import React from 'react';
import { Document, Page, Text, View, StyleSheet } from '@react-pdf/renderer';
import LineChartPDF from './LineChartPDF';
import MultiBarChartPDF from './MultiBarChartPDF';
import AreaChartPDF from './AreaChartPDF';

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
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 10,
    justifyContent: 'space-between',
  },
  gridThreeColumns: {
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
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  kpiCardThreeColumns: {
    width: '31%',
    marginBottom: 10,
    backgroundColor: '#ffffff',
    padding: 10,
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
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    border: '1 solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  twoColumn: {
    flexDirection: 'row',
    gap: 10,
    justifyContent: 'space-between',
  },
  column: {
    flex: 1,
    minWidth: 0,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 10,
    borderRadius: 6,
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 9,
    fontWeight: 'medium',
    color: '#374151',
  },
  statValue: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  statRowBlue: {
    backgroundColor: '#eff6ff',
  },
  statValueBlue: {
    color: '#2563eb',
  },
  statRowGreen: {
    backgroundColor: '#ecfdf5',
  },
  statValueGreen: {
    color: '#10b981',
  },
  statRowOrange: {
    backgroundColor: '#fff7ed',
  },
  statValueOrange: {
    color: '#f59e0b',
  },
  statRowPurple: {
    backgroundColor: '#f5f3ff',
  },
  statValuePurple: {
    color: '#8b5cf6',
  },
  statRowIndigo: {
    backgroundColor: '#eef2ff',
  },
  statValueIndigo: {
    color: '#6366f1',
  },
  statRowGray: {
    backgroundColor: '#f9fafb',
  },
  statValueGray: {
    color: '#374151',
  },
  statRowRed: {
    backgroundColor: '#fef2f2',
  },
  statValueRed: {
    color: '#dc2626',
  },
  statRowEmerald: {
    backgroundColor: '#ecfdf5',
  },
  statValueEmerald: {
    color: '#10b981',
  },
  threeColumn: {
    flexDirection: 'row',
    gap: 10,
    marginTop: 10,
  },
  amountCard: {
    flex: 1,
    textAlign: 'center',
    padding: 12,
    borderRadius: 6,
  },
  amountLabel: {
    fontSize: 9,
    color: '#6b7280',
    marginBottom: 6,
  },
  amountValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  emptyState: {
    padding: 20,
    textAlign: 'center',
    color: '#6b7280',
    fontSize: 10,
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
  if (value >= 1000000000) {
    return (value / 1000000000).toFixed(1) + 'Md';
  } else if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M';
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K';
  }
  return value.toString();
};

const formatPercent = (value) => {
  if (!value && value !== 0) return '0%';
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return '0%';
  return numValue.toFixed(1) + '%';
};

const formatNumber = (value) => {
  if (!value && value !== 0) return '0';
  return new Intl.NumberFormat('fr-FR').format(value);
};

// Composant pour une carte KPI
const KPICard = ({ title, value, subtitle, color = 'blue', threeColumns = false }) => {
  return (
    <View style={threeColumns ? styles.kpiCardThreeColumns : styles.kpiCard}>
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

// Composant pour une ligne de statistique
const StatRow = ({ label, value, color = 'blue' }) => {
  const rowStyle = styles[`statRow${color.charAt(0).toUpperCase() + color.slice(1)}`] || styles.statRowBlue;
  const valueStyle = styles[`statValue${color.charAt(0).toUpperCase() + color.slice(1)}`] || styles.statValueBlue;
  
  return (
    <View style={[styles.statRow, rowStyle]}>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={[styles.statValue, valueStyle]}>{value}</Text>
    </View>
  );
};

export default function OperationnelPDF({ 
  summary,
  indicateursCles,
  performanceCollectes,
  performanceAttributions,
  performanceFacturation
}) {
  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* En-tête */}
        <View style={styles.header}>
          <Text style={styles.title}>Performance Opérationnelle</Text>
          <Text style={styles.subtitle}>Analyse des collectes, attributions et facturation</Text>
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
          <Text style={styles.sectionTitle}>Indicateurs Clés de Performance</Text>
          <View style={styles.grid}>
            <KPICard
              title="Total Collectes"
              value={formatNumber(summary?.total_collectes || 0)}
              color="blue"
            />
            <KPICard
              title="Taux de Clôture"
              value={formatPercent(summary?.taux_cloture_moyen || 0)}
              color="green"
            />
            <KPICard
              title="Taux de Recouvrement"
              value={formatPercent(summary?.taux_recouvrement_moyen || 0)}
              color="purple"
            />
            <KPICard
              title="Total Demandes"
              value={formatNumber(summary?.total_demandes || 0)}
              color="orange"
            />
          </View>
        </View>

        {/* Indicateurs Détaillés du Trimestre */}
        {indicateursCles?.indicateurs && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>
              Performance du Trimestre {indicateursCles.periode?.trimestre} - {indicateursCles.periode?.annee}
            </Text>
            <View style={styles.gridThreeColumns}>
              <KPICard
                title="Collectes - Taux Clôture"
                value={formatPercent(indicateursCles.indicateurs.taux_cloture || 0)}
                color="green"
                threeColumns={true}
              />
              <KPICard
                title="Collectes - Taux Recouvrement"
                value={formatPercent(indicateursCles.indicateurs.taux_recouvrement || 0)}
                color="purple"
                threeColumns={true}
              />
              <KPICard
                title="Collectes - Durée Moyenne"
                value={`${formatNumber(indicateursCles.indicateurs.duree_moyenne_collecte?.toFixed(0) || 0)} jours`}
                color="blue"
                threeColumns={true}
              />
              <KPICard
                title="Attributions - Taux Approbation"
                value={formatPercent(indicateursCles.indicateurs.taux_approbation || 0)}
                color="green"
                threeColumns={true}
              />
              <KPICard
                title="Attributions - Délai Moyen"
                value={`${formatNumber(indicateursCles.indicateurs.delai_moyen_attribution?.toFixed(0) || 0)} jours`}
                color="orange"
                threeColumns={true}
              />
              <KPICard
                title="Facturation - Délai Paiement"
                value={`${formatNumber(indicateursCles.indicateurs.delai_moyen_paiement?.toFixed(0) || 0)} jours`}
                color="red"
                threeColumns={true}
              />
            </View>
          </View>
        )}

        {/* Performance Collectes */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Performance des Collectes</Text>
          <View style={styles.twoColumn}>
            {/* Vue d'Ensemble */}
            <View style={[styles.column, styles.card]}>
              <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10, color: '#111827' }}>
                Vue d'Ensemble
              </Text>
              {performanceCollectes?.global ? (
                <View>
                  <StatRow
                    label="Total Collectes"
                    value={formatNumber(performanceCollectes.global.total_collectes || 0)}
                    color="blue"
                  />
                  <StatRow
                    label="Collectes Clôturées"
                    value={formatNumber(performanceCollectes.global.total_cloturees || 0)}
                    color="green"
                  />
                  <StatRow
                    label="Collectes Ouvertes"
                    value={formatNumber(performanceCollectes.global.total_ouvertes || 0)}
                    color="orange"
                  />
                  <StatRow
                    label="Taux de Clôture Moyen"
                    value={formatPercent(performanceCollectes.global.taux_cloture_moyen || 0)}
                    color="purple"
                  />
                  <StatRow
                    label="Taux de Recouvrement"
                    value={formatPercent(performanceCollectes.global.taux_recouvrement_moyen || 0)}
                    color="indigo"
                  />
                  <StatRow
                    label="Durée Moyenne"
                    value={`${formatNumber(performanceCollectes.global.duree_moyenne_jours?.toFixed(0) || 0)} jours`}
                    color="gray"
                  />
                </View>
              ) : (
                <View style={styles.emptyState}>
                  <Text>Chargement...</Text>
                </View>
              )}
            </View>

            {/* Évolution Trimestrielle */}
            <View style={[styles.column, styles.card]}>
              <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10, color: '#111827' }}>
                Évolution Trimestrielle
              </Text>
              {performanceCollectes?.par_trimestre && performanceCollectes.par_trimestre.length > 0 ? (
                <LineChartPDF
                  data={performanceCollectes.par_trimestre.map(item => ({
                    ...item,
                    trimestre: `T${item.trimestre}`
                  }))}
                  dataKeys={[
                    { key: 'total_collectes', color: '#3b82f6', name: 'Collectes', yAxisId: 'left' },
                    { key: 'taux_recouvrement', color: '#8b5cf6', name: 'Taux (%)', yAxisId: 'right' }
                  ]}
                  labelKey="trimestre"
                  width={270}
                  height={300}
                />
              ) : (
                <View style={styles.emptyState}>
                  <Text>Aucune donnée disponible</Text>
                </View>
              )}
            </View>
          </View>

          {/* Montants Collectes */}
          {performanceCollectes?.global && (
            <View style={[styles.card, { marginTop: 10 }]}>
              <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10, color: '#111827' }}>
                Montants des Collectes
              </Text>
              <View style={styles.threeColumn}>
                <View style={[styles.amountCard, { backgroundColor: '#eff6ff' }]}>
                  <Text style={styles.amountLabel}>Montant à Recouvrer</Text>
                  <Text style={[styles.amountValue, { color: '#2563eb' }]}>
                    {formatCurrencyShort(performanceCollectes.global.montant_total_a_recouvrer || 0)} FCFA
                  </Text>
                </View>
                <View style={[styles.amountCard, { backgroundColor: '#ecfdf5' }]}>
                  <Text style={styles.amountLabel}>Montant Recouvré</Text>
                  <Text style={[styles.amountValue, { color: '#10b981' }]}>
                    {formatCurrencyShort(performanceCollectes.global.montant_total_recouvre || 0)} FCFA
                  </Text>
                </View>
                <View style={[styles.amountCard, { backgroundColor: '#fff7ed' }]}>
                  <Text style={styles.amountLabel}>Reste à Recouvrer</Text>
                  <Text style={[styles.amountValue, { color: '#f59e0b' }]}>
                    {formatCurrencyShort(
                      (performanceCollectes.global.montant_total_a_recouvrer || 0) - 
                      (performanceCollectes.global.montant_total_recouvre || 0)
                    )} FCFA
                  </Text>
                </View>
              </View>
            </View>
          )}
        </View>

        {/* Performance Attributions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Performance des Attributions</Text>
          <View style={styles.twoColumn}>
            {/* Vue d'Ensemble */}
            <View style={[styles.column, styles.card]}>
              <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10, color: '#111827' }}>
                Vue d'Ensemble
              </Text>
              {performanceAttributions?.global ? (
                <View>
                  <StatRow
                    label="Total Demandes"
                    value={formatNumber(performanceAttributions.global.total_demandes || 0)}
                    color="blue"
                  />
                  <StatRow
                    label="Demandes Approuvées"
                    value={formatNumber(performanceAttributions.global.total_approuvees || 0)}
                    color="green"
                  />
                  <StatRow
                    label="Demandes Rejetées"
                    value={formatNumber(performanceAttributions.global.total_rejetees || 0)}
                    color="red"
                  />
                  <StatRow
                    label="En Attente"
                    value={formatNumber(performanceAttributions.global.total_en_attente || 0)}
                    color="orange"
                  />
                  <StatRow
                    label="Taux d'Approbation"
                    value={formatPercent(performanceAttributions.global.taux_approbation_moyen || 0)}
                    color="purple"
                  />
                  <StatRow
                    label="Délai Moyen"
                    value={`${formatNumber(performanceAttributions.global.delai_moyen_jours?.toFixed(0) || 0)} jours`}
                    color="gray"
                  />
                </View>
              ) : (
                <View style={styles.emptyState}>
                  <Text>Chargement...</Text>
                </View>
              )}
            </View>

            {/* Graphique Évolution */}
            <View style={[styles.column, styles.card]}>
              <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10, color: '#111827' }}>
                Évolution des Demandes
              </Text>
              {performanceAttributions?.par_trimestre && performanceAttributions.par_trimestre.length > 0 ? (
                <MultiBarChartPDF
                  data={performanceAttributions.par_trimestre}
                  dataKeys={[
                    { key: 'demandes_approuvees', color: '#10b981', name: 'Approuvées' },
                    { key: 'demandes_rejetees', color: '#ef4444', name: 'Rejetées' },
                    { key: 'demandes_en_attente', color: '#f59e0b', name: 'En Attente' }
                  ]}
                  labelKey="trimestre"
                  width={220}
                  height={300}
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

      {/* Page 2: Performance Facturation */}
      <Page size="A4" style={styles.page}>
        {/* Performance Facturation */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Performance de la Facturation</Text>
          <View style={styles.twoColumn}>
            {/* Vue d'Ensemble */}
            <View style={[styles.column, styles.card]}>
              <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10, color: '#111827' }}>
                Vue d'Ensemble
              </Text>
              {performanceFacturation?.global ? (
                <View>
                  <StatRow
                    label="Factures Émises"
                    value={formatNumber(performanceFacturation.global.total_factures_emises || 0)}
                    color="blue"
                  />
                  <StatRow
                    label="Factures Payées"
                    value={formatNumber(performanceFacturation.global.total_factures_payees || 0)}
                    color="green"
                  />
                  <StatRow
                    label="Taux de Paiement"
                    value={formatPercent(performanceFacturation.global.taux_paiement_pct || 0)}
                    color="purple"
                  />
                  <StatRow
                    label="Taux de Recouvrement"
                    value={formatPercent(performanceFacturation.global.taux_recouvrement_pct || 0)}
                    color="indigo"
                  />
                  <StatRow
                    label="Délai Moyen de Paiement"
                    value={`${formatNumber(performanceFacturation.global.delai_moyen_paiement?.toFixed(0) || 0)} jours`}
                    color="gray"
                  />
                  <StatRow
                    label="Montant Total Facturé"
                    value={formatCurrencyShort(performanceFacturation.global.montant_total_facture || 0) + ' FCFA'}
                    color="emerald"
                  />
                </View>
              ) : (
                <View style={styles.emptyState}>
                  <Text>Chargement...</Text>
                </View>
              )}
            </View>

            {/* Graphique Montants */}
            <View style={[styles.column, styles.card]}>
              <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10, color: '#111827' }}>
                Évolution des Montants
              </Text>
              {performanceFacturation?.par_trimestre && performanceFacturation.par_trimestre.length > 0 ? (
                <AreaChartPDF
                  data={performanceFacturation.par_trimestre.map(item => ({
                    ...item,
                    trimestre: `T${item.trimestre}`
                  }))}
                  dataKeys={[
                    { key: 'montant_facture', color: '#3b82f6', name: 'Facturé' },
                    { key: 'montant_paye', color: '#10b981', name: 'Payé' }
                  ]}
                  labelKey="trimestre"
                  width={220}
                  height={300}
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
    </Document>
  );
}

