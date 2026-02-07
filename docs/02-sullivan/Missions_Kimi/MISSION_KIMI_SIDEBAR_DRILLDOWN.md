# MISSION KIMI : Sidebar Drill-Down navigable

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 5 fevrier 2026
**Priorite** : HAUTE

---

## Objectif

Creer un composant sidebar + zone principale qui permet de naviguer
dans le genome enrichi (N0 Genome → N1 Corps → N2 Organes → N3 Atomes).

## Donnees source

`output/studio/genome_enrichi.json` — le genome a 9 corps, 20 organes, 44 atomes.

## Ce que tu dois creer

### Fichier : `Frontend/drilldown-sidebar.html`

Page HTML autonome (standalone, testable directement) qui :

1. Charge `genome_enrichi.json` au demarrage (fetch)
2. Affiche une sidebar a gauche avec l'arbre du genome
3. Affiche une zone principale a droite selon le noeud selectionne

### Sidebar (gauche, 280px fixe)

```
Mon App
├── Studio [todo]
│   ├── Reports
│   │   ├── Get Ir Report
│   │   └── Get Arbitrage Report
│   ├── Arbitrage
│   │   └── ...
│   └── Navigation
│       └── ...
├── Sullivan Agent [todo]
│   └── ...
├── Designer [todo]
│   └── ...
└── System [todo]
    └── health
```

- Arbre collapsible (clic sur un noeud = expand/collapse ses enfants)
- Double-clic sur un noeud = selectionne ET affiche dans la zone principale
- Icones par niveau : 📄 Corps, 📦 Organe, ⚛️ Atome
- Statut colore : todo=gris, wip=orange, ok=vert

### Zone principale (droite)

Selon le niveau du noeud selectionne :

**N0 - Genome** (etat initial) :
- Nom du projet
- Stats (9 corps, 20 organes, 44 atomes)
- Barre de progression
- Liste des Corps avec leurs statuts

**N1 - Corps** :
- Nom du corps
- Liste de ses organes
- Nombre d'atomes total

**N2 - Organe** :
- Nom de l'organe
- Liste de ses atomes avec visual_hint et component_ref

**N3 - Atome** :
- Nom, endpoint, method
- visual_hint et wireframe_sketch
- component_ref (lien vers library.json)
- Boutons : [Valider] [Remplacer] [Supprimer]

### Breadcrumb (haut de la zone principale)

```
Genome > Studio > Reports > Get Ir Report
```
Chaque element cliquable pour remonter.

## Style

- DaisyUI + Tailwind CDN (coherent avec la library)
- Theme sombre (#1a1a1a fond, #7cb342 accent)
- Meme charte que arbiter-showcase.html

## Contraintes techniques

- HTML/CSS/JS vanilla (pas de framework)
- Tailwind CDN : `<script src="https://cdn.tailwindcss.com"></script>`
- DaisyUI CDN : `<link href="https://cdn.jsdelivr.net/npm/daisyui@4/dist/full.min.css" rel="stylesheet">`
- Fetch le JSON depuis : `/output/studio/genome_enrichi.json`
  (ou chemin relatif si servi par le serveur statique 8080)

## Test

Ouvrir dans le navigateur via le serveur statique :
```
http://localhost:8080/drilldown-sidebar.html
```

## Important

- PAS de generation de composants, juste de la NAVIGATION
- Le but c'est voir l'arbre et cliquer dedans
- Simple, propre, fonctionnel

---

*— Claude-Code Senior*
