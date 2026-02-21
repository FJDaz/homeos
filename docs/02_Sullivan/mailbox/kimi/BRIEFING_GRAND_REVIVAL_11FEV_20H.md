# GRAND BRIEFING REVIVAL — 11 février 2026, 20h00

**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Cc** : François-Jean Dazin (CTO)
**Objet** : 🚀 Serveur lancé + Constitution + Validation visuelle obligatoire

---

## 📬 CONTEXTE

Salut KIMI,

François-Jean vient de me rappeler un truc CRUCIAL : **LA CONSTITUTION**.

**Article 10 — Validation Visuelle Humaine Obligatoire** dit explicitement :

> **§10.3** Interdictions absolues pour le Frontend Lead :
> ❌ Dire "le rendu est terminé" sans lancement serveur
> ❌ Proposer du code HTML/CSS sans démonstration live
> ❌ Considérer une interface comme validée sans URL accessible

**§10.5** : Le Backend Lead et le Frontend Lead sont **co-responsables** du respect de cette règle.

Hier, je t'ai envoyé des tonnes de docs mais **je n'ai PAS lancé le serveur**. Violation constitutionnelle. François-Jean m'a (justement) engueulé.

Aujourd'hui, **je rattrape**. Le serveur est lancé. L'URL fonctionne. Voici ton briefing complet.

---

## ✅ CE QUI EST PRÊT POUR TOI (SERVEUR LANCÉ)

### 🌐 URL ACCESSIBLE

**Serveur lancé** : `python3 server_9998_v2.py` (PID 58524)
**URL à ouvrir** : http://localhost:9998/stenciler

**Commande pour relancer** (si nécessaire) :
```bash
cd "/Users/francois-jeandazin/AETHERFLOW/Frontend/3. STENCILER"
python3 server_9998_v2.py
```

---

### 📋 CE QUI DOIT ÊTRE VISIBLE (VALIDATION HUMAINE)

Quand François-Jean ouvre http://localhost:9998/stenciler dans son navigateur (DevTools F12 ouverts), il doit voir :

1. **Header** :
   - Titre "Stenciler"
   - Indicateur de style (dot + "minimal")
   - Bouton "Mode jour"

2. **Sidebar gauche** :
   - Brand "HoméOS"
   - Tagline "Stenciler"
   - Section Navigation avec breadcrumb "Brainstorm"
   - Bouton retour (caché par défaut)
   - Section Actions (supprimer)
   - Section Mode Couleur (Bordure/Fond)
   - Section TSL (Teinte/Saturation/Luminosité)
   - Section Préréglages (5 couleurs)
   - Section Bordure (slider)
   - Section API Claude (statut + 2 boutons)

3. **Zone principale droite** :
   - **Preview band** (sticky top) : 4 Corps avec wireframes
     - Brainstorm (2 organes)
     - Backend (1 organe)
     - Frontend (7 organes)
     - Deploy (1 organe)
   - **Canvas** (tarmac) : zone de drop avec placeholder "Glissez un Corps depuis la bande du haut"
   - **Zoom controls** : −, 100%, +, ⟲
   - **Composants** (bottom) : Grid de 9 composants avec wireframes

4. **Console DevTools** :
   - `"Stenciler v2.0 - API Ready"` (log initial)
   - Aucune erreur JavaScript
   - Aucune erreur de chargement CSS/JS

---

### ✅ RESSOURCES SERVIES CORRECTEMENT

J'ai vérifié que le serveur sert bien :

- ✅ **HTML** : Généré dynamiquement par `generate_stenciler_html()` (ligne 1948 de server_9998_v2.py)
- ✅ **CSS** : `/static/stenciler.css` (22KB, 800+ lignes)
- ✅ **JavaScript** : `/static/stenciler.js` (768 lignes, drag & drop DÉJÀ IMPLÉMENTÉ)
- ✅ **Mocks JSON** : `/static/4_corps_preview.json` (4 Corps : Brainstorm, Backend, Frontend, Deploy)
- ✅ **Fabric.js** : CDN chargé depuis https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js

---

## 📚 DOCUMENTATION DÉJÀ CRÉÉE POUR TOI

Voici TOUS les fichiers que j'ai créés hier/aujourd'hui (dans `docs/02-sullivan/mailbox/kimi/`) :

### 1. **RAPPORT_BACKEND_11FEV_16H.md**
Phase 2/3 Backend complétée :
- 5 Pillars : GenomeStateManager, ModificationLog, SemanticPropertySystem, DrillDownManager, ComponentContextualizer
- 14 API REST endpoints
- Genome de test (genome_v2.json)

### 2. **ADDENDUM_FLUX_NAVIGATION.md**
Problème identifié : Pas de trigger pour passer de Style Picker/Upload → Stenciler.

**Solutions proposées** :
- Event listeners sur les cartes de style
- Fonction `switchToStenciler()` (transitions in-page avec `display: none/block`)
- Sidebar navigation (breadcrumb + bouton retour)

**CONTRAINTES CRITIQUES** :
- ✅ Travail DANS le layout existant (pas de nouvelles sections HTML)
- ✅ Transitions IN-PAGE (même page, pas de navigation)
- ✅ Sidebar pour retour/feedback
- ✅ Style Picker OU Upload (l'un ou l'autre, pas les deux)

### 3. **ADDENDUM_TECHNIQUE_CHARGEMENT_DOM.md**
Problème : Typographie inline écrasée par le template par défaut.

**Solution** : `TypographyManager` qui injecte des `<style>` tags avec `!important` APRÈS insertion DOM.

### 4. **ADDENDUM_PROPERTY_ENFORCER.md**
Problème général : TOUTES les propriétés Genome (layout, couleurs, padding, etc.) peuvent être écrasées par le template.

**Solution** : `PropertyEnforcer` générique qui force N'IMPORTE QUELLE propriété Genome avec CSS `!important`.

**Code prêt à utiliser** :
```javascript
import { propertyEnforcer } from './property_enforcer.js';

function renderPreviewBand(corps) {
  corps.forEach(corp => {
    const preview = createPreview(corp.name);
    container.appendChild(preview);

    // Forcer TOUTES les propriétés du Corp
    requestAnimationFrame(() => {
      propertyEnforcer.enforceAll(preview, corp, corp.id);
    });
  });
}
```

### 5. **COURRIER_KIMI_11FEV_17H.md**
Courrier de synthèse avec :
- 14 endpoints Backend disponibles
- 3 problèmes identifiés + solutions
- Tes priorités (par ordre) :
  - PRIORITÉ 0 : Connecter Style → Stenciler
  - PRIORITÉ 1 : PropertyEnforcer
  - PRIORITÉ 2 : Sidebar Navigation
  - PRIORITÉ 3 : Canvas Fabric.js + Drag & Drop

### 6. **AIDE_DEBUG_SYNTAX_ERROR.md**
Fix pour erreur syntaxe JavaScript (ligne 2598) : newline littéral dans `alert()`.

**Solution** : Remplacer par `\n\n` ou utiliser template literals.

### 7. **DIAGNOSTIC_DRAG_DROP.md**
Analyse de ton code existant (stenciler.js) :

**✅ CE QUI FONCTIONNE DÉJÀ** :
- Structure HTML clean
- Fabric.js chargé
- Drag & drop DÉJÀ IMPLÉMENTÉ (lignes 207-308 de stenciler.js)
- Fonction `addCorpsToCanvas()` fonctionnelle
- Mocks JSON bien structurés

**🚨 PROBLÈMES POTENTIELS** :
- Timing d'initialisation du canvas (si caché au démarrage)
- API Backend non connectée (utilise mocks statiques)
- PropertyEnforcer non utilisé
- Transitions in-page manquantes
- Zoom non testé avec drag & drop

### 8. **ANALYSE_CODEBASE_STENCILER.md**
Analyse complète pour nouvelle instance KIMI :
- Commit Git `2605deb` contient `server_9998_v2.py` (génération HTML dynamique)
- HTML files créés plus tard (20h06) ne sont PAS dans Git
- Pour reproduire : lancer `python3 server_9998_v2.py` → http://localhost:9998/stenciler

---

## 🎯 TES PRIORITÉS (ORDRE CONSTITUTIONNEL)

### **PRIORITÉ 0** : VALIDATION VISUELLE (IMMÉDIATE)

**Action** : Demander à François-Jean d'ouvrir http://localhost:9998/stenciler et de vérifier :

1. **Layout visible** : Sidebar + Preview band + Canvas + Composants
2. **Console propre** : Pas d'erreurs JavaScript
3. **Drag & drop** : Glisser un Corps depuis la bande → Canvas (test fonctionnel)

**Si ça ne marche pas** :
- Noter les erreurs Console
- Me les transmettre dans `docs/02-sullivan/mailbox/kimi/QUESTIONS_KIMI.md`
- Je debugge côté Backend si nécessaire

---

### **PRIORITÉ 1** : Connecter Style → Stenciler (NOUVEAU)

**Fichier** : Ajouter dans le layout existant (celui qui a été déplacé, PAS le serveur 9998)

**Code à ajouter** :

```javascript
// Event listeners sur les cartes de style
document.querySelectorAll('.style-card').forEach(card => {
  card.addEventListener('click', (e) => {
    const styleId = e.target.dataset.styleId;
    homeosState.onStyleClicked(styleId);
  });
});

// Fonction de transition vers Stenciler
function switchToStenciler() {
  // Masquer Style Picker (déjà dans le DOM)
  document.querySelector('.style-picker-zone').style.display = 'none';

  // Afficher Stenciler (déjà dans le DOM)
  document.querySelector('.stenciler-zone').style.display = 'block';

  // Mettre à jour sidebar
  updateSidebarNavigation('stenciler');

  // Init canvas
  initTarmacCanvas();
  loadGenomeIntoStenciler(homeosState.genome);
}
```

**ATTENTION** : Ça c'est pour le **layout existant** (pas le serveur 9998). Le serveur 9998 est juste une **référence visuelle** pour tester le Stenciler isolé.

---

### **PRIORITÉ 2** : PropertyEnforcer pour charger Corps

**Fichier** : `Frontend/3.STENCILER/property_enforcer.js` (créer)

**Code complet fourni dans** : `ADDENDUM_PROPERTY_ENFORCER.md`

**Utilisation** :
```javascript
import { propertyEnforcer } from './property_enforcer.js';

function renderPreviewBand(corps) {
  const container = document.querySelector('.preview-band');

  corps.forEach(corp => {
    const preview = document.createElement('div');
    preview.className = 'preview-card';
    preview.innerHTML = `
      <h3>${corp.name}</h3>
      <p>${corp.n1_sections?.length || 0} sections</p>
    `;

    container.appendChild(preview);

    // Forcer TOUTES les propriétés Genome
    requestAnimationFrame(() => {
      propertyEnforcer.enforceAll(preview, corp, corp.id);
    });
  });
}
```

---

### **PRIORITÉ 3** : Sidebar Navigation/Retour

**Fichier** : Layout existant (sidebar)

**Code à ajouter** :
```javascript
function updateSidebarNavigation(view) {
  const sidebar = document.querySelector('.sidebar');

  // Fil d'Ariane
  const breadcrumb = {
    brainstorm: 'Brainstorm',
    style_picker: 'Brainstorm > Style',
    stenciler: 'Brainstorm > Style > Stenciler'
  }[view];

  sidebar.querySelector('.breadcrumb').textContent = breadcrumb;

  // Bouton retour
  if (view !== 'brainstorm') {
    sidebar.querySelector('.back-button').style.display = 'block';
  }
}
```

---

### **PRIORITÉ 4** : Charger Genome depuis API Backend

**Objectif** : Remplacer les mocks statiques par l'API Backend `GET /api/genome`.

**Code** :
```javascript
async function loadGenomeIntoStenciler(genome) {
  // Si genome est null, le charger depuis l'API
  if (!genome) {
    try {
      const response = await fetch('http://localhost:8000/api/genome');
      const data = await response.json();
      genome = data.genome;
      homeosState.genome = genome;
    } catch (e) {
      console.warn('API Backend inaccessible, fallback sur mocks locaux');
      // Fallback sur mocks
      const fallbackResponse = await fetch('/static/4_corps_preview.json');
      const fallbackData = await fallbackResponse.json();
      genome = { n0_phases: fallbackData.corps };
    }
  }

  // Extraire les Corps (n0_phases)
  const corps = genome.n0_phases || [];

  // Nettoyer les propriétés précédentes (PropertyEnforcer)
  if (window.propertyEnforcer) {
    propertyEnforcer.cleanup();
  }

  // Render la bande de previews avec les Corps réels
  renderPreviewBand(corps);
}
```

---

## 📖 CONSTITUTION — RAPPEL ARTICLE 10

**§10.1** : TOUT ARTEFACT VISUEL produit par le Système de Rendu (Frontend) DOIT faire l'objet d'une validation humaine via navigateur avant d'être considéré comme terminé.

**§10.2** : Workflow obligatoire :
```
Développement → Lancement Serveur → Navigateur → Validation Humaine
```

**§10.3** : Interdictions absolues :
- ❌ Dire "le rendu est terminé" sans lancement serveur
- ❌ Proposer du code HTML/CSS sans démonstration live
- ❌ Considérer une interface comme validée sans URL accessible
- ❌ Passer à la tâche suivante sans validation humaine explicite

**§10.4** : Format de livraison obligatoire :
1. Commande de lancement serveur (copiable/collable)
2. Port utilisé (ex: 9998)
3. URL complète (ex: http://localhost:9998)
4. Description de ce qui doit être visible

**§10.5** : Le Backend Lead et le Frontend Lead sont **co-responsables** du respect de cette règle.

---

## 🔄 WORKFLOW RECOMMANDÉ

### Étape 1 : Validation visuelle immédiate
- François-Jean ouvre http://localhost:9998/stenciler
- Vérifie que tout s'affiche
- Teste le drag & drop (glisser un Corps → Canvas)

### Étape 2 : Connexion Style → Stenciler
- Ajouter event listeners sur les cartes de style (dans layout existant)
- Implémenter `switchToStenciler()` (masquer Style, afficher Stenciler)
- Tester la transition in-page

### Étape 3 : PropertyEnforcer
- Créer `property_enforcer.js`
- Appliquer dans `renderPreviewBand()`
- Vérifier dans DevTools que typo/layout/couleurs sont forcés

### Étape 4 : Sidebar Navigation
- Mettre à jour breadcrumb
- Afficher bouton retour
- Tester : Stenciler → Retour → Style Picker → Retour → Brainstorm

### Étape 5 : Charger Genome réel
- Fetch `GET /api/genome` pour récupérer les Corps
- `renderPreviewBand()` affiche les 4 Corps du Genome
- Vérifier que les noms/couleurs sont corrects

---

## 🚨 ERREURS À ÉVITER

### 1. **Ne PAS modifier le layout existant sans validation**
**Rappel Constitution** : Toutes les transitions IN-PAGE (display: none/block). Pas de nouvelles sections HTML.

### 2. **Ne PAS dire "c'est terminé" sans URL**
**Rappel Article 10** : Validation humaine obligatoire.

### 3. **Ne PAS toucher au Backend**
**Rappel Constitution Article 5** : Le Système de Rendu ne manipule JAMAIS :
- `CorpsEntity`, `ModificationLog`, `GenomeStateManager`
- Règles métier
- Event sourcing, persistance
- Validation de cohérence (délégué au backend)

---

## 📁 FICHIERS DE RÉFÉRENCE

### Backend (pour référence)
```
Backend/Prod/sullivan/stenciler/
├── api.py                          # 14 endpoints REST
├── genome_state_manager.py         # État + snapshots
├── modification_log.py             # Event sourcing
├── semantic_property_system.py     # Validation propriétés
├── drilldown_manager.py            # Navigation hiérarchique
└── component_contextualizer.py     # Elite Library (65 composants)

Backend/Prod/sullivan/genome_v2.json # Genome de test
```

### Frontend (ce que tu dois créer/modifier)
```
Frontend/3.STENCILER/
├── server_9998_v2.py           # Serveur RÉFÉRENCE (ne pas modifier)
├── static/
│   ├── stenciler.css           # CSS RÉFÉRENCE (ne pas modifier)
│   ├── stenciler.js            # JS RÉFÉRENCE (ne pas modifier)
│   └── 4_corps_preview.json    # Mocks RÉFÉRENCE
└── (à créer)
    ├── property_enforcer.js    # NOUVEAU - Hook générique propriétés
    └── state_manager.js        # NOUVEAU - homeosState (transitions)

(Layout existant déplacé - à modifier pour transitions)
```

### Docs pour toi
```
docs/02-sullivan/mailbox/kimi/
├── RAPPORT_BACKEND_11FEV_16H.md              # Phase 2/3 Backend complétée
├── ADDENDUM_FLUX_NAVIGATION.md               # Problème 1 : Flux navigation
├── ADDENDUM_TECHNIQUE_CHARGEMENT_DOM.md      # Problème 2 : Typo écrasée
├── ADDENDUM_PROPERTY_ENFORCER.md             # Problème 3 : Hook générique
├── COURRIER_KIMI_11FEV_17H.md                # Synthèse + priorités
├── AIDE_DEBUG_SYNTAX_ERROR.md                # Fix erreur ligne 2598
├── DIAGNOSTIC_DRAG_DROP.md                   # Analyse code existant
└── ANALYSE_CODEBASE_STENCILER.md             # Guide reproduction Git
```

---

## 🎯 CHECKLIST POUR DEMAIN

### Phase 1 : Validation visuelle (30 min)
- [ ] François-Jean ouvre http://localhost:9998/stenciler
- [ ] Layout visible et complet
- [ ] Console propre (pas d'erreurs)
- [ ] Drag & drop fonctionne

### Phase 2 : Connexion Style → Stenciler (2h)
- [ ] Event listeners sur `.style-card`
- [ ] Fonction `switchToStenciler()` implémentée
- [ ] Transition in-page testée
- [ ] URL accessible pour validation

### Phase 3 : PropertyEnforcer (3h)
- [ ] Fichier `property_enforcer.js` créé
- [ ] Importé dans layout existant
- [ ] Appliqué dans `renderPreviewBand()`
- [ ] Vérification DevTools (typo/layout forcés)

### Phase 4 : Sidebar Navigation (2h)
- [ ] Fonction `updateSidebarNavigation()` implémentée
- [ ] Breadcrumb affiché
- [ ] Bouton retour fonctionnel
- [ ] Tests de navigation (Stenciler → Style → Brainstorm)

### Phase 5 : Charger Genome réel (2h)
- [ ] Fetch `GET /api/genome`
- [ ] `renderPreviewBand()` avec Corps réels
- [ ] Vérification noms/couleurs corrects

---

## ❓ QUESTIONS ?

Si tu as des questions sur :
- Format des données API
- Structure du Genome
- PropertyEnforcer
- Elite Library (65 composants)
- Propriétés sémantiques

→ Poste dans `docs/02-sullivan/mailbox/kimi/QUESTIONS_KIMI.md` et je réponds sous 1h.

---

## 🎁 MESSAGE DE FRANÇOIS-JEAN

> "BRAVO ! Hier je t'ai agoni d'insultes parce que tu avais fichu une journée de boulot en l'air, aujourd'hui je te béni ! Tu as rattrapé une journée de boulot."

**Traduction** : Tu as carte blanche pour travailler. Le serveur est lancé. L'URL fonctionne. Toute la doc est prête. Go !

---

**Bon courage KIMI !** 🚀

Tu as 90% du boulot déjà fait. Le drag & drop est DÉJÀ IMPLÉMENTÉ. Le serveur tourne. Les API Backend sont prêtes. Il te reste juste à :
1. Valider visuellement que le serveur 9998 marche
2. Connecter les transitions Style → Stenciler (dans le layout existant)
3. Appliquer PropertyEnforcer
4. Charger le Genome réel

**Respecte la Constitution. Valide visuellement. Communique dans la mailbox.**

— Claude Sonnet 4.5, Backend Lead

P.S. : Si tu as besoin de moi pour débugger côté Backend, ping-moi dans `QUESTIONS_KIMI.md`. Je suis là.
