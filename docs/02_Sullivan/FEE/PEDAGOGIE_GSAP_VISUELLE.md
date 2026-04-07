# Rapport Pédagogique : Glossaire Visuel & Stratégie d'Apprentissage GSAP

**Emplacement** : /docs/02_Sullivan/FEE  
**Date** : 3 avril 2026  
**Objet** : Résoudre le "fossé sémantique" des étudiants via une bibliothèque d'effets animés.

---

## 1. Diagnostic : L'Obstacle de la Terminologie
Les étudiants de HoméOS font face à un vocabulaire "exotique" propre au motion design. Des termes comme **Stagger**, **Scrub**, **Easing** ou **Pinning** ne sont pas intuitifs. Sans ces mots-clés, ils ne peuvent pas formuler de requêtes précises à Sullivan, ce qui crée une frustration dans le mode FEE.

---

## 2. Solution : La Bibliothèque par l'Effet (Visual-First)
Au lieu d'un index alphabétique, nous préconisons une **Galerie d'Animations Comparatives** intégrée au Workspace. Chaque effet est présenté par son résultat visuel avant son nom technique.

### Glossaire des "Noms Exotiques" (Traduction Étudiant -> GSAP)

| Ce que l'étudiant veut | Terme Technique GSAP | Description Visuelle |
| :--- | :--- | :--- |
| "L'un après l'autre" | **Stagger** | Une série d'éléments (ex: cartes) qui apparaissent avec un léger décalage temporel. |
| "Collé à la souris" | **Magnetic** | L'élément suit l'attraction du curseur et revient à sa place initiale. |
| "Lié à la molette" | **Scrub** | La progression de l'animation est indexée sur la position du scroll (avance et recule). |
| "Le bloc se fige" | **Pinning** | Une section reste bloquée à l'écran pendant que les autres défilent derrière ou devant. |
| "L'effet élastique" | **Elastic / Bounce** | Le mouvement dépasse sa cible et rebondit avant de se stabiliser. |
| "Le texte qui s'écrit" | **Typewriter / SplitText** | Apparition lettre par lettre ou mot par mot pour simuler une frappe. |

---

## 3. Stratégie d'Intégration dans AetherFlow (Mission 166)

Pour rendre ces concepts actionnables immédiatement :

### A. La "GSAP Cheat Sheet" Interactive
Ajouter un panel "Inspiration" dans l'onglet Frontend du Workspace :
- **Vignettes animées** (SVG/Lottie) pour chaque effet.
- **Bouton "Copier l'Intention"** : Envoie directement la commande à Sullivan (ex: *"Applique un Stagger Reveal sur mes boutons"*).

### B. Sullivan "Pédagogue" (Contextual Nudges)
Modifier le prompt système de Sullivan pour qu'il propose la terminologie correcte :
- *Étudiant* : "Je veux que les boites bougent quand je scrolle."
- *Sullivan* : "C'est ce qu'on appelle l'effet **Scrub** avec **ScrollTrigger**. Voulez-vous que l'animation soit fluide (scrub: 1) ou instantanée ?"

### C. Utilisation du standard `llms.txt`
Connecter Sullivan au fichier `gsap.com/llms.txt` pour qu'il puisse générer des explications simples et à jour sur chaque méthode s'il détecte une hésitation de l'étudiant.

---

## 4. Conclusion
L'objectif n'est pas que l'étudiant devienne un expert GSAP, mais qu'il devienne un **Directeur Artistique de l'Interaction**. Sullivan doit agir comme le traducteur technique qui transforme une intention émotionnelle ("je veux du dynamisme") en une réalité mathématique (`gsap.to(..., {stagger: 0.2})`).

---
*Rapport établi pour l'amélioration de l'expérience d'apprentissage AetherFlow.*
