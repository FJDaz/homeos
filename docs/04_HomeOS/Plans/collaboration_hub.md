# Collaboration Hub Claude ↔ KIMI

---

## 🎯 MISSION KIMI : ÉTAPE 11 — Drag & Drop Aperçus

**Date** : 2026-02-12 23:10:00
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Status** : 🟡 EN COURS KIMI (démarré 21:45)

### Instructions

Rendre les aperçus (N0/N1/N2) draggables depuis le preview band vers le canvas.

**Documentation complète** : `docs/02-sullivan/FIGMA-Like/ROADMAP_LOT2.md` (ÉTAPE 11, lignes 91-118)

### Tâches à réaliser

- [ ] Modifier `Frontend/3. STENCILER/static/stenciler.js`
- [ ] Ajouter attribut `draggable="true"` sur éléments `.preview-item`
- [ ] Implémenter listeners `dragstart` pour chaque aperçu (N0, N1, N2)
- [ ] Transmettre `entity_id` + `niveau` dans `event.dataTransfer`
- [ ] Gérer `dragover` et `drop` sur le canvas Fabric.js
- [ ] Instancier le bon composant selon le niveau (N0→Corps, N1→Organe, N2→Cellule)

### Livrable

- Aperçus draggables depuis le preview band
- Drop sur canvas → création d'instance visuelle
- Gestion des 3 niveaux (N0, N1, N2)

### Validation requise (Article 10 Constitution)

François-Jean doit valider visuellement :
- Drag aperçu "Brainstorm" → canvas
- Vérifier création Corps
- Drag aperçu Organe (N1) → canvas
- Vérifier création Organe

### Signal de fin attendu

Une fois terminé, écrire dans `collaboration_hub.md` :

```
@CLAUDE_VALIDATE

## CR KIMI : ÉTAPE 11 TERMINÉE

**Date** : [timestamp]
**Status** : ✅ TERMINÉ

### Résumé

[Résumé des modifications]

### Fichiers modifiés

- Frontend/3. STENCILER/static/stenciler.js
- [autres fichiers si nécessaire]

### Tests effectués

- [Liste des tests]
```

**URL validation** : http://localhost:9998/stenciler

---

**Note Backend Lead** : L'ÉTAPE 12 (Backend endpoint `/api/components/instantiate`) sera démarrée après validation FJ de cette étape.
