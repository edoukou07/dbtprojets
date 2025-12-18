import React from 'react';
import { View, Text, Svg, Line, G, Defs, ClipPath, Rect, Path } from '@react-pdf/renderer';

export default function RiskBarChartPDF({ 
  data, 
  width = 250, 
  height = 200,
  style 
}) {
  if (!data || data.length === 0) {
    return (
      <View style={[{ width, height, justifyContent: 'center', alignItems: 'center' }, style]}>
        <Text style={{ fontSize: 12, color: '#6b7280' }}>Aucune donnée disponible</Text>
      </View>
    );
  }

  const maxValue = Math.max(...data.map(item => item.nombre_clients || 0));
  
  // Dimensions basées sur la structure Recharts fournie
  const padding = 5; // Padding pour éviter le débordement
  const yAxisLabelWidth = 70; // Largeur pour les labels Y (réduite pour moins de margin-left)
  const chartAreaX = yAxisLabelWidth + padding; // Position X du début de la zone de graphique
  const chartAreaWidth = width - chartAreaX - padding; // Largeur de la zone de graphique (avec padding)
  const chartAreaHeight = 210; // Hauteur de la zone de graphique (210 dans Recharts: de y=5 à y=215)
  const chartAreaY = 5; // Position Y du début de la zone de graphique
  const xAxisY = chartAreaY + chartAreaHeight; // Position Y de l'axe X (215 dans Recharts)
  const xAxisHeight = 30; // Hauteur pour l'axe X et ses labels
  
  // Dimensions des barres (basées sur le SVG: barres de 84px de haut)
  const barHeight = 84; // Hauteur des barres (84px dans Recharts)
  const totalBars = data.length;
  
  // Calculer les positions verticales des barres (centrées dans chartAreaHeight)
  const totalBarsHeight = totalBars * barHeight;
  const barVerticalSpacing = (chartAreaHeight - totalBarsHeight) / (totalBars + 1);
  
  // Toutes les barres sont bleues comme sur la page web (#0ea5e9)
  const barColor = '#0ea5e9';
  
  // Calculer les graduations pour l'axe X (5 graduations)
  const tickCount = 5;
  const ticks = Array.from({ length: tickCount }, (_, i) => {
    const value = (maxValue / (tickCount - 1)) * i;
    return Math.round(value);
  });
  
  // Positions des ticks de l'axe X (basées sur le SVG: 105, 180.25, 255.5, 330.75, 406)
  const tickPositions = ticks.map((_, i) => {
    return chartAreaX + (i / (tickCount - 1)) * chartAreaWidth;
  });
  
  // Positions verticales des barres (basées sur le SVG: y=15.5 et y=120.5)
  const barPositions = data.map((_, index) => {
    return chartAreaY + barVerticalSpacing + (index * (barHeight + barVerticalSpacing));
  });
  
  // Positions des lignes horizontales de la grille (au centre de chaque barre)
  const horizontalGridLines = barPositions.map(y => y + barHeight / 2);

  return (
    <View style={[{ width, height: chartAreaY + chartAreaHeight + xAxisHeight }, style]}>
      {/* Conteneur SVG principal (recharts-surface) */}
      <Svg 
        style={{ 
          position: 'relative',
          width: width,
          height: chartAreaY + chartAreaHeight + xAxisHeight
        }}
        viewBox={`0 0 ${width} ${chartAreaY + chartAreaHeight + xAxisHeight}`}
      >
        {/* Defs avec ClipPath */}
        <Defs>
          <ClipPath id="recharts-clip">
            <Rect 
              x={chartAreaX} 
              y={chartAreaY} 
              width={chartAreaWidth} 
              height={chartAreaHeight} 
            />
          </ClipPath>
        </Defs>
        
        {/* Groupe recharts-cartesian-grid */}
        <G>
          {/* Groupe recharts-cartesian-grid-horizontal */}
          <G>
            {/* Lignes horizontales de la grille (stroke-dasharray="3 3", stroke="#ccc") */}
            {horizontalGridLines.map((yPosition, index) => {
              // Créer des segments pointillés manuellement
              const dashLength = 3;
              const gapLength = 3;
              const segments = [];
              let currentX = chartAreaX;
              while (currentX < chartAreaX + chartAreaWidth) {
                segments.push(
                  <Line
                    key={`h-${index}-seg-${segments.length}`}
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
            {/* Lignes aux bords (y=5 et y=215) */}
            {[chartAreaY, xAxisY].map((yPosition, index) => {
              const dashLength = 3;
              const gapLength = 3;
              const segments = [];
              let currentX = chartAreaX;
              while (currentX < chartAreaX + chartAreaWidth) {
                segments.push(
                  <Line
                    key={`h-edge-${index}-seg-${segments.length}`}
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
          
          {/* Groupe recharts-cartesian-grid-vertical */}
          <G>
            {/* Lignes verticales de la grille (alignées avec les ticks de l'axe X) */}
            {tickPositions.map((xPosition, i) => {
              // Créer des segments pointillés manuellement (stroke-dasharray="3 3")
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
        </G>
            
        {/* Groupe recharts-cartesian-axis recharts-xAxis (axe X) */}
        <G>
          {/* Ligne d'axe X (orientation="bottom") - ligne horizontale en bas */}
          <Line
            x1={chartAreaX}
            y1={xAxisY}
            x2={chartAreaX + chartAreaWidth}
            y2={xAxisY}
            stroke="#666"
            strokeWidth={1}
          />
          
          {/* Groupe recharts-cartesian-axis-ticks */}
          <G>
            {/* Ticks de l'axe X */}
            {ticks.map((tick, i) => {
              const xPosition = tickPositions[i];
              return (
                <G key={i}>
                  {/* Ligne de tick (petite marque verticale vers le bas) */}
                  <Line
                    x1={xPosition}
                    y1={xAxisY + 6}
                    x2={xPosition}
                    y2={xAxisY}
                    stroke="#666"
                    strokeWidth={1}
                  />
                </G>
              );
            })}
          </G>
        </G>
        
        {/* Groupe recharts-cartesian-axis recharts-yAxis (axe Y) */}
        <G>
          {/* Ligne d'axe Y (orientation="left") - ligne verticale à gauche */}
          <Line
            x1={chartAreaX}
            y1={chartAreaY}
            x2={chartAreaX}
            y2={xAxisY}
            stroke="#666"
            strokeWidth={1}
          />
          
          {/* Groupe recharts-cartesian-axis-ticks */}
          <G>
            {/* Ticks de l'axe Y (marques horizontales vers la gauche) */}
            {horizontalGridLines.map((yPosition, index) => {
              return (
                <G key={index}>
                  {/* Ligne de tick (petite marque horizontale vers la gauche) */}
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
        </G>
        
        {/* Groupe recharts-layer recharts-bar */}
        <G clipPath="url(#recharts-clip)">
          {/* Groupe recharts-bar-rectangles */}
          <G>
            {data.map((item, index) => {
              const value = item.nombre_clients || 0;
              const barLength = maxValue > 0 ? (value / maxValue) * chartAreaWidth : 0;
              const barY = barPositions[index];
              const barX = chartAreaX;
              
              // Créer un path avec coins arrondis à droite (radius="0,8,8,0")
              const radius = 8;
              const path = `M${barX},${barY}L${barX + barLength - radius},${barY}A${radius},${radius},0,0,1,${barX + barLength},${barY + radius}L${barX + barLength},${barY + barHeight - radius}A${radius},${radius},0,0,1,${barX + barLength - radius},${barY + barHeight}L${barX},${barY + barHeight}Z`;
              
              return (
                <G key={index}>
                  <Path
                    d={path}
                    fill={barColor}
                  />
                </G>
              );
            })}
          </G>
        </G>
      </Svg>
      
      {/* Labels Y - Niveau de risque (en dehors du SVG) */}
      <View style={{ 
        position: 'absolute', 
        left: 0, 
        top: chartAreaY, 
        width: yAxisLabelWidth, 
        height: chartAreaHeight 
      }}>
        {data.map((item, index) => {
          const yPosition = horizontalGridLines[index];
          return (
            <View 
              key={index}
              style={{ 
                position: 'absolute',
                top: yPosition - 6,
                width: '100%',
                height: 12,
                justifyContent: 'center',
                alignItems: 'flex-end',
                paddingRight: 8
              }}
            >
              <Text style={{ 
                fontSize: 8, 
                color: '#666', 
                textAlign: 'right'
              }}>
                {String(item.niveau_risque || '')}
              </Text>
            </View>
          );
        })}
      </View>
      
      {/* Labels X - Valeurs numériques (en dehors du SVG) */}
      <View style={{ 
        position: 'absolute', 
        left: chartAreaX, 
        top: xAxisY + 8, 
        width: chartAreaWidth, 
        height: xAxisHeight - 8 
      }}>
        {ticks.map((tick, i) => {
          const xPosition = tickPositions[i] - chartAreaX;
          return (
            <View 
              key={i}
              style={{
                position: 'absolute',
                left: xPosition,
                alignItems: 'center',
                transform: [{ translateX: -15 }]
              }}
            >
              <Text style={{ 
                fontSize: 8, 
                color: '#666',
                textAlign: 'center',
                minWidth: 30
              }}>
                {tick.toLocaleString('fr-FR')}
              </Text>
            </View>
          );
        })}
      </View>
    </View>
  );
}
