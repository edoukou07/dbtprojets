import React from 'react';
import { View, Text, Svg, Line, G, Defs, ClipPath, Rect, Path } from '@react-pdf/renderer';

export default function MultiBarChartPDF({ 
  data, 
  dataKeys = [], // Array of { key, color, name }
  labelKey = 'label',
  width = 500, 
  height = 400,
  style 
}) {
  if (!data || data.length === 0 || !dataKeys || dataKeys.length === 0) {
    return (
      <View style={[{ width, height, justifyContent: 'center', alignItems: 'center' }, style]}>
        <Text style={{ fontSize: 12, color: '#6b7280' }}>Aucune donnée disponible</Text>
      </View>
    );
  }

  // Calculer la valeur maximale parmi toutes les séries
  const maxValue = Math.max(
    ...data.flatMap(item => 
      dataKeys.map(dk => item[dk.key] || 0)
    )
  );

  // Dimensions du graphique
  const padding = 5;
  const yAxisLabelWidth = 80;
  const chartAreaX = yAxisLabelWidth + padding;
  const chartAreaWidth = width - chartAreaX - padding - 20;
  const chartAreaHeight = height - 100; // Réserver de l'espace pour les labels X et la légende
  const chartAreaY = 20;
  const xAxisY = chartAreaY + chartAreaHeight;
  const xAxisHeight = 60; // Plus d'espace pour les labels X inclinés
  const legendHeight = 30;

  // Calculer les graduations pour l'axe Y
  const tickCount = 5;
  const yTicks = Array.from({ length: tickCount }, (_, i) => {
    const value = (maxValue / (tickCount - 1)) * i;
    return Math.round(value);
  });

  // Fonction pour formater les valeurs de l'axe Y
  const formatYValue = (value) => {
    if (value === 0) return '0';
    if (value >= 1000000) {
      return (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
      return (value / 1000).toFixed(1) + 'K';
    }
    return value.toString();
  };

  // Dimensions des barres
  const totalBars = data.length;
  const barGroupWidth = chartAreaWidth / totalBars;
  const barWidth = (barGroupWidth * 0.7) / dataKeys.length; // 70% de l'espace pour les barres, divisé par le nombre de séries
  const barSpacing = barWidth * 0.2; // Espacement entre les barres d'un même groupe

  // Calculer les positions X des groupes de barres
  const barGroupPositions = data.map((_, index) => {
    return chartAreaX + (index * barGroupWidth) + (barGroupWidth * 0.15); // Centrer le groupe
  });

  return (
    <View style={[{ width, height: chartAreaY + chartAreaHeight + xAxisHeight + legendHeight }, style]}>
      <Svg 
        style={{ 
          position: 'relative',
          width: width,
          height: chartAreaY + chartAreaHeight + xAxisHeight
        }}
        viewBox={`0 0 ${width} ${chartAreaY + chartAreaHeight + xAxisHeight}`}
      >
        <Defs>
          <ClipPath id="multi-bar-chart-clip">
            <Rect 
              x={chartAreaX} 
              y={chartAreaY} 
              width={chartAreaWidth} 
              height={chartAreaHeight} 
            />
          </ClipPath>
        </Defs>

        {/* Grille horizontale */}
        <G>
          {yTicks.map((tick, i) => {
            const yPosition = chartAreaY + chartAreaHeight - (tick / maxValue) * chartAreaHeight;
            const dashLength = 3;
            const gapLength = 3;
            const segments = [];
            let currentX = chartAreaX;
            while (currentX < chartAreaX + chartAreaWidth) {
              segments.push(
                <Line
                  key={`h-${i}-seg-${segments.length}`}
                  x1={currentX}
                  y1={yPosition}
                  x2={Math.min(currentX + dashLength, chartAreaX + chartAreaWidth)}
                  y2={yPosition}
                  stroke="#ccc"
                  strokeWidth={0.5}
                />
              );
              currentX += dashLength + gapLength;
            }
            return segments;
          })}
        </G>

        {/* Grille verticale */}
        <G>
          {barGroupPositions.map((xPosition, i) => {
            const dashLength = 3;
            const gapLength = 3;
            const segments = [];
            let currentY = chartAreaY;
            while (currentY < xAxisY) {
              segments.push(
                <Line
                  key={`v-${i}-seg-${segments.length}`}
                  x1={xPosition}
                  y1={currentY}
                  x2={xPosition}
                  y2={Math.min(currentY + dashLength, xAxisY)}
                  stroke="#ccc"
                  strokeWidth={0.5}
                />
              );
              currentY += dashLength + gapLength;
            }
            return segments;
          })}
        </G>

        {/* Axe X */}
        <G>
          <Line
            x1={chartAreaX}
            y1={xAxisY}
            x2={chartAreaX + chartAreaWidth}
            y2={xAxisY}
            stroke="#666"
            strokeWidth={1}
          />
        </G>

        {/* Axe Y */}
        <G>
          <Line
            x1={chartAreaX}
            y1={chartAreaY}
            x2={chartAreaX}
            y2={xAxisY}
            stroke="#666"
            strokeWidth={1}
          />
          {yTicks.map((tick, i) => {
            const yPosition = chartAreaY + chartAreaHeight - (tick / maxValue) * chartAreaHeight;
            return (
              <G key={i}>
                <Line
                  x1={chartAreaX - 6}
                  y1={yPosition}
                  x2={chartAreaX}
                  y2={yPosition}
                  stroke="#666"
                  strokeWidth={1}
                />
              </G>
            );
          })}
        </G>

        {/* Barres groupées */}
        <G clipPath="url(#multi-bar-chart-clip)">
          {data.map((item, itemIndex) => {
            const groupX = barGroupPositions[itemIndex];
            
            return dataKeys.map((dataKey, keyIndex) => {
              const value = item[dataKey.key] || 0;
              const barHeight = maxValue > 0 ? (value / maxValue) * chartAreaHeight : 0;
              const barX = groupX + (keyIndex * (barWidth + barSpacing));
              const barY = chartAreaY + chartAreaHeight - barHeight;
              const barBottomY = chartAreaY + chartAreaHeight;
              
              // Créer un rectangle simple sans coins arrondis
              const path = `M${barX},${barBottomY}L${barX + barWidth},${barBottomY}L${barX + barWidth},${barY}L${barX},${barY}Z`;
              
              return (
                <G key={`${itemIndex}-${keyIndex}`}>
                  <Path
                    d={path}
                    fill={dataKey.color}
                  />
                </G>
              );
            });
          })}
        </G>
      </Svg>

      {/* Labels Y */}
      <View style={{ 
        position: 'absolute', 
        left: 0, 
        top: chartAreaY, 
        width: yAxisLabelWidth, 
        height: chartAreaHeight 
      }}>
        {yTicks.map((tick, i) => {
          const yPosition = chartAreaHeight - (tick / maxValue) * chartAreaHeight;
          return (
            <View 
              key={i}
              style={{ 
                position: 'absolute',
                top: yPosition - 4,
                width: '100%',
                height: 8,
                justifyContent: 'center',
                alignItems: 'flex-end',
                paddingRight: 8
              }}
            >
              <Text style={{ 
                fontSize: 8, 
                color: '#666', 
                textAlign: 'right',
                fontFamily: 'Helvetica',
                lineHeight: 1
              }}>
                {formatYValue(tick)}
              </Text>
            </View>
          );
        })}
      </View>

      {/* Labels X (inclinés) */}
      <View style={{ 
        position: 'absolute', 
        left: chartAreaX, 
        top: xAxisY + 8, 
        width: chartAreaWidth, 
        height: xAxisHeight - 8 
      }}>
        {data.map((item, index) => {
          const groupX = barGroupPositions[index] - chartAreaX;
          let label = String(item[labelKey] || '');
          // Formater les trimestres (T1, T2, etc.)
          if (typeof item[labelKey] === 'number' || /^\d+$/.test(label)) {
            label = `T${label}`;
          }
          
          return (
            <View 
              key={index}
              style={{
                position: 'absolute',
                left: groupX + (barGroupWidth / 2) - 20,
                top: 0,
                width: 40,
                height: 50,
                justifyContent: 'flex-start',
                alignItems: 'center'
              }}
            >
              <Text style={{ 
                fontSize: 8, 
                color: '#666',
                textAlign: 'center',
                transform: [{ rotate: '-45deg' }]
              }}>
                {label}
              </Text>
            </View>
          );
        })}
      </View>

      {/* Légende */}
      <View style={{
        position: 'absolute',
        left: chartAreaX,
        bottom: 5,
        width: chartAreaWidth,
        height: legendHeight,
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 40
      }}>
        {dataKeys.map((dataKey, index) => (
          <View key={index} style={{
            flexDirection: 'row',
            alignItems: 'center',
          }}>
            <Svg width={14} height={14} viewBox="0 0 32 32" style={{ marginRight: 4 }}>
              <Path
                d="M0,4h32v24h-32z"
                fill={dataKey.color}
              />
            </Svg>
            <Text style={{
              fontSize: 8,
              color: '#666'
            }}>
              {dataKey.name}
            </Text>
          </View>
        ))}
      </View>
    </View>
  );
}

