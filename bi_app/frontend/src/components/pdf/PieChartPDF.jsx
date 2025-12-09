import React from 'react';
import { View, Text, StyleSheet, Svg, Path, G } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginVertical: 10,
  },
  chartContainer: {
    width: 200,
    height: 200,
    position: 'relative',
    marginBottom: 15,
    alignItems: 'center',
    justifyContent: 'center',
  },
  svgContainer: {
    width: 200,
    height: 200,
  },
  legend: {
    marginTop: 15,
    width: '100%',
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    paddingHorizontal: 8,
  },
  colorDot: {
    width: 14,
    height: 14,
    borderRadius: 7,
    marginRight: 10,
  },
  legendContent: {
    flex: 1,
  },
  legendLabel: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 2,
  },
  legendDetails: {
    fontSize: 8,
    color: '#6b7280',
  },
});

// Helper pour convertir un angle en radians
const toRadians = (angle) => (angle * Math.PI) / 180;

// Helper pour calculer les coordonnées d'un point sur un cercle
const getPointOnCircle = (centerX, centerY, radius, angle) => {
  const rad = toRadians(angle);
  return {
    x: centerX + radius * Math.cos(rad),
    y: centerY + radius * Math.sin(rad)
  };
};

// Créer un path SVG pour un secteur de cercle (pie slice)
const createPieSlice = (centerX, centerY, radius, startAngle, endAngle) => {
  const start = getPointOnCircle(centerX, centerY, radius, startAngle);
  const end = getPointOnCircle(centerX, centerY, radius, endAngle);
  
  const largeArc = endAngle - startAngle > 180 ? 1 : 0;
  
  return `M ${centerX} ${centerY} L ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArc} 1 ${end.x} ${end.y} Z`;
};

export default function PieChartPDF({ data, dataKey, labelKey, colors, size = 200, style, showLegend = true, showLabels = true }) {
  if (!data || data.length === 0) {
    return (
      <View style={[styles.container, style]}>
        <Text style={{ fontSize: 10, color: '#6b7280' }}>Aucune donnée disponible</Text>
      </View>
    );
  }

  // Calculer le total pour les pourcentages
  const total = data.reduce((sum, item) => sum + (item[dataKey] || 0), 0);
  
  const centerX = size / 2;
  const centerY = size / 2;
  // Rayon proportionnel à celui de la page web (outerRadius={80} dans un container de ~250px)
  const radius = size * 0.32;
  const labelRadius = radius * 1.25; // Position des labels à l'extérieur du cercle (125% du rayon)
  
  // Calculer les angles pour chaque segment
  let currentAngle = -90; // Commencer en haut (-90 degrés)
  const segments = data.map((item, index) => {
    const value = item[dataKey] || 0;
    const percentage = total > 0 ? (value / total) * 100 : 0;
    const angle = (value / total) * 360;
    const startAngle = currentAngle;
    const endAngle = currentAngle + angle;
    const midAngle = startAngle + angle / 2; // Angle au milieu du segment
    
    currentAngle = endAngle;
    
    // Position du label à l'extérieur du segment
    const labelPos = getPointOnCircle(centerX, centerY, labelRadius, midAngle);
    // Point de connexion sur le bord du cercle
    const connectionPoint = getPointOnCircle(centerX, centerY, radius, midAngle);
    
    // S'assurer qu'on a toujours un nom pour le segment
    const segmentName = item[labelKey] || item.segment_client || `Segment ${index + 1}`;
    
    return {
      ...item,
      value,
      percentage,
      startAngle,
      endAngle,
      midAngle,
      path: createPieSlice(centerX, centerY, radius, startAngle, endAngle),
      labelPos,
      connectionPoint,
      segmentName, // Nom du segment garanti
      color: colors[index % colors.length]
    };
  });

  return (
    <View style={[styles.container, { width: size }, style]}>
      {/* Graphique en camembert avec SVG */}
      <View style={styles.chartContainer}>
        <Svg width={size} height={size} style={styles.svgContainer}>
          <G>
            {/* Dessiner les segments */}
            {segments.map((segment, index) => (
              <Path
                key={index}
                d={segment.path}
                fill={segment.color}
                stroke="#ffffff"
                strokeWidth={2}
              />
            ))}
            
            {/* Lignes de connexion pour les labels */}
            {showLabels && segments.map((segment, index) => {
              return (
                <Path
                  key={`line-${index}`}
                  d={`M ${segment.connectionPoint.x} ${segment.connectionPoint.y} L ${segment.labelPos.x} ${segment.labelPos.y}`}
                  stroke={segment.color}
                  strokeWidth={1}
                  fill="none"
                />
              );
            })}
          </G>
        </Svg>
        
        {/* Labels positionnés à l'extérieur du graphique */}
        {showLabels && segments.map((segment, index) => {
          // Utiliser le nom du segment garanti
          const segmentName = segment.segmentName || segment[labelKey] || segment.segment_client || `Segment ${index + 1}`;
          const labelText = `${segmentName}: ${segment.value}`;
          
          // Déterminer l'alignement du texte selon la position (gauche ou droite)
          const isLeftSide = segment.labelPos.x < centerX;
          const textAlign = isLeftSide ? 'right' : 'left';
          const labelOffsetX = isLeftSide ? -5 : 5;
          
          // Ajuster la taille de la police pour les petits segments
          const fontSize = segment.percentage < 5 ? 6 : 7;
          
          return (
            <View
              key={`label-${index}`}
              style={{
                position: 'absolute',
                left: segment.labelPos.x + labelOffsetX - (isLeftSide ? 60 : 0),
                top: segment.labelPos.y - 5,
                width: 60,
                alignItems: isLeftSide ? 'flex-end' : 'flex-start',
                justifyContent: 'center',
              }}
            >
              <Text style={{ 
                color: segment.color,
                fontSize: fontSize,
                fontWeight: 'bold',
                textAlign: textAlign,
              }}>
                {labelText}
              </Text>
            </View>
          );
        })}
      </View>
      
      {/* Légende détaillée */}
      {showLegend && (
        <View style={styles.legend}>
          {segments.map((segment, index) => (
            <View key={index} style={styles.legendItem}>
              <View style={[styles.colorDot, { backgroundColor: segment.color }]} />
              <View style={styles.legendContent}>
                <Text style={styles.legendLabel}>{segment[labelKey]}</Text>
                <Text style={styles.legendDetails}>
                  {segment.value} clients • {segment.percentage.toFixed(1)}%
                </Text>
              </View>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

