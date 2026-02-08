# GENOME FRD - Couche 2 : Logique métier et réflexions

**Projet** : AetherFlow / HomeOS - Genome Viewer  
**Public cible** : 75% des utilisateurs non-techniques écartés par les outils IA existants  

---

## 1. Pourquoi une métaphore biologique ?

### 1.1 Le problème de l'abstraction technique
Les interfaces de développement traditionnelles utilisent un vocabulaire élitiste :
- "Components", "Containers", "State Management"
- Hiérarchies abstraites (atomic design sans contexte)
- Concepts techniques déconnectés de l'expérience utilisateur

### 1.2 La force de la métaphore organique
**L'hypothèse** : Si les utilisateurs comprennent intuitivement l'anatomie humaine, ils comprendront l'anatomie d'une interface.

| Niveau biologique | Analogie interface | Intuition utilisateur |
|-------------------|-------------------|----------------------|
| Corps | Pages/Templates | "C'est tout moi, mon enveloppe" |
| Organes | Zones fonctionnelles | "Le cœur pompe, le cerveau pense" |
| Cellules | Blocs d'action | "Les cellules travaillent ensemble" |
| Atomes | Éléments simples | "Les briques de base" |

### 1.3 Choix de la terminologie
**Pourquoi pas "Atomic Design" classique ?**
- Atomes → Molécules → Organismes → Templates → Pages
- Trop de niveaux (5), trop abstrait
- Pas de hiérarchie cognitive évidente

**Notre approche** :
- 4 niveaux uniquement (règle des 4±1 Miller)
- Termes du quotidien médical (universel)
- Ordre hiérarchique évident (Corps > Organes > Cellules > Atomes)

---

## 2. Stratégie d'ordonnancement pédagogique

### 2.1 Principe : du concret à l'abstrait

#### Corps (point d'entrée)
**Logique** : L'utilisateur commence toujours par voir quelque chose.

- **Premier** : `preview` (Aperçu maquette)
  - Visuel, immédiat, concret
  - "Je vois mon design, je comprends où je vais"
  
- **Ensuite** : `table`, `dashboard`, `grid`
  - Organisation de l'information
  - "Comment mes données sont présentées"

#### Organes (orientation)
**Logique** : Une fois dans l'interface, l'utilisateur se demande "Où suis-je ?"

- **Premier** : `stepper` (Étapes du processus)
  - "J'en suis où dans mon projet ?"
  - Repère temporel et spatial
  
- **Ensuite** : `breadcrumb`, `status`
  - Navigation et santé du système

#### Cellules (actions)
**Logique** : Maintenant que je sais où je suis, que puis-je faire ?

- **Premier** : `upload` (Déposer un fichier)
  - Action initiale la plus fréquente
  - "Je commence par donner mon matériel"
  
- **Ensuite** : `color-palette`, `stencil-card`, `choice-card`
  - Traitement et décision

#### Atomes (interactions fines)
**Logique** : Les détails de l'interaction

- `button`, `launch-button`, `apply-changes`
- "Je valide, je lance, je confirme"

### 2.2 Règle heuristique appliquée
> "L'utilisateur doit reconnaître son parcours dans l'ordre d'affichage"

Si l'ordre reflète l'expérience réelle, l'apprentissage est gratuit (pas besoin de mode d'emploi).

---

## 3. Design de l'interface : sobriété et clarté

### 3.1 Contre les interfaces "développeur"

#### Ce qu'on a évité
- Badges techniques partout ("GET", "POST", "N2", "API")
- Code visible en premier plan
- Émojis excessifs (distraction cognitive)
- Jargon ("distillation", "endpoint", "health check")

#### Ce qu'on a privilégié
- **Verbes d'action** : "Voir", "Créer", "Modifier"
- **Phrases complètes** : "Navigation dans l'architecture"
- **Contexte explicatif** : chaque section a sa raison d'être décrite

### 3.2 La règle du filet
**Décision** : Un filet (`border-top`) au-dessus de chaque row, rien en dessous.

**Pourquoi ?**
- L'œil lit de haut en bas
- Le filet sépare sans enfermer
- Pas d'effet "boîtes dans des boîtes" (évite l'effet matriochka)

### 3.3 Les flèches Wingdings 2
**Pourquoi pas des SVG ?**
- Dépendance externe si SVG custom
- Complexité de code si SVG inline

**Pourquoi Wingdings 2 ?**
- Police système sur Windows
- Caractères 6 (▼) et 5 (▶) immédiatement reconnaissables
- Un seul caractère = légèreté
- Fallback gracieux (carré vide non gênant si police manquante)

---

## 4. Wireframes : entre fidélité et abstraction

### 4.1 Le dilemme
**Trop abstrait** → L'utilisateur ne comprend pas ce que ça fait  
**Trop réaliste** → L'utilisateur pense que c'est déjà fait

### 4.2 Notre solution : "Wireframes éducatifs"
Chaque wireframe doit répondre à :
1. **Qu'est-ce que c'est ?** (nom clair)
2. **À quoi ça sert ?** (description)
3. **Comment je l'utilise ?** (interaction visible)

#### Exemple : stencil-card
**Avant** : "Veille du Système", "Garder/Réserve"  
**Après** : "Suivi du projet", "Conserver/À étudier"

**Différence** : Le premier parle technologie, le second parle intention utilisateur.

### 4.3 La règle du "non-emoji"
**Décision** : Remplacer tous les émojis par du texte ou des symboles simples.

**Pourquoi ?**
- Accessibilité (lecteurs d'écran)
- Cohérence cross-plateforme
- Professionnalisme (public B2B visé)

---

## 5. La sidebar comme guide de lecture

### 5.1 Structure cognitive
```
[Qu'est-ce que c'est ?]     ← Section pédagogique
        ↓
[À quel point c'est fiable ?] ← Confiance globale
        ↓
[Quelle est la taille ?]     ← Statistiques
        ↓
[De quoi est-ce fait ?]      ← Types de composants
```

### 5.2 Section "Le Genome" : le manifeste
**Objectif** : En 3 phrases, expliquer le concept.

**Structure** :
1. **Métaphore** : "ADN de votre application"
2. **Méthode** : "Confrontation de 4 sources"
3. **Organisation** : "Hiérarchie biologique"

**Pourquoi cette structure ?**
- Définition → Processus → Structure
- Le lecteur comprend d'abord QUOI, puis COMMENT, puis ORGANISATION

---

## 6. Gestion des onglets (BRS/BKD/DPL)

### 6.1 Pourquoi masquer le layout pour BRS/BKD/DPL ?
**Logique** : Ces onglets sont des promesses, pas des réalités.

Si on garde la sidebar visible :
- L'utilisateur croit que les données sont là
- Il cherche, ne trouve pas, pense que c'est cassé

**Solution** : Page blanche avec picto centré
- C'est clairement "en construction"
- Pas de fausses pistes
- Le "FRD" actif ressort par contraste

---

## 7. Méthodologie "Kimi innocent"

### 7.1 Pourquoi "innocent" ?
L'agent IA ne part pas avec des préjugés sur l'architecture. Il lit, confronte, infère.

### 7.2 Les 4 sources de vérité
| Source | Ce qu'elle apporte | Risque si seule |
|--------|-------------------|-----------------|
| Documentation | Intention du créateur | Peut être obsolète |
| Code source | Réalité technique | Peut être incompris |
| Logs utilisateur | Comportement réel | Peut être bruité |
| Inférence | Complétion logique | Peut être erronée |

**Confrontation** : Quand 3 sources convergent, c'est probablement vrai.

### 7.3 Le taux de confiance
Affiché en grand (42px) car c'est la première question de l'utilisateur :
> "Est-ce que je peux faire confiance à ce qui est proposé ?"

---

## 8. Leçons apprises

### 8.1 Ce qui a fonctionné
- Métaphore biologique : compréhension immédiate
- Ordre pédagogique : pas besoin de mode d'emploi
- Wireframes textuels : accessibilité accrue
- 4 colonnes : scan rapide sans perte

### 8.2 Ce qui a été abandonné
- Hiérarchie trop complexe initiale
- Émojis dans les wireframes (distraction)
- Labels techniques (API, endpoints)

### 8.3 Ce qui pourrait être amélioré
- Mode édition pour modifier les composants
- Aperçu interactif (cliquer pour voir détail)
- Filtrage par type
- Recherche textuelle

---

## 9. Principes directeurs

### 9.1 Pour le public cible (75% non-techniques)
1. **Pas de jargon** sans explication
2. **Pas d'émoji** dans les fonctionnalités
3. **Pas de code** en premier plan
4. **Toujours un contexte** : pourquoi c'est là, à quoi ça sert

### 9.2 Pour la maintenabilité
1. **Pas de dépendance** externe
2. **Code séquentiel** (pas de framework JS)
3. **Génération server-side** (rapide, fiable)
4. **Structure JSON simple** (facile à modifier)

---

## 10. Transition vers Figma Editor

### 10.1 Déclencheur
Le bouton **"Valider (n)"** permet de sélectionner des Corps et de basculer vers l'éditeur visuel.

### 10.2 Pré-layouts
Au moment du switch (Vue 1 → Vue 2) :
- Génération des miniatures dans Row Corps
- États : ⏳ skeleton / ✅ aperçu / ⚠️ dimensions manquantes
- Si ⚠️ → Brainstorm modal pour définir dimensions

### 10.3 Workflow cible
1. Vue Genome → Coche Corps
2. Valider → Switch Vue Figma
3. Drag Corps sur canvas
4. Double-clic → Navigation drill-down
5. Export → JSON structuré

---

## Conclusion

Le Genome FRD n'est pas qu'un outil technique. C'est une **interface pédagogique** qui apprend à l'utilisateur comment penser son application.

La métaphore biologique transforme l'abstraction technique en intuition corporelle. L'objectif : que l'utilisateur comprenne naturellement que son application a une anatomie, et qu'il peut la concevoir en pensant par niveaux d'organisation.

---

*Document de réflexion - AetherFlow / HomeOS*
