# 🏗️ Proposition d'Architecture : Moteur de Layout Dynamique pour Sullivan

## 1. Le Constat Structurel

Actuellement, le pipeline d'inférence de layout (Génome -> SVG) souffre du **"Syndrome du Mock"**. 
Le fichier `archetype_renderers.py` utilise des templates de dessin statistiques et hardcodés (ex: `draw_dashboard` dessine toujours 3 métriques fictives et un bar chart prédéfini). Il ignore :
- La sémantique réelle (`description_ui`, `name`).
- La distribution interne des éléments N3.
- Les notions de grilles variées, collapsibilité, et Z-index (modal/panels).

**Problème majeur** : L'effondrement modal. L'IA générative tend à reproduire le même layout SaaS générique pour tous les rôles, car elle manque de vocabulaire spatial explicite.

---

## 2. La Solution : Découplage de la Topologie et du Composant

Nous devons abandonner l'approche "Renderers Statiques" pour une approche **"Constraint Solver" (Moteur de Résolution de Contraintes)**.

### A. La Base de Connaissance Topologique (Le Vocabulaire)
Au lieu de fournir à l'IA des références de style (couleurs, polices), il faut lui fournir des **"Squelettes Topologiques"**.

**Qu'est-ce qu'une topologie ?**
C'est un arbre de distribution spatiale pur, agnostique du contenu.
Exemples :
- `Bento_Asymétrique_3x3` (Gros à gauche, 4 petits à droite).
- `Split_Pane_Sticky` (Content flex à gauche, Sidebar fixe à droite).
- `Z_Pattern_Landing` (Texte (L) -> Image (R) -> Image (L) -> Texte (R)).
- `Data_Dense_Grid` (Tableau 100% width surmonté de 4 métriques 25%).

### B. Modification du Pipeline (Les Nouvelles Passes)

#### 1. `genome_enricher.py` (La Nouvelle Pass 4)
L'enricher doit intégrer une **Pass 4 : Inférence Topologique**.
- **Input :** `ui_role` de l'organe N2 + liste des enfants N3.
- **Action :** Choix déterministe ou assisté par LLM d'une `layout_strategy` depuis la base de topologies.
- **Output dans le JSON :**
  ```json
  "layout_context": {
    "strategy": "bento_grid",
    "distribution": "flex-col-spaced",
    "z_index": "base"
  }
  ```

#### 2. `archetype_renderers.py` (Le Moteur Dynamique)
Destruction de `draw_dashboard`, `draw_form_panel`, etc. Remplacement par **`draw_dynamic_organ()`**.
- **Lecture :** Prend la `layout_strategy` et lit les VRAIS enfants N3 de cet organe.
- **Calcul :** Assigne à chaque composant N3 ses coordonnées `(X, Y, W, H)` en fonction de la stratégie spatiale (un moteur Flex/Grid mathématique en Python).
- **Dessin :** Dessine la boîte N3 *au bon endroit* avec son vrai nom (`name`) tiré du génome.

---

## 3. Stratégie d'Acquisition des Données (Topological Scraping)

Pour que ce moteur fonctionne, il lui faut une base de données de layouts (le "DataSet"). Nous ne voulons pas le CSS complet, uniquement la **structure d'agencement**.

### Où et Comment récupérer ces données ?

**1. Scraping des Marketplaces (ThemeForest, TailwindUI, Framer)**
Ces plateformes sont des mines d'or car elles classifient déjà les layouts par "purpose" (Dashboard, E-commerce, Blog, Portfolio).
- **La Méthode :** Utiliser Puppeteer / Playwright pour charger les URLs de démo.
- **L'Extraction :** Injecter un script JS qui parcourt l'arbre DOM et extrait uniquement les boîtes englobantes (`getBoundingClientRect`) et les types balises majeures (`<header>`, `<main>`, `<aside>`, `display: grid/flex`).
- **Le Résultat :** Un arbre JSON spatial représentant la mise en page sans le style.

**2. Utilisation de Datasets Publics Existants**
- **WebUI Dataset** : Dataset de 400 000 sites web taggés (utilisé pour entraîner des LLMs HTML). Nous pouvons en extraire les arbres DOM.
- **Rico Dataset** : Historiquement pour le mobile (Android), très utile pour extraire l'emplacement des FAB (Floating Action Buttons), sidebars et bottom-navs.

**3. La solution MVP (Phase 1) : Définition Manuelle "Experte"**
Avant de scrapper 10 000 sites, nous devons prouver le concept sur le moteur SVG.
- Créer un dictionnaire Python `TOPOLOGY_BANK` avec 15-20 structures fondamentales (Z-pattern, F-pattern, Bento, Dashboard-Grid, Masonry).
- Ces 20 structures permettront déjà de générer 90% des interfaces B2B modernes sans tomber dans la généricité.

---

## 4. Bénéfices Immédiats

1. **Fin du "Fake Data"** : Le SVG `genome_zones.svg` montrera exactement les composants demandés par le manifeste (plus de "42% fictif").
2. **Déblocage de l'IA (Refinement)** : Quand Gemini verra le SVG, il validera la structure exacte et non un template statistique.
3. **Préparation à Homeos Studio** : Le moteur de génération dynamique posera les fondations mathématiques (X, Y flex) que l'IA utilisera plus tard pour écrire le CSS Grid réel.
