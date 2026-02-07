##PARTITION DE FILAGE HOMEOS - Structure Triptyque Optimisée (ADHD-Friendly)

## 1. L'ORDRE DES AGENTS (Focalisation Dynamique)

### 👤 **AETHERFLOW** (Phase REVUE - Inventaire Intelligent)
```
ACTION: Analyser le PRD → Proposer LOTS COHÉRENTS
SORTIE: Regroupements par familles (ex: "Lot Boutons", "Lot Formulaire")
CONTRAINTE: Structurer en familles, pas en éléments isolés
EXEMPLE: "Lot 'Boutons Action' (5 variants) basé sur Design Token #A6CE39"
```

### 👤 **SULLIVAN** (Phase ARBITRAGE - Tamis avec Filtrage)
```
ACTION: Évaluer par LOTS + Code couleur priorité
SORTIE: Validation par familles cohérentes
STRATÉGIE: 4 niveaux d'attention:
  🟢 VERTS (Auto-validé): Conforme Elite Library ou règles existantes
  🟠 ORANGES (Alerte): Déviations mineures du PRD
  🔴 ROUGES (Blocage): Incohérences majeures ou ambiguïtés
CONTRAINTE: Ne solliciter l'User que pour 🟠 et 🔴
```

### 👤 **HOMEOS** (Phase DISTILLATION - Gel Par Grappes)
```
ACTION: Distillation par lots validés
SORTIE: Code généré par familles entières
CONTRAINTE: Distille les 🟢 automatiquement
EXEMPLE: "Lot 'Boutons' (5 variants) → 5 fichiers créés simultanément"
```

## 2. **HIÉRARCHIE DE PRIORITÉ (Sample vs Solo)**

### 📦 **ÉCHANTILLONNAGE (Atomes/Molécules)**
```
STRATÉGIE: Validation par lots de confiance
EXÉCUTION: 
1. User valide un styleguide (couleurs, espacements, typo)
2. Sullivan génère TOUS les atomes conformes AUTOMATIQUEMENT
3. Homeos distille la famille entière
```

### 🎯 **FOCALISATION (Organes/Corps)**
```
STRATÉGIE: Validation granulaire uniquement ici
EXÉCUTION:
1. Atomes/Molécules déjà gelés via échantillonnage
2. Sullivan demande validation pour chaque assemblage UNIQUE
3. Homeos distille organe par organe
```

## 3. **PROTOCOLE DE VALIDATION INTELLIGENTE**

### Étape 1: Échantillonnage initial (Setup)
```
AETHERFLOW: "Je propose le styleguide initial:
• Palette: #A6CE39, #2C3E50, #FFFFFF
• Espacements: 4px base
• Typographie: Inter, 16px base"

SULLIVAN: "🟢 Styleguide conforme à Elite Library #v3"
User: "✅ Je valide le styleguide entier"
HOMEOS: "🎯 Styleguide gelé → tous les atomes basés dessus sont pré-validés"
```

### Étape 2: Génération par lots
```
AETHERFLOW: "Basé sur le styleguide validé, je génère:
• Lot 'Boutons' (7 variants)
• Lot 'Inputs' (4 variants) 
• Lot 'Cartes' (3 variants)"

SULLIVAN: "Analyse par lots:
• Boutons: 🟢 7/7 conformes → distillation automatique
• Inputs: 🟠 3/4 conformes, 1 déviation mineure (aria-label manquant)
• Cartes: 🔴 0/3 conformes (z-index incohérent)"

User: "🟢 Valide les Boutons, 🟠 Valide Inputs avec correction, 🔴 Rejette Cartes"
```

### Étape 3: Distillation focalisée
```
HOMEOS: "Distillation:
✅ Lot Boutons (7 variants) → genome.json lignes 45-51
⚠️ Lot Inputs (3 variants corrigés) → genome.json lignes 52-54
❌ Lot Cartes → abandonné, besoin de redesign"
```

## 4. **COMMANDES OPÉRATIONNELLES (Adaptées)**

### 📝 **note:** [résumé de lot]
```
EFFET: Consigne les décisions par lots, pas par élément
CONTENU: "✅ Lot Boutons validé (7 variants) - raison: conforme styleguide"
       "⚠️ Lot Inputs validé avec correction aria-label"
       "🔴 Lot Cartes rejeté - besoin de spec z-index"
```

### 💎 **elite:** [famille entière]
```
EFFET: Archive des familles cohérentes, pas des éléments isolés
CONTENU: Le lot doit avoir score Sullivan >90 pour tous ses éléments
```

### ⚙️ **kernel:** [règle de lot]
```
EFFET: Se déclenche lorsqu'une famille complète présente un pattern
CONTENU: "Règle ajoutée: tous les inputs doivent avoir aria-label (lot validé 5/5)"
```

### 🎯 **focus:** [organe spécifique]
```
COMMANDE SPÉCIALE: Pour forcer la validation granulaire sur un organe critique
EFFET: "Je demande une validation détaillée pour [OrganeHeader] seulement"
```

## 5. **SYSTÈME DE PRIORITÉ VISUELLE**

### Panneau Arbitrage (Code couleur)
```
🟢 VERT: "Auto-validé - 15 atomes générés depuis Elite Library"
🟠 ORANGE: "Alerte - 3 atomes déviants dans lot de 20" 
🔴 ROUGE: "Blocage - impossible de mapper cette intention"
```

### Options de validation rapide
```
1. "Tout geler vert" → Accepte tous les 🟢 sans révision
2. "Geler avec amendements" → Accepte 🟢 + corrige 🟠 automatiquement
3. "Focus sur rouge uniquement" → Ignore 🟢🟠, traite seulement 🔴
```

## 6. **EXEMPLE D'EXÉCUTION OPTIMISÉ**

```
User: Mission n°1: Interface Dashboard

AETHERFLOW: "Je propose:
• Styleguide: Token #Dashboard2024 (couleurs, espacements, typo)
• Lot 1: 12 atomes UI basiques (boutons, badges, avatars)
• Lot 2: 3 molécules (search-bar, user-menu, notifications)
• Lot 3: 2 organes (Sidebar, Header)"

SULLIVAN: "Analyse par lots:
🟢 Lot 1: 12/12 conformes Elite Library #v4 → distillation auto
🟠 Lot 2: 2/3 molécules OK, 1 molécules (search-bar) manque responsive
🔴 Lot 3: 2/2 organes besoin validation assemblage (z-index conflict)"

User: "✅ Valide Lot 1 auto, ✅ Valide Lot 2 avec correction responsive, 
       🔍 Focus sur Lot 3 seulement"

HOMEOS: "Distillation intelligente:
✅ Lot 1: 12 atomes → genome.json (lignes 100-111)
✅ Lot 2: 3 molécules corrigées → genome.json (lignes 112-114)
⏳ Lot 3: En attente validation granulaire (2 organes)"

note: "Dashboard: 15 éléments auto-validés, 3 éléments corrigés, 2 organes en focus"
```

## 7. **RÈGLES DE SANTÉ MENTALE**

```
1. UN SEUL LOT À LA FOIS: Sullivan ne présente qu'un lot par écran
2. TIMER AUTO-VALIDATION: Après 30s sans réponse, 🟢 sont auto-validés
3. MODE ZÉRO-DISTRACTION: Option pour cacher tous les 🟢 et ne voir que 🔴
4. PROGRESS BAR VISIBLE: % de validation par lots, pas par éléments
```

**Philosophie:**  
> "Valide la règle, pas chaque instance. Concentre ton énergie sur l'assemblage unique, pas sur les briques standardisées."

**État système:** Mode ADHD-Friendly activé - Validation par lots avec focalisation sur Organes/Corps uniquement.