# ROADMAP — 12 février 2026

**Objectif** : Du qui marche à du qui sert — Interface fonctionnelle

---

## 🎯 PHASE 1 : MATIN (11h-13h) — QUICK WINS

### 1. PropertyEnforcer ⚡ PRIORITÉ 1

**Backend (Claude)** :
- [ ] Créer endpoint `GET /api/genome/{id}/css`
- [ ] Générer CSS avec `!important` pour forcer propriétés Genome
- [ ] Tester avec curl
- **ETA** : 1h

**Frontend (KIMI)** :
- [ ] Créer `property_enforcer.js`
- [ ] Injecter CSS dynamique après render
- [ ] Tester sur 3 Corps (couleurs visibles)
- **ETA** : 30min

**Validation (FJ)** :
- [ ] Vérifier que les couleurs Genome (Brainstorm #fbbf24, Backend #94bbfb, Frontend #9dd5c2) s'affichent correctement
- [ ] Vérifier que le template CSS ne les écrase plus

---

### 2. Drill-down (double-clic) ⚡ PRIORITÉ 1

**Backend (Claude)** :
- [ ] Tester endpoints `/api/drilldown/enter` et `/exit`
- [ ] Vérifier breadcrumb `GET /api/breadcrumb`
- [ ] Documenter format requête/réponse
- **ETA** : 30min

**Frontend (KIMI)** :
- [ ] Écouter événement `dblclick` sur Canvas
- [ ] Appeler `POST /api/drilldown/enter`
- [ ] Afficher Organes (N1) retournés
- [ ] Afficher breadcrumb en haut
- **ETA** : 2h

**Validation (FJ)** :
- [ ] Double-clic sur Corps Brainstorm → voir Organes
- [ ] Breadcrumb visible : "Brainstorm"
- [ ] Bouton retour fonctionnel

---

### 3. Sauvegarde persistance disque 💾 PRIORITÉ 2

**Backend (Claude)** :
- [ ] Ajouter `save_to_file()` dans GenomeStateManager
- [ ] Sauvegarder dans `genome_v2_modified.json`
- [ ] Appel automatique après chaque modification
- **ETA** : 30min

**Frontend (KIMI)** :
- [ ] Rien à faire (Backend automatique)

**Validation (FJ)** :
- [ ] Faire une modification, redémarrer Backend, vérifier que c'est sauvegardé

---

## 🎯 PHASE 2 : APRÈS-MIDI (14h-18h) — CORE FEATURES

### 4. Connexion Backend réelle 🔗 PRIORITÉ 1

**Backend (Claude)** :
- [ ] Vérifier que tous les endpoints répondent
- **ETA** : 15min

**Frontend (KIMI)** :
- [ ] Modifier `stenciler.js` ligne 130 : `/static/4_corps_preview.json` → `http://localhost:8000/api/genome`
- [ ] Ajouter gestion erreurs (fallback mocks si Backend down)
- **ETA** : 30min

**Validation (FJ)** :
- [ ] Vérifier DevTools : API Backend appelée
- [ ] Vérifier que les 3 Corps s'affichent depuis l'API

---

### 5. Undo/Redo ↩️ PRIORITÉ 2

**Backend (Claude)** :
- [ ] Créer `POST /api/modifications/undo`
- [ ] Créer `POST /api/modifications/redo`
- [ ] Ajouter undo_stack et redo_stack
- **ETA** : 1h

**Frontend (KIMI)** :
- [ ] Ajouter boutons Undo/Redo
- [ ] Écouter Ctrl+Z / Ctrl+Shift+Z
- [ ] Appeler endpoints Backend
- **ETA** : 1h

**Validation (FJ)** :
- [ ] Faire modification → Undo → vérifier retour arrière
- [ ] Redo → vérifier réapplication

---

### 6. Snap mode 📐 PRIORITÉ 3

**Backend (Claude)** :
- [ ] N/A (100% Frontend)

**Frontend (KIMI)** :
- [ ] Activer `canvas.snapToGrid = true`
- [ ] Définir grille (ex: 10px)
- [ ] Ajouter toggle UI "Snap: ON/OFF"
- **ETA** : 1h

**Validation (FJ)** :
- [ ] Drag composant → alignement automatique grille
- [ ] Toggle snap OFF → drag libre

---

### 7. Édition inline 📝 PRIORITÉ 3 (SI TEMPS)

**Backend (Claude)** :
- [ ] Créer `PATCH /api/components/{id}/property`
- [ ] Valider propriétés modifiées
- **ETA** : 1h

**Frontend (KIMI)** :
- [ ] Double-clic → mode édition (contentEditable)
- [ ] Changement détecté → appel Backend
- **ETA** : 2h

**Validation (FJ)** :
- [ ] Double-clic texte → éditer inline
- [ ] Changement sauvegardé

---

## 🏆 OBJECTIF FIN DE JOURNÉE (20h)

**Livrables attendus** :
1. ✅ PropertyEnforcer opérationnel (couleurs Genome respectées)
2. ✅ Drill-down fonctionnel (double-clic → navigation)
3. ✅ Sauvegarde persistance (modifications sauvegardées)
4. ✅ Connexion Backend réelle (mocks → API)
5. ✅ Undo/Redo basique
6. ⚠️ Snap mode (si temps)
7. ⚠️ Édition inline (si temps)

**Résultat** : Une page desktop "à peu près potable" avec workflow complet.

---

## 📊 PRIORISATION

**MUST HAVE (non négociable)** :
1. PropertyEnforcer
2. Drill-down
3. Sauvegarde persistance
4. Connexion Backend réelle

**SHOULD HAVE (très utile)** :
5. Undo/Redo

**NICE TO HAVE (confort)** :
6. Snap mode
7. Édition inline

---

## ✅ VALIDATION FJ

**[] On est d'accord sur cette roadmap ?**

Si OUI → on démarre.
Si NON → dites-moi ce qu'il faut changer.
