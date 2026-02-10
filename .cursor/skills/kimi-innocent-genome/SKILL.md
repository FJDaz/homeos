# SKILL: Kimi Innocent - Genome Inference

**Version**: 1.0  
**Date**: 7 février 2026  
**Statut**: OPÉRATIONNEL

---

## 🎯 Objectif

Produire un **Genome Spatialisé N0-N3** avec **29 composants exactement** qui permette à un développeur frontend de générer l'interface sans connaissance préalable du projet.

---

## 🚨 Activation Condition

Ce SKILL s'active quand:
- L'utilisateur demande une inférence de genome frontend
- Il y a besoin de structurer N0-N3 (World > Body > Organ > Atom)
- Le projet Homeos/Sullivan est concerné

---

## 📋 Workflow Exécutable

### ÉTAPE 1: Lecture des 4 Bundles (30 min)

```python
# Ordre STRICT de priorité (Logs > Code > Doc)
bundles = [
    "docs/04-homeos/STATUS_REPORT_HOMEOS.md",  # Plus récent = priorité max
    "docs/02-sullivan/UX/Parcours UX Sullivan.md",  # Flow utilisateur
    "docs/04-homeos/PRD/PRD_HOMEOS_ETAT_ACTUEL.md",  # Contexte général
    "Backend/Prod/sullivan/studio_routes*.py",  # Endpoints réels
]
```

### ÉTAPE 2: Table de Confrontation

Créer markdown:
```markdown
| Phase UX | Intention | Endpoint | Statut | Visual Hint |
|----------|-----------|----------|--------|-------------|
| 1. IR | Inventorier | /studio/reports/ir | ✅ | table |
| 2. Arbiter | Décider | /studio/arbitrage/forms | ✅ | stencil-card |
```

**Légende**:
- ✅ = 2+ sources confirment
- ⚠️ = 1 source seule
- ❓ = Contradiction non résolue

### ÉTAPE 3: Extraction N0-N3

Structure obligatoire:
```json
{
  "n0_phases": [{
    "n1_sections": [{
      "n2_features": [{
        "n3_components": [{
          "id": "comp_xxx",
          "name": "Nom UI-Friendly",
          "endpoint": "/studio/...",
          "method": "GET",
          "visual_hint": "table|card|stencil-card|...",
          "layout_hint": "grid|flex|stack",
          "interaction_type": "click|submit|drag",
          "description_ui": "L'utilisateur voit..."
        }]
      }]
    }]
  }]
}
```

### ÉTAPE 4: Application des 10 Wireframes FRD V2

Pour chaque composant, choisir parmi:

1. **status** → LEDs santé projet (4 indicateurs)
2. **zoom-controls** → Navigation ← Out / 🔍 Corps ▼ / In →
3. **download** → Carte ZIP + bouton 📥
4. **chat-input** → Champ + 📎😊 + envoi
5. **color-palette** → 4 swatches + chips style
6. **choice-card** → Radio cards 2×2 (styles)
7. **stencil-card** → Fiche pouvoir Garder/Réserve
8. **detail-card** → Fiche technique endpoint
9. **launch-button** → Bouton fusée 🚀
10. **apply-changes** → 💾 Appliquer / ↩️ Annuler

### ÉTAPE 5: Réinterprétations UI

Traductions obligatoires:
- GET → "📖 Voir"
- POST → "➕ Ajouter"  
- PUT → "✏️ Modifier"
- DELETE → "🗑️ Supprimer"

Nettoyage: Supprimer "Comp ", "Component " des noms.

### ÉTAPE 6: Validation Comptage

**DOIT avoir exactement 29 composants.**

Si ≠ 29:
- < 29 → Ajouter composants manquants (inférence)
- > 29 → Fusionner ou supprimer doublons

### ÉTAPE 7: Normalisation & Output

```python
def normalize_keys(obj):
    """Normalise MAJUSCULES → minuscules"""
    if isinstance(obj, dict):
        return {k.lower(): normalize_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [normalize_keys(item) for item in obj]
    return obj
```

Output: `genome_inferred_kimi_innocent.json`

---

## 🎨 Templates Wireframes HTML

### Template: stencil-card
```html
<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
  <div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:6px;">💡 {titre}</div>
  <div style="font-size:10px;color:#6b7280;margin-bottom:10px;">{description}</div>
  <div style="display:flex;gap:8px;">
    <span style="flex:1;padding:6px;background:#22c55e;border-radius:4px;text-align:center;font-size:10px;color:white;">🟢 Garder</span>
    <span style="flex:1;padding:6px;background:#f3f4f6;border-radius:4px;text-align:center;font-size:10px;color:#6b7280;">⚪ Réserve</span>
  </div>
</div>
```

### Template: detail-card
```html
<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
  <div style="font-size:11px;font-weight:600;font-family:monospace;margin-bottom:6px;">🔧 {endpoint}</div>
  <div style="font-size:9px;color:#6b7280;margin-bottom:8px;">Type: {method}</div>
  <div style="display:flex;gap:8px;">
    <span style="flex:1;padding:6px;background:#f3f4f6;border-radius:4px;text-align:center;font-size:10px;">📋 Copier</span>
    <span style="flex:1;padding:6px;background:#3b82f6;border-radius:4px;text-align:center;font-size:10px;color:white;">↗️ Tester</span>
  </div>
</div>
```

### Template: zoom-controls
```html
<div style="background:white;border:2px solid #e5e7eb;border-radius:8px;padding:12px;">
  <div style="font-size:10px;font-weight:600;color:#374151;margin-bottom:8px;">🔭 Navigation</div>
  <div style="display:flex;gap:6px;margin-bottom:10px;">
    <span style="flex:1;padding:8px;background:#f3f4f6;border-radius:4px;text-align:center;font-size:10px;">← Out</span>
    <span style="flex:1;padding:8px;background:#3b82f6;color:white;border-radius:4px;text-align:center;font-size:10px;font-weight:600;">🔍 Corps ▼</span>
    <span style="flex:1;padding:8px;background:#f3f4f6;border-radius:4px;text-align:center;font-size:10px;">In →</span>
  </div>
  <div style="display:flex;align-items:center;justify-content:center;gap:8px;font-size:9px;color:#6b7280;">
    <span style="color:#22c55e;font-weight:bold;">◉ Corps</span><span>></span><span>○ Organe</span><span>></span><span>○ Atome</span>
  </div>
</div>
```

---

## ✅ Checklist Validation

Avant commit:
- [ ] 29 composants exactement
- [ ] Structure N0-N3 complète
- [ ] 10 wireframes FRD V2 présents
- [ ] Réinterprétations naming appliquées
- [ ] Normalisation JSON ok
- [ ] Route /studio supportée
- [ ] Layout élégant (tabs, sidebar, sticky header)
- [ ] Tests curl: 200 sur /studio?step=4
- [ ] Git commit + push

---

## 🔗 Références

- Méthode complète: `docs/02-sullivan/Methodologies/METHODE_KIMI_INNOCENT.md`
- Exemple output: `docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/genome_inferred_kimi_innocent.json`
- Serveur viewer: `docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py`

---

**Mémo**: "4 bundles, 5 phases, 29 composants, 10 wireframes, 0 approximation."
