# Phase 3 : Le "Filage" avec Cursor — Spécification (Archive)

**Objectif** : Validation manuelle du flux avant d'automatiser Sullivan. Ce document est une **archive de spécification** : tout ce qui doit être fait en Phase 3 est décrit ici ; l'implémentation effective se fera en **Phase 3b (Revue d'implémentation)** à partir de cette spec.

**Référence ROADMAP** : [docs/02-sullivan/ ROADMAP Passage à HTMX.md](../02-sullivan/%20ROADMAP%20Passage%20à%20HTMX.md) — Phase 3.

---

## 1. Initialisation

### 1.1 Partition de filage

- **Document de référence** : [docs/02-sullivan/PROMPT CURSOR FILAGE ARBITRGE.md](../02-sullivan/PROMPT%20CURSOR%20FILAGE%20ARBITRGE.md) — **PARTITION DE FILAGE HOMEOS**.
- **Action en Phase 3** : Charger cette partition dans Cursor comme référence pour le filage (ordre des agents AETHERFLOW → SULLIVAN → HOMEOS, hiérarchie Atomes/Molécules vs Organes/Corps, protocole de validation par lots, code couleur 🟢🟠🔴).
- **Livrable Phase 3** : Aucun code ; la partition existe déjà. En Phase 3b, s'assurer que le Studio HTMX (triptyque Revue | Arbitrage | Distillation) affiche ou référence cette partition (lien ou section "Comment valider").

---

## 2. Échantillonnage (Atomes) — Styleguide et lots de confiance

### 2.1 Styleguide de référence

- **Fichier** : [docs/04-homeos/design_tokens.yaml](design_tokens.yaml).
- **Contenu actuel** : `colors` (primary, secondary, background, text, text_muted), `typography` (font_family, font_size_base, line_height), `spacing` (spacing_unit, padding_sm/md/lg), `border_radius` (sm, md, lg).
- **Action en Phase 3** : Valider en Cursor que ce styleguide est la source de vérité pour les atomes. Aucune modification du YAML en Phase 3 (spec seulement).
- **Critère de conformité (pour Phase 3b)** : Tout atome (bouton, input, badge, etc.) généré doit utiliser exclusivement ces tokens (couleurs, espacements, typo, border_radius). Sullivan marque 🟢 si conforme, 🟠 si déviation mineure (ex. aria-label manquant), 🔴 si incohérence majeure.

### 2.2 Lots de confiance — Atomes

| Lot | Famille | Variants à prévoir | Critères de validation |
|-----|---------|--------------------|-------------------------|
| **Lot 1** | Boutons | 5–7 (primary, secondary, danger, ghost, disabled, size sm/md/lg) | Tailwind aligné sur `design_tokens.yaml`, `aria-label` si icône seule, état disabled visible. |
| **Lot 2** | Inputs | 4 (text, email, password, textarea) | Même tokens, `label` associé (for/id ou aria-label), erreur/validation visuelle optionnelle. |

- **Action en Phase 3** : Documenter ces deux lots comme "premiers lots de confiance". En Phase 3b, AETHERFLOW proposera le styleguide puis ces lots ; Sullivan validera par lot ; HOMEOS écrira les familles validées dans le génome (voir §4).
- **Pas d'implémentation en Phase 3** : pas de génération de composants HTMX/Tailwind dans ce document ; uniquement la spec des lots et critères.

---

## 3. Focalisation (Organes) — Exemple : Chat

### 3.1 Organe cible

- **Organe** : Bloc "Chat" (formulaire d’intention + zone message/réponse), tel que décrit dans la PARTITION DE FILAGE et le Studio (panneau Revue / Arbitrage / Distillation).
- **Objectif** : Répéter le passage **mapping Aetherflow → arbitrage Sullivan** sur un élément complexe (assemblage d’atomes/molécules), sans valider chaque atome un par un (déjà fait via §2).

### 3.2 Flux attendu (spec, à implémenter en Phase 3b)

1. **AETHERFLOW (Revue)** : Propose l’organe "Chat" (structure : input message, bouton envoyer, zone réponses) en s’appuyant sur le styleguide et les atomes déjà gelés (boutons, inputs).
2. **SULLIVAN (Arbitrage)** : Affiche le lot "Organe Chat" avec code couleur (🟢 conforme / 🟠 alerte / 🔴 blocage). L’utilisateur ne valide que ce lot (Accept / Reject / Refine).
3. **HOMEOS (Distillation)** : Une fois le lot validé, écrit l’organe dans le génome (ou structure équivalente) et l’expose pour le Studio (fragment HTMX, endpoint, etc.).

### 3.3 Critères de validation pour l’organe Chat

- Utilise uniquement des atomes/molécules déjà validés (boutons, inputs).
- Accessibilité : label pour le champ, focus visible, feedback visuel sur envoi.
- Intégrable dans le triptyque Studio (Revue | Arbitrage | Distillation) sans casser le layout existant.

- **Action en Phase 3** : Cette section sert de **spec pour Phase 3b**. Aucun code Chat en Phase 3.

---

## 4. Glaçage du Génome

### 4.1 Rôle du génome dans le filage

- **Fichier cible** : `output/studio/homeos_genome.json` (généré par `Backend/Prod/core/genome_generator.py` à partir de l’OpenAPI). Pour le filage, on peut étendre ou maintenir un **genome de construction** qui décrit les familles validées (atomes, molécules, organes).
- **Règle** : Homeos écrit les **familles validées** (lots entiers) dans le génome, pas des éléments isolés. Exemple : "Lot Boutons (7 variants) → genome.json lignes 45-51" (cf. PARTITION DE FILAGE).

### 4.2 Règles d’écriture (spec pour Phase 3b)

- Chaque lot validé (🟢 ou 🟠 corrigé) est enregistré comme une **famille** avec : identifiant, liste de variants (fichiers ou fragments), référence au styleguide (design_tokens.yaml).
- Les organes validés (ex. Chat) sont enregistrés comme **organes** avec : id, label, liste d’atomes/molécules utilisés, endpoint ou fragment HTMX associé si applicable.
- **Action en Phase 3** : Documenter ces règles ici. L’implémentation (où et comment Homeos met à jour le genome) sera faite en Phase 3b.

---

## 5. Checklist Phase 3 (spec uniquement)

- [x] Référence à la PARTITION DE FILAGE (document chargé dans Cursor).
- [x] Styleguide de référence (design_tokens.yaml) et critères de conformité.
- [x] Lots de confiance Lot 1 (Boutons) et Lot 2 (Inputs) décrits avec variants et critères.
- [x] Organe exemple (Chat) : flux AETHERFLOW → SULLIVAN → HOMEOS et critères de validation.
- [x] Règles de glaçage du génome (familles et organes).

**Phase 3b** : Implémenter à partir de cette archive (UI Revue/Arbitrage/Distillation, appels AETHERFLOW/Sullivan, écriture genome, premier lot Boutons/Inputs, puis organe Chat).

---

*Document créé dans le cadre de la Phase 3 ROADMAP HTMX — Filage avec Cursor (spécification, pas d’implémentation au fil de l’eau).*
