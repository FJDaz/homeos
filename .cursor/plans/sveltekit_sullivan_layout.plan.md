# Plan : Frontend Sullivan en SvelteKit (révisé)

## Clarifications

- **Layout** (structure de la page) : en SvelteKit, **fluide et bien défini** — header, aside chatbot, main. Un seul layout cohérent, pas éclaté.
- **Contenu produit par Sullivan** pour l’utilisateur courant : **HTML + CSS** (sortie du backend). Ce n’est pas du Svelte compilé ; Sullivan renvoie du HTML/CSS que le front doit **afficher** dans la zone main.
- **Affichage** : manuel si possible — le front reçoit le HTML (et éventuellement le CSS) depuis l’API et l’affiche tel quel dans le main (injection HTML ou iframe).

---

## 1. Layout SvelteKit (fluide, bien défini)

- **Header** : pleine largeur, thème sombre, texte vert (OS, Sullivan, Backend).
- **Aside** : chatbot (messages FJ / S, input). Largeur fixe ou min/max, flex pour remplir la hauteur.
- **Main** : zone dédiée au **contenu Sullivan** (HTML/CSS). Flex 1, overflow géré.
- Tout dans un **+layout.svelte** (ou une page unique) pour garder une structure claire et un seul fichier de layout principal.

---

## 2. Affichage du contenu Sullivan (HTML/CSS)

- **Source** : l’API Sullivan produit du **HTML** (et éventuellement du **CSS**) pour l’utilisateur courant (layout inféré du genome, ou layout amendé).
- **Options d’affichage dans le main** :
  - **Option A (manuelle)** : un endpoint (ex. `GET /sullivan/layout` ou `GET /studio/layout`) renvoie du HTML (et optionnellement une URL de feuille de style ou du CSS inline). Le front SvelteKit affiche ce HTML dans un conteneur dédié.
  - **Option B** : **`{@html content}`** en Svelte : le front reçoit une chaîne HTML (ex. via fetch), la stocke dans une variable, et l’affiche avec `{@html content}`. Si le CSS est inclus dans le HTML (balise `<style>`) ou chargé via lien, le rendu sera correct. Attention : ne pas utiliser `{@html}` avec du contenu utilisateur non contrôlé sans sanitization (ici le contenu vient de Sullivan/API, à traiter comme “trusted” ou à sanitiser côté API).
  - **Option C** : **iframe** avec `srcdoc` (ou `src` vers une URL qui sert le HTML) pour isoler complètement le HTML/CSS produit par Sullivan du reste de l’app SvelteKit. Approche la plus sûre si le HTML peut contenir du script.
- **Recommandation** : privilégier **Option B** si l’API ne renvoie que du HTML/CSS statique (sans script) et que tu veux une intégration manuelle simple ; sinon **Option C** (iframe) pour l’isolation.

---

## 3. Flux de données

1. **Layout** : SvelteKit gère la structure (header, aside, main).
2. **Chat** : messages et requêtes vers l’API Sullivan (search, dev/analyze, designer/analyze) comme aujourd’hui.
3. **Contenu main** : au chargement ou après amendement, le front demande à l’API le **layout courant** (HTML/CSS) pour l’utilisateur ; l’API renvoie le HTML (et optionnellement le CSS) produit par Sullivan ; le front l’affiche dans le main (via `{@html}` ou iframe).

Si aujourd’hui l’API ne fournit pas encore un endpoint “layout HTML pour l’utilisateur”, le plan devra prévoir soit :
- un nouvel endpoint (ex. `GET /studio/layout?user_id=...`) qui retourne le HTML (et CSS) du layout Sullivan pour cet utilisateur, soit
- la réutilisation d’un endpoint existant qui renvoie déjà du HTML (ex. prévisualisation) et l’affichage de ce HTML dans le main.

---

## 4. Résumé des points à implémenter

| Élément | Détail |
|--------|--------|
| Layout SvelteKit | Un layout fluide et bien défini (header, aside, main) dans un fichier/structure unique. |
| Contenu Sullivan | Affichage du **HTML/CSS** produit par Sullivan dans la zone main (`{@html}` ou iframe), de préférence de façon **manuelle** (fetch puis affichage). |
| Chat | Aside = chatbot ; appels API existants (search, dev/analyze, designer/analyze). |
| API | Prévoir ou réutiliser un endpoint qui renvoie le HTML (et si besoin CSS) du layout pour l’utilisateur courant. |

---

## 5. Suite du plan technique SvelteKit

Le reste du plan précédent reste valable : création du projet SvelteKit (`frontend-svelte/`), composants Header, AsideChat, MainGenomeLayout, intégration API, thème sombre, service du build par FastAPI. La seule modification importante est que **MainGenomeLayout** (ou équivalent) doit prévoir un conteneur dédié pour **afficher le HTML/CSS renvoyé par Sullivan** (via `{@html}` ou iframe), et non seulement des organes construits côté client à partir du JSON genome — sauf si tu veux garder les deux (fallback organes depuis genome JSON + remplacement par le HTML Sullivan quand disponible).
