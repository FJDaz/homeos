# MISSION KIMI : Enrichir le Genome avec structure Corps/Organes/Atomes

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 5 fevrier 2026
**Priorite** : HAUTE (bloquant pour le drill-down)

---

## Contexte

L'IR visuelle est faite (44 endpoints mappes avec DaisyUI).
Maintenant il faut structurer le Genome en niveaux navigables :

```
N0 Genome → N1 Corps (pages) → N2 Organes (zones) → N3 Atomes (composants)
```

## Source

Le fichier IR visuel : `output/studio/ir_visuel_edite.md`
La library : `output/components/library.json`

## Ce que tu dois faire

### 1. Lire l'IR visuelle et grouper les endpoints par "page" (Corps)

Regles de groupement :
- `/studio/*` → Corps "Studio"
- `/sullivan/agent/*` → Corps "Sullivan Agent"
- `/sullivan/designer/*` → Corps "Designer"
- `/sullivan/preview/*` → Corps "Preview"
- `/health` → Corps "System"
- `/homeos/*` → Corps "HomeOS"
- `/components/*` → Corps "Components"
- `/execute` → Corps "Execute"

### 2. Pour chaque Corps, identifier les Organes (zones fonctionnelles)

Exemple pour Corps "Studio" :
- Organe "Reports" (ir, arbitrage)
- Organe "Navigation" (step, next, zoom)
- Organe "Arbitrage" (forms, validate, typologies)
- Organe "Session" (session, reset)
- Organe "Genome" (genome, summary, finalize)

### 3. Pour chaque Organe, lister les Atomes (composants DaisyUI)

Prendre le `inferred_daisy_component` de l'IR visuelle.

### 4. Produire le fichier enrichi

**Fichier a creer** : `output/studio/genome_enrichi.json`

```json
{
  "genome": {
    "name": "AetherFlow Studio",
    "version": "1.0-enriched",
    "source": "ir_visuel_edite.md",
    "corps": [
      {
        "id": "studio",
        "name": "Studio",
        "status": "todo",
        "figma_type": "FRAME",
        "organes": [
          {
            "id": "studio_reports",
            "name": "Reports",
            "figma_type": "COMPONENT_SET",
            "atomes": [
              {
                "id": "ir_report_list",
                "name": "Liste IR",
                "endpoint": "/studio/reports/ir",
                "method": "GET",
                "component_ref": "daisy_list",
                "figma_type": "INSTANCE",
                "visual_hint": "list"
              },
              {
                "id": "arbitrage_report_list",
                "name": "Liste Arbitrage",
                "endpoint": "/studio/reports/arbitrage",
                "method": "GET",
                "component_ref": "daisy_list",
                "figma_type": "INSTANCE",
                "visual_hint": "list"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 5. Stats a la fin

```json
{
  "stats": {
    "total_corps": N,
    "total_organes": N,
    "total_atomes": N,
    "coverage": "44/44 endpoints mappes"
  }
}
```

## Important

- TOUS les 44 endpoints de l'IR doivent apparaitre dans un Atome
- Chaque Atome pointe vers un composant DaisyUI de la library (`component_ref`)
- Le `status` de chaque Corps est "todo" par defaut
- Ne pas inventer d'endpoints — utilise UNIQUEMENT ceux de l'IR

---

*— Claude-Code Senior*
