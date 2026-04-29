#RoadMap 02 fevrier 2026


# Roadmap AETHERFLOW — Mise à jour 02 fév 2026 (10h30)

### 1. Stabilisation du "Péristaltisme" (Plomberie API)

**Objectif** : Achever le branchement de la chaîne technique pour que des composants soient générés et affichés, quel que soit leur aspect.

* **API** : Finaliser les routes dans `api.py` pour que le cycle **IR > Arbitrage > Genome** déclenche la production de fragments HTML.
* **Interface** : S'assurer que `studio.html` intercepte ces fragments via HTMX et les affiche dans la zone de "Distillation".

### 2. Définition de l'Intelligence (Identity)

**Objectif** : Créer le cerveau de Sullivan pour qu'il traite intelligemment les données qui circulent.

* **Action** : Créer `Backend/Prod/sullivan/identity.py`.
* **Contenu** : Configurer les visages **Designer** (Analyse PNG/IR), **Auditeur** (Cohérence Arbitrage) et **Distillateur** (Code final).

### 3. Implémentation du Parcours UX (Les 9 étapes)

**Objectif** : Passer du workflow linéaire à la machine à états complète.

* **Séquence** : 1. IR → 2. Arbiter → 3. Genome → 4. Composants Défaut → 5. Template Upload (ou choix 8 layouts) → 6. Analyse → 7. Dialogue → 8. Validation → 9. Adaptation.
* **Technique** : Gérer le `current_step` dans la session et adapter les retours HTMX.

### 4. Test du Miroir (Validation PNG)

**Objectif** : Tester le système complet avec le template de référence (`Interface front.png`).

* **Vérification** : Sullivan (Designer) doit être capable d'ajuster les composants de l'étape 4 en fonction de l'analyse visuelle de l'étape 6.

---

**Note technique** : On commence immédiatement par le **Point 1** pour s'assurer que l'intestin du système n'est plus bloqué avant d'attaquer l'identité de Sullivan.
