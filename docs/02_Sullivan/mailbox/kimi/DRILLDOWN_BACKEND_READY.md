# DRILL-DOWN BACKEND — PRÊT ✅

**Date** : 12 février 2026, 14:15
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Objet** : Endpoints `/api/drilldown/*` fonctionnels

---

## ✅ ÉTAPE 3 TERMINÉE

Les 3 endpoints de navigation hiérarchique sont créés, corrigés et testés. Tu peux démarrer l'Étape 4.

---

## 🔗 ENDPOINTS DISPONIBLES

### 1. POST /api/drilldown/enter — Descendre d'un niveau

**URL** :
```
POST http://localhost:8000/api/drilldown/enter
```

**Body** (JSON) :
```json
{
  "path": "n0[0]",
  "child_index": 0
}
```

**Paramètres** :
- `path` : Chemin actuel (ex: `"n0[0]"` pour le premier Corps)
- `child_index` : Index de l'enfant à explorer (défaut: 0)

**Réponse** :
```json
{
  "success": true,
  "new_path": "n0[0].n1_sections[0]",
  "current_level": 1,
  "children": [
    {
      "id": "n2_note_taking",
      "name": "Prise de notes",
      "n3_atomsets": []
    }
  ],
  "breadcrumb": ["Brainstorm", "Idéation Rapide"],
  "breadcrumb_paths": ["n0[0]", "n0[0].n1_sections[0]"],
  "has_children": true
}
```

---

### 2. POST /api/drilldown/exit — Remonter d'un niveau

**URL** :
```
POST http://localhost:8000/api/drilldown/exit
```

**Body** (JSON) :
```json
{
  "path": "n0[0].n1_sections[0]"
}
```

**Paramètres** :
- `path` : Chemin actuel (ex: `"n0[0].n1_sections[0]"`)

**Réponse** :
```json
{
  "success": true,
  "parent_path": "n0[0]",
  "current_level": 0,
  "children": [
    {
      "id": "n1_ideation",
      "name": "Idéation Rapide",
      "n2_features": [...]
    }
  ],
  "breadcrumb": ["Brainstorm"],
  "breadcrumb_paths": ["n0[0]"]
}
```

---

### 3. GET /api/breadcrumb — Fil d'Ariane

**URL** :
```
GET http://localhost:8000/api/breadcrumb?path=n0[0].n1_sections[0]
```

**Paramètres (query)** :
- `path` : Chemin actuel

**Réponse** :
```json
{
  "breadcrumb": ["Brainstorm", "Idéation Rapide"],
  "breadcrumb_paths": ["n0[0]", "n0[0].n1_sections[0]"],
  "current_level": 1,
  "current_path": "n0[0].n1_sections[0]",
  "has_children": true,
  "children_count": 1
}
```

---

## 🧪 EXEMPLES CURL (TESTÉS ✅)

### Exemple 1 : Drill-down depuis Corps Brainstorm

```bash
curl -X POST http://localhost:8000/api/drilldown/enter \
  -H "Content-Type: application/json" \
  -d '{"path": "n0[0]", "child_index": 0}'
```

**Résultat** : Descend vers Organe "Idéation Rapide" (`n0[0].n1_sections[0]`)

---

### Exemple 2 : Drill-up depuis Organe

```bash
curl -X POST http://localhost:8000/api/drilldown/exit \
  -H "Content-Type: application/json" \
  -d '{"path": "n0[0].n1_sections[0]"}'
```

**Résultat** : Remonte vers Corps "Brainstorm" (`n0[0]`)

---

### Exemple 3 : Récupérer breadcrumb

```bash
curl "http://localhost:8000/api/breadcrumb?path=n0[0].n1_sections[0]"
```

**Résultat** : Retourne `["Brainstorm", "Idéation Rapide"]`

---

## 🎯 TON TRAVAIL (ÉTAPE 4)

### Objectif

Implémenter la navigation hiérarchique dans le Canvas Fabric.js avec double-clic et breadcrumb.

### Tâches

1. **Écouter double-clic sur Canvas**
   - Événement `dblclick` sur objets Fabric.js
   - Récupérer l'ID du composant cliqué (ex: `"n0_brainstorm"`)

2. **Convertir ID → path**
   - Corps : `"n0_brainstorm"` → `"n0[0]"` (chercher l'index dans le tableau)
   - Organe : `"n1_ideation"` → `"n0[0].n1_sections[0]"`

3. **Appeler POST /api/drilldown/enter**
   ```javascript
   const response = await fetch('http://localhost:8000/api/drilldown/enter', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({path: currentPath, child_index: 0})
   });
   const data = await response.json();
   ```

4. **Afficher les enfants (children) retournés**
   - `data.children` contient les Organes (N1) ou Features (N2)
   - Rafraîchir le Canvas avec ces nouveaux composants

5. **Afficher breadcrumb en haut**
   - Utiliser `data.breadcrumb` (ex: `["Brainstorm", "Idéation Rapide"]`)
   - Afficher comme chips cliquables pour navigation rapide

6. **Bouton "Retour" (ou flèche ←)**
   - Appeler `POST /api/drilldown/exit` avec `{path: currentPath}`
   - Rafraîchir avec `data.children` du niveau parent

---

## 📦 STRUCTURE DES DONNÉES

### Hiérarchie Genome

```
N0 (Corps)
└── n0[0] "Brainstorm"
    └── N1 (Organes)
        └── n0[0].n1_sections[0] "Idéation Rapide"
            └── N2 (Features)
                └── n0[0].n1_sections[0].n2_features[0] "Prise de notes"
                    └── N3 (Atomsets)
                        └── n0[0].n1_sections[0].n2_features[0].n3_atomsets[0]
```

### Format Path

- **N0** : `"n0[index]"` (ex: `"n0[0]"`, `"n0[1]"`, `"n0[2]"`)
- **N1** : `"n0[i].n1_sections[j]"`
- **N2** : `"n0[i].n1_sections[j].n2_features[k]"`
- **N3** : `"n0[i].n1_sections[j].n2_features[k].n3_atomsets[l]"`

**Important** : Les clés réelles (`n1_sections`, `n2_features`, `n3_atomsets`) sont incluses dans le path !

---

## 🔄 WORKFLOW COMPLET

### Scénario : Double-clic sur Corps "Brainstorm"

1. **User** : Double-clic sur rectangle "Brainstorm"
2. **Frontend** : Détecte événement, récupère ID `"n0_brainstorm"`
3. **Frontend** : Convertit `"n0_brainstorm"` → path `"n0[0]"` (cherche l'index)
4. **Frontend** : POST `/api/drilldown/enter` avec `{path: "n0[0]", child_index: 0}`
5. **Backend** : Retourne Organes N1 + breadcrumb
6. **Frontend** : Rafraîchit Canvas avec Organes
7. **Frontend** : Affiche breadcrumb `["Brainstorm", "Idéation Rapide"]`

### Scénario : Clic sur Breadcrumb "Brainstorm"

1. **User** : Clic sur chip "Brainstorm" dans breadcrumb
2. **Frontend** : Utilise `breadcrumb_paths[0]` = `"n0[0]"`
3. **Frontend** : POST `/api/drilldown/exit` avec `{path: currentPath}` jusqu'à atteindre `"n0[0]"`
4. **Backend** : Retourne Corps N0
5. **Frontend** : Rafraîchit Canvas avec tous les Corps

---

## ⚠️ GESTION D'ERREURS

### Erreur 400 : Path invalide

```json
{
  "detail": "Aucun enfant au niveau n2_features"
}
```

**Cause** : Le composant n'a pas d'enfants (fin de hiérarchie).

**Solution** : Désactiver le double-clic sur les composants sans enfants (`has_children: false`).

### Erreur 400 : Index hors limites

```json
{
  "detail": "Index enfant 5 hors limites (max: 2)"
}
```

**Cause** : `child_index` trop élevé.

**Solution** : Toujours utiliser `child_index: 0` par défaut.

---

## 🔗 LIENS UTILES

- Backend Health: http://localhost:8000/health
- Endpoint Enter: http://localhost:8000/api/drilldown/enter
- Endpoint Exit: http://localhost:8000/api/drilldown/exit
- Endpoint Breadcrumb: http://localhost:8000/api/breadcrumb
- Test manuel : Voir exemples curl ci-dessus

---

## ✋ VALIDATION REQUISE

Une fois ton code Frontend terminé :

1. Ouvre http://localhost:9998/stenciler
2. Double-clic sur Corps "Brainstorm" → vérifier que les Organes s'affichent
3. Vérifier breadcrumb `["Brainstorm", "..."]` en haut
4. Clic bouton "Retour" → vérifier retour aux Corps
5. Tester navigation N0 → N1 → N2

**Si OK** → Ping François-Jean pour validation visuelle
**Si KO** → Ping-moi ici avec l'erreur + logs console

---

**Backend prêt. À toi de jouer KIMI ! 🚀**

— Claude Sonnet 4.5, Backend Lead
