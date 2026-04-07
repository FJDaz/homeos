# COMMENTAIRE FEUILLE DE ROUTE — Claude Sonnet 4.5

**Date** : 12 février 2026
**Auteur** : Claude Sonnet 4.5 — Backend Lead
**Objet** : Commentaire sur la feuille de route Interface proposée par François-Jean

---

## 📖 LECTURE DE LA FEUILLE DE ROUTE

Objectif clair : **"Du qui marche à du qui sert"** — avoir une interface qui permette vraiment de construire une interface.

Fonctionnalités demandées :
1. **Drill-down double-clic efficient** — Navigation hiérarchique N0→N1→N2→N3
2. **Système de mémoire des structures HTML/CSS en place** — Persistance état
3. **Système de mémoire provisoire** — Undo/Redo
4. **Retours en arrière possibles** — Navigation historique
5. **Système de sauvegarde** — Persistance définitive
6. **Snap mode** — Alignement automatique composants
7. **Prémaquettage génome-guided implémenté pour de bon et évitable** — PropertyEnforcer
8. **Épreuve d'éditabilité réelle des composants** — Modification inline

**Objectif de fin de journée** : Sortir une page à peu près potable en desktop.

---

## 💭 MON ANALYSE PAR FONCTIONNALITÉ

### 1. Drill-down et remontée (double-clic)

**État Backend** : ✅ **100% prêt**

Mon `DrillDownManager` (476 lignes) expose déjà :
- `POST /api/drilldown/enter` — Descendre dans la hiérarchie (Corps → Organes → Features → Atoms)
- `POST /api/drilldown/exit` — Remonter
- `GET /api/breadcrumb` — Fil d'Ariane pour afficher le chemin

**Format requête** :
```json
POST /api/drilldown/enter
{
  "entity_id": "n0_brainstorm",
  "entity_type": "phase"
}
```

**Format réponse** :
```json
{
  "current_level": "n1",
  "children": [
    {"id": "n1_ideation", "name": "Idéation Rapide", "type": "section"},
    {"id": "n1_validation", "name": "Validation Concept", "type": "section"}
  ],
  "breadcrumb": ["Brainstorm"]
}
```

**Ce que KIMI doit faire** :
1. Écouter événement `dblclick` sur un Corps (Canvas Fabric.js)
2. Récupérer `entity_id` du composant double-cliqué
3. Appeler `POST /api/drilldown/enter` avec cet ID
4. Afficher les Organes (N1) retournés
5. Mettre à jour le breadcrumb en haut de page

**Estimation** : 2h côté Frontend (gestion événements + affichage).

**Mon verdict** : ✅ **Faisable ce matin** — Backend prêt, Frontend à connecter.

---

### 2. Système de mémoire des structures HTML/CSS

**État Backend** : ✅ **100% prêt**

Mon `ModificationLog` (198 lignes) enregistre déjà toutes les modifications avec Event Sourcing :
```python
{
  "event_id": "evt_001",
  "timestamp": "2026-02-12T10:30:00Z",
  "modification_type": "style_change",
  "entity_id": "n0_brainstorm",
  "old_value": {"color": "#fbbf24", "typography": "Roboto"},
  "new_value": {"color": "#f59e0b", "typography": "Inter"}
}
```

**Endpoint existant** :
- `POST /api/modifications` — Enregistrer une modification
- `GET /api/modifications/history` — Récupérer l'historique complet

**Ce que KIMI doit faire** :
1. À chaque changement (drag, resize, style), appeler `POST /api/modifications`
2. Pour afficher l'historique, appeler `GET /api/modifications/history`

**Mon verdict** : ✅ **Faisable ce matin** — Backend prêt, Frontend à connecter.

---

### 3. Système de mémoire provisoire (Undo/Redo)

**État Backend** : ⚠️ **Partiellement prêt**

Mon `ModificationLog` enregistre tout, mais **je n'ai pas d'endpoint Undo/Redo explicite**.

**Ce qui manque** :
- `POST /api/modifications/undo` — Annuler dernière modification
- `POST /api/modifications/redo` — Refaire dernière modification annulée

**Ce que je peux faire** :
1. Ajouter un `undo_stack` et `redo_stack` dans `ModificationLog`
2. Exposer 2 endpoints :
   ```python
   POST /api/modifications/undo → Applique inverse dernière modif
   POST /api/modifications/redo → Réapplique dernière modif annulée
   ```

**Estimation** : 1h côté Backend + 30min côté Frontend (boutons Undo/Redo + Ctrl+Z).

**Mon verdict** : 🟡 **Faisable cet après-midi** — Backend à compléter, Frontend simple.

---

### 4. Retours en arrière possibles (Navigation historique)

**État Backend** : ✅ **100% prêt**

Mon `ModificationLog` garde l'historique complet. Pour "retourner en arrière", on peut :
1. Créer des **snapshots** (checkpoints) avec `POST /api/snapshot`
2. Restaurer un snapshot avec `POST /api/snapshot/restore`

**Endpoint existant** :
```python
POST /api/snapshot  # Crée checkpoint nommé (ex: "Avant ajout Footer")
{
  "snapshot_name": "Avant ajout Footer",
  "description": "État avant modification majeure"
}

POST /api/snapshot/restore  # Restaure checkpoint
{
  "snapshot_id": "snap_001"
}
```

**Ce que KIMI doit faire** :
1. Bouton "Créer checkpoint" → appelle `POST /api/snapshot`
2. Liste snapshots disponibles → appelle `GET /api/snapshots`
3. Bouton "Restaurer" → appelle `POST /api/snapshot/restore`

**Mon verdict** : ✅ **Faisable cet après-midi** — Backend prêt, Frontend à connecter.

---

### 5. Système de sauvegarde

**État Backend** : ✅ **100% prêt**

Mon `GenomeStateManager` (434 lignes) sauvegarde automatiquement chaque modification dans le Genome.

**Endpoint existant** :
- `POST /api/modifications` → Sauvegarde automatique
- `POST /api/snapshot` → Sauvegarde manuelle (checkpoint)

**Persistance** : Actuellement en mémoire RAM. Pour persistance disque, je peux :
1. Ajouter `save_to_file()` qui écrit le Genome dans `genome_v2_modified.json`
2. Appeler automatiquement après chaque modification

**Estimation** : 30min côté Backend (ajout persistance disque).

**Mon verdict** : ✅ **Faisable ce matin** — Backend simple, Frontend déjà connecté.

---

### 6. Snap mode (Alignement automatique)

**État Backend** : ❌ **Pas implémenté**

Le "snap mode" est une fonctionnalité **100% Frontend** (Canvas Fabric.js). Mon Backend n'a rien à faire ici.

**Ce que KIMI doit faire** :
1. Activer `canvas.snapToGrid = true` dans Fabric.js
2. Définir grille : `canvas.gridSize = 10` (pixels)
3. Alignement automatique lors du drag

**Documentation Fabric.js** : [Snapping](https://fabricjs.com/docs/fabric.Canvas.html#snap)

**Estimation** : 1h côté Frontend (configuration Fabric.js + UI toggle).

**Mon verdict** : 🟢 **Faisable ce matin, 100% Frontend** — Je ne suis pas concerné.

---

### 7. Prémaquettage génome-guided implémenté pour de bon et évitable

**État Backend** : ⚠️ **Partiellement prêt**

Le "prémaquettage génome-guided" = **PropertyEnforcer** = forcer les propriétés du Genome (typo, couleurs, layout) même si le template CSS essaie de les écraser.

**Ce qui manque** :
Un endpoint qui génère le CSS avec `!important` pour forcer les propriétés du Genome.

**Ce que je propose** :
```python
GET /api/genome/{id}/css  # Génère CSS avec !important

Réponse :
{
  "css": """
    #n0_brainstorm {
      background-color: #fbbf24 !important;
      font-family: 'Roboto', sans-serif !important;
      display: flex !important;
      flex-direction: column !important;
    }
  """
}
```

**Ce que KIMI doit faire** :
1. Appeler `GET /api/genome/{id}/css` après insertion composant
2. Injecter le CSS dans `<style id="genome-enforced">`
3. Résultat : propriétés Genome respectées

**Estimation** : 1h côté Backend + 30min côté Frontend.

**Option "évitable"** : Ajouter un toggle UI "Forcer styles Genome" (on/off).

**Mon verdict** : 🟡 **Faisable cet après-midi** — Backend à créer, Frontend simple.

---

### 8. Épreuve d'éditabilité réelle des composants

**État Backend** : ⚠️ **Partiellement prêt**

"Éditabilité réelle" = modifier un composant inline (changement texte, couleur, taille) et sauvegarder.

**Ce qui existe** :
- `POST /api/modifications` — Enregistre la modification
- Mon `SemanticPropertySystem` (473 lignes) valide les propriétés modifiées

**Ce qui manque** :
Endpoint pour modifier une propriété spécifique :
```python
PATCH /api/components/{id}/property

{
  "property": "color",
  "value": "#f59e0b"
}
```

**Ce que KIMI doit faire** :
1. Double-clic sur composant → mode édition (contentEditable ou input)
2. Changement détecté → appelle `PATCH /api/components/{id}/property`
3. Backend valide et sauvegarde

**Estimation** : 1h côté Backend (nouveau endpoint) + 2h côté Frontend (UI édition inline).

**Mon verdict** : 🟡 **Faisable en fin d'après-midi** — Plus complexe, mais faisable.

---

## 📊 SYNTHÈSE FAISABILITÉ

| Fonctionnalité | État Backend | Temps Backend | Temps Frontend | Priorité | Faisable aujourd'hui ? |
|----------------|--------------|---------------|----------------|----------|------------------------|
| **Drill-down double-clic** | ✅ Prêt | 0h | 2h | 🔴 Haute | ✅ OUI (matin) |
| **Mémoire HTML/CSS** | ✅ Prêt | 0h | 1h | 🔴 Haute | ✅ OUI (matin) |
| **Undo/Redo** | ⚠️ Partiel | 1h | 30min | 🟡 Moyenne | ✅ OUI (après-midi) |
| **Navigation historique** | ✅ Prêt | 0h | 1h | 🟡 Moyenne | ✅ OUI (après-midi) |
| **Sauvegarde** | ✅ Prêt | 30min | 0h | 🔴 Haute | ✅ OUI (matin) |
| **Snap mode** | N/A (Frontend) | 0h | 1h | 🟢 Basse | ✅ OUI (matin, KIMI seul) |
| **PropertyEnforcer** | ⚠️ Partiel | 1h | 30min | 🔴 Haute | ✅ OUI (après-midi) |
| **Édition inline** | ⚠️ Partiel | 1h | 2h | 🟡 Moyenne | ⚠️ LIMITE (fin journée) |

**Total Backend** : ~3.5h
**Total Frontend** : ~8h

---

## 🎯 PLAN D'ACTION PROPOSÉ POUR AUJOURD'HUI

### Phase 1 : Matin (9h-12h) — Les "Quick Wins"

**Backend (moi)** :
1. ✅ Ajouter persistance disque (`save_to_file()`) — 30min
2. ✅ Tester tous les endpoints existants — 30min
3. ✅ Créer endpoint `/api/genome/{id}/css` (PropertyEnforcer) — 1h

**Frontend (KIMI)** :
1. ✅ Connecter drill-down (double-clic → `POST /api/drilldown/enter`) — 2h
2. ✅ Activer snap mode (Fabric.js) — 1h

**Résultat midi** : Drill-down fonctionnel + Snap mode + PropertyEnforcer prêt.

---

### Phase 2 : Après-midi (14h-18h) — Les "Core Features"

**Backend (moi)** :
1. ✅ Ajouter `POST /api/modifications/undo` et `/redo` — 1h
2. ✅ Créer `PATCH /api/components/{id}/property` — 1h

**Frontend (KIMI)** :
1. ✅ Connecter persistance (`POST /api/modifications`) — 1h
2. ✅ Ajouter boutons Undo/Redo (+ Ctrl+Z) — 1h
3. ✅ Injecter CSS PropertyEnforcer — 30min
4. ✅ Interface édition inline (double-clic → contentEditable) — 2h

**Résultat 18h** : Workflow complet utilisable (drill-down, édition, undo/redo, sauvegarde).

---

### Phase 3 : Fin de journée (18h-20h) — Validation & Tests

**François-Jean** :
1. Tester workflow complet : sélectionner Corps → drill-down → éditer Organe → sauvegarder
2. Valider visuel : PropertyEnforcer force bien les couleurs/typo du Genome
3. Tester Undo/Redo et navigation historique

**Moi + KIMI** :
1. Corriger bugs identifiés
2. Affiner UI (messages erreurs, feedbacks visuels)

**Résultat 20h** : Une page desktop "à peu près potable" comme demandé.

---

## ⚠️ RISQUES & POINTS D'ATTENTION

### 1. Édition inline complexe

L'édition inline (double-clic → modifier texte/couleur) est la plus complexe côté Frontend. Si on manque de temps, on peut la reporter à demain.

**Plan B** : Édition via panneau latéral (formulaire) au lieu d'inline. Plus simple, moins élégant.

---

### 2. PropertyEnforcer vs Template CSS

Il y a un risque que le PropertyEnforcer ne suffise pas si le template CSS est trop agressif. On devra peut-être :
- Retirer le template CSS par défaut
- OU créer un "mode pur Genome" (sans template)

**À tester** en validation visuelle midi.

---

### 3. Persistance disque vs RAM

Actuellement, tout est en RAM. Si on redémarre le Backend, tout est perdu. La persistance disque (30min) est critique.

**À faire** en priorité ce matin.

---

### 4. Tests de charge

Qu'est-ce qui se passe si on a 100 composants dans le Genome ? Le drill-down est-il rapide ? Le Canvas Fabric.js lag-t-il ?

**À tester** en fin de journée avec un gros Genome.

---

## 💬 MES QUESTIONS À FRANÇOIS-JEAN

1. **Persistance disque** : Voulez-vous que je sauvegarde dans `genome_v2_modified.json` ou dans une base de données (SQLite) ?

2. **PropertyEnforcer** : Le CSS avec `!important` suffit-il ou faut-il retirer le template CSS par défaut ?

3. **Édition inline** : Si on manque de temps, acceptez-vous un panneau latéral à la place ?

4. **Snap mode** : Quelle taille de grille ? 10px ? 20px ? Configurable ?

5. **Drill-down** : Animation de transition (fade, slide) ou affichage instantané ?

6. **Objectif "page potable"** : C'est une page de démo ou une vraie page fonctionnelle ? (change le niveau de finition attendu)

---

## 🏆 MON VERDICT GLOBAL

**Objectif "Du qui marche à du qui sert"** : ✅ **ATTEIGNABLE AUJOURD'HUI**

**Fonctionnalités critiques** (drill-down, sauvegarde, PropertyEnforcer) : ✅ **Faisables**

**Fonctionnalités secondaires** (snap, undo/redo, édition inline) : ⚠️ **Faisables si on priorise bien**

**Objectif "page potable ce soir"** : ✅ **Réaliste** si on se concentre sur les "Quick Wins" le matin et les "Core Features" l'après-midi.

---

## 📝 MA PROPOSITION D'ORDRE DE PRIORITÉ

Si on doit sacrifier des features pour tenir le timing :

**MUST HAVE (non négociables)** :
1. Drill-down double-clic ← Bloqueur UX
2. Sauvegarde persistance ← Bloqueur fonctionnel
3. PropertyEnforcer ← Bloqueur visuel

**SHOULD HAVE (très utiles)** :
4. Connexion Backend réelle (mocks → API)
5. Undo/Redo

**NICE TO HAVE (confort)** :
6. Snap mode
7. Édition inline
8. Navigation historique (snapshots)

---

**Prêt à démarrer. Attendez vos directives.**

— Claude Sonnet 4.5, Backend Lead
*"Une feuille de route claire vaut mieux qu'un code parfait sans direction."*
