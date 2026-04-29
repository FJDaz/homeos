# Plan : Workflow idéal Sullivan (template → écrans câblés)

## Workflow cible (résumé)

1. **Image** → analyse (designer) → **génération HTML** à partir du design  
2. **Inférence de principes graphiques** génériques basés sur le template  
3. **Câblage avec le backend** (genome/API)  
4. **Plan de génération des écrans** nécessaires à l’expression du genome  
5. **Génération des corps** (écrans) → **STOP**  
6. **Corps 1 (écran 1)** : proposition des **organes** selon lecture du genome  
7. **Interaction user** (chatbot Sullivan, z-index 10) pour affinage des **cellules** (molécules) en adéquation avec le dernier template  
8. Si mauvaise interprétation → **upload addendum graphique** → questions Sullivan → affinage en interaction → **passage au corps 2**, etc.

---

## Ce qui existe déjà (Sullivan lit et construit)

| Brique | Rôle actuel | Fichier / composant |
|--------|-------------|----------------------|
| **Designer** | Lit l’image, extrait structure (sections, composants), Miroir (Intention → Corps → Organes → Molécules → Atomes) | `sullivan/modes/designer_mode.py`, `design_analyzer.py`, `ui_inference_engine.py` |
| **Build** | Genome (JSON) → HTML single-file | `sullivan/builder/sullivan_builder.py`, `refinement.py` |
| **Genome** | OpenAPI → `homeos_genome.json` (endpoints, topology) | `core/genome_generator.py` |
| **UI inference** | Propose intention, corps, organes, molécules, atomes | `ui_inference_engine.py` |
| **Knowledge** | Patterns, STAR, matching | `knowledge/knowledge_base.py` |

**Manques principaux :**

- Designer ne produit **pas** de HTML, seulement une structure (JSON).
- Pas d’**extraction de principes graphiques** (couleurs, typo, espacements) depuis le template.
- Pas de **plan d’écrans** dérivé du genome puis génération **corps par corps**.
- Pas de **chatbot** Sullivan (z-index 10) pour affinage par écran.
- Pas d’**addendum graphique** ni de boucle « question Sullivan → affinage → passage au corps suivant ».

---

## Phases de construction

### Phase 1 : Template → HTML (designer produit la page)

**Objectif :** À partir d’une image (template), produire un **fichier HTML/CSS/JS** (single-file) qui reflète le design, en **partant d’une page entièrement vierge** (autoconstruction).

- **Entrée :** image (template), optionnellement `frontend_structure` du designer actuel.
- **Sortie :** `output/studio/studio_index.html` généré **à partir du design uniquement**, pas du genome.

#### Contrainte : page vierge (autoconstruction)

En Phase 1 nous sommes en **autoconstruction** : aucun layout préexistant. Sullivan ne doit **pas** s’appuyer sur un squelette genome (sidebar + organes) ni sur un thème par défaut. Il part d’une **page blanche** et construit le HTML/CSS/JS uniquement à partir de :
1. L’**analyse du template** (structure design + composants),
2. La **webographie de référence** (tendances webdesign ci‑dessous).

Le générateur reçoit donc en entrée : structure design + (optionnel) description visuelle du template ; **pas** de HTML pré-rempli.

#### Références webdesign (webographie Sullivan)

Les tendances sur lesquelles Sullivan s’appuie pour interpréter les templates sont décrites dans :

**`docs/02-sullivan/Références webdesign de Sullivan.md`**

Résumé des **8 URLs stratégiques** à injecter dans le prompt (analyse comparative, « grammaire » visuelle) :

| Tendance | URL | Rôle pour l’interprétation |
|----------|-----|----------------------------|
| Brutalisme radical | gumroad.com | Trait noir épais, aplats ; identité visuelle Sullivan. |
| Logiciel d’élite | linear.app | Clarté, minimalisme sombre, listes, menus contextuels. |
| Utilitaire brut | tally.so | Formulaires ultra-propres (x-ui-hint: form). |
| Ingénierie UX | vercel.com/dashboard | Pipelines, déploiement (Phase Deploy). |
| Micro-typographie | ia.net | Vide, lisibilité (ex. Terminal Emulator). |
| Grille tactile | family.co | Relief, skeuomorphisme, physique des composants. |
| Navigation systémique | stripe.com/docs | Structure menu (ex. Brainstorm > Back > Front). |
| Origine du web | berkshirehathaway.com | Minimalisme HTML sans CSS, probité. |

**Instruction à ancrer dans le prompt (Phase 1) :**  
*« Sullivan, pour interpréter mon template et générer le HTML, base-toi sur les patterns de navigation de Stripe, la rigueur typographique de iA.net et l’esthétique brute de Gumroad. Voici les URLs de référence : [liste]. Ton but : extraire la grammaire de ces sites pour l’appliquer à l’autoconstruction du Studio à partir d’une page vierge. »*

Le module Phase 1 doit **charger** le contenu (ou le chemin) de `Références webdesign de Sullivan.md` et l’injecter dans le contexte du générateur HTML (Gemini).

#### Implémentation possible

- Nouveau module (ex. `sullivan/generator/design_to_html.py`) ou extension de DesignerMode :
  - **Entrée :** `design_structure`, `frontend_structure`, chemin vers l’image (ou description), **chemin vers la webographie** (`docs/02-sullivan/Références webdesign de Sullivan.md`).
  - **Pas de squelette HTML en entrée** : prompt du type « À partir de cette structure de design et de cette image, et en t’appuyant sur les références webdesign fournies, produis un document HTML/CSS/JS **complet**, single-file, brutalist. Partir d’une page vierge (pas de layout pré-défini). »
- Utiliser la **structure design** (sections, composants) + le **texte de la webographie** (ou les URLs + résumé) comme contexte Gemini.
- Écrire le résultat dans `output/studio/studio_index.html` (ou chemin configurable).

**Livrable :**  
Une commande ou option du type `sullivan -d image.png --output-html` qui produit une page HTML alignée sur le template, construite **from scratch** avec la webographie Sullivan.

---

### Phase 2 : Principes graphiques depuis le template

**Objectif :** Extraire du template des **règles réutilisables** (couleurs, typo, espacements, style) pour tous les écrans.

- **Entrée :** image + structure design (sections, composants).
- **Sortie :** structure « design tokens » / principes (ex. `primary_color`, `font_family`, `spacing_unit`, `border_radius`).

**Implémentation possible :**

- Dans `DesignAnalyzer` ou un nouveau `DesignPrinciplesExtractor` : appel Gemini Vision avec prompt du type « À partir de cette maquette, liste les principes graphiques (couleurs principales, typographie, espacements, style des bords, ombres). Retourne du JSON. »
- Stocker le résultat (ex. `output/studio/design_principles.json`) et l’injecter dans toutes les étapes suivantes (génération HTML, génération des corps).

**Livrable :**  
Fichier de principes généré à chaque analyse de template, et utilisé par le générateur HTML (phase 1) et les écrans (phases suivantes).

---

### Phase 3 : Câblage genome + plan d’écrans

**Objectif :** Relier le **genome** (API) au design et définir **quels écrans** (corps) sont nécessaires pour exprimer le genome.

- **Entrée :** genome (`homeos_genome.json`) + structure design (et principes).
- **Sortie :** **Plan d’écrans** : liste de « corps » (écran 1, écran 2, …), chacun avec les endpoints / flux du genome qu’il doit exprimer.

**Implémentation possible :**

- Module **ScreenPlanner** : à partir du genome (topology, endpoints, x_ui_hint), produire une liste de corps (écrans) et pour chaque corps la liste des organes (blocs fonctionnels) et leur lien aux endpoints.
- Réutiliser la logique existante de `ui_inference_engine` (intention, corps, organes) en l’alimentant avec le genome au lieu d’une global function simulée.
- Stocker le plan (ex. `output/studio/screen_plan.json`) : `[{ "corps_id": "1", "label": "…", "organes": [...], "endpoints": [...] }, …]`.

**Livrable :**  
Un « plan de génération des écrans » exploitable par la phase 4 (génération des corps) et la phase 5 (organes par écran).

---

### Phase 4 : Génération des corps (écrans) puis STOP

**Objectif :** Générer **un squelette par écran** (corps 1, corps 2, …) à partir du plan et du template, puis **s’arrêter** (pas encore d’affinage organe par organe).

- **Entrée :** plan d’écrans (phase 3) + principes graphiques (phase 2) + dernier template (ou structure design).
- **Sortie :** Pour chaque corps, une **page/écran** (HTML ou structure) minimale : layout, zones, pas encore d’organes détaillés (ou placeholders).

**Implémentation possible :**

- Boucle sur chaque corps du plan : pour chaque corps, générer un fragment HTML (ou une section) en respectant les principes et la structure du template.
- Assemblage soit en **une seule page** (sections ancrées) soit en **plusieurs fichiers** (un par écran). Choix à trancher (single-page vs multi-page).
- **STOP** après génération de tous les corps : pas encore d’interaction user, pas encore d’affinage des organes.

**Livrable :**  
Application avec N écrans (corps) générés, prête à passer en phase 5 (focus sur corps 1 + chatbot).

---

### Phase 5 : Corps 1 – Organes + Chatbot Sullivan (z-index 10)

**Objectif :** Sur **l’écran 1 (corps 1)** uniquement : proposer les **organes** selon le genome, puis permettre l’**affinage des cellules (molécules)** via un **chatbot Sullivan** en overlay (z-index 10), en restant aligné sur le dernier template (et addendum si présent).

- **Entrée :** Corps 1 (HTML ou structure), genome (pour les organes de cet écran), template actuel + principes, éventuel addendum.
- **Sortie :** Corps 1 affiné (organes proposés, cellules/molécules ajustées selon les retours user).

**Implémentation possible :**

- **Backend :**  
  - Endpoint(s) pour « proposer organes pour corps N » (lecture genome + règles UI).  
  - Endpoint(s) pour le **chatbot** : envoi du message user + contexte (corps actuel, template, addendum, dernier état) → Sullivan (Gemini) répond et peut proposer des modifications (diff ou instructions pour le front).
- **Frontend :**  
  - Afficher l’écran 1 avec les organes proposés.  
  - **Chatbot Sullivan** : panneau ou floating widget (z-index 10), conversation avec le backend.  
  - Actions possibles : « affiner les cellules ici », « ce bloc doit être un formulaire », « upload addendum », etc.  
  - Si l’user uploade un **addendum graphique** : envoi au backend → Sullivan pose des **questions de compréhension** (ou génère des hypothèses) → affinage du contenu de l’écran 1 en interaction.

**Livrable :**  
Corps 1 éditable avec chatbot Sullivan et, si possible, upload d’addendum + questions Sullivan pour recadrer l’interprétation du template.

---

### Phase 6 : Addendum graphique + questions Sullivan + passage au corps 2

**Objectif :** Gérer la **mauvaise interprétation** du template : upload d’un **addendum graphique**, **questions de Sullivan** pour comprendre le template, **affinage en interaction**, puis **passage au corps 2** (et répéter le même schéma pour les corps suivants).

- **Addendum :** nouvelle image (ou zone d’image) uploadée par l’user ; fusionnée ou comparée au template initial pour mettre à jour « dernier template » et principes.
- **Questions Sullivan :** à partir de l’addendum (et du contexte écran actuel), Sullivan (Gemini) génère 1–3 questions courtes pour clarifier l’intention (ex. « Ce bloc doit-il être une liste ou un formulaire ? »). Réponses user utilisées pour l’affinage.
- **Passage au corps 2 :** une fois l’écran 1 validé (ou « passer à la suite »), même boucle que phase 5 mais pour le **corps 2** : proposition d’organes, chatbot, addendum possible, etc.

**Implémentation possible :**

- **Backend :**  
  - Upload addendum → stockage temporaire, passage à Designer (ou module léger) pour mise à jour de la structure / principes.  
  - Endpoint « questions pour comprendre le template » (contexte = écran actuel + addendum + dernier état) → retour liste de questions.  
  - Endpoint « valider écran N et passer à N+1 » : sauvegarde état écran N, retour contexte écran N+1.
- **Frontend :**  
  - Bouton « Ajouter addendum » (upload image).  
  - Affichage des questions Sullivan + champs réponses.  
  - Bouton « Passer à l’écran suivant » (corps 2, 3, …) avec reprise du même flow (organes → chatbot → addendum si besoin).

**Livrable :**  
Boucle complète : addendum → questions → affinage → passage au corps suivant, répétable pour tous les corps.

---

## Ordre recommandé (comment construire maintenant)

1. **Phase 1** (template → HTML) : rend le designer « visible » tout de suite et réutilise Sullivan qui lit et construit déjà (en ajoutant la brique « structure → HTML »).
2. **Phase 2** (principes graphiques) : améliore la cohérence de tout ce qui sera généré ensuite.
3. **Phase 3** (plan d’écrans depuis le genome) : définit la cible (combien d’écrans, quoi dedans) avant de générer.
4. **Phase 4** (génération des corps puis STOP) : produit la première version de l’app multi-écrans.
5. **Phase 5** (corps 1 + organes + chatbot) : ajoute l’interaction et l’affinage sur un seul écran.
6. **Phase 6** (addendum + questions + passage corps 2, 3, …) : généralise à tous les écrans et boucle jusqu’à satisfaction.

---

## Fichiers / modules à créer ou étendre (résumé)

| Phase | Créer / étendre |
|-------|------------------|
| 1 | `sullivan/generator/design_to_html.py` ou extension de `designer_mode.py` + appel Gemini « structure + image → HTML complet » |
| 2 | `sullivan/analyzer/design_principles.py` (ou dans `design_analyzer.py`) + `output/studio/design_principles.json` |
| 3 | `sullivan/planner/screen_planner.py` (ou dans `core/`) + lecture genome + `screen_plan.json` |
| 4 | Extension du builder ou nouveau `sullivan/builder/corps_generator.py` (génération N écrans) |
| 5 | Backend : endpoints chatbot + « proposer organes pour corps N ». Front : chatbot overlay (z-index 10) + écran 1 |
| 6 | Backend : upload addendum, « questions Sullivan », « valider écran N ». Front : upload addendum, formulaire questions, « écran suivant » |

---

## Comment démarrer tout de suite

- **Immédiat :** implémenter la **Phase 1** (designer → HTML) en s’appuyant sur `DesignerMode` et `frontend_structure` existants, plus un appel Gemini « génère un document HTML/CSS/JS complet à partir de cette structure et du style brutalist ».
- En parallèle : documenter le **format** de `frontend_structure` et de `design_structure` pour que le générateur HTML (phase 1) et le ScreenPlanner (phase 3) partagent les mêmes concepts (corps, organes, molécules).

Ce document peut servir de **référence unique** pour le workflow idéal et de **checklist** pour les phases suivantes (2 → 6).
