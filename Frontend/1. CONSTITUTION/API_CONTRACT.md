# API CONTRACT — AetherFlow HomeOS
> Source de vérité partagée entre agents BKD (backend) et FRD (frontend).
> **Règle absolue : tout run BKD qui crée ou modifie une route doit mettre ce fichier à jour dans la même mission.**
> Gemini reçoit ce fichier en `input_files` dans toutes les missions FRD impliquant des appels API.

---

## Domaine FRD — `/api/frd`

### `GET /api/frd/file?name=<filename>`
Récupère le contenu d'un template HTML.
```
→ { status: "ok", name: string, content: string }
→ 404 si fichier non trouvé
```

### `POST /api/frd/file`
Sauvegarde un template HTML.
```
payload: { name: string, content: string }
→ { status: "ok", message: "Sauvegardé ✓" }
```

### `POST /api/frd/chat`  *(FastAPI server_v3.py — port 9998)*
Envoie un message à Sullivan (LLM). **[Mission 64] Mode Engineer : Orchestration Groq (Router/Patch JS) + Gemini (Executeur HTML).**
```
payload: { message: string, html: string, mode?: "construct"|"design"|"conseil", assets?: [], name?: string }
→ { explanation: string, html: string }
   explanation = réponse textuelle Sullivan ou Groq
   html = HTML modifié ou inchangé
```

### `POST /api/frd/kimi/start`  *(FastAPI server_v3.py)*
Lance une génération KIMI async.
```
payload: { instruction: string, html: string }
→ { job_id: string }
```

### `GET /api/frd/kimi/result/{job_id}`  *(FastAPI server_v3.py)*
Demande une variante design à KIMI.
```
payload: { instruction: string, html: string }
→ { variants: [{ label: string, html: string }] }
```

### `POST /api/frd/wire`  *(FastAPI server_v3.py)*
Diagnostic statique HTML+JS via Codestral.
```
payload: { html: string }
→ { diagnostic: string }  ← markdown structuré
```

### `GET /api/frd/manifest/{name}`
Retourne le manifeste JSON du template (contrat DOM machine-readable).
```
→ { $schema, file, js_controller, version, required_elements, required_classes, required_scripts, forbidden, update_protocol }
→ 404 si aucun manifeste pour ce template
```

### `GET /api/frd/manifest/{name}/prompt`
Retourne le bloc de contrainte système à injecter dans tout prompt agent modifiant ce template.
```
→ { constraint_prompt: string }  ← texte brut multilignes
→ 404 si aucun manifeste pour ce template
```

---

## Domaine BKD — `/api/bkd`

### `GET /api/bkd/projects`
Liste les projets enregistrés.
```
→ { projects: [{ id, name, path, created_at, last_opened }] }
```

### `POST /api/bkd/projects`
Crée un projet.
```
payload: { name: string, path: string }
→ { status: "ok", project: { id, name, path, created_at, last_opened } }
```

### `DELETE /api/bkd/projects/{project_id}`
Supprime un projet.

### `GET /api/bkd/file?project_id=<id>&path=<rel_path>`
Lit un fichier du projet.
```
→ { content: string, path: string }
```

### `POST /api/bkd/file`
Écrit un fichier du projet.
```
payload: { project_id: string, path: string, content: string }
→ { status: "ok" }
```

### `POST /api/bkd/chat`
Chat Sullivan BKD (backend/devops).
```
payload: { message: string, history?: [{role, text}], project_id?: string }
→ { text: string, provider: string, model: string }
```

### `GET /api/sullivan/pulse`
État des providers LLM.
```
→ { gemini: { ok, latency_ms, ts }, mimo: { ok, latency_ms, ts } }
```

---

## Domaine Genome — `/api/genome`, `/api/layout`, `/api/manifest`

### `GET /api/genome` / `POST /api/genome`
Retourne ou sauvegarde le génome enrichi complet.

### `POST /api/layout`
Met à jour le layout (`{ ...overrides } → { ok: true }`).

### `POST /api/manifest/patch`
Patch partiel (`{ elements: [{id, ...updates}] } → { ok: true }`).

### `POST /api/organ-move` / `POST /api/comp-move`
Déplace organe ou composant, relance le composer.
```
payload: { id, x, y, s? }  →  { ok: true }
```

### `POST /api/infer_layout`
Inférence layout heuristique ou LLM.
```
payload: { organs: [], mode?: "heuristic"|"llm" }
→ { result: {}, tier: "heuristic"|"llm"|"heuristic_fallback" }
```

---

## Domaine Retro-Genome — `/api/retro-genome`

### `GET /api/retro-genome/status`
État du pipeline (`→ { step, message }`).

### `POST /api/retro-genome/upload`
Upload PNG(s) multipart pour analyse.

### `POST /api/retro-genome/upload-svg`
Upload SVG Figma (`{ svg, name } → { visual_analysis, archetype }`).

### `POST /api/retro-genome/chat`
Chat Sullivan sur l'analyse (`{ message } → { explanation }`).

### `POST /api/retro-genome/approve`
Valide le rendu reality (`→ { status: "ok" }`).

### `POST /api/retro-genome/generate-html`
Génère reality.html (`→ { status, html_path }`).

### `POST /api/retro-genome/export-zip`
Exporte en ZIP (`→ { status, zip_path }`).

### `POST /api/retro-genome/export-manifest`
Exporte le manifest inféré (`→ { status, manifest_path }`).

---

## Domaine BRS — `/api/brs`

### `GET /api/brs/buffer-questions`
Retourne les questions de buffering Sullivan.
```
→ { questions: string[] }
```

### `POST /api/brs/dispatch`
Dispatch un prompt vers les 3 modèles en parallèle (mode COUNCIL).
```
payload: { session_id: string, prompt: string, buffer_answers?: {} }
→ { status: "streaming" }
```

### `GET /api/brs/stream/{session_id}/{provider}`
SSE — stream des tokens d'un provider après dispatch.
```
provider: "gemini" | "groq" | "codestral"
events: token(data: string) | done
```

### `GET /api/brs/chat/{provider}`  *(FastAPI server_v3.py — SSE via GET)*
Chat individuel persistant (mode MULTIPLEX).
```
provider: "gemini" | "groq" | "codestral"
payload: { session_id: string, message: string }
→ SSE stream: event:token(data: string) | event:done
```

### `POST /api/brs/capture`
Capture une pépite dans le basket.
```
payload: { session_id: string, text: string, provider: string }
→ { status: "ok", nugget_id: string }
```

### `GET /api/brs/basket/{session_id}`
Récupère le basket de la session.
```
→ { session_id: string, basket: nugget[] }
```

### `POST /api/brs/generate-prd`
Génère un PRD depuis le basket.
```
payload: { session_id: string, project_name: string }
→ { prd_content: string } | { error: string }
```

### `GET /api/brs/search?q=<query>`
Recherche plein texte dans les messages BRS.
```
→ { status: "ok", query: string, results: [{ provider, content, excerpt }] }
```

### `GET /api/brs/arbitrate/{session_id}`
SSE — synthèse Sullivan automatique après COUNCIL.
```
events: message(data: string token) | done
```

### `POST /api/brs/rank`
Classement arbitré des 3 réponses COUNCIL.
```
payload: { session_id: string }
→ { ranking: string }  ← markdown : tableau + synthèse qualifiée
→ { error: string } si aucune réponse en session
```

---

## Convention de mise à jour

Lors de toute mission BKD :
1. Implémenter la route
2. Ajouter/modifier l'entrée correspondante dans ce fichier
3. Indiquer `🔴 À IMPLÉMENTER` pour les routes déclarées côté frontend mais pas encore backend

*Dernière mise à jour : 2026-03-24 — Migration FastAPI complète (M85→M87-D). Serveur : server_v3.py port 9998. server_9998_v2.py archivé.*
