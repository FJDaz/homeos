# Formalisation UX HomeOS - Version Clarifiée

## ✅ **Décisions Prises**

### **Q1 - Génération des États : D+C ✅**
**Choix** : Option D (Background) + C (Lazy) combinées
- **Priorité 1** : Corps sélectionné généré immédiatement
- **Background** : Autres Corps générés en tâche de fond
- **Placeholder** : Skeleton screen pour Corps non-générés

### **Q2 - Navigation : Breadcrumb + Double-clic ✅**
- **Breadcrumb** en haut : `Corps > Organe > Atome` (cliquable)
- **Double-clic** sur élément → drill down
- **Double-clic** arrière-plan → remontée niveau supérieur

### **Q3 - Synchronisation État : Clarification ✅**
**Correction** : Les Corps n'apparaissent **pas dans la sidebar** mais dans le **row dédié** en haut (cf capture)

**Workflow de synchronisation :**
```
1. Rendu Frontend du Genome → Corps dans row haut
2. Drag Corps vers Main Area → Activation
3. Modification dans Main Area → Mise à jour après :
   - 3 secondes d'inactivité OU
   - Sortie du Corps (double-clic/breadcrumb) OU
   - Action manuelle "Sauvegarder"
4. Miniature dans row → mise à jour en conséquence
```

### **Q4 - Sélection Multiple : Limité ✅**
- **Corps** : Pas de sélection multiple (un seul Corps actif dans Main Area)
- **Organes/Atomes** : Possible si l'API Figma le permet
- **Actions batch** : Supprimer, dupliquer (seulement pour Organes/Atomes)

---

## 🎯 **Priorités Réajustées**

### **P0 (MVP - Implémenter immédiatement)**
1. **Three-pane layout** avec row Corps en haut
2. **Drag & drop** Corps → Main Area
3. **Double-clic navigation** hiérarchique
4. **Breadcrumb** navigation contextuelle
5. **Brainstorm phase** auto sur dimensions manquantes
6. **Skeleton screens** pour Corps non-générés

### **P1 (Valeur ajoutée rapide)**
1. **Historique visuel** avec timeline (backend DB à prévoir)
2. **Heatmap** d'utilisation des Corps
3. **Filtres** par état/complexité
4. **Background jobs** génération miniatures

### **P2 (Nice-to-have différé)**
1. **Suggestions contextuelles** (mode "nudge" seulement si nécessaire)
2. **Sélection multiple** Organes (si API Figma permet)
3. **Collaboration** (v2+ si demandé)

---

## 🔄 **Workflow Clarifié**

### **Étape 0 : Génération du Genome**
```
Sullivan analyse → Genome JSON → Rendu Frontend
                                     ↓
                  Row Corps en haut avec miniatures
                  (skeletons pour non-générés)
```

### **Étape 1 : Sélection & Drag**
```
[UTILISATEUR]
1. Voir row des Corps avec états : ⏳/✅/⚠️
2. Drag un Corps vers Main Area
3. Si dimensions définies → Placement immédiat
4. Si dimensions manquantes → Brainstorm auto
```

### **Étape 2 : Brainstorm Phase**
```
[DIMENSIONS MANQUANTES]
    ↓
[POPUP HOMEOS]
"Ce Corps nécessite des dimensions. Analyse du contexte :
- Type : Dashboard admin
- Usage : Desktop principal
- Recommandation : 1440×900
- Breakpoints : [375, 768, 1440]

✅ Appliquer ces dimensions
✏️ Personnaliser
❌ Ignorer (garder flexible)"
```

### **Étape 3 : Navigation Hiérarchique**
```
[MAIN AREA - Corps visible]
    ↓ double-clic sur Corps
[VUE ORGANES] (à l'intérieur du Corps)
    ↓ double-clic sur Organe  
[VUE ATOMES] (à l'intérieur de l'Organe)
    
[BREADCRUMB] : Corps > Header > BoutonPrincipal
    ↓ clic sur "Corps"
[RETOUR VUE CORPS]
```

### **Étape 4 : Synchronisation**
```
[MODIFICATION dans Main Area]
    ↓ (3s inactivité OU sortie élément)
[AUTO-SAVE] → Mise à jour :
1. Élément dans Main Area
2. Miniature dans row Corps
3. Backend persistence
```

---

## 🎨 **Éléments d'Interface Définitifs**

### **A. Row Corps (en haut)**
```
[MINIATURE CORPS 1] [✅ Dashboard] 3 Organes
[MINIATURE CORPS 2] [⏳ Profile] Génération...
[MINIATURE CORPS 3] [⚠️ Settings] Dimensions manquantes
```

### **B. Breadcrumb (sous le row)**
```
🏠 Dashboard > 🔤 Header > 🔘 BoutonPrincipal
```

### **C. Sidebar Outils Figma**
```
OUTILS FIGMA
├─ Sélection (V)
├─ Frame (F)
├─ Rectangle (R)
├─ Texte (T)
├─ Composant (C)
└─ Instance (I)
```

**Position** : Sous la hiérarchie d'accords

### **D. Hiérarchie Accordéon**
```
└─ Corps Actif (MAX LUM)
    ├─ Organe A (MIDDLE LUM)
    ├─ Organe B (MIDDLE LUM)
    └─ Organe C (MIDDLE LUM)
    
[autres Corps] (MIN LUM - collapsed)
```

---

## ⚠️ **Points d'Attention Techniques**

### **1. Génération Background**
- **Worker threads** pour générer les miniatures
- **Queue de priorité** : D'abord Corps visibles, puis autres
- **Cache** : Stocker miniatures générées (localStorage + backend)

### **2. Synchronisation État**
- **Debounce** 3s pour auto-save
- **Conflict resolution** : Dernier à sauver gagne
- **Undo/Redo stack** : Limité à 10 actions

### **3. Performance**
- **Virtual scrolling** pour hiérarchie longue
- **Lazy loading** des miniatures complexes
- **Web Workers** pour génération d'aperçus

---

## ❓ **Questions Restantes**

1. **API Figma** : L'API permet-elle les sélections multiples d'éléments ?
2. **Complexité des miniatures** : Quel niveau de détail dans les aperçus ?
3. **Export** : Formats d'export depuis Main Area (Figma, PNG, PDF) ?
4. **Collaboration temps réel** : À prévoir en v2 seulement ?

---

## 📊 **Succès UX à Mesurer**

### **Métriques Quantitatives**
- **Temps** pour placer premier Corps → première modification
- **Taux d'utilisation** Brainstorm phase
- **Précision** des suggestions de dimensions
- **Latence** génération miniatures

### **Métriques Qualitatives**
- **Intuitivité** double-clic navigation
- **Utilité** breadcrumb
- **Clarté** états (⏳/✅/⚠️)
- **Fluidité** drag & drop

---

**Résumé** : Interface centrée sur le **row de Corps** comme point d'entrée, navigation hiérarchique intuitive (double-clic + breadcrumb), et assistance IA contextuelle mais discrète (brainstorm seulement si nécessaire). Synchronisation intelligente avec auto-save différé pour éviter les pertes de données.