# Missions potentiellement bloquantes — Identity Sullivan

**Date** : 2 février 2026  
**Contexte** : Identités Sullivan (identity.py, PRD, stencils) et missions à risque de blocage.

---

## 1. Upload images (designer stencil) — RÉSOLU

**Problème** : Images trop volumineuses → base64 dépasse la limite Gemini (~20MB inline).

**Solution implémentée** : Mode upload `sullivan/upload/image_preprocessor.py`
- Resize si dimension > 1920px
- Compression JPEG (quality 85)
- Cible ~3MB max
- Intégré dans DesignAnalyzer, DesignPrinciplesExtractor

**Fichiers** : `Backend/Prod/sullivan/upload/`, `design_analyzer.py`, `design_principles_extractor.py`

---

## 2. DesignAnalyzer — appel vision réel

**Problème** : Le mock était encore présent (retour simulé au lieu d’appel Gemini).

**Statut** : Corrigé — appel réel à `GeminiClient.generate_with_image()`.

---

## 3. frd generate — contexte > 50k tokens

**Risque** : `design_structure` + `genome` + `webography` peut dépasser 50k tokens → Gemini utilisé, mais si > 1M tokens → échec possible.

**Mitigation** : Tronquer le prompt à 50k caractères (déjà en place dans frontend_mode.py).

---

## 4. Orchestrator — limites fichiers — RÉSOLU

**Problème** : `MAX_FILE_SIZE = 50KB`, `MAX_TOTAL_SIZE = 100KB` par step. Contexte trop gros → troncature.

**Solution** : Limites augmentées à 200KB/file, 1MB total (orchestrator.py). Troncature ajustée (160KB + 40KB).

---

## 5. SullivanAuditor — images screenshots — RÉSOLU

**Risque** : `generate_with_image` avec screenshots Playwright. Si la page est très grande → image trop lourde.

**Solution implémentée** : `preprocess_for_gemini` / `preprocess_bytes_for_gemini` intégrés dans `_image_to_base64` (sullivan_auditor.py). Screenshots path ou bytes sont resize/compressés avant envoi à Gemini.

---

## 6. Inférence top-down (PRD)

**Problème** : Structures génériques (`generic_organe`, `generic_molecule`) au lieu d’inférence réelle.

**Impact** : Frontend généré peu adapté au backend.

**Priorité** : Haute (PRD).

---

## 7. Sauvegarde composants

**Problème** : Génération OK, fichiers souvent en temporaire. Pas de sauvegarde systématique vers Elite Library.

**Priorité** : Moyenne.

---

## 8. DesignPrinciplesExtractor — doublon de classe

**Note** : Deux classes `DesignPrinciplesExtractor` dans le même fichier. La seconde écrase la première. Les deux ont été corrigées (signature generate_with_image, preprocessing).

---

## Synthèse par stencil (identity.py)

| Stencil    | Endpoint                    | Risque bloquant                    |
|-----------|-----------------------------|------------------------------------|
| monitoring | /health                     | Aucun                              |
| orchestrator | /execute                 | Aucun                              |
| gallery   | /sullivan/search, /components | Aucun                          |
| **designer** | /sullivan/designer/upload | **Images trop grosses** — résolu   |
| preview   | /sullivan/preview            | Aucun                              |

---

## Recommandations

1. **Pillow** : Ajouter à `requirements.txt` pour le mode upload (déjà fait).
2. **SullivanAuditor** : Intégrer `preprocess_for_gemini` pour les screenshots — fait.
3. **Orchestrator** : Revoir `MAX_FILE_SIZE` / `MAX_TOTAL_SIZE` — fait (200KB/file, 1MB total).
4. **DesignPrinciplesExtractor** : Vérifier la signature ligne 205.

---

## 9. Chunking agressif — Solution Gemini timeouts — RÉSOLU

**Problème** : Plans aetherflow > 30k tokens envoyés en bloc à Gemini → timeouts fréquents (65k tokens pour 2 steps).

**Solution implémentée** (02 fév 2026) :
- `smart_context_router.py` : `CHUNK_THRESHOLD` réduit de 30k à **15k tokens**
- `step_chunker.py` : `DEFAULT_CHUNK_SIZE` réduit de 20k à **12k tokens**, `MAX_CHUNK_SIZE` aligné à 15k

**Effet** : Les steps > 15k tokens sont automatiquement découpés en chunks de ~12k tokens, traités séquentiellement par le système existant (`StepChunker`, `SectionGenerator`).

**Fichiers** : `Backend/Prod/models/smart_context_router.py`, `Backend/Prod/models/step_chunker.py`
