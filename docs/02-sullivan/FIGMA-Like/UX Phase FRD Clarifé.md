# Synthèse UX Finale - HomeOS Product Builder

## 🎯 **Vision Clarifiée**
Interface de construction visuelle **Vanilla JS + Canvas** pour génération et édition de Corps (pages) basée sur le Genome Sullivan, avec navigation hiérarchique intuitive et assistance IA contextuelle minimale.

---

## 🔄 **Workflow Complet - Depuis la Validation**

### **Étape 0 : Validation Genome ✅**
```
[Clic "Valider"] → Transition CSS scroll douce → Affichage Genome
```

### **Étape 1 : Présentation du Row Corps (en haut)**
```
ROW CORPS (sans sidebar)
├─ [🎨 Dashboard] ✅ 3 Organes • 1440×900
├─ [🎨 Profile] ⏳ Génération en cours...
└─ [🎨 Settings] ⚠️ Dimensions manquantes
```

**Génération miniatures** :
- **Corps sélectionné** : Génération immédiate
- **Autres Corps** : Background jobs
- **Non-générés** : Skeleton screens

### **Étape 2 : Drag & Drop vers Main Area**
```
[Utilisateur drag Corps] → [Drop dans Canvas Fabric.js]
    ↓
[Si dimensions] → Placement avec taille définie
[Sinon] → Brainstorm Phase auto
```

### **Étape 3 : Brainstorm Phase (dimensions manquantes)**
```
POPUP HOMEOS (discrète) :
"Dimensions recommandées pour ce dashboard :
📱 Mobile: 375px
📟 Tablet: 768px  
🖥️ Desktop: 1440px

[✅ Appliquer]  [✏️ Personnaliser]  [❌ Flexbox auto]"
```

### **Étape 4 : Navigation Hiérarchique**
```
MAIN AREA → Double-clic sur Corps → Vue Organes
BREADCRUMB : Dashboard > Header > Button (cliquable)
Double-clic arrière-plan → Remontée niveau supérieur
```

### **Étape 5 : Synchronisation & Sauvegarde**
```
Modification dans Canvas → Auto-save après :
- 3 secondes inactivité OU
- Sortie du Corps (double-clic/breadcrumb) OU  
- Clic "Sauvegarder"
```

---

## 🛠️ **Stack Technique Simplifiée**

### **Outil** | **Pourquoi**
--- | ---
**Fabric.js CDN** | Canvas manipulable, zéro build, léger
**Vanilla JS** | Pas de framework, contrôle total
**CSS Grid/Flex** | Layout responsive simple
**localStorage** | Persistence offline immédiate
**Service Worker** | Background jobs génération miniatures
**IndexedDB** | Historique visuel + snapshots

---

## 🏗️ **Architecture d'Interface Finale**

```
┌─────────────────────────────────────────────────┐
│ ROW CORPS (miniatures avec états)               │
├─────────────────────────────────────────────────┤
│ Breadcrumb: Dashboard > Header > Button         │
├───────┬───────────────────────────────┬─────────┤
│       │                               │         │
│HIÉRAR-│     CANVAS FABRIC.JS          │ OUTILS  │
│CHIE   │     (Main Work Area)          │ FIGMA   │
│Accor- │                               │ Sélection│
│déon   │                               │ Frame   │
│       │                               │ Rectangle│
│       │                               │ Texte   │
│       │                               │ Composant│
└───────┴───────────────────────────────┴─────────┘
```

**Points clés :**
1. **Pas de Corps dans sidebar** → Uniquement dans row haut
2. **Sidebar** = Hiérarchie accordéon + Outils Figma
3. **Main Area** = Canvas Fabric.js pur

---

## 🎯 **Priorités d'Implémentation Révisées**

### **P0 (MVP Immédiat)**
1. **Transition validation** → scroll douce vers Genome
2. **Row Corps** avec miniatures + états (✅⏳⚠️)
3. **Canvas Fabric.js** pour Main Area
4. **Drag & drop** Corps → Canvas
5. **Brainstorm phase** auto sur dimensions manquantes
6. **Double-clic navigation** + Breadcrumb

### **P1 (Valeur Ajoutée)**
1. **Background jobs** génération miniatures (Service Worker)
2. **Auto-save** avec debounce 3s
3. **Historique visuel** (IndexedDB + timeline)
4. **Heatmap** utilisation Corps

### **P2 (Différé)**
1. **Sélection multiple Organes** (si API Figma permet)
2. **Suggestions nudge** (très discrètes)
3. **Collaboration** (v2+ si demandé)
4. **Filtres avancés**

---

## ⚙️ **Détails Techniques Critiques**

### **1. Génération Miniatures**
```javascript
// Service Worker pour background generation
serviceWorker.register('generate-preview', (corps) => {
  const canvas = document.createElement('canvas');
  // Génération miniature
  return canvas.toDataURL();
});
```

### **2. Persistence**
```javascript
// localStorage pour état courant
localStorage.setItem('homeos-current-project', JSON.stringify(project));

// IndexedDB pour historique
const db = indexedDB.open('homeos-history');
```

### **3. Synchronisation**
```javascript
// Debounce auto-save
let saveTimeout;
canvas.on('object:modified', () => {
  clearTimeout(saveTimeout);
  saveTimeout = setTimeout(saveChanges, 3000);
});
```

---

## 🎨 **États Visuels Clairs**

### **Miniature Corps :**
- **✅ Prêt** : Aperçu + métriques
- **⏳ Génération** : Spinner + "Génération..."
- **⚠️ Problème** : Icône alerte + message court

### **Breadcrumb :**
```
🏠 Dashboard (cliquable) > 🔤 Header (cliquable) > 🔘 Button
```

### **Canvas États :**
- **Corps placé** : Bordures bleues
- **Édition active** : Surbrillance jaune
- **Problème** : Bordures rouges clignotantes

---

## ❓ **Questions Techniques Restantes**

1. **Performance Canvas** : Combien d'éléments max dans Fabric.js avant lag ?
2. **Export Formats** : PNG/PDF depuis Canvas ?
3. **Mobile** : Touch gestures pour drag & drop ?
4. **Undo/Redo** : Stack dans IndexedDB ou mémoire ?

---

## 📊 **Mesures de Succès**

### **À Tester Utilisateurs :**
- Temps pour placer premier Corps → première modification
- Taux d'acceptation suggestions dimensions
- Intuitivité double-clic navigation
- Fluidité drag & drop

### **Performances :**
- Latence génération miniature < 2s
- Temps chargement Canvas < 1s
- Auto-save < 100ms

---

**Résumé Final** : Interface **Canvas-based** légère avec row de Corps comme point d'entrée, navigation hiérarchique intuitive (double-clic + breadcrumb), assistance IA discrète seulement quand nécessaire, et persistence offline immédiate. Stack Vanilla JS pour contrôle total et rapidité.