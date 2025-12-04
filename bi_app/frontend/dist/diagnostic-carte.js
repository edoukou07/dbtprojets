console.log('%c=== DIAGNOSTIC CARTE ===', 'color: blue; font-size: 16px; font-weight: bold');

// 1. Vérifier que Leaflet est chargé
console.log('1. Leaflet chargé:', typeof window.L !== 'undefined' ? '✅ OUI' : '❌ NON');
if (typeof window.L !== 'undefined') {
  console.log('   Version Leaflet:', window.L.version);
}

// 2. Vérifier le CSS Leaflet
const leafletCSS = Array.from(document.styleSheets).some(sheet => {
  try {
    return sheet.href && sheet.href.includes('leaflet');
  } catch(e) {
    return false;
  }
});
console.log('2. CSS Leaflet chargé:', leafletCSS ? '✅ OUI' : '❌ NON');

// 3. Vérifier si le conteneur de carte existe
setTimeout(() => {
  const mapContainer = document.querySelector('.leaflet-container');
  console.log('3. Conteneur carte trouvé:', mapContainer ? '✅ OUI' : '❌ NON');
  
  if (mapContainer) {
    const styles = window.getComputedStyle(mapContainer);
    console.log('   Hauteur:', styles.height);
    console.log('   Largeur:', styles.width);
    console.log('   Display:', styles.display);
    console.log('   Position:', styles.position);
  }
  
  // 4. Vérifier le nombre de tiles chargées
  const tiles = document.querySelectorAll('.leaflet-tile');
  console.log('4. Tiles de carte:', tiles.length, tiles.length > 0 ? '✅' : '⚠️');
  
  // 5. Vérifier les erreurs réseau
  console.log('5. Ouvrez l\'onglet Network pour voir si les tiles se chargent');
  
  // 6. Vérifier React DevTools
  console.log('6. Vérifiez dans React DevTools:');
  console.log('   - Composant Occupation > viewMode');
  console.log('   - Composant ZonesMap > zones.length');
  
}, 2000);

// Helper: Forcer le viewMode à 'map'
window.forceMapView = () => {
  console.log('%cForçage du mode carte...', 'color: orange; font-weight: bold');
  console.log('Essayez de cliquer sur le bouton "Carte" dans l\'interface');
};

console.log('%cPour forcer le mode carte, tapez: forceMapView()', 'color: green');
