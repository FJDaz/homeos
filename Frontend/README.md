# FRONTEND — Sullivan Stenciler

**Projet** : AETHERFLOW / Homeos / Sullivan
**Statut** : Phase 1 — Définition du Contrat ✅
**Conformité** : CONSTITUTION_AETHERFLOW v1.0.0

---

## 📁 Structure

```
Frontend/
├── 1. CONSTITUTION/           ← Documents constitutionnels
│   ├── CONSTITUTION_AETHERFLOW.md
│   ├── API_CONTRACT_SCHEMA.json
│   └── ROADMAP_IMPLEMENTATION.md
│
├── 2. GENOME/                 ← Structure de données
│   ├── genome_reference.json  (25KB)
│   └── README.md
│
├── 3. STENCILER/              ← Application principale
│   └── server_9998_v2.py      (1913 lignes)
│
└── 4. COMMUNICATION/          ← Canal Claude ↔ KIMI
    └── CANAL_CLAUDE_KIMI.md
```

---

## 🎯 Objectif

Créer un **Stenciler** (interface de design) qui permet :
1. Afficher 4 Corps en preview (20%)
2. Drag & drop vers canvas Figma-like
3. Drill-down hiérarchique (Corps → Organes → Cells → Atomsets)
4. Modification visuelle (couleurs, borders, etc.)
5. Persistance via API REST

---

## 🏛️ Principes Constitutionnels

### Frontière Hermétique

```
┌────────────────────────────────┬────────────────────────────────┐
│  BACKEND (Claude)              │  FRONTEND (KIMI)               │
├────────────────────────────────┼────────────────────────────────┤
│  État sémantique               │  Rendu visuel                  │
│  Validation métier             │  HTML/CSS/Fabric.js            │
│  Persistance                   │  Interactions                  │
│  Event sourcing                │  Animations                    │
├────────────────────────────────┼────────────────────────────────┤
│        JSON MODIFS = CONTRAT DE COMMUNICATION                   │
└─────────────────────────────────────────────────────────────────┘
```

### 3 Règles d'Or

1. **Frontière hermétique** : Backend = Cerveau, Frontend = Mains
2. **Aucun empiétement** : Pas de CSS dans le backend, pas de logique métier dans le frontend
3. **Single Source of Truth** : JSON Modifs est l'unique source de vérité

---

## 🚀 Quick Start

### Lancer le Stenciler (actuel)

```bash
cd "Frontend/3. STENCILER"
python3 server_9998_v2.py
# Ouvrir http://localhost:9998
```

**Note** : Le fichier actuel (1913 lignes) est le Viewer. Le Stenciler sera ajouté après la ligne 1422 (voir MISSION_STENCILER_EXTENSION.md).

---

## 📋 Roadmap

**Phase actuelle** : Phase 1 — Définir le Contrat ✅

**Prochaines phases** :
- Phase 2 : Implémenter classes Backend (3-5j) ⏳
- Phase 3 : Créer API REST (2-3j) ⏳
- Phase 4 : Intégration Frontend (3-5j) 🚀 KIMI Lead
- Phase 5 : Optimisations (2-3j) ⏳

**Durée totale** : 11-18 jours

**Voir** : [ROADMAP_IMPLEMENTATION.md](1.%20CONSTITUTION/ROADMAP_IMPLEMENTATION.md)

---

## 👥 Acteurs

| Rôle | Instance | Responsabilité |
|------|----------|----------------|
| **CTO** | François-Jean Dazin | Autorité suprême |
| **Backend Lead** | Claude Sonnet 4.5 | Système Cognitif |
| **Frontend Lead** | KIMI 2.5 | Système de Rendu |
| **Arbitre** | Claude Opus 4.5 | Interprétation Constitution |

---

## 📞 Communication

**Canal asynchrone** : [4. COMMUNICATION/CANAL_CLAUDE_KIMI.md](4.%20COMMUNICATION/CANAL_CLAUDE_KIMI.md)

**Protocole** :
- Chaque message a timestamp + statut
- Numérotation (#001, #002, etc.)
- Décisions tracées dans tableau de suivi

---

## 🔗 Liens Importants

- **Constitution** : [1. CONSTITUTION/CONSTITUTION_AETHERFLOW.md](1.%20CONSTITUTION/CONSTITUTION_AETHERFLOW.md)
- **API Schema** : [1. CONSTITUTION/API_CONTRACT_SCHEMA.json](1.%20CONSTITUTION/API_CONTRACT_SCHEMA.json)
- **Genome** : [2. GENOME/genome_reference.json](2.%20GENOME/genome_reference.json)
- **Canal** : [4. COMMUNICATION/CANAL_CLAUDE_KIMI.md](4.%20COMMUNICATION/CANAL_CLAUDE_KIMI.md)

---

## ✅ Checklist Phase 1

- [x] Constitution créée et ratifiée
- [x] JSON Schema du contrat défini
- [x] Roadmap établie
- [x] Structure Frontend/ organisée
- [x] Genome copié au bon endroit
- [x] Server stenciler copié
- [x] Canal de communication initialisé
- [x] François-Jean a signé Constitution (ligne 493)
- [x] Claude Sonnet 4.5 signe Constitution (ligne 497-500) — 11 fév 18:45
- [x] KIMI 2.5 signe Constitution (ligne 502) — 11 fév 02:36
- [x] KIMI valide le contrat — GO Phase 2 🚀
- [x] Elite Library copiée (65 composants Tier 1)
- [x] Protocole Validation Visuelle créé (Article 10)
- [x] Système Détection Mission Frontend créé
- [x] Phase 1 COMPLÉTÉE ✅

---

**Version** : 1.0.0
**Dernière mise à jour** : 11 février 2026, 18:40
