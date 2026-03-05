# MISSION CONTROL : AETHERFLOW ROADMAP

> Missions complètes archivées dans [ROADMAP_ACHIEVED.md](./ROADMAP_ACHIEVED.md).

---

## Mission 25B — Figma Bridge & JSON Manifest

**STATUS: COMPLÉTÉE**
**DATE: 2026-03-04**

### Objectif
Établir le pont technique entre le Stenciler (AetherFlow) et Figma via un manifeste JSON vivant. Ce fichier doit permettre d'exporter les composants KIMI, leurs positions, leurs intents et leurs métadonnées vers le plugin Figma.

### Tâches (Backend & Bridge)
- [x] Génération du `manifest.json` dans `exports/` par le `07_composer.py`.
- [x] Calcul des coordonnées absolues (x, y) et dimensions (w, h) pour Figma.
- [x] Inclusion du `genome_hash` pour tracking de version.
- [x] API `GET /api/manifest` pour servir les données au plugin.
- [x] API `POST /api/manifest/patch` pour synchronisation bidirectionnelle.
- [x] Scaffolding du plugin Figma (`manifest.json`, `ui.html`, `code.js`).

---

## MISSION SUIVANTE

- [ ] MISSION 25C : RETRO-GENOME (BOUCLE RETOUR FIGMA) - **À VENIR**
- [ ] MISSION 27 : CHATBOT PÉDAGOGIQUE (GEMINI API) - **BACKLOG**
- [ ] MISSION 26 : RAG ENGINE SYSTEM - **BACKLOG**