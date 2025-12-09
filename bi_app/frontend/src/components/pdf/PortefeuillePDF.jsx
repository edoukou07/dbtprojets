import React from 'react';
import { Document, Page, Text, View, StyleSheet, Font } from '@react-pdf/renderer';
import PieChartPDF from './PieChartPDF';
import BarChartPDF from './BarChartPDF';
import RiskBarChartPDF from './RiskBarChartPDF';
import SectorBarChartPDF from './SectorBarChartPDF';

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
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    border: '1 solid #e5e7eb',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 15,
  },
  kpiCard: {
    width: '23%',
    marginRight: '2%',
    marginBottom: 15,
    backgroundColor: '#ffffff',
    padding: 12,
    borderRadius: 8,
    border: '1 solid #e5e7eb',
  },
  kpiTitle: {
    fontSize: 9,
    color: '#6b7280',
    marginBottom: 5,
  },
  kpiValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 3,
  },
  kpiSubtitle: {
    fontSize: 8,
    color: '#9ca3af',
  },
  twoColumn: {
    flexDirection: 'row',
    gap: 15,
  },
  column: {
    flex: 1,
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
  segmentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#f9fafb',
    borderRadius: 4,
    marginBottom: 6,
  },
  colorDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  riskCard: {
    padding: 8,
    borderRadius: 4,
    marginBottom: 6,
    borderLeft: '4 solid',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  statCard: {
    width: '23%',
    padding: 12,
    borderRadius: 6,
    border: '1 solid',
  },
  pageBreak: {
    marginTop: 20,
    paddingTop: 20,
    borderTop: '1 solid #e5e7eb',
  },
});

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];
const RISK_COLORS = {
  'Risque faible': '#10b981',
  'Risque moyen': '#f59e0b',
  'Risque élevé': '#ef4444'
};

const getSegmentColor = (segment) => {
  const colors = {
    'Premium': '#9333ea',
    'VIP': '#f43f5e',
    'Standard': '#0284c7',
    'Basique': '#f59e0b',
    'Nouveau': '#10b981'
  };
  return colors[segment] || '#64748b';
};

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

export default function PortefeuillePDF({ 
  summary, 
  segmentation, 
  topClients, 
  atRisk, 
  comportement, 
  occupation 
}) {
  return (
    <Document>
      <Page size="A4" style={styles.page}>
        {/* En-tête */}
        <View style={styles.header}>
          <Text style={styles.title}>Portefeuille Clients</Text>
          <Text style={styles.subtitle}>Analyse et segmentation du portefeuille</Text>
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
          <Text style={styles.sectionTitle}>Vue d'Ensemble du Portefeuille</Text>
          <View style={styles.grid}>
            <View style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>Total Clients</Text>
              <Text style={styles.kpiValue}>
                {String(summary?.total_clients?.toLocaleString('fr-FR') || '0')}
              </Text>
              <Text style={styles.kpiSubtitle}>Entreprises actives</Text>
            </View>
            <View style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>Créances Totales</Text>
              <Text style={styles.kpiValue}>
                {`${formatCurrencyShort(summary?.ca_impaye)} FCFA`}
              </Text>
              <Text style={styles.kpiSubtitle}>
                {`${formatPercent(summary?.taux_impaye_pct)} du CA`}
              </Text>
            </View>
            <View style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>Délai Moyen Paiement</Text>
              <Text style={styles.kpiValue}>
                {`${Math.round(summary?.delai_moyen_paiement || 0)} jours`}
              </Text>
              <Text style={styles.kpiSubtitle}>Moyenne par client</Text>
            </View>
            <View style={styles.kpiCard}>
              <Text style={styles.kpiTitle}>Factures en Retard</Text>
              <Text style={styles.kpiValue}>
                {String(summary?.factures_retard_total?.toLocaleString('fr-FR') || '0')}
              </Text>
              <Text style={styles.kpiSubtitle}>À relancer</Text>
            </View>
          </View>
        </View>

        {/* Segmentation et Risque */}
        <View style={styles.section}>
          <View style={styles.twoColumn}>
            {/* Segmentation Clients */}
            <View style={[styles.column, styles.card]}>
              <Text style={styles.sectionTitle}>Segmentation du Portefeuille</Text>
              {segmentation?.par_segment && segmentation.par_segment.length > 0 ? (
                <View>
                  <View style={{ alignItems: 'center', marginBottom: 15 }}>
                    <PieChartPDF
                      data={segmentation.par_segment}
                      dataKey="nombre_clients"
                      labelKey="segment_client"
                      colors={segmentation.par_segment.map(s => getSegmentColor(s.segment_client))}
                      size={200}
                      showLegend={false}
                      showLabels={true}
                    />
                  </View>
                  
                  <View style={{ marginTop: 15 }}>
                    {segmentation.par_segment.map((segment, index) => (
                      <View key={index} style={styles.segmentItem}>
                        <View style={[styles.colorDot, { 
                          backgroundColor: getSegmentColor(segment.segment_client) 
                        }]} />
                        <View style={{ flex: 1 }}>
                          <Text style={{ fontSize: 10, fontWeight: 'bold', color: '#111827' }}>
                            {segment.segment_client}
                          </Text>
                          <Text style={{ fontSize: 8, color: '#6b7280' }}>
                            {segment.nombre_clients} clients • Taux: {formatPercent(segment.taux_paiement_moyen)}
                          </Text>
                        </View>
                        <Text style={{ fontSize: 9, fontWeight: 'bold', color: '#374151' }}>
                          {formatCurrencyShort(segment.ca_total)}
                        </Text>
                      </View>
                    ))}
                  </View>
                </View>
              ) : (
                <Text style={{ fontSize: 10, color: '#6b7280', textAlign: 'center' }}>
                  Aucune donnée disponible
                </Text>
              )}
            </View>

            {/* Analyse de Risque */}
            <View style={[styles.column, styles.card]}>
              <Text style={styles.sectionTitle}>Répartition par Niveau de Risque</Text>
              {segmentation?.par_niveau_risque && segmentation.par_niveau_risque.length > 0 ? (
                <View>
                  <View style={{ 
                    marginBottom: 15, 
                    alignItems: 'center',
                    paddingHorizontal: 10,
                    paddingVertical: 5
                  }}>
                    <RiskBarChartPDF
                      data={segmentation.par_niveau_risque}
                      width={230}
                      height={200}
                    />
                  </View>
                  
                  <View>
                    {segmentation.par_niveau_risque.map((risque, index) => (
                      <View key={index} style={[styles.riskCard, {
                        borderLeftColor: RISK_COLORS[risque.niveau_risque] || '#64748b',
                        backgroundColor: `${RISK_COLORS[risque.niveau_risque] || '#64748b'}20`
                      }]}>
                        <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 }}>
                          <Text style={{ fontSize: 10, fontWeight: 'bold', color: '#111827' }}>
                            {risque.niveau_risque}
                          </Text>
                          <Text style={{ 
                            fontSize: 10, 
                            fontWeight: 'bold',
                            color: RISK_COLORS[risque.niveau_risque] || '#64748b'
                          }}>
                            {risque.nombre_clients} clients
                          </Text>
                        </View>
                        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                          <Text style={{ fontSize: 8, color: '#6b7280' }}>
                            CA: {formatCurrencyShort(risque.ca_total)}
                          </Text>
                          <Text style={{ fontSize: 8, color: '#6b7280' }}>
                            Créances: {formatCurrencyShort(risque.ca_impaye)}
                          </Text>
                        </View>
                      </View>
                    ))}
                  </View>
                </View>
              ) : (
                <Text style={{ fontSize: 10, color: '#6b7280', textAlign: 'center' }}>
                  Aucune donnée disponible
                </Text>
              )}
            </View>
          </View>
        </View>
      </Page>

      {/* Page 2: Comportement de Paiement */}
      {comportement?.par_taux_paiement && (
        <Page size="A4" style={styles.page}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Analyse du Comportement de Paiement</Text>
            
            {/* Cartes récapitulatives */}
            <View style={styles.statsGrid}>
              {comportement.par_taux_paiement.map((cat, idx) => {
                const bgColors = ['#ecfdf5', '#eff6ff', '#fefce8', '#fef2f2'];
                const borderColors = ['#10b981', '#3b82f6', '#eab308', '#ef4444'];
                const textColors = ['#10b981', '#3b82f6', '#eab308', '#ef4444'];
                
                return (
                  <View key={idx} style={[styles.statCard, {
                    backgroundColor: bgColors[idx] || '#f9fafb',
                    borderColor: borderColors[idx] || '#e5e7eb'
                  }]}>
                    <Text style={{ fontSize: 9, fontWeight: 'bold', color: textColors[idx], marginBottom: 6 }}>
                      {cat.categorie}
                    </Text>
                    <View style={{ gap: 4 }}>
                      <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                        <Text style={{ fontSize: 8, color: '#6b7280' }}>Clients:</Text>
                        <Text style={{ fontSize: 9, fontWeight: 'bold', color: '#111827' }}>
                          {String(cat.count || 0)}
                        </Text>
                      </View>
                      <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                        <Text style={{ fontSize: 8, color: '#6b7280' }}>CA:</Text>
                        <Text style={{ fontSize: 9, fontWeight: 'bold', color: '#111827' }}>
                          {formatCurrency(cat.ca_total || 0)}
                        </Text>
                      </View>
                      <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                        <Text style={{ fontSize: 8, color: '#6b7280' }}>Délai moyen:</Text>
                        <Text style={{ fontSize: 9, fontWeight: 'bold', color: '#111827' }}>
                          {`${cat.delai_moyen || 0}j`}
                        </Text>
                      </View>
                    </View>
                  </View>
                );
              })}
            </View>

            {/* Graphique: Répartition des clients */}
            <View style={[styles.card, { marginTop: 15 }]}>
              <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 10, color: '#111827' }}>
                Répartition des Clients par Taux de Paiement
              </Text>
              <BarChartPDF
                data={comportement.par_taux_paiement}
                dataKey="count"
                labelKey="categorie"
                color="#0ea5e9"
                width={500}
                height={250}
              />
            </View>

            {/* Délai de Paiement */}
            {comportement.par_delai_paiement && comportement.par_delai_paiement.length > 0 && (
              <View style={[styles.card, { marginTop: 15 }]}>
                <Text style={{ fontSize: 12, fontWeight: 'bold', marginBottom: 15, color: '#111827' }}>
                  Distribution par Délai de Paiement
                </Text>
                <View style={styles.twoColumn}>
                  <View style={styles.column}>
                    <Text style={{ fontSize: 10, fontWeight: 'bold', marginBottom: 8, color: '#374151' }}>
                      Nombre de Clients
                    </Text>
                    <BarChartPDF
                      data={comportement.par_delai_paiement}
                      dataKey="count"
                      labelKey="plage_delai"
                      color="#8b5cf6"
                      width={240}
                      height={200}
                    />
                  </View>
                  <View style={styles.column}>
                    <Text style={{ fontSize: 10, fontWeight: 'bold', marginBottom: 8, color: '#374151' }}>
                      Taux de Paiement Moyen
                    </Text>
                    <BarChartPDF
                      data={comportement.par_delai_paiement}
                      dataKey="taux_paiement_moyen"
                      labelKey="plage_delai"
                      color="#f59e0b"
                      width={240}
                      height={200}
                    />
                  </View>
                </View>
              </View>
            )}
          </View>
        </Page>
      )}

      {/* Page 3: Top Clients et Clients à Risque */}
      <Page size="A4" style={styles.page}>
        <View style={styles.section}>
          <View style={styles.twoColumn}>
            {/* Top Clients */}
            <View style={[styles.column, styles.card]}>
              <Text style={styles.sectionTitle}>
                Top Clients par CA ({topClients?.top_chiffre_affaires?.length || 0})
              </Text>
              {topClients?.top_chiffre_affaires && topClients.top_chiffre_affaires.length > 0 ? (
                <View style={styles.table}>
                  <View style={styles.tableHeader}>
                    <Text style={[styles.tableHeaderCell, { width: '10%' }]}>#</Text>
                    <Text style={[styles.tableHeaderCell, { width: '35%' }]}>Client</Text>
                    <Text style={[styles.tableHeaderCell, { width: '25%' }]}>CA Total</Text>
                    <Text style={[styles.tableHeaderCell, { width: '15%' }]}>Taux</Text>
                    <Text style={[styles.tableHeaderCell, { width: '15%' }]}>Segment</Text>
                  </View>
                  {topClients.top_chiffre_affaires.slice(0, 10).map((client, index) => (
                    <View key={client.entreprise_id} style={styles.tableRow}>
                      <Text style={[styles.tableCell, { width: '10%' }]}>{index + 1}</Text>
                      <View style={{ width: '35%' }}>
                        <Text style={[styles.tableCell, { fontWeight: 'bold' }]}>
                          {client.raison_sociale}
                        </Text>
                        <Text style={[styles.tableCell, { fontSize: 7, color: '#6b7280' }]}>
                          {client.secteur_activite || 'N/A'}
                        </Text>
                      </View>
                      <Text style={[styles.tableCell, { width: '25%', fontWeight: 'bold' }]}>
                        {formatCurrencyShort(client.chiffre_affaires_total)}
                      </Text>
                      <Text style={[styles.tableCell, { width: '15%' }]}>
                        {formatPercent(client.taux_paiement_pct)}
                      </Text>
                      <View style={{ width: '15%' }}>
                        <View style={[styles.badge, {
                          backgroundColor: getSegmentColor(client.segment_client),
                          color: '#ffffff'
                        }]}>
                          <Text style={{ fontSize: 7, color: '#ffffff' }}>
                            {client.segment_client || 'N/A'}
                          </Text>
                        </View>
                      </View>
                    </View>
                  ))}
                </View>
              ) : (
                <Text style={{ fontSize: 10, color: '#6b7280' }}>Aucun client</Text>
              )}
            </View>

            {/* Clients à Risque */}
            <View style={[styles.column, styles.card]}>
              <Text style={styles.sectionTitle}>
                Clients à Risque ({atRisk?.nombre_total || 0})
              </Text>
              {atRisk?.total_creances && (
                <Text style={{ fontSize: 9, color: '#6b7280', marginBottom: 10 }}>
                  Créances totales: {formatCurrency(atRisk.total_creances)}
                </Text>
              )}
              {atRisk?.clients_a_risque && atRisk.clients_a_risque.length > 0 ? (
                <View style={styles.table}>
                  <View style={[styles.tableHeader, { backgroundColor: '#fef2f2' }]}>
                    <Text style={[styles.tableHeaderCell, { width: '40%' }]}>Client</Text>
                    <Text style={[styles.tableHeaderCell, { width: '25%' }]}>Créances</Text>
                    <Text style={[styles.tableHeaderCell, { width: '20%' }]}>Taux</Text>
                    <Text style={[styles.tableHeaderCell, { width: '15%' }]}>Risque</Text>
                  </View>
                  {atRisk.clients_a_risque.slice(0, 10).map((client) => (
                    <View key={client.entreprise_id} style={styles.tableRow}>
                      <View style={{ width: '40%' }}>
                        <Text style={[styles.tableCell, { fontWeight: 'bold' }]}>
                          {client.raison_sociale}
                        </Text>
                        <Text style={[styles.tableCell, { fontSize: 7, color: '#6b7280' }]}>
                          {client.secteur_activite || 'N/A'}
                        </Text>
                      </View>
                      <Text style={[styles.tableCell, { width: '25%', fontWeight: 'bold', color: '#dc2626' }]}>
                        {formatCurrencyShort(client.ca_impaye)}
                      </Text>
                      <Text style={[styles.tableCell, { width: '20%' }]}>
                        {formatPercent(client.taux_paiement_pct)}
                      </Text>
                      <View style={{ width: '15%' }}>
                        <View style={[styles.badge, {
                          backgroundColor: `${RISK_COLORS[client.niveau_risque] || '#64748b'}20`,
                          color: RISK_COLORS[client.niveau_risque] || '#64748b'
                        }]}>
                          <Text style={{ 
                            fontSize: 7, 
                            color: RISK_COLORS[client.niveau_risque] || '#64748b' 
                          }}>
                            {client.niveau_risque || 'N/A'}
                          </Text>
                        </View>
                      </View>
                    </View>
                  ))}
                </View>
              ) : (
                <Text style={{ fontSize: 10, color: '#6b7280' }}>Aucun client à risque</Text>
              )}
            </View>
          </View>
        </View>

        {/* Analyse Occupation des Lots */}
        {occupation && (
          <View style={[styles.section, { marginTop: 20 }]}>
            <Text style={styles.sectionTitle}>Analyse de l'Occupation des Lots Industriels</Text>
            <View style={styles.statsGrid}>
              <View style={[styles.statCard, { backgroundColor: '#eff6ff', borderColor: '#3b82f6' }]}>
                <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#3b82f6', marginBottom: 4 }}>
                  {occupation.avec_lots?.nombre_clients || 0}
                </Text>
                <Text style={{ fontSize: 9, fontWeight: 'bold', color: '#111827', marginBottom: 4 }}>
                  Clients avec Lots
                </Text>
                <Text style={{ fontSize: 8, color: '#6b7280' }}>
                  {`${occupation.avec_lots?.total_lots || 0} lots • ${occupation.avec_lots?.superficie_totale?.toLocaleString('fr-FR') || 0} m²`}
                </Text>
              </View>

              <View style={[styles.statCard, { backgroundColor: '#f9fafb', borderColor: '#6b7280' }]}>
                <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#6b7280', marginBottom: 4 }}>
                  {occupation.sans_lots?.nombre_clients || 0}
                </Text>
                <Text style={{ fontSize: 9, fontWeight: 'bold', color: '#111827', marginBottom: 4 }}>
                  Clients sans Lots
                </Text>
                <Text style={{ fontSize: 8, color: '#6b7280' }}>
                  Prospects potentiels
                </Text>
              </View>

              <View style={[styles.statCard, { backgroundColor: '#ecfdf5', borderColor: '#10b981' }]}>
                <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#10b981', marginBottom: 4 }}>
                  {formatCurrencyShort(occupation.avec_lots?.ca_moyen)}
                </Text>
                <Text style={{ fontSize: 9, fontWeight: 'bold', color: '#111827', marginBottom: 4 }}>
                  CA Moyen (avec lots)
                </Text>
                <Text style={{ fontSize: 8, color: '#6b7280' }}>
                  Par client occupant
                </Text>
              </View>

              <View style={[styles.statCard, { backgroundColor: '#fff7ed', borderColor: '#f59e0b' }]}>
                <Text style={{ fontSize: 18, fontWeight: 'bold', color: '#f59e0b', marginBottom: 4 }}>
                  {formatCurrencyShort(occupation.sans_lots?.ca_moyen)}
                </Text>
                <Text style={{ fontSize: 9, fontWeight: 'bold', color: '#111827', marginBottom: 4 }}>
                  CA Moyen (sans lots)
                </Text>
                <Text style={{ fontSize: 8, color: '#6b7280' }}>
                  Par client non-occupant
                </Text>
              </View>
            </View>
          </View>
        )}

        {/* Secteurs d'Activité */}
        {segmentation?.par_secteur && segmentation.par_secteur.length > 0 && (
          <View style={[styles.section, { marginTop: 20 }]}>
            <Text style={styles.sectionTitle}>Top Secteurs d'Activité</Text>
            <View style={styles.card}>
              <View style={{ 
                alignItems: 'flex-start',
                paddingHorizontal: 10,
                paddingVertical: 5,
                paddingLeft: -10
              }}>
                <SectorBarChartPDF
                  data={segmentation.par_secteur}
                  width={480}
                  height={300}
                />
              </View>
            </View>
          </View>
        )}
      </Page>
    </Document>
  );
}

