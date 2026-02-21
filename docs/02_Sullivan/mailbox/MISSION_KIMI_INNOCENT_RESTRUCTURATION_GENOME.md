# Mission KIMI Innocent - Inférence Génome Frontend

**Date**: 10 février 2026
**Agent**: KIMI Innocent (Gemini)
**Méthode**: 4-Source Confrontation
**Statut**: 🔴 À EXÉCUTER

---

## 🎯 OBJECTIF

Appliquer la **Méthode Kimi Innocent** pour inférer le génome complet du frontend HomeOS à partir des 4 bundles de vérité, sans connaissance préalable du projet.

**Output attendu** : Fichier JSON structuré N0-N3 avec ~25-35 composants UI, hiérarchie cohérente, et rapport d'incertitudes.

---

## 📚 MÉTHODE DE RÉFÉRENCE

**Fichier à suivre strictement** :
```
/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Methodologies/METHODE_KIMI_INNOCENT.md
```

Cette méthode définit les **5 phases obligatoires** :
1. Lecture Séquentielle (30 min)
2. Table de Confrontation (20 min)
3. Extraction N0-N3 (30 min)
4. Validation Frontend (20 min)
5. Rapport d'Incertitudes (10 min)

---

## 📦 LES 4 BUNDLES (Sources de Vérité)

### Ordre de priorité (du + faible au + fort)

| # | Bundle | Fiabilité | Utilisation |
|---|--------|-----------|-------------|
| **A** | Documentation | ⚠️ Basse | Contexte général (peut être obsolète) |
| **B** | Code | ✅ Moyenne | Endpoints réels, routes API |
| **C** | Logs | ✅✅ Haute | Appels HTTP confirmés, erreurs 200/404 |
| **D** | Inférence | ✅✅✅ Complète | Composants UI manquants |

**Règle d'or** : Logs > Code > Doc

---

## 📂 SOURCES À CONSULTER

### Bundle A - Documentation (Contexte)

Lire dans cet ordre :

1. **Workflow Utilisateur** (priorité max) :
   ```
   /Users/francois-jeandazin/AETHERFLOW/docs/04-homeos/WORKFLOW_UTILISATEUR.md
   ```
   → Décrit les grandes phases du système et les étapes utilisateur

2. **PRD Actuel** :
   ```
   /Users/francois-jeandazin/AETHERFLOW/docs/04-homeos/PRD_HOMEOS_ETAT_ACTUEL.md
   ```
   → État production du système

3. **Parcours UX** (si disponible) :
   ```
   /Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Parcours_UX/
   ```

4. **Rapport Genome** (référence technique) :
   ```
   /Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/GENOME_OPT_2026_02_09/Rapport complet Genome enrichi.md
   ```

### Bundle B - Code (Endpoints réels)

Parser les routes FastAPI :

```
/Users/francois-jeandazin/AETHERFLOW/Backend/Prod/api.py
/Users/francois-jeandazin/AETHERFLOW/Backend/Prod/studio_routes.py
/Users/francois-jeandazin/AETHERFLOW/Backend/Prod/sullivan/
```

**Extraire** :
- Liste complète des endpoints `/studio/*`
- Méthodes HTTP (GET, POST, PUT, DELETE)
- Paramètres de route

### Bundle C - Logs (Appels confirmés)

Si disponibles, analyser :
```
/Users/francois-jeandazin/AETHERFLOW/Backend/Prod/logs/access.log
/Users/francois-jeandazin/AETHERFLOW/Backend/Prod/logs/server.log
```

**Identifier** :
- Endpoints réellement appelés (status 200)
- Endpoints en erreur (404, 500)
- Fréquence d'utilisation

### Bundle D - Inférence (Composants manquants)

À partir des bundles A, B, C :
- Déduire les composants UI nécessaires mais non documentés
- Proposer visual_hints cohérents
- Compléter la hiérarchie N0-N3

---

## 🔬 PROCESSUS D'EXÉCUTION

### Phase 1 : Lecture Séquentielle (30 min)

1. Lire `WORKFLOW_UTILISATEUR.md` en entier
2. Lire `PRD_HOMEOS_ETAT_ACTUEL.md`
3. Parser les routes dans `api.py` et `studio_routes.py`
4. Consulter le Rapport Genome pour comprendre la structure N0-N3

**Prendre des notes** sur :
- Les grandes phases du système (si mentionnées)
- Les workflows utilisateur identifiés
- Les endpoints listés
- Les patterns récurrents

### Phase 2 : Table de Confrontation (20 min)

Créer un tableau de mapping :

| Workflow/Étape User | Endpoint Code | Logs (si dispo) | Statut | Visual Hint Proposé |
|---------------------|---------------|-----------------|--------|---------------------|
| Exemple: "Upload Design" | `/studio/step/5/upload` | ✅ POST 200 | Confirmé | upload/dropzone |
| ... | ... | ... | ... | ... |

**Légende Statut** :
- ✅ = Confirmé par au moins 2 sources (Doc + Code, ou Code + Logs)
- ⚠️ = Présent dans 1 source seule
- ❓ = Contradictions non résolues

### Phase 3 : Extraction N0-N3 (30 min)

**IMPORTANT** : Ne pas présupposer la structure. Inférer la hiérarchie à partir des sources.

#### Questions à se poser :

1. **Quel est le niveau N0 (World) ?**
   - Y a-t-il des "grandes phases" ou "onglets principaux" mentionnés dans le workflow utilisateur ?
   - Le code contient-il des préfixes de routes qui suggèrent une organisation ?
   - Exemple : Si je vois des routes `/brs/*`, `/bkd/*`, `/frd/*`, `/dpl/*` → N0 pourrait être ces 4 catégories

2. **Quel est le niveau N1 (Organes/Sections) ?**
   - Les workflows utilisateur (étapes) sont-ils des N1 ou des N0 ?
   - Combien y a-t-il d'étapes distinctes dans le parcours ?

3. **Quel est le niveau N2 (Features) ?**
   - Regroupements intermédiaires de composants ?
   - Sections logiques dans une même étape ?

4. **Quel est le niveau N3 (Atomes/Components) ?**
   - Les composants UI atomiques (boutons, cartes, tableaux, etc.)
   - Chacun correspond à un endpoint ou une interaction utilisateur

#### Structure à produire :

```json
{
  "genome_version": "3.1-kimi-innocent-inferred",
  "inference_method": "4-source-confrontation",
  "metadata": {
    "confidence_global": 0.XX,
    "composants_count": XX,
    "date_inference": "2026-02-10",
    "sources_consultees": ["WORKFLOW_UTILISATEUR.md", "api.py", "studio_routes.py"]
  },
  "n0_[NOM_NIVEAU]": [
    {
      "id": "...",
      "name": "...",
      "description": "...",
      "n1_[NOM_NIVEAU]": [
        {
          "id": "...",
          "name": "...",
          "n2_[NOM_NIVEAU]": [
            {
              "id": "...",
              "name": "...",
              "n3_components": [
                {
                  "id": "comp_xxx",
                  "name": "Nom clair utilisateur",
                  "endpoint": "/studio/...",
                  "method": "GET|POST|PUT|DELETE",
                  "visual_hint": "table|card|upload|...",
                  "layout_hint": "grid|flex|stack",
                  "interaction_type": "click|hover|submit|drag",
                  "description_ui": "L'utilisateur voit... et peut..."
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**CONTRAINTES N3 (CRITIQUE)** :

Chaque composant N3 DOIT avoir :
- `id` : Identifiant unique
- `name` : Nom user-friendly (pas de préfixe technique)
- `endpoint` : URL exacte (ex: "/studio/reports/ir")
- `method` : GET/POST/PUT/DELETE
- `visual_hint` : Type de composant (voir liste ci-dessous)
- `layout_hint` : grid/flex/stack/absolute
- `interaction_type` : click/hover/submit/drag/scroll
- `description_ui` : "L'utilisateur voit... et peut..."

### Phase 4 : Validation Frontend (20 min)

Pour chaque N3, vérifier :
- "Un dev junior peut-il coder ça sans me poser de question ?"
- "Quelles classes Tailwind/DaisyUI utiliser ?"
- "Que se passe-t-il en mobile ?"
- "Quel état loading ? Quel état error ?"

Si inconnu → Marquer `"confidence": 0.5` et documenter l'incertitude.

### Phase 5 : Rapport d'Incertitudes (10 min)

Créer le fichier `RAPPORT_INFERENCE_KIMI_INNOCENT.md` avec :

```markdown
# Rapport d'Inférence - KIMI Innocent

**Date** : 2026-02-10
**Confidence globale** : X.XX

## Structure N0-N3 Inférée

- **N0** : [Nom du niveau] (X éléments)
- **N1** : [Nom du niveau] (X éléments)
- **N2** : [Nom du niveau] (X éléments)
- **N3** : Components (X atomes)

## Justification de la Hiérarchie

**Pourquoi N0 = [ce que j'ai choisi] ?**
- Source 1 : WORKFLOW_UTILISATEUR.md mentionne...
- Source 2 : Routes dans api.py organisées par...
- Conclusion : ...

**Pourquoi N1 = [ce que j'ai choisi] ?**
- ...

## Incertitudes Résolues

1. **Composant X** : Hésitation entre N0 ou N1 → Choix : N1 (raison : ...)
2. ...

## Incertitudes Non Résolues

1. **Endpoint Y** : Pas trouvé dans doc ni code → Confidence 0.3
2. ...

## Table de Confrontation (Top 10)

| Workflow | Endpoint | Doc | Code | Logs | Statut |
|----------|----------|-----|------|------|--------|
| ... | ... | ✅ | ✅ | ⚠️ | Confirmé |
```

---

## 🎨 VISUAL HINTS DE RÉFÉRENCE

### 10 Wireframes FRD V2 (Différenciés)

| Visual Hint | Usage | Différenciation Clé |
|-------------|-------|---------------------|
| `status` | Check santé projet | 4 LEDs (vertes/grises) + texte |
| `zoom-controls` | Navigation | ← Out / 🔍 Corps ▼ / In → + breadcrumb |
| `download` | Export ZIP | Carte fichier + bouton 📥 |
| `chat-input` | Message utilisateur | Champ + 📎😊 + bouton envoi |
| `color-palette` | Style détecté | 4 swatches + chips (rounded/font) |
| `choice-card` | Sélection style | Radio cards 2×2 |
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
- **chat/bubble** : Bulles conversation
- **editor** : Éditeur code avec toolbar
- **dashboard** : Métriques + mini graphiques
- **accordion** : Contenu pliable
- **breadcrumb** : Navigation hiérarchique
- **modal** : Fenêtre modale
- **stepper** : Indicateur d'étapes
- **button** : Bouton action simple

---

## 📤 OUTPUTS ATTENDUS

### 1. Fichier JSON Inféré

**Nom** : `genome_inferred_kimi_innocent_v2.json`
**Emplacement** : `/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/`

**Contraintes** :
- Syntaxe JSON valide (testable avec `jq`)
- Structure N0-N3 cohérente
- 25-35 composants N3 environ
- Tous les champs obligatoires présents

### 2. Rapport d'Inférence

**Nom** : `RAPPORT_INFERENCE_KIMI_INNOCENT.md`
**Emplacement** : `/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/mailbox/`

**Contenu** :
- Justification de la structure N0-N3 choisie
- Table de confrontation des sources
- Liste des incertitudes résolues/non résolues
- Statistiques (nombre de N0, N1, N2, N3)
- Confidence globale

---

## ✅ CHECKLIST DE VALIDATION

Avant de considérer la mission terminée :

- [ ] J'ai lu les 4 bundles (A, B, C, D)
- [ ] J'ai créé une table de confrontation
- [ ] J'ai inféré la structure N0-N3 **sans présupposés**
- [ ] Chaque N3 a tous les champs obligatoires
- [ ] J'ai documenté mes choix de hiérarchie
- [ ] JSON valide : `jq . genome_inferred_kimi_innocent_v2.json`
- [ ] Confidence >= 0.70
- [ ] Rapport d'inférence créé
- [ ] Incertitudes listées

---

## 🚨 INTERDICTIONS

### NE PAS Faire

- ❌ **Ne pas** copier-coller une structure existante sans confrontation
- ❌ **Ne pas** présupposer que N0 = "les 9 workflows" (c'est peut-être vrai, peut-être pas)
- ❌ **Ne pas** inventer des endpoints qui n'existent pas dans le code
- ❌ **Ne pas** ignorer les contradictions entre sources

### Faire ABSOLUMENT

- ✅ Lire `WORKFLOW_UTILISATEUR.md` EN ENTIER
- ✅ Parser TOUS les endpoints dans le code
- ✅ Confronter Doc vs Code vs Logs
- ✅ Documenter CHAQUE choix de hiérarchie
- ✅ Lister les incertitudes

---

## 💡 CONSEILS

1. **Commencer simple** : Identifier d'abord les patterns évidents dans le workflow utilisateur
2. **Compter les niveaux** : Combien de "couches" distinctes vois-tu dans la doc ?
3. **Vérifier la cohérence** : Si tu as 4 N0, 9 N1, et 30 N3, c'est cohérent ? Ou déséquilibré ?
4. **Documenter les hésitations** : Si tu hésites entre 2 structures, note les 2 dans le rapport
5. **Tester le JSON** : Utilise `jq` pour valider la syntaxe avant livraison

---

**Bonne chance KIMI Innocent ! Applique la méthode rigoureusement et documente tout. 🚀**
