# 🚀 Expérience Front Gemini : L'Approche "WordPress Premium"

L'objectif de cette expérimentation (sur la branche `experience_front_gemini`) est de **tuer le syndrome du layout générique et ennuyeux**. 

Pour que Gemini arrête d'allumer de simples boîtes empilées (Header / Main / Footer), nous devons le transformer en un **Créateur de Thème WordPress / Architecte Tailwind UI Senior**.

Voici la proposition d'intervention sans démonter le backend actuel.

---

## 1. Le Changement de Rôle (Le Nouveau System Prompt)

Jusqu'à présent, Gemini est considéré comme un "Valideur de code" ou un "Traducteur d'Intentions API". 
Nous allons injecter un **System Prompt spécifique au Frontend** lorsqu'il analyse le SVG ou enrichit le génome :

> *Tu es l'Architecte Principal d'un Studio Web habitué à vendre des thèmes WordPress Premium sur ThemeForest et des templates SaaS sur TailwindUI.*
> *Ta mission n'est pas de faire un "wireframe qui marche", mais de concevoir une structure spatiale vibrante, dynamique et asymétrique.*
> 
> *RÈGLES D'ARCHITECTURE WP-INSPIRED :*
> *1. **Macro-Zones (Layouts Modernes)** : Déteste la symétrie parfaite. Propose des Split-screens (50/50), des Sidebars d'outils (Context-Panels), des Hero sections (Pleine largeur).*
> *2. **Micro-Zones (Composants Riches)** : Ne fais pas de "Listes". Si c'est un Dashboard, utilise des "KPI Cards" en haut (col_span=1 par carte), suivis d'un "Graphique Pleine Largeur" (col_span=3).*
> *3. **Densité Visuelle** : Laisse de l'air où il le faut (Padding massif) et condense l'information technique (Tableaux denses, Sidebars resserrées).*

---

## 2. Le "RAG Créatif" (La Base de Connaissances)

"Comment tu fais pour un dashboard WordPress ?"
Gemini ne doit plus deviner. Nous allons lui **fournir le contexte de notre Skill `ui-ux-pro-max`**.

Avant que Gemini n'enrichisse un organe du génome, le backend lui injectera le contenu de nos dictionnaires de références (`topology_bank.py`, ou un extrait de `products.csv`). 

*Exemple de RAG Injected Context pour Gemini :*
`"Voici la structure type d'un Dashboard SaaS Top-Tier (Ref: Stripe, Vercel) : Grille Masonry, Top KPIs métriques réparties en 4 colonnes, suivi d'un Activity Feed asymétrique 66%/33%."`

---

## 3. Plomberie : Où Gemini intervient-il ?

Plutôt que de tout recoder, nous branchons cette nouvelle intelligence Gemini exactement là où le code Python fait actuellement des devinettes statistiques.

### A. L'Enrichisseur Sémantique (La "Pass 4")
Dans `genome_enricher.py`, quand vient le tour d'un organe (ex: "Espace Client"), le script appelle **Gemini Planner** avec la liste des fonctions techniques (GET /profil, POST /avatar).
**Gemini répond par un JSON purement topologique :**
```json
{
  "layout_strategy": "bento_grid",
  "zone_assignment": {
    "header-hero": ["GET /profil (Profile Card)"],
    "sidebar-left": ["Settings Navigation"],
    "main-masonry": ["KPI Activity", "Security Settings"]
  }
}
```

### B. Le Juge Final (SVG Zone Validator)
Quand Gemini (dans `svg_zone_validator.py`) regarde le SVG généré par le moteur, on durcit ses critères.
* **Actuel :** "Il y a un header et un main. C'est OK ! PASS."
* **Nouveau (WP-Mode) :** "C'est nul. Le layout 'Dashboard' est juste une colonne verticale de 500px de large. Il manque une grille de métriques asymétrique. REJECT. Modifie l'organe X pour utiliser `layout_strategy: 'dashboard_grid'`."

---

## Pourquoi ça marche sans tout casser ?

1.  **Le Génome reste le Contrat** : On ne change pas l'API ni les endpoints.
2.  **Métadonnées Supplémentaires** : On injecte simplement des données de "Layout Style" (`layout_strategy`, `col_span` dynamiques) dans le JSON que le moteur SVG lira bêtement.
3.  **Contrôle Qualité IA** : Le moteur SVG applique bêtement le layout "Bento", et si c'est moche, le Juge Gemini le voit sur l'image et ordonne de re-router les composants N3.

Est-ce que cette vision (Prompt + RAG Créatif + Pass 4 + Juge Intransigeant) est exactement la direction "WordPress / ThemeForest" que tu veux pour cette branche `experience_front_gemini` ?
Si oui, je commence à écrire le **System Prompt Gemini "ThemeForest Architect"** dans `prompts/`.
