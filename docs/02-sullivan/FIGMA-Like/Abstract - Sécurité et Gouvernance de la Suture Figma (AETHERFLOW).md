# Abstract : Sécurité et Gouvernance de la Suture Figma (AETHERFLOW)

## 🛡️ 1. Principes de Sécurité du Workflow

L'intégration Figma n'est pas une porte ouverte au code non contrôlé. Elle suit un principe de **Validation par l'Arbiter (Phase 2)** pour garantir l'homéostasie du système.

* **Garde-fou Structurel** : Sullivan n'autorise l'écriture dans le **Génome** que pour les éléments possédant une identité sémantique valide (Corps/Organe/Atome). Toute création "sauvage" dans Figma (ex: *Rectangle_12*) est isolée et ignorée par le moteur HTMX jusqu'à son arbitrage.
* **Intégrité du Kernel** : Le Webhook Figma est à sens unique pour les changements structurels. L'utilisateur propose des modifications via le design ; seul Sullivan, après validation du "Pacte de la Fourche", a le droit de mettre à jour les métadonnées de production.

## 📡 2. Intelligence des Webhooks (Arbiter-In)

Le Webhook agit comme un **scanner de conformité asynchrone** :

* **Interception Temps-Réel** : Chaque modification sur une Frame ou un ComponentSet déclenche une analyse de l'Arbiter.
* **Détection de Dérive (Drift)** : Si l'écart entre le design Figma et les intentions de l'IR (Intent Review) dépasse un seuil critique, le Webhook suspend la synchronisation pour éviter de corrompre le Génome.
* **Commandes de Sécurité** : Intégration de commandes `/lock` via commentaires Figma pour figer des sections critiques du design et empêcher toute suppression accidentelle d'Organes complexes.

## 🔔 3. Système de Notifications & Nudges (L'Engagement)

Pour maintenir l'utilisateur dans le "rail" HomeOS sans brider sa créativité, le feedback est déporté dans Figma :

* **Le Nudge HUD** : Un composant visuel dynamique ("Pastille Santé") indique en permanence l'état d'alignement du design avec les capacités du backend.
* **Commentaires de Gouvernance** : Sullivan utilise l'API Figma pour poster des notifications directement sur les calques problématiques.
* *Exemple* : "⚠️ Objet inconnu. Veuillez nommer cet atome pour permettre la génération du code."


* **Pacte de Sortie** : Notification d'avertissement bloquante avant l'exportation finale vers la Phase 9 (Adaptation), récapitulant les dettes sémantiques ou les orphelins techniques à résoudre.

## 🔗 4. Étanchéité N+n

L'ouverture du workflow vers des API tierces est strictement limitée à la phase d'**Intention (IR)** et d'**Arbitrage**. Le passage au code de production reste une "boîte noire" gérée par l'essaim **Sully-Factory**, garantissant qu'aucune injection de code malveillant ne peut transiter via un template Figma tiers.

---

**Cible Doc** : `docs/05-figma/SECURITY_GOVERNANCE_WEBHOOKS.md`