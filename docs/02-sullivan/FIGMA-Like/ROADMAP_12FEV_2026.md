# ROADMAP — 12 février 2026

**Objectif** : Du qui marche à du qui sert — Interface fonctionnelle pour construire une interface

**Participants** :
- **Claude** : Backend Lead
- **KIMI** : Frontend Lead
- **François-Jean** : CTO (Validation)

---

## 🎯 ÉTAPES SYNCHRONES (PAS DE CHEVAUCHEMENT)

### ÉTAPE 1 : PropertyEnforcer Backend (✅ TERMINÉE)

**Qui** : Claude uniquement
**Durée** : 45min (réalisé)
**Statut** : ✅ **TERMINÉE 10:46**

**Tâches Claude** :
- [x] Créer endpoint `GET /api/genome/{id}/css` → `Backend/Prod/sullivan/stenciler/api.py:368`
- [x] Générer CSS avec `!important` pour forcer propriétés Genome
- [x] Tester : `curl http://localhost:8000/api/genome/default/css` → OK (6 règles CSS)
- [x] Redémarrer Backend (PID 2230)
- [x] Documenter pour KIMI → `docs/02-sullivan/mailbox/kimi/PROPERTY_ENFORCER_BACKEND_READY.md`

**Livrable** :
- Endpoint fonctionnel : http://localhost:8000/api/genome/default/css
- 6 règles CSS générées (3 Corps + 3 Organes)
- Documentation complète avec exemple de code pour KIMI

**✅ KIMI PEUT DÉMARRER ÉTAPE 2**

---

### ÉTAPE 2 : PropertyEnforcer Frontend (🔴 BLOQUANT)

**Qui** : KIMI uniquement
**Durée** : 30min
**Dépend de** : Étape 1 terminée

**Tâches KIMI** :
- [ ] Créer fichier `Frontend/3. STENCILER/static/property_enforcer.js`
- [ ] Fetch CSS depuis `http://localhost:8000/api/genome/default/css`
- [ ] Injecter dans `<style id="genome-enforced">`
- [ ] Tester sur 3 Corps (Brainstorm #fbbf24, Backend #94bbfb, Frontend #9dd5c2)

**✋ VALIDATION FJ REQUISE** :
- [x] Ouvrir http://localhost:9998/stenciler
- [x] Vérifier couleurs Genome visibles
- [x] **GO** → Passage étape 3

**CR KIMI** :
- `property_enforcer.js` créé (3KB, 90 lignes)
- Module auto-init au DOMContentLoaded
- Fetch CSS depuis :8000/api/genome/default/css
- Injection `<style id="genome-enforced">` avec !important
- Console: "✅ Propriétés Genome appliquées"
- **Validation FJ**: Couleurs OK (Brainstorm #fbbf24, Backend #94bbfb, Frontend #9dd5c2)

---

### ÉTAPE 3 : Drill-down Backend (✅ TERMINÉE)

**Qui** : Claude uniquement
**Durée** : 30min (réalisé)
**Statut** : ✅ **TERMINÉE 14:15**

**Tâches Claude** :
- [x] Corriger endpoints existants (`POST /api/drilldown/enter`, `/exit`, `GET /api/breadcrumb`)
- [x] Corriger bug calcul niveau dans `DrillDownManager` → `Backend/Prod/sullivan/stenciler/drilldown_manager.py:163`
- [x] Documenter format requête/réponse avec exemples curl
- [x] Tester avec curl (3 endpoints OK)
- [x] Redémarrer Backend (PID 62093+)
- [x] Documenter pour KIMI → `docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md`

**Livrable** :
- Endpoints fonctionnels :
  - POST http://localhost:8000/api/drilldown/enter
  - POST http://localhost:8000/api/drilldown/exit
  - GET http://localhost:8000/api/breadcrumb
- Tests curl réussis (N0→N1, retour, breadcrumb)
- Documentation complète avec exemples pour KIMI

**✅ KIMI PEUT DÉMARRER ÉTAPE 4**

---

### ÉTAPE 4 : Drill-down Frontend (🔴 BLOQUANT)

**Qui** : KIMI uniquement
**Durée** : 2h
**Dépend de** : Étape 3 terminée

**Tâches KIMI** :
- [ ] Écouter `dblclick` sur Canvas Fabric.js
- [ ] Récupérer `entity_id` du composant
- [ ] Appeler `POST /api/drilldown/enter`
- [ ] Afficher Organes (N1) retournés
- [ ] Afficher breadcrumb en haut
- [ ] Bouton "Retour" → `POST /api/drilldown/exit`

**✋ VALIDATION FJ REQUISE** :
- [ ] Double-clic Corps "Brainstorm" → voir Organes
- [ ] Breadcrumb visible
- [ ] Bouton retour fonctionne
- [ ] GO/NO-GO avant étape suivante

---

### ÉTAPE 5 : Sauvegarde persistance (🟡 MOYENNE)

**Qui** : Claude uniquement
**Durée** : 30min
**Bloque** : Rien (KIMI peut se reposer)

**Tâches Claude** :
- [ ] Ajouter `save_to_file()` dans `GenomeStateManager`
- [ ] Sauvegarder dans `Backend/Prod/sullivan/genome_v2_modified.json`
- [ ] Appeler automatiquement après `POST /api/modifications`
- [ ] Charger depuis fichier au démarrage

**✋ VALIDATION FJ REQUISE** :
- [ ] Faire modification dans interface
- [ ] Redémarrer Backend
- [ ] Vérifier modification conservée
- [ ] GO/NO-GO avant étape suivante

---

### ÉTAPE 6 : Connexion Backend réelle (🔴 BLOQUANT)

**Qui** : KIMI uniquement (Claude vérifie juste)
**Durée** : 30min
**Dépend de** : Étape 5 terminée

**Tâches Claude (5min)** :
- [ ] Vérifier `GET /api/genome` retourne 3 Corps
- [ ] `curl http://localhost:8000/api/genome | jq '.genome.n0_phases[].name'`

**Tâches KIMI (30min)** :
- [ ] Modifier `Frontend/3. STENCILER/static/stenciler.js` ligne ~130
- [ ] Remplacer `fetch('/static/4_corps_preview.json')` par `fetch('http://localhost:8000/api/genome')`
- [ ] Ajouter gestion erreurs (fallback mocks si Backend down)
- [ ] Adapter parsing : `data.genome.n0_phases` au lieu de `data.corps`

**✋ VALIDATION FJ REQUISE** :
- [ ] DevTools → Network
- [ ] Recharger http://localhost:9998/stenciler
- [ ] Vérifier appel API (statut 200)
- [ ] Vérifier 3 Corps affichés
- [ ] GO/NO-GO avant étape suivante

---

### ÉTAPE 7 : Undo/Redo Backend (🟡 SI TEMPS)

**Qui** : Claude uniquement
**Durée** : 1h
**Bloque** : KIMI attend la fin

**Tâches Claude** :
- [ ] Créer `POST /api/modifications/undo`
- [ ] Créer `POST /api/modifications/redo`
- [ ] Ajouter `undo_stack` et `redo_stack` dans `ModificationLog`
- [ ] Retourner nouvel état après undo/redo
- [ ] Documenter avec exemples

**✋ KIMI ATTEND ICI** — Ne pas commencer boutons avant

---

### ÉTAPE 8 : Undo/Redo Frontend (🟡 SI TEMPS)

**Qui** : KIMI uniquement
**Durée** : 1h
**Dépend de** : Étape 7 terminée

**Tâches KIMI** :
- [ ] Ajouter boutons "↩️ Undo" et "↪️ Redo" dans header
- [ ] Écouter `Ctrl+Z` → Undo, `Ctrl+Shift+Z` → Redo
- [ ] Appeler endpoints Backend
- [ ] Rafraîchir Canvas avec nouvel état

**✋ VALIDATION FJ REQUISE** :
- [ ] Drag composant
- [ ] Ctrl+Z → vérifier retour
- [ ] Ctrl+Shift+Z → vérifier réapplication

---

### ÉTAPE 9 : Snap mode (🟢 SI TEMPS, FRONTEND SEUL)

**Qui** : KIMI uniquement
**Durée** : 1h
**Dépend de** : Rien (peut se faire entre deux étapes)

**Tâches KIMI** :
- [ ] Activer `canvas.snapToGrid = true` dans Fabric.js
- [ ] Définir grille 10px
- [ ] Toggle UI "📐 Snap: ON/OFF"
- [ ] localStorage persistence

**✋ VALIDATION FJ** : Drag → alignement grille

---

### ÉTAPE 10 : Édition inline (🟢 SI TEMPS, COMPLEXE)

**Qui** : Claude puis KIMI
**Durée** : 3h total (1h Claude + 2h KIMI)

**Tâches Claude (1h)** :
- [ ] `PATCH /api/components/{id}/property`
- [ ] Validation + ModificationLog
- [ ] Documentation

**Tâches KIMI (2h)** :
- [ ] Double-clic → contentEditable
- [ ] Changement → appel Backend
- [ ] Feedback visuel

**✋ VALIDATION FJ** : Double-clic → éditer → Enter → sauvegardé

---

## 🏆 POINTS D'ARRÊT ET VALIDATION

**MINIMUM VIABLE (Étapes 1-6)** :
- Étape 1-2 : PropertyEnforcer → **✋ VALIDATION FJ OBLIGATOIRE**
- Étape 3-4 : Drill-down → **✋ VALIDATION FJ OBLIGATOIRE**
- Étape 5 : Sauvegarde → **✋ VALIDATION FJ OBLIGATOIRE**
- Étape 6 : Connexion réelle → **✋ VALIDATION FJ OBLIGATOIRE**

**SI TEMPS (Étapes 7-10)** :
- Étape 7-8 : Undo/Redo → **✋ VALIDATION FJ RECOMMANDÉE**
- Étape 9 : Snap mode → **✋ VALIDATION FJ OPTIONNELLE**
- Étape 10 : Édition inline → **✋ VALIDATION FJ OPTIONNELLE**

**Résultat attendu (Étapes 1-6)** : Workflow fonctionnel complet = PropertyEnforcer + Drill-down + Sauvegarde + API Backend réelle

---

## ⚠️ RÈGLES ANTI-CHEVAUCHEMENT

1. **Une étape à la fois** — Pas de parallélisme Claude/KIMI
2. **Validation obligatoire** — FJ valide avant passage étape suivante
3. **KIMI attend Claude** — Sur étapes 1, 3, 5, 7
4. **Claude attend KIMI** — Sur étapes 2, 4
5. **Communication ici** — Annoncer "Étape X terminée" avant de passer à la suivante

---

## 📊 TIMING OPTIMISTE

| Étape | Durée | Heure fin |
|-------|-------|-----------|
| 1. PropertyEnforcer Backend | 1h | 12h00 |
| 2. PropertyEnforcer Frontend | 30min | 12h30 |
| ✋ PAUSE DÉJEUNER | 1h30 | 14h00 |
| 3. Drill-down Backend | 30min | 14h30 |
| 4. Drill-down Frontend | 2h | 16h30 |
| 5. Sauvegarde | 30min | 17h00 |
| 6. Connexion réelle | 30min | 17h30 |
| **MINIMUM VIABLE ATTEINT** | | **17h30** |
| 7. Undo/Redo Backend | 1h | 18h30 |
| 8. Undo/Redo Frontend | 1h | 19h30 |
| 9. Snap mode | 1h | 20h30 |
| 10. Édition inline | 3h | 23h30 |

**Objectif réaliste** : Étapes 1-6 (minimum viable) pour 17h30

---

## 🔗 LIENS UTILES

- Backend API: http://localhost:8000
- Frontend: http://localhost:9998/stenciler
- Genome Viewer: http://localhost:9998/
- API Health: http://localhost:8000/health
- API Docs: http://localhost:8000/docs

---

## 📞 COMMUNICATION

**Questions Backend/API** → Poser ici directement à Claude
**Questions Frontend/Rendu** → Poser ici directement à KIMI
**Validation GO/NO-GO** → François-Jean

---

---

## ✅ VALIDATION FINALE

**Status** : ⏳ **EN ATTENTE GO FJ**

**François-Jean, êtes-vous d'accord avec cette roadmap SYNCHRONE (pas de chevauchement) ?**

Si OUI → Claude démarre Étape 1 (PropertyEnforcer Backend)
Si NON → Dites ce qu'il faut modifier
