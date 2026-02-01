## 🎯 **HCI DE L'INTENT REFACTORING**
*Version détaillée - Sullivan Interface Design*

---

### **1. PRINCIPE FONDAMENTAL**

> "L'HCI de l'IR doit rendre visible l'invisible : montrer les écarts entre l'intention déclarée et l'implémentation réelle."

---

### **2. ARCHITECTURE VISUELLE**

#### **2.1. Layout à 3 Panels**
```
┌─────────────────────────────────────────────────────────┐
│                     HEADER (z-index: 10000)             │
│  [IR Progress] │ [Current Phase] │ [Validation Status]  │
├────────────────┬──────────────────┬─────────────────────┤
│                                                │        │
│                                                │        │
│        PANEL 1                    │   PANEL 3  │        │
│        INTENTIONS                  │   ACTIONS  │        │
│        (Manifeste)                 │   (Décisions)      │
│                                                │        │
│                                                │        │
├────────────────┼──────────────────┤            │        │
│                                                │        │
│        PANEL 2                    │            │        │
│        IMPLÉMENTATION             │            │        │
│        (Code existant)            │            │        │
│                                                │        │
└─────────────────────────────────────────────────────────┘
```

#### **2.2. Stratification Z-Index**
```css
.ir-overlay {
  z-index: 10000; /* Interface IR complète */
}

.ir-phase-indicator {
  z-index: 10001; /* Indicateur de phase flottant */
}

.ir-highlight {
  z-index: 9999; /* Surbrillance du code analysé */
}

.ir-tooltip {
  z-index: 10002; /* Info-bulles contextuelles */
}
```

---

### **3. PHASES VISUELLES DE L'IR**

#### **Phase 1 : Inventaire Fonctionnel**
```
┌─────────────────────────────────────────────────────┐
│ PHASE 1/7: INVENTORY                                │
├─────────────────────────────────────────────────────┤
│ 📊 142 features détectées                           │
│ ⚠️  23 features sans intention claire              │
│ ✅ 119 features mappées                             │
├─────────────────────────────────────────────────────┤
│ [Voir les features orphelines]                      │
│ [Analyser les dépendances]                          │
│ [Exporter l'inventaire]                             │
└─────────────────────────────────────────────────────┘

VISUALISATION: Nuage de points avec:
- Axe X: Couverture intention
- Axe Y: Complexité d'implémentation
- Taille: Nombre de dépendances
- Couleur: Statut (validé/orphelin/ambigu)
```

#### **Phase 2 : Mapping Intention ↔ Features**
```
┌─────────────────────────────────────────────────────┐
│ OBJECTIF: "Créer une interface utilisateur simple"  │
├─────────────────────────────────────────────────────┤
│ Features associées (8):                             │
│   ✅ F_045 - Page layout system                     │
│   ✅ F_078 - Responsive grid                        │
│   ⚠️  F_112 - Animation engine (sur-implémentation) │
│   ❌ F_156 - Dark mode toggle (manquant)            │
├─────────────────────────────────────────────────────┤
│ Couverture: 75%                                     │
│ Gaps identifiés: Accessibilité mobile              │
│ Redondances: 2 systèmes de grille                  │
└─────────────────────────────────────────────────────┘

VISUALISATION: Diagramme de Venn interactif
- Cercle gauche: Intentions du manifeste
- Cercle droit: Features implémentées
- Intersection: Features alignées
- Zones externes: Orphelins/manquants
```

#### **Phase 3 : Détection des Zones Floues**
```
┌─────────────────────────────────────────────────────┐
│ AMBIGUÏTÉ #7: Feature F_112 "Animation engine"      │
├─────────────────────────────────────────────────────┤
│ Problème: Aucune intention d'animation dans le      │
│          manifeste, mais 2,4k lignes de code.      │
│                                                    │
│ Hypothèse système: "L'utilisateur veut des UI      │
│                   animées pour un meilleur UX"     │
│                                                    │
│ Risque: Complexité accrue, maintenance difficile   │
│                                                    │
│ Options:                                           │
│   ◯ Garder (Core)    ◯ Réserve     ◯ Obsolète      │
│                                                    │
│ Commentaire: [__________________________]          │
└─────────────────────────────────────────────────────┘

VISUALISATION: Carte thermique du code
- Zones à forte complexité
- Dettes techniques identifiées
- Code mort en grisé
```

#### **Phase 4 : Explication Pédagogique**
```
┌─────────────────────────────────────────────────────┐
│ 🎓 EXPLICATION: Pourquoi F_045 existe?              │
├─────────────────────────────────────────────────────┤
│ Ce que ça fait: Système de layout basé sur CSS Grid │
│ Pourquoi: Le manifeste demande "UI simple et lisible"│
│ Cas d'usage: Pages admin, dashboards, formulaires   │
│ Si ignoré: Layouts incohérents, maintenance manuelle│
│                                                    │
│ 👁️ Aperçu visuel: [▶ Voir le composant]           │
│ 📊 Métriques: Performance 92%, Accessibilité 85%    │
│ 🏷️ Tags: core, layout, responsive, essential       │
└─────────────────────────────────────────────────────┘

VISUALISATION: Micro-preview du composant
- Rendu live miniaturisé
- Métriques en temps réel
- Tags interactifs
```

#### **Phase 5 : Dialogue de Décision**
```
┌─────────────────────────────────────────────────────┐
│ DECISION TIME: 23 features en attente              │
├─────────────────────────────────────────────────────┤
│ F_112: Animation engine                            │
│   ◉ Garder (Core)    ○ Réserve     ○ Obsolète      │
│   📝 Note: "Utile pour les transitions UI"         │
│                                                    │
│ F_156: Dark mode toggle                            │
│   ○ Garder    ◉ Réserve    ○ Obsolète              │
│   📝 Note: "Hors scope v1, mais intéressant"       │
│                                                    │
│ [Valider ce lot] [Tout mettre en réserve] [Ignorer]│
└─────────────────────────────────────────────────────┘

VISUALISATION: Tableau Kanban interactif
- Colonnes: À décider / Core / Support / Réserve / Obsolète
- Cartes draggables avec résumé
- Regroupement par catégorie
```

#### **Phase 6 : Compartimentation**
```
┌─────────────────────────────────────────────────────┐
│ 📦 COMPARTIMENTS FINAUX                             │
├─────────────────────────────────────────────────────┤
│ CORE (42 features)                                 │
│ • Authentification système                         │
│ • Générateur de code                               │
│ • Validateur Sullivan                              │
│                                                    │
│ SUPPORT (31 features)                              │
│ • Logging avancé                                   │
│ • Templates supplémentaires                        │
│                                                    │
│ RESERVE (19 features)                              │
│ • Dark mode (futur)                                │
│ • Export PDF (niche)                               │
│                                                    │
│ DEPRECATED (50 features)                           │
│ • Ancien système de routing                        │
│ • Compatibilité IE11                               │
└─────────────────────────────────────────────────────┘

VISUALISATION: Diagramme sunburst
- Centre: Core
- Anneau 1: Support
- Anneau 2: Reserve
- Anneau 3: Deprecated
- Interaction: Clic pour explorer
```

#### **Phase 7 : Gel du Génome**
```
┌─────────────────────────────────────────────────────┐
│ 🔐 GÉNOME v1 PRÊT                                  │
├─────────────────────────────────────────────────────┤
│ ✅ 100% des intentions couvertes                   │
│ ✅ Mapping validé par l'utilisateur                │
│ ✅ Compartiments définis                           │
│ ✅ Aucune ambiguïté non résolue                    │
│                                                    │
│ 📁 Artefacts générés:                              │
│   • genome_v1.json (signé)                        │
│   • intent_feature_map.csv                        │
│   • audit_report.md                               │
│                                                    │
│ [Télécharger le génome] [Visualiser le graphe]     │
│                                                    │
│ ⚠️ Après validation, l'IR sera verrouillé         │
└─────────────────────────────────────────────────────┘

VISUALISATION: Graphe de dépendances animé
- Nœuds: Features
- Arêtes: Dépendances
- Groupes: Compartiments (couleurs)
- Animation: "Gel" progressif
```

---

### **4. COMPOSANTS HCI SPÉCIFIQUES**

#### **4.1. Intent Card**
```svelte
<!-- components/IntentCard.svelte -->
<script>
  export let intent;
  export let coverage;
  export let features = [];
  
  let isExpanded = false;
</script>

<div class="intent-card {coverage}">
  <header on:click={() => isExpanded = !isExpanded}>
    <h3>{intent.title}</h3>
    <span class="coverage-badge">{coverage}%</span>
    <Icon name={isExpanded ? 'chevron-up' : 'chevron-down'} />
  </header>
  
  {#if isExpanded}
    <div class="intent-details">
      <p>{intent.description}</p>
      
      <div class="feature-list">
        {#each features as feature}
          <FeatureRow {feature} />
        {/each}
      </div>
      
      <div class="action-buttons">
        <Button>Ajouter une feature</Button>
        <Button variant="outline">Signaler un écart</Button>
      </div>
    </div>
  {/if}
</div>

<style>
  .intent-card {
    border: 2px solid;
    border-radius: 8px;
    margin: 1rem 0;
    cursor: pointer;
  }
  
  .intent-card.complete { border-color: var(--success); }
  .intent-card.partial { border-color: var(--warning); }
  .intent-card.none { border-color: var(--error); }
  
  header {
    display: flex;
    align-items: center;
    padding: 1rem;
    gap: 1rem;
  }
</style>
```

#### **4.2. Feature Matrix**
```svelte
<!-- components/FeatureMatrix.svelte -->
<script>
  export let features = [];
  export let onFeatureSelect;
  
  // Matrice: Intentions × Features
  let matrix = computeMatrix(features);
  
  function handleCellClick(intentId, featureId) {
    onFeatureSelect({ intentId, featureId });
  }
</script>

<div class="feature-matrix">
  <table>
    <thead>
      <tr>
        <th>Intentions →<br/>Features ↓</th>
        {#each Object.keys(matrix.intents) as intentId}
          <th>{intentId}</th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#each Object.keys(matrix.features) as featureId}
        <tr>
          <td class="feature-name">{featureId}</td>
          {#each Object.keys(matrix.intents) as intentId}
            <td 
              class="cell {matrix.cells[featureId][intentId].status}"
              on:click={() => handleCellClick(intentId, featureId)}
              title="{matrix.cells[featureId][intentId].description}"
            >
              {matrix.cells[featureId][intentId].icon}
            </td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
</div>
```

#### **4.3. Ambiguity Scanner**
```svelte
<!-- components/AmbiguityScanner.svelte -->
<script>
  export let codebase;
  export let onIssueFound;
  
  let scanProgress = 0;
  let issues = [];
  
  async function scan() {
    // Scanner le code pour:
    // 1. Variables mal nommées
    // 2. Fonctions trop longues
    // 3. Code dupliqué
    // 4. TODO/FIXME non résolus
    // 5. Complexité cyclomatique élevée
  }
  
  function fixIssue(issueId, suggestion) {
    // Appliquer une correction automatique
  }
</script>

<div class="scanner">
  <ProgressBar value={scanProgress} max={100} />
  
  {#if issues.length > 0}
    <div class="issues-list">
      {#each issues as issue}
        <div class="issue {issue.severity}">
          <h4>{issue.title}</h4>
          <p>{issue.description}</p>
          <code>{issue.codeSnippet}</code>
          
          <div class="suggestions">
            {#each issue.suggestions as suggestion}
              <button on:click={() => fixIssue(issue.id, suggestion)}>
                {suggestion}
              </button>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>
```

---

### **5. INTERACTIONS ET FEEDBACK**

#### **5.1. Drag & Drop des Features**
```
[F_112] ───┐
           ▼
┌─────────────────────┐
│       CORE          │
│ ┌─────────────────┐ │
│ │ F_045           │ │
│ │ F_078           │ │
│ └─────────────────┘ │
│                     │
│     RÉSERVE         │
│ ┌─────────────────┐ │
│ │ F_156           │ │
│ └─────────────────┘ │
└─────────────────────┘

Feedback visuel:
- Zone valide: Bordure verte
- Zone invalide: Bordure rouge + message
- Confirmation: Animation de "snap"
```

#### **5.2. Validation en Temps Réel**
```javascript
// Lors de la modification d'une décision
function updateFeatureStatus(featureId, newStatus) {
  // Validation immédiate
  const validation = validateDecision(featureId, newStatus);
  
  if (!validation.valid) {
    showToast({
      type: 'error',
      message: validation.error,
      action: 'Voir les conflits'
    });
    return;
  }
  
  // Mise à jour visuelle
  animateStatusChange(featureId, newStatus);
  
  // Recalcul des métriques
  updateMetrics();
}
```

#### **5.3. Undo/Redo Stack**
```
[Timeline de décisions]
│
├─ 10:15: Création inventaire
├─ 10:22: F_112 → Core
├─ 10:25: F_156 → Réserve
├─ 10:30: F_045 → Core (✓)
└─ ▶ Position actuelle

[Undo] [Redo] [Sauvegarder un checkpoint]
```

---

### **6. ÉTATS D'UTILISATEUR ET GUIDANCE**

#### **6.1. Premier Usage (Onboarding)**
```
┌─────────────────────────────────────────────────────┐
│ 👋 BIENVENUE DANS L'INTENT REFACTORING              │
├─────────────────────────────────────────────────────┤
│ Vous allez aligner votre code avec vos intentions.  │
│                                                     │
│ Étape 1: L'IA analyse votre code (auto)            │
│ Étape 2: Vous validez le mapping (manuel)          │
│ Étape 3: L'IA suggère des améliorations            │
│ Étape 4: Vous décidez quoi garder                  │
│                                                     │
│ ⏱️  Temps estimé: 15-30 minutes                    │
│                                                     │
│ [Commencer] [Voir un exemple]                      │
└─────────────────────────────────────────────────────┘
```

#### **6.2. Décision Difficile (Assistance)**
```
┌─────────────────────────────────────────────────────┐
│ 🤔 INCERTAIN SUR F_112 ?                           │
├─────────────────────────────────────────────────────┤
│ Sullivan suggère:                                  │
│                                                     │
│ • Score d'utilité: 65/100                          │
│ • Utilisation: 12% des utilisateurs                │
│ • Maintenance: Coûte 3h/semaine                    │
│                                                     │
│ Recommandation: Mettre en RÉSERVE                  │
│ Raison: Hors scope manifeste, coût élevé           │
│                                                     │
│ [Accepter la suggestion] [Ignorer] [Demander +]    │
└─────────────────────────────────────────────────────┘
```

#### **6.3. Validation Finale**
```
┌─────────────────────────────────────────────────────┐
│ ✅ PRÊT À GELER LE GÉNOME ?                         │
├─────────────────────────────────────────────────────┤
│ Vérifications:                                      │
│   ✓ Toutes les intentions couvertes                │
│   ✓ Aucune feature orpheline active                │
│   ✓ Compartiments équilibrés                       │
│   ✓ Consensus Sullivan/Utilisateur                 │
│                                                     │
│ Impact du gel:                                      │
│ • Code stabilisé pour la phase front               │
│ • Plus de modifications hors IR                    │
│ • Base solide pour le développement                │
│                                                     │
│ [Geler le génome] [Revoir une section]             │
└─────────────────────────────────────────────────────┘
```

---

### **7. ACCESSIBILITÉ ET ÉCOLOGIE**

#### **7.1. Accessibilité**
- **Navigation clavier** complète
- **Screen reader** supporté avec ARIA labels
- **Contraste** WCAG AA minimum
- **Taille de texte** ajustable
- **Mode daltonien** disponible

#### **7.2. Performance**
- **Temps de chargement** < 2s
- **Mémoire utilisée** < 100MB
- **Updates temps réel** via WebSockets
- **Cache intelligent** des analyses

#### **7.3. Écologie**
- **Dark mode par défaut** (économie énergétique)
- **Compression des données** (moindre bande passante)
- **Mise en veille** après inactivité
- **Choix écologique** suggéré (ex: "Cette feature consomme X énergie")

---

### **8. INTÉGRATION AVEC LE STUDIO**

#### **8.1. Position dans le Workflow**
```
STUDIO NAVIGATION:
┌───┐   ┌───┐   ┌───┐   ┌───┐   ┌───┐
│🧠 │ → │⚙️ │ → │🎯│ → │🎨│ → │🚀│
└───┘   └───┘   └───┘   └───┘   └───┘
Brain  Back   IR    Front  Deploy
storm  end          end
```

#### **8.2. Fenêtre IR dans le Studio**
```javascript
// Studio intégre l'IR comme overlay
<SullivanOverlay zIndex={10000}>
  <IntentRefactoringUI
    manifeste={currentManifeste}
    codebase={analyzedCodebase}
    onComplete={(genome) => {
      // Passe à la phase Frontend
      navigateToFrontendPhase(genome);
    }}
  />
</SullivanOverlay>
```

#### **8.3. État Persistant**
```json
{
  "ir_session": {
    "id": "ir_20260131_1030",
    "phase": "decision_dialogue",
    "progress": 65,
    "decisions_made": 42,
    "pending_decisions": 23,
    "last_saved": "2026-01-31T10:30:00Z",
    "autosave_enabled": true
  }
}
```

---

### **9. RÈGLES HCI ABSOLUES**

1. **Une décision à la fois** → Focus sur un seul écarte
2. **Feedback immédiat** → Toute action a une réponse visuelle
3. **Pas de perte de données** → Undo illimité, autosave fréquent
4. **Guidance progressive** → Aide contextuelle, pas de bombardment
5. **Transparence totale** → L'IA explique tous ses raisonnements
6. **Souveraineté humaine** → L'utilisateur a toujours le dernier mot
7. **Rapidité d'exécution** → Aucune attente > 3s sans feedback
8. **Consistance visuelle** → Mêmes patterns dans toutes les phases

---

## 🎨 **MAQUETTES VISUELLES**

### **Vue d'ensemble**
```
┌─────────────────────────────────────────────────────────┐
│ INTENT REFACTORING - Phase 3/7: Zones Floues           │
│ ┌─────────────────┐  ┌─────────────────┐               │
│ │📊 COUVERTURE    │  │🎯 INTENTIONS     │               │
│ │ • Complete 42%  │  │ • UI simple     │               │
│ │ • Partial 38%   │  │ • Rapide        │               │
│ │ • None    20%   │  │ • Accessible    │               │
│ └─────────────────┘  └─────────────────┘               │
│                                                        │
│ ┌──────────────────────────────────────────────────┐   │
│ │🚨 AMBIGUÏTÉS (5)                                │   │
│ │ 1. F_112: Animation engine - 2,4k LOC           │   │
│ │ 2. F_156: Dark mode - Aucune intention          │   │
│ │ 3. F_089: Logging complexe - Redondant          │   │
│ │                                                │   │
│ │ [Explorer F_112] [Corriger auto] [Ignorer]     │   │
│ └──────────────────────────────────────────────────┘   │
│                                                        │
│ Progress: ████████▊ 65%        [Phase suivante →]     │
└─────────────────────────────────────────────────────────┘
```

### **Vue détaillée d'une ambiguïté**
```
┌─────────────────────────────────────────────────────────┐
│ 🔍 F_112: ANIMATION ENGINE                             │
├─────────────────────────────────────────────────────────┤
│ 📍 Fichiers: /src/animation/* (12 fichiers)           │
│ 📏 Taille: 2,418 lignes                                │
│ 🔗 Dépendances: UI components (8), Router (1)         │
│ 🏷️ Origin: Opportunisme (ajouté par dev)             │
│                                                        │
│ 🎯 INTENTIONS MANQUANTES:                             │
│ • Aucune mention d'animation dans le manifeste        │
│ • "UI simple" pourrait exclure animations complexes   │
│                                                        │
│ 🤖 HYPOTHÈSE SYSTÈME:                                 │
│ • "Les utilisateurs préfèrent les transitions douces" │
│                                                        │
│ ⚠️ RISQUE:                                            │
│ • Complexité accrue (score: 8/10)                     │
│ • Maintenance difficile (score: 7/10)                 │
│ • Performance impact (score: 5/10)                    │
│                                                        │
│ 💡 SUGGESTIONS SULLIVAN:                              │
│ 1. Mettre en RÉSERVE (70% de confiance)              │
│ 2. Simplifier à animations basiques (25%)            │
│ 3. Supprimer (5%)                                    │
│                                                        │
│ [Mettre en réserve] [Simplifier] [Garder tel quel]    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 **IMPLÉMENTATION TECHNIQUE**

### **Structure des composants**
```
sullivan/ir_interface/
├── components/
│   ├── PhaseIndicator.svelte
│   ├── IntentMatrix.svelte
│   ├── AmbiguityScanner.svelte
│   ├── DecisionPanel.svelte
│   └── GenomeVisualizer.svelte
├── stores/
│   ├── irState.store.js
│   ├── decisions.store.js
│   └── validation.store.js
├── services/
│   ├── aetherflowIR.service.js
│   ├── realtimeUpdates.service.js
│   └── persistence.service.js
└── views/
    ├── InventoryPhase.svelte
    ├── MappingPhase.svelte
    ├── AmbiguityPhase.svelte
    └── ValidationPhase.svelte
```

### **Communication avec Aetherflow**
```javascript
// WebSocket pour les updates temps réel
const irSocket = new WebSocket('ws://localhost:8000/ir-updates');

irSocket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'inventory_update':
      irStore.updateInventory(data.payload);
      break;
    case 'ambiguity_found':
      showAmbiguityNotification(data.payload);
      break;
    case 'decision_validated':
      updateDecisionStatus(data.payload);
      break;
  }
};
```

---

## ✅ **CHECKLIST DE VALIDATION HCI**

- [ ] **Phase 1** : L'inventaire est compréhensible en < 30s
- [ ] **Phase 2** : Le mapping montre clairement les écarts
- [ ] **Phase 3** : Les ambiguïtés sont expliquées simplement
- [ ] **Phase 4** : Les explications sont pédagogiques (pas techniques)
- [ ] **Phase 5** : Les décisions sont faciles à prendre
- [ ] **Phase 6** : La compartimentation est visuellement claire
- [ ] **Phase 7** : Le gel est un acte conscient et réversible
- [ ] **Global** : Navigation fluide entre les phases
- [ ] **Global** : Pas de perte de données (autosave)
- [ ] **Global** : Accessibilité WCAG AA respectée

---

**Cette HCI de l'Intent Refactoring répond-elle à vos attentes ?** Faut-il ajuster certains aspects visuels ou d'interaction ?