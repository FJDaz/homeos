# Méthode "Kimi Innocent" - Inférence Genome Frontend

**Version**: 1.0  
**Date**: 7 février 2026  
**Auteur**: Binôme Kimi/Homeos  
**Statut**: Opérationnelle

---

## 🎯 Principe

Produire un **Genome Spatialisé N0-N3** qui permette à un développeur frontend de générer l'interface utilisateur **sans connaissance préalable du projet**.

Ce n'est pas une description technique. C'est un **cahier des charges UI exécutable**.

---

## 📦 Les 4 Bundles (Sources de Vérité)

### Ordre de priorité (du plus faible au plus fort)

| # | Bundle | Contenu | Priorité |
|---|--------|---------|----------|
| 1 | **A - Documentation** | PRD, Vision, Parcours UX | Basse (peut être obsolète) |
| 2 | **B - Code** | Endpoints réels, routes API | Moyenne |
| 3 | **C - Logs** | Appels HTTP, erreurs 200/404 | Haute |
| 4 | **D - Inférence** | Composants UI manquants | Complète |

**Règle d'or**: Logs > Code > Doc

---

## 🔬 Les 5 Phases

### Phase 1: Lecture Séquentielle (30 min)

Lire les bundles DANS CET ORDRE STRICT:

1. **STATUS_REPORT** (priorité max) → État actuel opérationnel
2. **Parcours UX** → Flow utilisateur étape par étape  
3. **PRD** → Contexte général (peut être obsolète)
4. **Code/Endpoints** → Liste brute des capacités techniques

### Phase 2: Table de Confrontation (20 min)

```markdown
| Phase UX | Intention utilisateur | Endpoints Code | Statut | Visual Hint |
|----------|----------------------|----------------|--------|-------------|
| 1. IR | Inventorier | /studio/reports/ir | ✅ Codé + Doc | table |
| 2. Arbiter | Décider | /studio/arbitrage/forms | ✅ Codé | stencil-card |
| 9. Adaptation | Zoom Atome | /studio/zoom/atome/{id} | ⚠️ Codé mais ? | detail-card |
```

**Légende Statut**:
- ✅ = Confirmé par au moins 2 sources (Doc + Code, ou Code + Logs)
- ⚠️ = Présent dans 1 source seule (risque d'hallucination)
- ❓ = Mentionné mais contradictions non résolues

### Phase 3: Extraction N0-N3 (30 min)

Structure obligatoire:

```
N0 (World/Phase) → Les 9 étapes du parcours UX
  └── N1 (Section/Espace) → Grands espaces de l'UI
       └── N2 (Feature/Fonctionnalité) → Capacités concrètes
            └── N3 (Component/Atome) → Éléments UI rendables
```

**Contraintes N3 (CRITIQUE)**:
Chaque N3 DOIT avoir:
- `endpoint`: URL exacte (ex: "/studio/reports/ir")
- `method`: GET/POST/PUT/DELETE
- `visual_hint`: Type de composant (voir liste ci-dessous)
- `layout_hint`: grid/flex/stack
- `interaction_type`: click/hover/submit/drag
- `description_ui`: "L'utilisateur voit... et peut..."

### Phase 4: Validation Frontend (20 min)

Pour chaque N3, se demander:
- "Un dev junior peut-il coder ça sans me poser de question ?"
- "Quelles classes Tailwind/DaisyUI utiliser ?"
- "Que se passe-t-il en mobile ?"
- "Quel état loading ? Quel état error ?"

Si inconnu → Marquer "uncertain" et justifier.

### Phase 5: Rapport d'Incertitudes (10 min)

Lister explicitement:
- Ce qu'on n'a pas compris
- Les contradictions non résolues
- Les endpoints mentionnés mais sans visualisation claire
- Les hypothèses faites

---

## 🎨 Visual Hints Obligatoires

### 10 Wireframes FRD V2 (Différenciés)

| Visual Hint | Usage | Différenciation Clé |
|-------------|-------|---------------------|
| `status` | Check santé projet | 4 LEDs (vertes/grises) + texte |
| `zoom-controls` | Navigation | ← Out / 🔍 Corps ▼ / In → + breadcrumb |
| `download` | Export ZIP | Carte fichier + bouton 📥 |
| `chat-input` | Message utilisateur | Champ + 📎😊 + bouton envoi |
| `color-palette` | Style détecté | 4 swatches + chips (rounded/font) |
| `choice-card` | Sélection style | Radio cards 2×2 (Minimal/Brutaliste/etc) |
| `stencil-card` | Fiche pouvoir | Titre + description + Garder/Réserve |
| `detail-card` | Fiche technique | Endpoint monospace + Copier/Tester |
| `launch-button` | Lancer processus | Bouton fusée 🚀 avec texte action |
| `apply-changes` | Sauvegarder | 💾 Appliquer / ↩️ Annuler côte à côte |

### Wireframes Classiques

- **table** : Tableau avec header + rows
- **card** : Carte avec header/body/footer
- **form** : Formulaire avec inputs + submit
- **list** : Liste verticale d'items
- **grid** : Galerie (3×2 pour layouts)
- **upload** : Zone drag & drop avec 📁
- **preview** : Image avec zones surlignées
- **chat/bubble** : Bulles S indigo + user
- **editor** : Éditeur code avec toolbar
- **dashboard** : Métriques + mini graphiques
- **accordion** : Contenu pliable
- **breadcrumb** : Navigation hiérarchique
- **modal** : Fenêtre modale
- **stepper** : Indicateur d'étapes
- **button** : Bouton action simple

---

## 🔄 Réinterprétations Naming (UI-Friendly)

### HTTP Methods → Actions Utilisateur

| Method | Technique | Utilisateur |
|--------|-----------|-------------|
| GET | GET | 📖 Voir |
| POST | POST | ➕ Ajouter |
| PUT | PUT | ✏️ Modifier |
| DELETE | DELETE | 🗑️ Supprimer |

### Nettoyage Noms

Supprimer les préfixes techniques:
- ❌ "Comp Vue Rapport IR"
- ❌ "Component Detail Organe"
- ✅ "Vue Rapport IR"
- ✅ "Détail Organe"

---

## 🔧 Opérations en Aval du Genome

### 1. Normalisation Structure

Problème: Fichiers legacy avec clés MAJUSCULES (N0_PHASES) vs nouvelles (n0_phases)

Solution:
```python
def normalize_keys(obj):
    if isinstance(obj, dict):
        return {k.lower(): normalize_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_keys(item) for item in obj]
    return obj
```

### 2. Routage Flexible

Le serveur doit accepter:
- `/`
- `/studio`
- `/studio?step=4`
- `/studio?any=params`

### 3. Gestion Erreurs Syntaxe

Dans les f-strings Python avec JSON:
- ❌ `{{}}` dans f-string (double accolades)
- ✅ `{}` avec valeurs par défaut gérées avant

### 4. Layout UI Élégant

Composants de la vue "le Génome":
- **Tabs**: Brainstorm | Backend | **Frontend** | Deploy
- **Sidebar**: 
  - Titre (HoméOS)
  - Confiance globale (%)
  - Stats (phases, composants)
  - Liste wireframes FRD V2
- **Sticky Header**: Checkbox "Tout sélectionner" + bouton "Valider (n)"
- **Stats**: 📖 Voir | ➕ Ajouter | ✏️ Modifier | Autres
- **Grid**: Cartes composants avec wireframes

---

## 📋 Checklist Finale

Avant livraison:
- [ ] 29 composants exactement (pas 38, pas 21)
- [ ] Structure N0-N3 complète
- [ ] Tous les visual hints explicites
- [ ] Routes /studio fonctionnelles
- [ ] Naming UI-friendly (📖 Voir, pas GET)
- [ ] Layout élégant (tabs, sidebar, sticky header)
- [ ] Normalisation JSON ok
- [ ] Commit + Push effectués

---

## 🎯 Output Attendu

### Fichier: `genome_inferred_kimi_innocent.json`

Structure:
```json
{
  "genome_version": "3.0-kimi-innocent",
  "inference_method": "4-source-confrontation",
  "metadata": {
    "confidence_global": 0.82,
    "composants_count": 29
  },
  "n0_phases": [
    {
      "id": "phase_1_ir",
      "name": "Intent Refactoring",
      "n1_sections": [{
        "n2_features": [{
          "n3_components": [{
            "id": "comp_ir_table",
            "name": "Vue Rapport IR",
            "endpoint": "/studio/reports/ir",
            "method": "GET",
            "visual_hint": "table"
          }]
        }]
      }]
    }
  ]
}
```

---

**Mémo**: "Pas de code sans mode, pas de mode sans routeur, pas de genome sans confrontation des 4 bundles."
