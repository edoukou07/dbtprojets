# Guide de Débogage - Carte Géographique

## Problème
La carte ne s'affiche pas dans la page Occupation

## Checklist de Vérification

### 1. Vérifier que le serveur frontend est démarré
✅ URL: http://localhost:5174/
✅ Statut: En cours d'exécution

### 2. Vérifier que l'API backend fonctionne
✅ URL: http://127.0.0.1:8000/api/zones/map/
✅ Données: 13 zones avec polygons
✅ Toutes les zones ont des coordonnées (latitude/longitude)

### 3. Packages installés
✅ leaflet (installé)
✅ react-leaflet@4.2.1 (compatible React 18)

### 4. Ouvrir la console du navigateur

**Étapes:**
1. Ouvrir http://localhost:5174/ dans le navigateur
2. Aller sur la page "Occupation"
3. Cliquer sur le bouton "Carte" (à côté de "Tableau")
4. Ouvrir la console développeur (F12)
5. Vérifier les messages console:

**Messages attendus:**
```
🗺️ Fetching zones data...
📡 API Response: {success: true, zones: Array(13)}
✅ Valid zones: 13/13
📍 First zone: {id: 6, nom: "BOUAKE", ...}
🔄 Converted coords: {original: 8, converted: 8}
```

### 5. Vérifier les erreurs possibles

**Erreur 1: Leaflet CSS non chargé**
- Symptôme: La carte est blanche ou mal affichée
- Solution: Le CSS Leaflet est importé dans `index.css`

**Erreur 2: CORS**
- Symptôme: Erreur "CORS policy" dans la console
- Solution: Vérifier que Django CORS est configuré

**Erreur 3: Données non chargées**
- Symptôme: Message "Chargement de la carte..." qui ne disparaît pas
- Solution: Vérifier les logs console et l'API

**Erreur 4: MapContainer ne s'affiche pas**
- Symptôme: La carte a une hauteur de 0px
- Solution: Vérifier le style `height` du MapContainer

### 6. Vérifier le DOM

**Dans les DevTools:**
1. Onglet "Elements" ou "Inspecteur"
2. Chercher `.leaflet-container`
3. Vérifier que l'élément existe et a une hauteur > 0

**Classe à chercher:**
```html
<div class="leaflet-container leaflet-touch ... z-0" style="height: 700px; width: 100%;">
```

### 7. Tester directement le composant

**URL de test:**
http://localhost:5174/#occupation

**Actions:**
1. Cliquer sur "Occupation" dans le menu
2. Cliquer sur le bouton "Carte" (icône Map)
3. La carte devrait apparaître

### 8. Vérifier les styles

**Dans la console développeur:**
```javascript
// Vérifier que Leaflet est chargé
console.log(window.L);

// Vérifier les styles
const mapElement = document.querySelector('.leaflet-container');
console.log('Map element:', mapElement);
console.log('Map height:', mapElement?.style.height);
console.log('Map display:', getComputedStyle(mapElement)?.display);
```

### 9. Si la carte est toujours invisible

**Vérifier le state `viewMode`:**
```javascript
// Dans la console React DevTools
// Chercher le composant Occupation
// Vérifier la valeur de viewMode (doit être 'map')
```

**Forcer l'affichage:**
```javascript
// Temporairement dans Occupation.jsx
const [viewMode, setViewMode] = useState('map') // Changer 'table' en 'map'
```

### 10. Logs de débogage ajoutés

Le composant ZonesMap affiche maintenant:
- 🗺️ Quand il commence à charger les données
- 📡 La réponse de l'API
- ✅ Le nombre de zones valides
- 📍 La première zone chargée
- 🔄 Les coordonnées converties pour chaque zone
- ⚠️ Les coordonnées invalides

## Solution Rapide

Si rien ne fonctionne, essayez:

```bash
# 1. Arrêter le serveur frontend (Ctrl+C)
# 2. Nettoyer le cache
cd bi_app/frontend
npm run build
rm -rf node_modules/.vite

# 3. Redémarrer
npm run dev
```

## Contact

Si le problème persiste:
1. Copier tous les logs de la console
2. Copier tous les messages d'erreur
3. Prendre une capture d'écran de la page
4. Noter les étapes exactes pour reproduire le problème
