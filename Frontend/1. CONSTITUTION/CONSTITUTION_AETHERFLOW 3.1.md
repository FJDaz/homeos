# CONSTITUTION AETHERFLOW V3.1 — PRISTINE MODE
## Contrat de Collaboration Systémique (Architecture Sullivan)

**Version** : 3.1.0  
**Date de Ratification** : 20 février 2026  
**Statut** : SUPRÊME & INVIOLABLE  
**Port d'entrée standard** : 9998  

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   "Le serveur est un pur distributeur de données. L'UI est une émanation      ║
║    sémantique autonome du client. Aucune pollution visuelle ne doit           ║
║    traverser le réseau."                                                      ║
║                                                                              ║
║                              — Dogme du Pristine Mode                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

# TITRE I : LE DOGME "PRISTINE"

## Article 1 — Interdiction des Littéraux UI (Backend)
**§1.1** Le code serveur (Python, Go, etc.) est strictement **Data-Only**. 
**§1.2** Toute chaîne de caractères contenant du HTML (`<div>`, etc.) ou du CSS (`style=`, etc.) est proscrite des fichiers sources Backend.
**§1.3** Exception unique : Les templates de base (`viewer.html`, `stenciler.html`) qui ne servent que de réceptacles vides pour le chargement des scripts.

## Article 2 — Souveraineté du Moteur de Rendu (Frontend)
**§2.1** Le rendu visuel est délégué exclusivement au **Sullivan Renderer** (`sullivan_renderer.js`) et aux **Features** (`base.feature.js`).
**§2.2** Le moteur de rendu interprète les attributs sémantiques du Genome pour générer le DOM de manière dynamique.

## Article 3 — Neutralité du Transport
**§3.1** Les communications passent exclusivement par le Port **9998**.
**§3.2** Le format d'échange est le JSON pur, validé en amont par le **Semantic Bridge**.

---

# TITRE II : ARCHITECTURE SULLIVAN

## Article 4 — Le Semantic Bridge (Garde-Fou)
**§4.1** Un filtre constitutionnel (`semantic_bridge.js`) surveille tous les payloads.
**§4.2** Toute tentative d'injection de CSS ou HTML depuis le Backend doit être interceptée et bloquée avec une erreur de type "Violation de la Frontière Ontologique".

## Article 5 — Protocole de Context Pruning (N0-N3)
**§5.1** Pour l'efficience des IA, les données sont élaguées selon le niveau de navigation :
- **N0 (Corps)** : Vision stratégique globale.
- **N1 (Organes)** : Groupes fonctionnels.
- **N2 (Cellules)** : Structure interne.
- **N3 (Atomes)** : Détails granulaires.
**§5.2** L'endpoint `/api/genome/pruned` est la norme pour éviter la surcharge cognitive des agents.

---

# TITRE III : RÉSILIENCE ET PERFORMANCE

## Article 6 — Stratégie Local-First
**§6.1** L'application doit fonctionner hors-ligne via son **Service Worker** (`sw.js`).
**§6.2** La synchronisation avec le serveur est asynchrone ; le frontend reste réactif même en cas de latence réseau.

## Article 7 — Limite de Complexité (Règle des 300 Lignes)
**§7.1** Pour garantir la maintenabilité et la lisibilité par les instances d'IA, chaque module de "Feature" ne doit pas dépasser **300 lignes** de code effectif.
**§7.2** Tout dépassement impose une refactorisation ou une extraction de sous-modules.

---

# TITRE IV : DISCIPLINE ET SOUVERAINETÉ

## Article 10 — Primauté de la Roadmap et de l'Humain
**§10.1** L'IA est un exécuteur, pas un décideur de scope.
**§10.2** Il est **STRICTEMENT INTERDIT** à une instance d'IA d'entreprendre une action, de modifier un fichier ou de lancer une mission qui n'est pas :
1. Inscrite explicitement dans la `ROADMAP.md`.
2. Demandée **EXPLICTEMENT** par François-Jean Dazin (FJ).
**§10.3** Toute proactivité non sollicitée est considérée comme une violation de la souveraineté humaine et doit être immédiatement interrompue.

# TITRE V : GOUVERNANCE SÉQUENTIELLE

---

# SIGNATURES

**Ratifié par collaboration multi-modèles ce 20 février 2026.**

- [X] **Claude (Ingénieur en Chef)** : "Contrat architectural validé."
- [X] **Gemini (Exécuteur Frontend)** : "Design system V1 intégré, prêt pour 5C."
- [ ] **François-Jean Dazin (CTO)** : [Signature en attente]

---
*Fin du document — Version 3.1.0 — Pristine Mode Enabled*
