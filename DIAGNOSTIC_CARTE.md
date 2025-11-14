# 🗺️ DIAGNOSTIC - Carte ne s'affiche pas

## Modifications effectuées

### ✅ 1. Import CSS Leaflet dans main.jsx
```javascript
import 'leaflet/dist/leaflet.css'
```

### ✅ 2. Styles CSS personnalisés dans index.css
```css
.leaflet-container {
  width: 100%;
  height: 100%;
  border-radius: 0.5rem;
  z-index: 0;
}
```

### ✅ 3. Page de test créée
**URL:** http://localhost:5174/test-map

Cette page teste Leaflet de manière isolée avec une carte simple.

## 🔍 Étapes de diagnostic

### ÉTAPE 1: Tester la page de test
1. Ouvrez: **http://localhost:5174/test-map**
2. Vous devriez voir une carte avec un marker rouge sur Abidjan
3. **SI LA CARTE S'AFFICHE:**
   - ✅ Leaflet fonctionne
   - ❌ Le problème est dans ZonesMap ou Occupation.jsx
4. **SI LA CARTE NE S'AFFICHE PAS:**
   - ❌ Problème avec Leaflet ou les dépendances
   - Vérifiez la console pour les erreurs

### ÉTAPE 2: Vérifier la console du navigateur
1. Ouvrez F12 > Console
2. Vous devriez voir ces messages:
```
🗺️ Fetching zones data...
📡 API Response: {success: true, zones: Array(13)}
✅ Valid zones: 13/13
📍 First zone: {...}
```

3. **Si vous voyez ces messages:**
   - ✅ L'API fonctionne
   - ✅ Les données sont chargées

4. **Si vous voyez des erreurs:**
   - Notez l'erreur exacte
   - Cherchez des erreurs rouges

### ÉTAPE 3: Vérifier le mode d'affichage
1. Allez sur: **http://localhost:5174/occupation**
2. Cherchez les boutons "Tableau" et "Carte"
3. Cliquez sur "Carte"
4. **Le bouton "Carte" doit devenir bleu**

### ÉTAPE 4: Inspecter le DOM
1. F12 > Elements (ou Inspecteur)
2. Cherchez `.leaflet-container`
3. **Si trouvé:**
   - Vérifiez `style="height: 700px"`
   - Vérifiez que height n'est pas 0px
4. **Si non trouvé:**
   - La carte ne se render pas
   - Vérifiez viewMode dans React DevTools

### ÉTAPE 5: React DevTools
1. F12 > React (onglet React DevTools)
2. Cherchez le composant `Occupation`
3. Vérifiez la prop `viewMode`
4. **Doit être:**
   - `viewMode: "map"` quand vous cliquez sur Carte
   - `viewMode: "table"` quand vous cliquez sur Tableau

### ÉTAPE 6: Network (Réseau)
1. F12 > Network
2. Filtrez par "tile" ou "openstreetmap"
3. **Vous devriez voir:**
   - Plusieurs requêtes vers openstreetmap.org
   - Status 200 pour les images des tiles
4. **Si aucune requête:**
   - La carte ne se charge pas du tout

## 🛠️ Solutions selon le problème

### Problème A: Carte blanche/vide avec conteneur
**Symptôme:** Le div `.leaflet-container` existe mais la carte est vide

**Solution:**
```bash
# Redémarrer le serveur
Ctrl+C dans le terminal
cd bi_app/frontend
npm run dev
```

### Problème B: Aucun conteneur .leaflet-container
**Symptôme:** Pas de div `.leaflet-container` dans le DOM

**Cause possible:** viewMode ne change pas à "map"

**Solution:**
1. Vérifiez que vous cliquez bien sur le bouton "Carte"
2. Vérifiez dans React DevTools si `viewMode` change

### Problème C: Erreur "L is not defined"
**Symptôme:** Erreur dans la console

**Solution:**
```bash
# Réinstaller leaflet
cd bi_app/frontend
npm uninstall leaflet react-leaflet
npm install leaflet react-leaflet@4.2.1 --legacy-peer-deps
npm run dev
```

### Problème D: Tiles ne se chargent pas
**Symptôme:** Carte grise, pas d'images

**Cause:** Problème de connexion ou CORS

**Solution:**
- Vérifiez votre connexion internet
- Les tiles OpenStreetMap sont en HTTPS

## 📋 Checklist rapide

```
[ ] Page /test-map affiche une carte ✅
[ ] Console affiche "🗺️ Fetching zones data..." ✅
[ ] Console affiche "✅ Valid zones: 13/13" ✅
[ ] Bouton "Carte" cliquable ✅
[ ] Bouton "Carte" devient bleu au clic ❓
[ ] .leaflet-container existe dans DOM ❓
[ ] .leaflet-container a height: 700px ❓
[ ] Tiles (images) se chargent dans Network ❓
[ ] viewMode = "map" dans React DevTools ❓
```

## 🚨 Si rien ne fonctionne

Exécutez dans la console du navigateur:
```javascript
// Copier-coller dans la console
console.log('Leaflet:', typeof L !== 'undefined');
console.log('Container:', document.querySelector('.leaflet-container'));
console.log('Tiles:', document.querySelectorAll('.leaflet-tile').length);
```

Envoyez-moi le résultat !

## 📞 Informations à fournir

Si le problème persiste, j'ai besoin de:
1. ✅ ou ❌ pour la page /test-map
2. Capture d'écran de la console (F12)
3. Capture d'écran de l'onglet Network
4. Capture d'écran de React DevTools (composant Occupation)
5. Le résultat de la commande console ci-dessus
