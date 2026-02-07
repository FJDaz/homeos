# MISSION UNIQUE POUR KIMI

**De** : Claude-Code (Senior)
**Pour** : KIMI Padawan
**Date** : 4 février 2026

---

## 🔴 MISSION : EXTRAIRE LES COMPOSANTS DE arbiter-interface.html

### URL SOURCE
```
http://localhost:8765/Frontend/arbiter-interface.html
```

### CE QUE TU DOIS FAIRE

1. **Ouvre le fichier** `Frontend/arbiter-interface.html`

2. **Extrais TOUS les composants visuels** :
   - Les cartes (profile-card, etc.)
   - Les boutons
   - Les badges
   - Les inputs
   - Les modals
   - Les headers/footers
   - Tout élément UI réutilisable

3. **Pour chaque composant extrait, récupère** :
   - Le **HTML** complet
   - Le **CSS** associé (inline ou depuis `<style>`)

4. **Nomme-les selon Atomic Design si possible** :
   - `atoms/` : boutons, inputs, badges, icônes
   - `molecules/` : cartes, form-groups, search-bars
   - `organisms/` : headers, sidebars, modals
   - `templates/` : layouts complets
   - `pages/` : pages entières

5. **Ajoute-les à la library** :
   - Fichier : `output/components/library.json`
   - Même structure que les composants existants

---

## EXEMPLE DE STRUCTURE À AJOUTER

```json
{
  "categories": {
    "molecules": {
      "profile_card": {
        "id": "molecules_profile_card",
        "category": "molecules",
        "name": "profile_card",
        "html": "<div class=\"profile-card\">...</div>",
        "css": ".profile-card { ... }",
        "description": "Carte de profil avec avatar",
        "tags": ["card", "profile", "user"]
      }
    }
  }
}
```

---

## FICHIERS

| Fichier | Action |
|---------|--------|
| `Frontend/arbiter-interface.html` | LIRE - Source des composants |
| `output/components/library.json` | MODIFIER - Ajouter les nouveaux composants |

---

## SI LE NOMMAGE ATOMIC EST DIFFICILE

Pas grave, nomme-les de façon descriptive :
- `arbiter_profile_card`
- `arbiter_status_badge`
- `arbiter_action_button`

On les recatégorisera après.

---

*— Claude-Code Senior*
