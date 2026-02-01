# Volet Deploy en Rust — Pertinence et stratégie

**Date** : 29 janvier 2026  
**Contexte** : Discussion sur un troisième pilier AETHERFLOW dédié au déploiement, implémenté entièrement en Rust.

---

## 1. Réécriture complète du système en Rust ?

**Conclusion** : Techniquement envisageable, mais peu rentable en « big bang ».

- **Volume** : ~133 fichiers Python (Backend/Prod), orchestration, Sullivan, API, RAG, Playwright, AST Python, etc.
- **Dépendances lourdes** : llama-index (RAG), Playwright (audit Sullivan), Python AST (surgical editor) n’ont pas d’équivalent direct en Rust.
- **Stratégie réaliste** : migration progressive (ex. API + clients LLM en Rust, reste en Python) ou laisser le cœur en Python et optimiser.

---

## 2. Troisième volet : Deploy uniquement en Rust

**Question** : Imaginer un troisième pilier « deploy » 100 % Rust est-il pertinent, réaliste, utile ?

### Pertinent

- **Rôle bien délimité** : L’orchestration (Python) et Sullivan (Python) définissent *quoi* construire ; le deploy définit *où* et *comment* livrer. Couche distincte.
- **Aligné avec la doc** : La synthèse deploy (`docs/guides/V2.0/Synthèse & Plan d'Action pour le Module deploy.md`) décrit déjà une **CLI pure** (`aethos deploy --target=railway`), export ZIP, validation locale, éco-score, magic links. Une CLI dédiée en Rust colle à ce design.
- **Pas de mélange avec l’IA** : Le deploy ne nécessite pas de LLM ni Sullivan au runtime ; il consomme des artefacts et de la config. Rust peut être le seul runtime pour ce volet.

### Réaliste

- **Périmètre borné** : CLI (clap), HTTP (Railway, Netlify…), SSH / magic links, Docker (bollard ou sous-process), ZIP, fichiers, env. Pas d’équivalent llama-index ou Playwright à réécrire.
- **Écosystème Rust adapté** : CLI, HTTP, JSON, processus, fichiers sont bien couverts.
- **Intégration** : Binaire `aetherflow-deploy` (ou `aethos deploy` appelant le binaire). Python continue à générer plans/artefacts ; Rust ne fait que déployer.

### Utile

- **CI / agents** : Un seul binaire, pas de venv ni `pip install` sur le runner. Idéal pour GitHub Actions, GitLab CI, ou un agent qui déploie.
- **Portabilité** : Un binaire par plateforme (Linux/macOS/Windows), éventuellement cross-compilé.
- **Séparation des risques** : Le deploy touche credentials, SSH, APIs. Un binaire Rust avec peu de dépendances réduit la surface d’attaque.
- **Message produit** : « AETHERFLOW = orchestration + Sullivan + deploy ». Le volet deploy en Rust renforce l’image d’un outil de delivery sérieux et portable.

---

## 3. Synthèse

| Critère   | Verdict |
|----------|--------|
| **Pertinent** | Oui : deploy = 3ᵉ pilier cohérent, déjà décrit dans la doc. |
| **Réaliste** | Oui : scope CLI + cibles (Railway, SSH, static, Docker), écosystème Rust suffisant. |
| **Utile**    | Oui : binaire unique, pas de Python en CI pour le deploy, portabilité et sécurité. |

**Recommandation** : Envisager le volet deploy comme un **sous-projet Rust** (ex. `deploy/` ou repo `aetherflow-deploy`), avec une CLI du type `aetherflow deploy` (wrapper Python qui appelle le binaire) ou `aetherflow-deploy` en standalone. Les phases 1–2 de la roadmap deploy (validation locale, export ZIP, éco-score simple) se prêtent bien à un MVP en Rust.

---

## 4. Références

- `docs/guides/V2.0/Synthèse & Plan d'Action pour le Module deploy.md` — Vision et roadmap du module deploy.
- Discussion du 29/01/2026 (réécriture complète vs. volet deploy Rust).
