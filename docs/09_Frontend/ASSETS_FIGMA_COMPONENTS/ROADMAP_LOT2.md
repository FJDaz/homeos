# ROADMAP LOT 2 — 12 février 2026

**Objectif** : Perfectionner l'expérience Stenciler — Du prototype fonctionnel à l'outil de production

**Participants** :
- **Claude** : Backend Lead
- **KIMI** : Frontend Lead
- **François-Jean** : CTO (Validation)

---

## 🎯 STATUT GLOBAL

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  📋 LOT 2 : 5 SECTIONS — 15 ÉTAPES IDENTIFIÉES              ║
║                                                              ║
║  Status : 🔴 EN ATTENTE                                      ║
║                                                              ║
║  Dépend de : LOT 1 (Étapes 1-10) ✅ TERMINÉES                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 📖 CONTEXTE

Ce Lot 2 s'appuie sur les fondations du Lot 1 (Étapes 1-10 terminées) pour apporter des améliorations UX/UI majeures :

**Acquis du Lot 1** :
- ✅ PropertyEnforcer (respect couleurs Genome)
- ✅ Drill-down/up (navigation N0→N3)
- ✅ Undo/Redo (historique visuel)
- ✅ Snap mode (grille magnétique)
- ✅ Édition inline (renommage)
- ✅ Sauvegarde persistance
- ✅ Connexion Backend réelle

**Outils d'orchestration** :
- ✅ Skill `/delegate-kimi` (délégation missions KIMI)
- ✅ Watcher Git LLM (surveillance + métriques Constitution V2.4)
  - ✅ Calcul ICC (Indice Charge Contextuelle)
  - ✅ Snapshots automatiques (si ICC >= 80%)
  - ✅ Compteur Compacts (limite: 4)
  - ✅ Statut visuel 🟢🟠🟣🔴
  - ✅ Alerte CRISE CONTEXTUELLE

**Objectifs du Lot 2** :
- Correspondance visuelle aperçus ↔ drag & drop
- Prémaquettage précis des Corps avec Organes positionnés
- Éditabilité complète des composants N1/N2
- Amélioration ergonomie UI (breadcrumbs cliquables, canvas recentré, raccourcis clavier)
- Font Picker typographique (classifications Vox-ATypI)

---

## 🗂️ ARCHITECTURE DES SECTIONS

### Section 1 : Correspondance Aperçus ↔ Drag & Drop
**Durée estimée** : 4h
**Étapes** : 11, 12, 13

### Section 2 : Prémaquettage Corps avec Organes
**Durée estimée** : 6h
**Étapes** : 14, 15, 16

### Section 3 : Éditabilité N1/N2
**Durée estimée** : 3h
**Étapes** : 17, 18

### Section 4 : Modifications UI
**Durée estimée** : 3h
**Étapes** : 19, 20, 21, 22, 23

### Section 5 : Font Picker
**Durée estimée** : 5h
**Étapes** : 24, 25

---

## 🎯 ÉTAPES SYNCHRONES (PAS DE CHEVAUCHEMENT)

---

### SECTION 1 : CORRESPONDANCE APERÇUS ↔ DRAG & DROP

---

### ÉTAPE 11 : Rendre les aperçus (N0/N1/N2) draggables

**Qui** : KIMI uniquement
**Durée** : 2h
**Dépend de** : Étapes 1-10 terminées
**Status** : 🔴 EN ATTENTE

**Tâches KIMI** :
- [ ] Modifier `Frontend/3. STENCILER/static/stenciler.js`
- [ ] Ajouter attribut `draggable="true"` sur éléments `.preview-item`
- [ ] Implémenter listeners `dragstart` pour chaque aperçu (N0, N1, N2)
- [ ] Transmettre `entity_id` + `niveau` dans `event.dataTransfer`
- [ ] Gérer `dragover` et `drop` sur le canvas Fabric.js
- [ ] Instancier le bon composant selon le niveau (N0→Corps, N1→Organe, N2→Cellule)

**Livrable** :
- Aperçus draggables depuis le preview band
- Drop sur canvas → création d'instance visuelle
- Gestion des 3 niveaux (N0, N1, N2)

**✋ VALIDATION FJ REQUISE** :
- [ ] Drag aperçu "Brainstorm" → canvas
- [ ] Vérifier création Corps
- [ ] Drag aperçu Organe (N1) → canvas
- [ ] Vérifier création Organe
- [ ] **GO** → Passage étape 12

---

### ÉTAPE 12 : Backend endpoint POST /api/components/instantiate

**Qui** : Claude uniquement
**Durée** : 1h30
**Dépend de** : Étape 11 terminée
**Status** : 🔴 EN ATTENTE

**Tâches Claude** :
- [ ] Créer endpoint `POST /api/components/instantiate` dans `Backend/Prod/sullivan/stenciler/api.py`
- [ ] Modèle requête : `{entity_id: str, niveau: str, position: {x: int, y: int}}`
- [ ] Créer instance du composant dans le Genome actif
- [ ] Générer `instance_id` unique (UUID)
- [ ] Retourner composant instancié avec ses propriétés
- [ ] Intégrer avec `ModificationLog` pour persistance
- [ ] Tester avec curl (3 niveaux : N0, N1, N2)

**Livrable** :
- Endpoint fonctionnel : `POST http://localhost:8000/api/components/instantiate`
- Format réponse : `{instance_id, entity_id, niveau, properties, position}`
- Tests validés (curl)
- Documentation pour KIMI

**✅ KIMI PEUT DÉMARRER ÉTAPE 13**

---

### ÉTAPE 13 : Connexion aperçus → Backend instanciation

**Qui** : KIMI uniquement
**Durée** : 30min
**Dépend de** : Étape 12 terminée
**Status** : 🔴 EN ATTENTE

**Tâches KIMI** :
- [ ] Modifier handler `drop` pour appeler `POST /api/components/instantiate`
- [ ] Envoyer `{entity_id, niveau, position: {x, y}}`
- [ ] Récupérer réponse Backend avec `instance_id`
- [ ] Afficher composant sur canvas avec `instance_id`
- [ ] Lier l'objet Fabric.js à l'instance Backend (`fabricObj.data.instance_id`)
- [ ] Gérer erreurs (toast notification)

**Livrable** :
- Drag & drop connecté au Backend
- Instanciation persistante dans Genome
- Objets canvas liés aux instances Backend

**✋ VALIDATION FJ REQUISE** :
- [ ] Drag aperçu → canvas
- [ ] Vérifier appel Backend (DevTools → Network)
- [ ] Refresh page → vérifier persistence
- [ ] **GO** → Passage Section 2

---

### SECTION 2 : PRÉMAQUETTAGE CORPS AVEC ORGANES

---

### ÉTAPE 14 : Définir layouts par défaut dans Genome

**Qui** : Claude uniquement
**Durée** : 2h
**Dépend de** : Section 1 terminée
**Status** : 🔴 EN ATTENTE

**Contexte** :
Actuellement, les Corps n'ont pas de layout par défaut pour leurs Organes. Cette étape ajoute des "templates" de positionnement dans le Genome pour chaque type de Corps.

**Tâches Claude** :
- [ ] Analyser `Backend/Prod/sullivan/genome_v2.json`
- [ ] Ajouter propriété `default_layout` pour chaque Corps N0
- [ ] Format : `{organes: [{entity_id, position: {x, y}, size: {width, height}}]}`
- [ ] Exemples :
  - **Brainstorm** : 3 Organes en disposition horizontale
  - **Backend** : 2 Organes en colonne gauche
  - **Frontend** : 2 Organes en grille 2×1
- [ ] Valider JSON (pas d'erreurs syntax)
- [ ] Documenter format pour KIMI

**Livrable** :
- `genome_v2.json` mis à jour avec `default_layout`
- 3 Corps (Brainstorm, Backend, Frontend) avec layouts définis
- Documentation format layout

**✅ KIMI PEUT DÉMARRER ÉTAPE 15**

---

### ÉTAPE 15 : Backend endpoint GET /api/components/{id}/default_layout

**Qui** : Claude uniquement
**Durée** : 1h
**Dépend de** : Étape 14 terminée
**Status** : 🔴 EN ATTENTE

**Tâches Claude** :
- [ ] Créer endpoint `GET /api/components/{entity_id}/default_layout` dans `api.py`
- [ ] Lire `default_layout` depuis Genome pour le Corps demandé
- [ ] Retourner liste Organes avec positions/tailles
- [ ] Gérer cas où `default_layout` est absent (retourner `[]`)
- [ ] Tester avec curl (3 Corps)

**Livrable** :
- Endpoint fonctionnel : `GET http://localhost:8000/api/components/brainstorm/default_layout`
- Format réponse : `{organes: [{entity_id, position, size}]}`
- Tests validés

**✅ KIMI PEUT DÉMARRER ÉTAPE 16**

---

### ÉTAPE 16 : Prémaquettage automatique au drill-down

**Qui** : KIMI uniquement
**Durée** : 3h
**Dépend de** : Étape 15 terminée
**Status** : 🔴 EN ATTENTE

**Tâches KIMI** :
- [ ] Modifier `static/drilldown_manager.js`
- [ ] Après appel `POST /api/drilldown/enter`, appeler `GET /api/components/{id}/default_layout`
- [ ] Si layout par défaut existe :
  - [ ] Instancier les Organes sur canvas avec positions/tailles définies
  - [ ] Ne pas les empiler au hasard
- [ ] Si layout absent :
  - [ ] Continuer comportement actuel (empilement)
- [ ] Permettre déplacement manuel après prémaquettage
- [ ] Sauvegarder modifications layout utilisateur (appel PATCH Backend)

**Livrable** :
- Drill-down → Organes positionnés selon layout Genome
- Éditable par utilisateur après prémaquettage
- Persistance des modifications layout

**✋ VALIDATION FJ REQUISE** :
- [ ] Double-clic Corps "Brainstorm"
- [ ] Vérifier 3 Organes positionnés selon layout
- [ ] Déplacer manuellement un Organe
- [ ] Drill-up puis drill-down → vérifier position modifiée conservée
- [ ] **GO** → Passage Section 3

---

### SECTION 3 : ÉDITABILITÉ N1/N2

---

### ÉTAPE 17 : Backend PATCH /api/components/{id}/configuration

**Qui** : Claude uniquement
**Durée** : 1h30
**Dépend de** : Section 2 terminée
**Status** : 🔴 EN ATTENTE

**Contexte** :
Actuellement, seules les propriétés simples (titre, couleur) sont éditables. Cette étape permet de modifier la **configuration interne** d'un composant (N1, N2) : ajouter/retirer des sous-composants, modifier leurs relations.

**Tâches Claude** :
- [ ] Créer endpoint `PATCH /api/components/{entity_id}/configuration`
- [ ] Modèle requête : `{action: "add"|"remove", child_entity_id: str, position?: {x, y}}`
- [ ] Validation : vérifier que le niveau enfant est cohérent (N1→N2, N2→N3)
- [ ] Mettre à jour Genome
- [ ] Intégrer `ModificationLog` pour undo/redo
- [ ] Tester avec curl (ajout/retrait Organe dans Corps)

**Livrable** :
- Endpoint fonctionnel : `PATCH http://localhost:8000/api/components/{id}/configuration`
- Actions : `add`, `remove`
- Tests validés
- Documentation pour KIMI

**✅ KIMI PEUT DÉMARRER ÉTAPE 18**

---

### ÉTAPE 18 : Interface édition configuration N1/N2

**Qui** : KIMI uniquement
**Durée** : 1h30
**Dépend de** : Étape 17 terminée
**Status** : 🔴 EN ATTENTE

**Tâches KIMI** :
- [ ] Ajouter bouton "⚙️ Configurer" dans sidebar (visible quand composant N1/N2 sélectionné)
- [ ] Ouvrir modal "Configuration du composant"
- [ ] Liste des enfants actuels (N2 pour N1, N3 pour N2)
- [ ] Bouton "➕ Ajouter enfant" → dropdown liste entités disponibles
- [ ] Bouton "🗑️ Retirer" sur chaque enfant
- [ ] Appeler `PATCH /api/components/{id}/configuration` pour chaque action
- [ ] Rafraîchir canvas après modification

**Livrable** :
- Modal configuration fonctionnelle
- Ajout/retrait enfants
- Synchronisation Backend

**✋ VALIDATION FJ REQUISE** :
- [ ] Sélectionner un Organe (N1)
- [ ] Clic "⚙️ Configurer"
- [ ] Ajouter une Cellule (N2)
- [ ] Vérifier apparition sur canvas
- [ ] Retirer la Cellule
- [ ] **GO** → Passage Section 4

---

### SECTION 4 : MODIFICATIONS UI

---

### ÉTAPE 19 : Breadcrumbs cliquables dans header

**Qui** : KIMI uniquement
**Durée** : 45min
**Dépend de** : Section 3 terminée
**Status** : 🔴 EN ATTENTE

**Tâches KIMI** :
- [ ] Déplacer breadcrumbs depuis sidebar vers `<div class="stenciler-header">`
- [ ] Rendre chaque élément breadcrumb cliquable
- [ ] Format : `N0 > N1 > N2` (clic sur N0 → retour niveau 0, clic sur N1 → retour niveau 1)
- [ ] Appeler `POST /api/drilldown/exit` avec niveau cible
- [ ] Supprimer bouton "↩️ Retour" (remplacé par breadcrumbs)
- [ ] Remplacer emojis par pictos SVG (Material Icons ou Feather Icons)

**Livrable** :
- Breadcrumbs dans header
- Navigation cliquable entre niveaux
- Pictos SVG au lieu d'emojis

**✋ VALIDATION FJ REQUISE** :
- [ ] Drill-down jusqu'à N2
- [ ] Clic sur breadcrumb N0 → retour racine
- [ ] Vérifier navigation fluide
- [ ] **GO** → Étape suivante

---

### ÉTAPE 20 : Recentrer canvas placeholder

**Qui** : KIMI uniquement
**Durée** : 15min
**Dépend de** : Étape 19 terminée
**Status** : 🔴 EN ATTENTE

**Tâches KIMI** :
- [ ] Modifier `Frontend/3. STENCILER/static/styles.css`
- [ ] Identifier règle CSS pour `#canvas-placeholder`
- [ ] Ajuster `margin`, `left`, ou layout flex/grid pour centrer le canvas
- [ ] Vérifier responsive (pas de débordement)

**Livrable** :
- Canvas visuellement centré dans la zone de travail

**✋ VALIDATION FJ REQUISE** :
- [ ] Vérifier centrage canvas
- [ ] **GO** → Étape suivante

---

### ÉTAPE 21 : Raccourci touche X (toggle fond/contour)

**Qui** : KIMI uniquement
**Durée** : 30min
**Dépend de** : Étape 20 terminée
**Status** : 🔴 EN ATTENTE

**Tâches KIMI** :
- [ ] Écouter touche `X` (keydown)
- [ ] Si objet sélectionné sur canvas :
  - [ ] Toggle entre mode "Fill" et mode "Stroke"
  - [ ] Mode Fill : `fill=couleur`, `stroke=transparent`
  - [ ] Mode Stroke : `fill=transparent`, `stroke=couleur`, `strokeWidth=2`
- [ ] Indicateur visuel (tooltip ou badge) pour mode actif

**Livrable** :
- Touche X fonctionnelle
- Toggle fond/contour instantané

**✋ VALIDATION FJ REQUISE** :
- [ ] Sélectionner un Corps
- [ ] Appuyer sur X → contour uniquement
- [ ] Appuyer sur X → fond rétabli
- [ ] **GO** → Étape suivante

---

### ÉTAPE 22 : Couleur "none" dans color picker

**Qui** : KIMI uniquement
**Durée** : 30min
**Dépend de** : Étape 21 terminée
**Status** : 🔴 EN ATTENTE

**Tâches KIMI** :
- [ ] Ajouter option "None" dans color picker sidebar
- [ ] Représentation visuelle : carré avec diagonale rouge (⊗ transparent)
- [ ] Clic sur "None" :
  - [ ] Si mode Fill → `fill=transparent`
  - [ ] Si mode Stroke → `stroke=transparent`
- [ ] Sauvegarder valeur `"none"` dans propriété Backend

**Livrable** :
- Option "None" dans color picker
- Rendu transparent fonctionnel

**✋ VALIDATION FJ REQUISE** :
- [ ] Sélectionner un composant
- [ ] Choisir couleur "None"
- [ ] Vérifier transparence
- [ ] **GO** → Étape suivante

---

### ÉTAPE 23 : Remplacer emojis par icônes SVG

**Qui** : KIMI uniquement
**Durée** : 1h
**Dépend de** : Étape 22 terminée
**Status** : 🔴 EN ATTENTE

**Contexte** :
Actuellement, l'interface utilise des emojis (📐, ↩️, ↪️, etc.). Remplacer par des icônes SVG professionnelles.

**Tâches KIMI** :
- [ ] Choisir bibliothèque : **Material Icons**, **Feather Icons**, ou **Heroicons**
- [ ] Identifier tous les emojis dans `static/stenciler.js` et `templates/stenciler.html`
- [ ] Remplacer par `<svg>` inline ou via CDN
- [ ] Exemples :
  - 📐 Snap Mode → `<svg>...</svg>` (grid icon)
  - ↩️ Undo → undo arrow icon
  - ↪️ Redo → redo arrow icon
  - ⚙️ Configurer → settings icon
- [ ] Ajuster tailles/couleurs CSS pour cohérence visuelle

**Livrable** :
- Tous emojis remplacés par icônes SVG
- Interface plus professionnelle

**✋ VALIDATION FJ REQUISE** :
- [ ] Vérifier apparence générale
- [ ] **GO** → Passage Section 5

---

### SECTION 5 : FONT PICKER

---

### ÉTAPE 24 : Backend intégration Google Fonts API

**Qui** : Claude uniquement
**Durée** : 2h
**Dépend de** : Section 4 terminée
**Status** : 🔴 EN ATTENTE

**Contexte** :
Intégrer un système de sélection de polices selon les classifications typographiques **Vox-ATypI**.

**Tâches Claude** :
- [ ] Créer endpoint `GET /api/fonts/categories`
- [ ] Retourner liste polices Google Fonts classées par catégorie :
  - **Humanes** : 5 polices (ex: Garamond, Jenson)
  - **Garaldes** : 10 polices (ex: Times, Baskerville)
  - **Réales** : 10 polices (ex: Georgia, Palatino)
  - **Didones** : 10 polices (ex: Bodoni, Didot)
  - **Mécanes modernes** : 4 polices (ex: Rockwell, Courier)
  - **Mécanes classiques** : 4 polices (ex: Clarendon)
  - **Linéales humanistiques** : 20 polices (ex: Gill Sans, Optima)
  - **Linéales géométriques** : 20 polices (ex: Futura, Avenir)
  - **Scriptes** : 20 polices (ex: Brush Script)
  - **Manuaires** : 20 polices (ex: Comic Sans)
  - **Non-latines** : 20 polices (ex: Noto Sans CJK)
  - **Fractures** : 10 polices (ex: Fraktur, Old English)
- [ ] Utiliser **Google Fonts API** pour récupérer listes
- [ ] Cacher résultat pour performances
- [ ] Tester avec curl

**Livrable** :
- Endpoint fonctionnel : `GET http://localhost:8000/api/fonts/categories`
- Format : `{category: string, fonts: [{name, family, variants}]}`
- 12 catégories Vox-ATypI
- Documentation pour KIMI

**✅ KIMI PEUT DÉMARRER ÉTAPE 25**

---

### ÉTAPE 25 : Font Picker UI dans sidebar

**Qui** : KIMI uniquement
**Durée** : 3h
**Dépend de** : Étape 24 terminée
**Status** : 🔴 EN ATTENTE

**Tâches KIMI** :
- [ ] Ajouter section "🔤 Font Picker" dans sidebar
- [ ] Fetch `GET /api/fonts/categories`
- [ ] Afficher dropdown 1 : "Catégorie" (12 choix)
- [ ] Afficher dropdown 2 : "Police" (liste polices de la catégorie)
- [ ] Aperçu typographique en direct (texte "Abc 123" dans la police sélectionnée)
- [ ] Appliquer police au composant sélectionné (propriété `font-family`)
- [ ] Charger dynamiquement police via Google Fonts CDN (`<link>` dans `<head>`)
- [ ] Sauvegarder choix dans Backend (`PATCH /api/components/{id}/property`)

**Livrable** :
- Font Picker fonctionnel
- 12 catégories Vox-ATypI
- Aperçu typographique en direct
- Synchronisation Backend

**✋ VALIDATION FJ REQUISE** :
- [ ] Ouvrir Font Picker
- [ ] Choisir "Garaldes" → "Times New Roman"
- [ ] Vérifier aperçu "Abc 123" dans la police
- [ ] Appliquer à un composant
- [ ] Vérifier rendu sur canvas
- [ ] **GO** → LOT 2 TERMINÉ

---

## 🏆 POINTS D'ARRÊT ET VALIDATION

**SECTION 1 (Étapes 11-13)** : Drag & drop aperçus → **✋ VALIDATION FJ OBLIGATOIRE**
**SECTION 2 (Étapes 14-16)** : Prémaquettage Corps → **✋ VALIDATION FJ OBLIGATOIRE**
**SECTION 3 (Étapes 17-18)** : Éditabilité N1/N2 → **✋ VALIDATION FJ OBLIGATOIRE**
**SECTION 4 (Étapes 19-23)** : Améliorations UI → **✋ VALIDATION FJ RECOMMANDÉE**
**SECTION 5 (Étapes 24-25)** : Font Picker → **✋ VALIDATION FJ OBLIGATOIRE**

---

## ⚠️ RÈGLES ANTI-CHEVAUCHEMENT

1. **Une étape à la fois** — Pas de parallélisme Claude/KIMI
2. **Validation obligatoire** — FJ valide avant passage section suivante
3. **KIMI attend Claude** — Sur étapes 12, 14, 15, 17, 24
4. **Claude attend KIMI** — Sur étapes 11, 13, 16, 18
5. **Communication ici** — Annoncer "Étape X terminée" avant de passer à la suivante

---

## 📊 TIMING OPTIMISTE

| Section | Étapes | Durée | Heure fin cumulée |
|---------|--------|-------|-------------------|
| **1. Drag & Drop** | 11-13 | 4h | 4h |
| **2. Prémaquettage** | 14-16 | 6h | 10h |
| **3. Éditabilité** | 17-18 | 3h | 13h |
| **4. UI** | 19-23 | 3h | 16h |
| **5. Font Picker** | 24-25 | 5h | **21h** |

**Objectif réaliste** : 3 jours de développement (7h/jour)

---

## 🔗 LIENS UTILES

- Backend API: http://localhost:8000
- Frontend Stenciler: http://localhost:9998/stenciler
- Genome Viewer: http://localhost:9998/
- API Health: http://localhost:8000/health
- API Docs: http://localhost:8000/docs
- Google Fonts API: https://fonts.google.com/

---

## 📞 COMMUNICATION

**Questions Backend/API** → Poser ici directement à Claude
**Questions Frontend/Rendu** → Poser ici directement à KIMI
**Validation GO/NO-GO** → François-Jean

---

## ✅ VALIDATION FINALE

**Status** : 🔴 **EN ATTENTE DÉMARRAGE**

Prêt à démarrer le Lot 2 après validation FJ du Lot 1.

---

## 📦 ÉVOLUTIONS FUTURES (Post-LOT 2)

**Status** : 📋 **BACKLOG** — Pas de date fixée

| Priorité | Fonctionnalité | Description | Complexité |
|----------|----------------|-------------|------------|
| 🟡 P1 | **Multi-sélection** | Sélectionner plusieurs objets + drag groupé | 2h |
| 🟢 P2 | **Copy/Paste** | Dupliquer des objets sur le canvas | 1h |
| 🔵 P3 | **Export PNG/SVG** | Exporter le canvas en image | 2h |
| 🔵 P3 | **Grid visible** | Afficher la grille de snap en arrière-plan | 1h |
| 🔵 P3 | **Historique Backend** | Sync undo/redo avec Backend (actuellement local) | 3h |

---

**Créé le** : 12 février 2026
**Auteur** : Claude Sonnet 4.5 (Backend Lead)
**Basé sur** : Notes François-Jean "Feuille de route FJ Lot 2.txt"
