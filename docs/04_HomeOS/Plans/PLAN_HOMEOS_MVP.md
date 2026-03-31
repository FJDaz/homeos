# Plan HoméOS — MVP Pédagogique
**Auteur :** FJD
**Date :** 2026-03-28
**Horizon :** Sandbox déployé, pipeline complet Figma → FRD → CI/CD

---

## Contexte — Ce qu'on a

L'app est conçue. L'UI est passée par Figma. Le pipeline technique existe mais les coutures entre les étapes sont cassées ou confuses. Le CI/CD n'existe pas.

Pipeline cible :
```
Figma / SVG / React / HTML
      ↓ Bridge
  Landing Import
      ↓
 Intent Viewer   ←  annotation + manifest
      ↓
  FRD Editor     ←  wire + implémentation
      ↓
  Test local     ←  aperçu
      ↓
  Deploy         ←  CI/CD sandbox
```

---

## PRIORITÉ 1 — Coutures cassées (bloquant pédagogie)

### M100 — Landing Import unifiée
**Problème :** les formats d'entrée sont éparpillés sur plusieurs écrans, le plugin Bridge est silencieux.
**Objectif :** un seul écran d'entrée qui :
- Reçoit le SVG Figma depuis le plugin Bridge (+ feedback visible : "X écrans reçus")
- Permet d'uploader un SVG Illustrator
- Permet d'uploader du HTML/CSS vanilla → conversion en SVG annoté
- Permet d'uploader du JSX/React (Kimi) → conversion en Tailwind + SVG annoté
- Liste les écrans reçus avec thumbnail, checkbox de sélection
- Bouton "Entrer dans HoméOS" pour les écrans cochés
- Impose la présence d'un `manifest.json` (projet courant) — sans manifest, bloqué

**Dépendance :** server_v3.py routes `/api/import/*` à créer ou consolider
**Actor :** CLAUDE (backend) + GEMINI (frontend)

---

### M101 — Bridge Plugin — feedback et robustesse
**Problème :** le plugin Figma Bridge est "tacitum" — aucun retour visuel, état inconnu.
**Objectif :**
- Toast de confirmation côté Figma ("Envoyé à HoméOS — 3 écrans")
- Côté Landing Import : notification push ou polling (badge de nouveaux écrans)
- Sélection des pages à exporter (Figma gratuit = 3 pages max → checkbox)
- Export propre SVG par page (pas un SVG global)

**Actor :** GEMINI (plugin Figma JS) + CLAUDE (backend webhook)

---

### M102 — Intent Viewer — refonte flux
**Problème :** le tableau intent est perdu de vue, le flux annotation → FRD est flou.
**Objectif :**
- [x] Afficher le tableau des intents après upload/import (Design Workbench)
- [x] Lancement de l'annotation (KIMI / AI) depuis ce tableau (Drawer Pattern)
- [x] Bouton "Ouvrir dans FRD Editor" par intent
- [x] Manifest obligatoire : affichage dans le header

**Actor :** CLAUDE (backend) + GEMINI (frontend)

---

## PRIORITÉ 2 — FRD Editor — Wire mode restructuré

### M103 — Wire mode v5 : analyse automatique + z-index bilan
**Problème actuel :** Wire = un collapse qu'on ouvre, on lance, on implémente. Pas assez fluide. L'audit UI est cosmétique.
**Objectif :**
- Wire se lance automatiquement à l'ouverture du mode Wire (pas de bouton "Analyser" à cliquer)
- Résultat affiché en overlay z-index sur la preview :
  - Colonne gauche : **Bilan** (intentions détectées, statut ok/error)
  - Colonne droite : **Plan** (étapes d'implémentation, bijection point par point)
  - Chaque ligne bilan face à sa ligne plan (bijection visuelle)
- Un seul bouton en bas : **IMPLÉMENTER**
- Suppression du collapse accordion — Wire est un mode à part entière
- L'audit UI actuel (cosmétique) est supprimé ou remplacé par le bilan Wire

**Dépendance :** M99 (wire-source, Monaco pop-in) — déjà livré
**Actor :** CLAUDE (wire_analyzer.py + server_v3.py) + GEMINI (frd_editor.html/css)

---

### M104 — Wire — enrichissement INTENT_MAP
**Problème :** seul `runWire` est mappé. Les templates étudiants ont des intents réels.
**Objectif :**
- Enrichir l'INTENT_MAP avec les routes réelles du projet courant (lecture du manifest + routes server_v3.py)
- Détecter aussi les `fetch('/api/...')` dans les scripts inline
- Afficher les intents non mappés comme "À implémenter" (pas juste "error")

**Actor :** CLAUDE (wire_analyzer.py)

---

## PRIORITÉ 3 — Test local → Deploy

### M105 — Mode Aperçu / Test local
**Objectif :**
- Bouton "Aperçu" dans FRD Editor → lance un serveur local temporaire sur le template courant
- Affiche dans un vrai onglet (pas une iframe) pour tester les interactions réelles
- Bouton "Retour FRD" si problème
- Bouton "Déployer" si OK

**Actor :** CLAUDE (server_v3.py — route /api/preview/run)

---

### M106 — CI/CD Sandbox 0€
**Contexte :** OVH = hébergement mutualisé "Perso" (offre 2012). Pas de SSH persistant, pas de Docker, pas de Python. L'OVH ne peut pas héberger FastAPI.

**Plateforme retenue : Hugging Face Spaces (Docker)**
- Compte HF déjà existant (Spinoza), `HF_TOKEN` déjà dans la stack
- Pas de trial, pas de CB, pas de sleep
- URL stable : `https://{username}-homeos.hf.space`
- Custom domain CNAME OVH possible

**Architecture retenue :**
```
GitHub (repo)
    ↓ push main
GitHub Actions  →  build + push HF Space (API)
                                    ↓
                       HF Spaces Docker (FastAPI)
                       server_v3.py + templates + API
                                    ↓
                   OVH DNS : CNAME homeos.fjdaz.com → {username}.hf.space
```

**Livrables M106 :**
- `Dockerfile` adapté HF Spaces (port 7860, USER 1000, pas de root)
- `README.md` Space (metadata YAML : `sdk: docker`, `app_port: 7860`)
- `.github/workflows/deploy-hf.yml` — push `main` → `git push hf-space` via token
- DNS OVH : CNAME `homeos` → `{username}-homeos.hf.space`
- Variables HF Spaces secrets : `HF_TOKEN`, `GOOGLE_API_KEY`, `MISTRAL_API_KEY`

**Ce qu'il faut de FJD avant M106 :**
- Username HF exact (pour nommer le Space)
- Repo GitHub cible (public ou privé)
- `HF_TOKEN` avec scope `write` (pour push Space via CI)

**Actor :** CLAUDE (Dockerfile, GitHub Actions YAML)

---

## Ordre d'exécution recommandé

```
M101-bis (Bridge design HoméOS)  — Gemini, 1 run
M100 (Landing Import)            — bloquant pédagogie, 2-3 sessions
M102 (Intent Viewer flux)        — dépend de M100
M103 (Wire v5)                   — UX core, 2 sessions
M104 (INTENT_MAP enrichi)        — dépend M103
M105 (Aperçu local)              — 1 session
M106 (CI/CD HF Spaces + OVH DNS) — FJD fournit username HF + repo GitHub, 1-2 sessions
```

---

## Ce qu'il faut de FJD pour M106

- Username HF exact + `HF_TOKEN` avec scope `write`
- Domaine OVH : `fjdaz.com` (accès zone DNS pour CNAME)
- Confirmation : repo GitHub où pousser (public ou privé)

---

*Document vivant — à mettre à jour après chaque mission.*
