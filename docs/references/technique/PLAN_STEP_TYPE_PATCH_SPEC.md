# Spec — Mode « patch » dans le schéma de plan AETHERFLOW

**Date** : 2026-02-01  
**Contexte** : Éviter l’écrasement d’un fichier existant quand le LLM ne génère qu’un fragment (ex. formulaire HTMX à insérer dans `studio.html`). En `code_generation`, le premier bloc remplace tout le fichier ; en `refactoring`, la sortie est écrite dans un `.generated.*` pour merge manuel. Le mode **patch** permet d’appliquer un fragment à un endroit précis du fichier cible sans remplacer l’ensemble.

---

## 1. Objectif

- **Type de step** : `patch`
- **Sémantique** : insérer ou remplacer un **fragment** de code dans un fichier **existant** à une position définie (marqueur ou ligne), sans remplacer tout le fichier.
- **Cas d’usage** : ajout d’un formulaire dans une page HTML, insertion d’une fonction dans un module, remplacement d’une section délimitée par des commentaires.

---

## 2. Schéma de plan (extensions)

### 2.1 Enum `type`

Ajouter `"patch"` à l’enum des types de step :

```json
"type": {
  "type": "string",
  "enum": ["code_generation", "refactoring", "analysis", "patch"],
  "description": "Type de task: code_generation (new/replace), refactoring (output to .generated), analysis (analyze), patch (insert/replace fragment in existing file)"
}
```

### 2.2 Contexte optionnel `patch`

Dans `context`, ajouter une propriété optionnelle `patch` qui décrit **où** et **comment** appliquer le fragment :

```json
"patch": {
  "type": "object",
  "description": "Requis si type === 'patch'. Indique où insérer ou remplacer le fragment dans le fichier cible.",
  "properties": {
    "position": {
      "type": "string",
      "enum": ["after", "before", "replace"],
      "description": "after = insérer le fragment après le marqueur/ligne ; before = avant ; replace = remplacer la section entre marker_start et marker_end (ou la ligne)"
    },
    "marker": {
      "type": "string",
      "description": "Chaîne à rechercher dans le fichier (première occurrence). Utilisé avec position after ou before. Ex: '<!-- END form 1.3 -->'"
    },
    "marker_start": {
      "type": "string",
      "description": "Début de la section à remplacer (position replace uniquement). Première occurrence."
    },
    "marker_end": {
      "type": "string",
      "description": "Fin de la section à remplacer (position replace uniquement). Première occurrence après marker_start."
    },
    "line": {
      "type": "integer",
      "minimum": 1,
      "description": "Numéro de ligne (1-based). Alternative à marker pour after/before. Si présent, prioritaire sur marker."
    },
    "idempotent": {
      "type": "boolean",
      "description": "Si true, vérifier si le fragment est déjà présent avant d'insérer ; si oui, ne pas modifier (évite doublon en re-run)."
    }
  },
  "required": ["position"],
  "oneOf": [
    { "required": ["marker"] },
    { "required": ["line"] },
    { "required": ["marker_start", "marker_end"] }
  ]
}
```

**Règles** :

- **position = after** : insérer le fragment **après** la ligne contenant `marker` (ou après la ligne `line`).
- **position = before** : insérer le fragment **avant** la ligne contenant `marker` (ou avant la ligne `line`).
- **position = replace** :
  - Si `marker_start` et `marker_end` sont fournis : remplacer tout le contenu **entre** la ligne contenant `marker_start` (incluse) et la ligne contenant `marker_end` (incluse) par le fragment.
  - Si seul `marker` est fourni (sans `marker_start`/`marker_end`) : remplacer **la ligne entière** qui contient le marqueur par le fragment (une seule ligne remplacée).

**Idempotence** : par défaut, ré-exécuter le step ré-insère le fragment (after/before) ou le ré-applique (replace), ce qui peut créer un doublon si le fragment contient lui-même le marqueur. Option **`idempotent`** (booléen, optionnel) : si `idempotent: true`, l’apply vérifie si le fragment (ou une signature, ex. première ligne significative) est déjà présent dans le fichier ; si oui, ne pas modifier et retourner succès. Utile pour re-runs sans duplicata.

---

## 3. Comportement de l’apply (`claude_helper.apply_generated_code`)

Pour `step_type === "patch"` :

1. **Cible** : `context.files` doit contenir **un seul** fichier existant (sinon échec ou appliquer au premier fichier selon la convention actuelle).
2. **Contenu** : comme aujourd’hui, extraire le premier bloc de code du step output (ou tout le step output si pas de bloc) = le **fragment**.
3. **Position** : lire `context.patch` :
   - Si `line` est présent : utiliser la ligne (1-based).
   - Sinon si `marker` est présent : chercher la première occurrence de `marker` dans le fichier, prendre son numéro de ligne.
   - Sinon si `marker_start` et `marker_end` sont présents (position = replace) : trouver les deux lignes.
4. **Action** :
   - **after** : insérer le fragment après la ligne cible (nouvelle ligne après, puis contenu du fragment).
   - **before** : insérer le fragment avant la ligne cible.
   - **replace** : remplacer la section (ou la ligne si seul `marker`) par le fragment.
5. **Idempotence** : si `context.patch.idempotent === true`, vérifier si le fragment (ou sa première ligne significative, ex. première ligne non vide) est déjà présent dans le fichier ; si oui, ne pas modifier et retourner `True`.
6. **Écriture** : écrire le contenu modifié dans le **fichier cible** (pas de `.generated`). Si le marqueur ou la ligne n’existe pas, logger une erreur et retourner `False`.

**Gestion des erreurs** :

- Fichier cible absent → échec (patch s’applique à un fichier existant).
- `context.patch` absent ou invalide pour un step `patch` → échec ou fallback (ex. écrire en `.generated` et avertir).
- Marqueur introuvable ou `line` hors limites → échec, ne pas modifier le fichier.

---

## 4. Routing / orchestration

- **Agent** : traiter `patch` comme une modification ciblée ; le router peut l’assimiler à `refactoring` (petit changement local) pour le choix du LLM (ex. Groq / Codestral pour petit patch, DeepSeek pour plus gros).
- **Workflow** : en PROD (-f), les steps `patch` passent par FAST puis BUILD comme les autres ; l’apply utilise la sortie BUILD et applique avec la logique patch.
- **Prompt** : dans la description du step, préciser que la sortie doit être **uniquement le fragment** à insérer (pas la page entière), et que le fragment sera inséré à l’emplacement indiqué par le plan.

---

## 5. Exemple de step (formulaire §1.4 dans studio.html)

```json
{
  "id": "step_1",
  "description": "Générer le fragment HTML du formulaire §1.4 Clés IR (même structure que les formulaires 1.2 et 1.3 dans studio.html). Sortie : uniquement le fragment (form avec hx-post, checkboxes Intents/Features/Compartments, section_id=1.4, bouton Valider), sans DOCTYPE ni page complète.",
  "type": "patch",
  "complexity": 0.3,
  "estimated_tokens": 600,
  "dependencies": [],
  "validation_criteria": ["Fragment contient form hx-post /studio/validate", "section_id=1.4", "3 checkboxes Intents, Features, Compartments"],
  "context": {
    "language": "html",
    "framework": "htmx",
    "files": ["Backend/Prod/templates/studio.html"],
    "input_files": ["Backend/Prod/templates/studio.html", "output/studio/ir_inventaire.md"],
    "patch": {
      "position": "after",
      "marker": "<!-- Rapport arbitrage complet (chargé en dessous) -->"
    }
  }
}
```

Résultat attendu : le fragment généré est inséré **après** la ligne qui contient `<!-- Rapport arbitrage complet (chargé en dessous) -->` (donc avant le bloc rapport arbitrage), sans toucher au reste de `studio.html`.

---

## 6. Résumé

| Élément        | Spec                                                                 |
|----------------|----------------------------------------------------------------------|
| **Type**       | `patch`                                                              |
| **Context**    | `context.patch` avec `position` (after / before / replace) + `marker` ou `line` ou `marker_start`/`marker_end` |
| **Apply**      | Insérer ou remplacer le fragment à la position donnée dans le fichier cible ; pas de `.generated` |
| **Cible**      | Un seul fichier existant dans `context.files`                        |
| **Sortie LLM** | Un seul fragment (premier bloc de code ou texte brut), pas la page entière |
| **Idempotence** | Optionnel `patch.idempotent: true` → ne pas insérer si fragment déjà présent |

---

*Fin de la spec.*
