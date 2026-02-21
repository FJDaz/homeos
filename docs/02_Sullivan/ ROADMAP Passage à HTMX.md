Voici la mise à jour de ta **ROADMAP d’Homéostasie**, intégrant ton nouveau rôle de chef d'orchestre, la stratégie du "Filage" (Répétition) et le protocole de validation par lots (ADHD-friendly).

---

# 🗺️ ROADMAP : Transition HTMX & Filage Sullivan

### Phase 1 : Décontamination & Nettoyage (La "Réparation")

*L'objectif est de supprimer le "bruit" pour ne garder que le signal pur de l'API.*

* **Archivage Radical** : Déplacer `frontend-svelte/` vers `archive_svelte/`.
* **Purge API** : Nettoyer les routes FastAPI des résidus Svelte (`trailingSlash`, `+layout.generated.js`).
* **Sanctuarisation** : Vérifier l'étanchéité du Kernel (`homeos/core/`, `homeos/ir/`, `homeos/construction/`).

### Phase 2 : Le Squelette HTMX (Installation des micros)

*Création du réceptacle visuel brut pour le Triptyque.*

* **FastAPI Monolithique** : Servir le `index.html` statique.
* **Layout Triptyque** : Implémenter la structure HTML/Tailwind : **Revue | Arbitrage | Distillation**.
* **Le Pont HTMX** : Configurer les endpoints pour qu'ils renvoient des fragments HTML (OOB Swaps) au lieu de JSON.

### Phase 3 : Le "Filage" avec Cursor (La Répétition Générale) 🟢 NEW

*Validation manuelle du flux avant d'automatiser Sullivan. Phase 3 = **spécification/archive** ; l’implémentation se fait en Phase 3b.*

* **Initialisation** : Charger la [PARTITION DE FILAGE](PROMPT%20CURSOR%20FILAGE%20ARBITRGE.md) dans Cursor. Spec : [docs/04-homeos/PHASE3_SPEC_FILAGE.md](../04-homeos/PHASE3_SPEC_FILAGE.md).
* **Échantillonnage (Atomes)** : Valider le premier **Styleguide** et générer les premiers **Lots de confiance** (Boutons, Inputs).
* **Focalisation (Organes)** : Répéter le passage du mapping Aetherflow à l'arbitrage Sullivan sur un élément complexe (ex: le Chat).
* **Glaçage du Génome** : Vérifier que Homeos écrit correctement les familles validées dans le `genome.json`.

### Phase 4 : Reconnexion & Phase C (Le "Branchement")

*L'intelligence Sullivan prend possession de son nouveau corps.*

* **Workflow Integration** : Rebrancher les flags Aetherflow (`-q`, `-f`, `-vfx`) sur le panneau Distillation via SSE.
* **HCI Intent Refactoring** : Activer le code couleur (🟢🟠🔴) dans le panneau Arbitrage pour le filtrage d'attention TDAH.
* **Elite Library & Kernel** : Automatiser l'archivage des composants parfaits et la mise à jour des règles de construction.

### Phase 5 : Finitions Sullivan (L'Excellence)

*Optimisation des capacités d'inférence supérieure.*

* **Intégration STAR** : Activer le modèle Situation-Task-Action-Result dans le Kernel.
* **GénomeEnricher** : Implémenter l'inférence bayésienne pour anticiper tes choix.
* **Réduction du "Generic"** : Supprimer les fallbacks au profit de tes composants d'élite.

---

### 📋 Pourquoi cette Roadmap est ta nouvelle boussole ?

1. **Elle est progressive** : On ne branche l'IA complexe (Phase 4-5) qu'une fois que la tuyauterie manuelle (Phase 1-3 + Phase 3b) est prouvée.
2. **Elle est ADHD-Friendly** : La Phase 3 (Filage) te permet de calibrer le niveau d'alerte de Sullivan pour éviter la saturation.
3. **Zéro Régression** : La sanctuarisation du Kernel Sullivan garantit que tes 80% de progrès actuels sont préservés pendant le changement d'interface.

**C'est ta partition finale. On commence par la Phase 1 ?**