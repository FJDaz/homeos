# Parcours UX Sullivan — Résumé exécutif

## 1. Les 9 étapes du parcours

| Étape | Rôle de Sullivan / AETHERFLOW | Objectif Technique |
| --- | --- | --- |
| **1. IR (Intention)** | **Designer** : Capture l'idée ou le besoin brut. | Créer le premier draft d'intention visuelle. |
| **2. Arbiter** | **Auditeur** : Confrontation avec les contraintes techniques. | Valider la faisabilité (routes API, données). |
| **3. Genome** | **Kernel** : Fixation de la topologie du produit. | Générer le fichier de métadonnées (endpoints, structure). |
| **4. Composants Défaut** | **Distillateur** : Pioche dans la bibliothèque de base. | Fournir une base fonctionnelle immédiate. |
| **5. Template Upload** | **Interface** : Réception du PNG de référence (votre capture). | Fournir le "Miroir" pour la personnalisation. |
| **6. Analyse / Interprétation** | **Designer** : Analyse visuelle du PNG via Gemini. | Extraire les classes Tailwind et le layout du template. |
| **7. Dialogue** | **Sullivan (Chat)** : Affinage avec l'utilisateur ("Collaboration Heureuse"). | Résoudre les ambiguïtés entre le PNG et le Génome. |
| **8. Validation** | **User Check** : Accord final sur la structure. | Figer le plan d'exécution de production (PROD). |
| **9. Adaptation** | **Distillateur** : Génération finale des fragments HTMX. | Appliquer le code via Surgical Edit ou remplacement. |

---

## 2. Récap des modules `identity.py`

| Module | Fonction |
| --- | --- |
| **Translator** | Change les routes JSON en "Intentions" (HCI). |
| **Stenciler** | Génère les schémas filaires (Blueprints) pour l'étape 4/6. |
| **Navigator** | Gère la pile (Stack) pour monter/descendre dans les Corps/Organes/Atomes. |
| **Auditor** | Vérifie que le design respecte toujours le Génome (Homéostasie). |

---

## 3. Points de décision UX

### Carrefour étape 5 — Personnalisation par l'image ou par l'inspiration ?

Une fois les composants par défaut validés, Sullivan pose la question : **Personnalisation par l'image ou par l'inspiration ?**

- **Option A — Import PNG** : L'utilisateur uploade son layout (capture d'écran). Sullivan analyse l'image pour en extraire le style et la structure.
- **Option B — Propositions de styles** : Sullivan génère 8 propositions de layouts (Minimaliste, Brutaliste, TDAH-friendly, etc.) pour éviter le syndrome de la page blanche.

*Si l'utilisateur saute l'étape 5, Sullivan bascule en mode Studio avec 8 variations de layout.*

---

### Top-Bottom étape 9 — L'entonnoir de validation granulaire

L'étape 9 (Adaptation) suit une approche **Top-Bottom par itération** :

| Niveau | Objet | Action |
| --- | --- | --- |
| **Niveau 1 — Corps** | Layout global (ex: "Page d'accueil") | Valider la structure (Triptyque, Dashboard, etc.) |
| **Niveau 2 — Organe** | Zone spécifique (ex: Header) | Valider présence et place des composants |
| **Niveau 3 — Atome** | Détail micro (ex: bouton santé) | Valider les micro-ajustements (icône pulsante vs texte) |

- **Ghost Mode** : Quand on zoome sur un Organe, le reste du Corps reste visible en filigrane (contexte spatial).
- **Backtrack** : `SullivanNavigator` permet de remonter (zoom_out) ou de sauter à une étape antérieure (ex: retour à l'Arbitrage).
- **Check d'Homéostasie** : L'Auditor alerte si une fonction vitale du Génome a été supprimée du design.
