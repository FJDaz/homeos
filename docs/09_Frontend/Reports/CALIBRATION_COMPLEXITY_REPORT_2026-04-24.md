# 📊 RAPPORT DE CALIBRAGE ET COMPLEXITÉ FRONTEND
**Date :** 2026-04-24
**Statut :** Audit pour Passation (Max)
**Périmètre :** Drill Onboarding, Impersonation Mode, Dashboard Prof.

---

## 1. RÉSUMÉ EXÉCUTIF
L'architecture actuelle du dispositif de Drill et d'Impersonation a atteint un point de maturité fonctionnelle, mais commence à saturer sur le plan structurel. Plusieurs fichiers clés dépassent ou approchent le seuil des **800-1000 lignes**, ce qui signale un besoin imminent de modularisation avant l'intégration du mode "Live Watch" (NLP/HCI).

---

## 2. MATRICE DE CALIBRAGE (Lignes de Code)

| Fichier | Lignes | Densité | Risque |
| :--- | :--- | :--- | :--- |
| **`auth_router.py`** | **946** | 🔴 Critique | Logique d'impersonation et rôles entremêlés. |
| **`teacher_dashboard.html`** | **805** | 🔴 Critique | Monolithe HTML/JS/CSS. Difficile à maintenir. |
| **`bkd_service.py`** | **758** | 🟡 Haute | Prompt engineering et RAG fusionnés. |
| **`WsStitchDrill.js`** | **726** | 🟡 Haute | Machine à état du drill codée en dur. |
| **`bootstrap.js`** | **681** | 🟡 Haute | Initialisation globale trop polyvalente. |
| **`ManifestBox.js`** | **552** | 🟢 Stable | Bien segmenté pour le moment. |

---

## 3. ANALYSE DES POINTS DE FRICTION

### 🧠 Logique d'Auth & Impersonation (`auth_router.py`)
Le fichier gère à la fois l'authentification standard et le tunnel d'impersonation prof -> élève. 
*   **Complexité excessive** : Les vérifications de permissions sont répétitives.
*   **Seuil des 1000 lignes** : Le fichier est à 54 lignes de devenir un "God Object".

### 🎓 Moteur de Drill (`WsStitchDrill.js`)
Les étapes pédagogiques (Steps 0-4) sont pilotées par des fonctions JS massives.
*   **Problème** : Changer un texte pédagogique ou une règle de validation nécessite de modifier le code logique. 
*   **Interface cible** : Un fichier `drill_schema.json` permettrait de séparer la pédagogie du code technique.

### 👁️ Dashboard Prof (`teacher_dashboard.html`)
Ce fichier est le plus fragile. Il contient toute l'interface de suivi, le panneau d'administration des utilisateurs et la gestion des signets.
*   **Solution** : Découpage en fragments Jinja2 ou composants JS autonomes.

---

## 4. PROPOSITIONS DE DÉCOUPLAGE (JSON/MD)

Pour ramener chaque fichier sous un seuil de confort (500 lignes), la stratégie suivante est recommandée :

1.  **Prompt Catalog (`.md`)** : Extraire les 300+ lignes de prompts système de `bkd_service.py` vers des fichiers Markdown par agent (Sullivan, Auditor, etc.).
2.  **Permissions Matrix (`roles.json`)** : Sortir la logique de contrôle d'accès de `auth_router.py`.
3.  **Drill Sequence (`steps.json`)** : Externaliser les étapes du Drill Onboarding pour permettre une mise à jour dynamique du parcours étudiant sans redéploiement JS.

---

## 5. CONCLUSION POUR PASSATION
Le système est robuste mais "tendu". Max devra prioriser le nettoyage du dashboard prof et l'externalisation des prompts pour libérer de la capacité cognitive et technique en vue des intégrations NLP/HCI futures.

---
*Document généré par Gemini CLI - Rapport de Vigilance Technique.*
