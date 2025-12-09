import React from 'react';
import { View, Text, StyleSheet, Svg, Path, Circle, Line } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginVertical: 10,
  },
  gaugeContainer: {
    width: 192,
    height: 96,
    position: 'relative',
    marginBottom: 8,
  },
  label: {
    fontSize: 9,
    fontWeight: 'bold',
    color: '#374151',
    marginTop: 4,
    textAlign: 'center',
  },
  legend: {
    flexDirection: 'row',
    gap: 6,
    marginTop: 4,
  },
  legendItem: {
    fontSize: 7,
    color: '#6b7280',
  },
});

export default function GaugeChartPDF({ 
  value, 
  max, 
  label, 
  threshold, 
  warningThreshold, 
  unit = '%' 
}) {
  const percentage = (value / max) * 100;
  const rotation = (percentage / 100) * 180 - 90;
  
  const getColor = () => {
    if (value >= threshold) return '#ef4444'; // Rouge
    if (value >= warningThreshold) return '#f59e0b'; // Orange
    return '#10b981'; // Vert
  };
  
  const color = getColor();
  
  // Dimensions du gauge
  const width = 192;
  const height = 96;
  const centerX = width / 2;
  const centerY = height;
  const radius = 80;
  
  // Calculer les points pour l'arc
  const startAngle = -90; // Commence à gauche
  const endAngle = 90; // Se termine à droite
  
  // Créer le path pour l'arc de fond
  const createArcPath = (start, end) => {
    const startRad = (start * Math.PI) / 180;
    const endRad = (end * Math.PI) / 180;
    const startX = centerX + radius * Math.cos(startRad);
    const startY = centerY + radius * Math.sin(startRad);
    const endX = centerX + radius * Math.cos(endRad);
    const endY = centerY + radius * Math.sin(endRad);
    const largeArc = end - start > 180 ? 1 : 0;
    return `M ${startX} ${startY} A ${radius} ${radius} 0 ${largeArc} 1 ${endX} ${endY}`;
  };
  
  // Calculer l'angle de la valeur
  const valueAngle = startAngle + (percentage / 100) * (endAngle - startAngle);
  const valueRad = (valueAngle * Math.PI) / 180;
  const needleLength = 60;
  const needleEndX = centerX + needleLength * Math.cos(valueRad);
  const needleEndY = centerY + needleLength * Math.sin(valueRad);
  
  return (
    <View style={styles.container}>
      <View style={styles.gaugeContainer}>
        <Svg width={width} height={height} viewBox="0 0 200 100">
          {/* Arc de fond */}
          <Path
            d={createArcPath(startAngle, endAngle)}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth="20"
            strokeLinecap="round"
          />
          
          {/* Arc coloré */}
          <Path
            d={createArcPath(startAngle, valueAngle)}
            fill="none"
            stroke={color}
            strokeWidth="20"
            strokeLinecap="round"
          />
          
          {/* Aiguille - dessinée directement sans transformation */}
          <Line
            x1={centerX}
            y1={centerY}
            x2={needleEndX}
            y2={needleEndY}
            stroke="#374151"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <Circle cx={centerX} cy={centerY} r="5" fill="#374151" />
        </Svg>
        
        {/* Valeur */}
        <View style={{
          position: 'absolute',
          bottom: 8,
          left: 0,
          right: 0,
          alignItems: 'center',
        }}>
          <Text style={{
            fontSize: 24,
            fontWeight: 'bold',
            color: color,
          }}>
            {value.toFixed(1)}{unit}
          </Text>
        </View>
      </View>
      
      <Text style={styles.label}>{label}</Text>
      
      <View style={styles.legend}>
        <Text style={[styles.legendItem, { color: '#10b981' }]}>
          ✓ &lt;{warningThreshold}{unit}
        </Text>
        <Text style={[styles.legendItem, { color: '#f59e0b' }]}>
          ⚠ {warningThreshold}-{threshold}{unit}
        </Text>
        <Text style={[styles.legendItem, { color: '#ef4444' }]}>
          ✗ &gt;{threshold}{unit}
        </Text>
      </View>
    </View>
  );
}

