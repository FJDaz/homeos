# Corpus UX — Recommandations de @clea_ux

Ce document compile de manière exhaustive les principes et "raccourcis" UX partagés par [@clea_ux](https://www.tiktok.com/@clea_ux). Ce corpus sert de base de référence pour l'étude ergonomique et la conception de HoméOS.

---

## 🏗️ Architecture de l'Information & Navigation

### 1. Le Fil d'Ariane Émotionnel
*   **Principe :** Ne pas se contenter d'une navigation technique (`Paramètres > Sécurité`).
*   **Application :** Rassurer l'utilisateur sur sa progression et ce qu'il a déjà accompli. Utiliser des intitulés sémantiques qui font sens pour l'humain.

### 2. Mode Focus
*   **Principe :** Supprimer les distractions (menu latéral, notifications, footer) lors d'étapes critiques.
*   **Application :** Onboarding, tunnels d'achat, ou configuration technique complexe. L'objectif est de réduire la charge cognitive pour garantir la complétion.

### 3. Dichotomie Landing vs SaaS
*   **Principe :** Séparer radicalement l'interface de "séduction" (Landing Page) de l'interface de "travail" (Dashboard/App).
*   **Application :** La landing doit vendre la valeur (bénéfices), le SaaS doit permettre l'exécution (efficacité).

---

## 🧠 Psychologie & Biais Cognitifs

### 4. L'Effet de Halo (Première Impression)
*   **Principe :** Soigner l'esthétique et la fluidité des 30 premières secondes.
*   **Impact :** Si l'onboarding est "Wow", l'utilisateur pardonnera plus facilement des bugs mineurs ou des manques fonctionnels par la suite.

### 5. L'Effet Zeigarnik (Tâches inachevées)
*   **Principe :** Le cerveau retient mieux ce qui n'est pas terminé.
*   **Application :** Utiliser des barres de progression ou des "checklists de succès" pour créer une tension mentale positive poussant à la complétion du profil.

### 6. L'Effet de Cadrage (Framing)
*   **Principe :** Présenter les choix en termes de gains plutôt que de pertes.
*   **Application :** Dire "75% de votre maison est sécurisée" plutôt que "Il reste 25% à configurer".

### 7. Aversion à la Perte
*   **Principe :** L'humain a plus peur de perdre ce qu'il a que de gagner ce qu'il n'a pas.
*   **Application :** Montrer ce que l'utilisateur va perdre (temps, sécurité, data) s'il ne termine pas son action.

---

## 🚀 Expérience SaaS & Onboarding

### 8. Time to Value (TTV) & Aha Moment
*   **Principe :** Réduire au maximum le temps entre l'inscription et la première "victoire" de l'utilisateur.
*   **Application :** Supprimer les barrières inutiles au début (demande de CB trop tôt, formulaires trop longs).

### 9. Onboarding Adaptatif (Profiling)
*   **Principe :** Poser 2 ou 3 questions clés au démarrage pour personnaliser l'interface.
*   **Application :** "Êtes-vous plutôt Architecte ou Développeur ?" → HoméOS adapte les terminologies affichées.

### 10. Célébration Asymétrique
*   **Principe :** Fêter les étapes franchies avec des animations discrètes (confettis, badges).
*   **Objectif :** Créer une boucle de dopamine qui renforce l'attachement au produit.

---

## 🕹️ Composants & Micro-interactions

### 11. CTA vs CTV (Call to Value)
*   **Principe :** Ne pas nommer les boutons par l'action, mais par la valeur.
*   **Exemples :** 
    *   *CTA :* "S'inscrire"
    *   *CTV :* "Accéder à mes outils" ou "Commencer à créer".

### 12. Micro-feedback Contextuel
*   **Principe :** Donner un retour visuel immédiat exactement au point d'interaction.
*   **Application :** Une encoche verte qui apparaît sur le bouton d'importation dès que le fichier est validé.

### 13. Validation en Temps Réel
*   **Principe :** Valider les champs de formulaire pendant la saisie (inline validation).
*   **Erreur à éviter :** Attendre le clic sur "Envoyer" pour afficher une liste d'erreurs en haut de page.

---

## 🛠️ Gestion des Erreurs & États Vides

### 14. Sauvegarder la 404
*   **Principe :** Une erreur est une opportunité de rebond. Proposer des liens vers les sections les plus populaires au lieu d'un simple message d'erreur.

### 15. Welcome State (vs Empty State)
*   **Principe :** Ne jamais laisser une liste vide.
*   **Application :** Remplir avec du "Dummy Content" inspirant ou des "Placeholders interactifs" qui guident l'utilisateur vers sa première création.

### 16. L'Erreur qui Guide
*   **Principe :** Ne pas se contenter de signaler l'erreur ("Email invalide"). Expliquer comment la réparer ("Veuillez vérifier le @ de votre adresse").

---

## 📉 Rétention & Sortie

### 17. Sauver le Désabonnement
*   **Principe :** Ne pas faciliter le divorce sans une dernière discussion.
*   **Application :** Proposer de mettre le compte en pause, de changer de forfait ou d'offrir un mois gratuit avant de confirmer la désinscription.

---

> [!IMPORTANT]
> Ce corpus est une compilation vivante. Il doit être interrogé à chaque nouvelle étape de conception de HoméOS pour s'assurer que nous ne créons pas seulement un outil technique, mais un produit psychologiquement performant.
