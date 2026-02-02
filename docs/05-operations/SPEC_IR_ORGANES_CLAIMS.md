# Spec IR → Arbitrage → Genome (Organes & Claims)

**Date** : 1er février 2026  
**Références** : FRONTEND AGENCY-LIKE, Roadmap_ARBITRAGE_GPT, Méthode d'arbitrage.

---

## 1. Contrat (schéma IR)

- **Schéma JSON** : `docs/references/technique/ir_schema.json`
- **Règle** : 1 section IR = 1 **Organe** ; 1 Organe contient **N claims** (cases à cocher).
- **Décision** : Accept / Revise / Reject **par Organe** (pas par claim).

| Niveau   | Rôle |
|----------|------|
| **IR Document** | Contient `source` + `organes[]`. Sortie Aetherflow (LLM → JSON pur). Entrée Studio. |
| **Organe** | `id`, `title`, `claims[]`, `verdict?`. Un formulaire = un Organe. |
| **Claim** | `id`, `text`, optionnel `description`, `type`, `confidence`, `checked`. Une case à cocher = un claim. |

Le LLM ne génère **que du JSON** conforme à ce schéma. Le front (Jinja + HTMX) mappe le JSON vers les composants (Agency).

---

## 2. Flux IR → Arbitrage → Genome

| Étape | Qui | Quoi |
|-------|-----|------|
| **IR** | Aetherflow / plan chunké | Produit `ir_inventaire.md` puis (ou directement) **IR JSON** (organes + claims). |
| **Revue** | Studio (colonne 1) | Affiche l’inventaire (Markdown ou rendu depuis IR JSON). |
| **Arbitrage** | Utilisateur + Sullivan | Par Organe : cocher les claims à garder, choisir **verdict** (Accept / Revise / Reject). |
| **Distillation** | POST /studio/validate | Enregistre `section_id`, `section_title`, `items` (claims cochés), `verdict`. |
| **Genome** | Backend | Les entrées distillation alimentent la mise à jour du genome (sections validées, priorités). |

**Renderer (Roadmap)** : le Renderer produit du contenu (style Méthode d’arbitrage) qui remplit les templates Jinja. Les blocs sont déterministes ; le LLM fournit le contenu, jamais la structure.

---

## 3. Verdict et rétrocompatibilité

- **Verdict** : `Accept` | `Revise` | `Reject`.  
- **Actuel** : `verdict = "Garder"` → traiter comme **Accept**.  
- **Évolution** : dans l’UI, proposer trois boutons/choix par Organe (Accept, Revise, Reject) et enregistrer l’un des trois. Garder la compatibilité lecture avec "Garder" = Accept.

---

## 4. Entrée distillation (format actuel étendu)

Fichier : `output/studio/distillation_entries.json`.

Chaque entrée après validation :

```json
{
  "section_id": "1.3",
  "section_title": "Endpoints",
  "items": ["POST /execute", "GET /health", "..."],
  "verdict": "Accept"
}
```

- `section_id` = `organe.id`
- `section_title` = `organe.title`
- `items` = liste des **claims cochés** (texte ou id selon implémentation)
- `verdict` = **Accept** | **Revise** | **Reject** (et "Garder" lu comme Accept)

---

## 5. Suite (option B complète)

Une note d’architecture plus longue pourra détailler :

- Pipeline Roadmap (Extractor → Scorer → Bayes Arbiter → Renderer) avec **entrée** = IR JSON + PRD.
- Mapping **claims** ↔ **sections PRD** (line_start, line_end).
- Mise à jour **genome** à partir des entrées distillation (quels champs, quels événements).

Ce document et le schéma `ir_schema.json` suffisent pour avancer sur l’agentification (génération IR JSON, templates Jinja par Organe, verdict par Organe).


---

## 6. Statut : logique décroissante, prompt system, meta

**Référence détaillée** : `docs/05-operations/Roadmap_ARBITRAGE_GPT.md`.

| Élément | Dans les docs | Implémenté côté code |
|--------|----------------|------------------------|
| **Logique décroissante (Bayes)** | Oui : prior, likelihood, posterior, décision Accept/Revise/Reject par claim, `bayes_update(prior, likelihood)`. | Non. Pas de calcul bayésien ni prior/posterior dans l'API ou le Studio. |
| **Prompt system** | Oui : rôles **System**, **Extractor**, **Evidence Scorer**, **Bayes Arbiter**, **Renderer** ; templates de prompts (chunk → claims JSON, claims → observations, observations → posterior + decision). | Non. Aucun appel LLM extractor/scorer/arbiter/renderer dans le backend. |
| **Meta (claims)** | Oui : `type` (perf, sécurité, UX, etc.), `confidence`, `source_line_start/end`, prior/posterior, `decision`, `why`. | Partiel : le schéma IR prévoit `type`, `confidence`, `source_line_*` et désormais **`description`**. Seuls `id`, `text`, `description`, `checked` sont utilisés dans le Studio. |
| **Enrichissement affichage** | — | Oui : champ **`description`** sur les claims (ir_schema + ir_inventaire.json) ; le formulaire d'arbitrage affiche la description sous chaque claim pour que « les features disent quelque chose ». |

**Prochaines étapes possibles** (sans ordre imposé) :

1. **Enrichir automatiquement** les descriptions (pipeline md→json ou LLM extractor sur ir_inventaire.md / PRD).
2. **Brancher l'Extractor** (LLM) sur chunks PRD/IR → claims avec `text`, `description`, `type`, `location`.
3. **Brancher Evidence Scorer + Bayes Arbiter** (LLM + calcul déterministe) → prior, likelihood, posterior, decision, why ; afficher en lecture dans l'UI et permettre surcharge manuelle (HTMX).
4. **Resserrer le prompt system** (Roadmap § feature flags) pour réduire appels LLM si besoin.
