# ÉTAPE 7 : Undo/Redo Backend

**Statut** : 🟡 SI TEMPS (après ÉTAPE 6)
**Qui** : Claude uniquement
**Durée estimée** : 1h
**Bloque** : KIMI attend la fin (ÉTAPE 8 dépend de celle-ci)

---

## 🎯 Objectif

Implémenter la fonctionnalité Undo/Redo côté Backend pour permettre d'annuler et refaire des modifications du Genome.

---

## 📋 Tâches

### 1. Créer `POST /api/modifications/undo`

**Endpoint** : `POST http://localhost:8000/api/modifications/undo`

**Body** : Aucun (ou optionnel `{"steps": 1}` pour undo multiple)

**Réponse** :
```json
{
  "success": true,
  "genome": { ... },  // Nouvel état du Genome
  "undone_modification": {
    "id": "mod_20260212_143000_123456",
    "path": "n0[0]",
    "property": "accent_color",
    "old_value": "#FF5722",
    "new_value": "#ORIGINAL"
  },
  "undo_available": true,   // Encore des actions à undo ?
  "redo_available": true    // Actions disponibles pour redo ?
}
```

---

### 2. Créer `POST /api/modifications/redo`

**Endpoint** : `POST http://localhost:8000/api/modifications/redo`

**Body** : Aucun (ou optionnel `{"steps": 1}` pour redo multiple)

**Réponse** :
```json
{
  "success": true,
  "genome": { ... },  // Nouvel état du Genome
  "redone_modification": {
    "id": "mod_20260212_143000_123456",
    "path": "n0[0]",
    "property": "accent_color",
    "old_value": "#ORIGINAL",
    "new_value": "#FF5722"
  },
  "undo_available": true,
  "redo_available": false
}
```

---

### 3. Ajouter `undo_stack` et `redo_stack` dans `ModificationLog`

**Fichier à créer** : `Backend/Prod/sullivan/stenciler/modification_log.py`

**Classe** : `ModificationLog`

```python
class ModificationLog:
    """
    Gestion des modifications avec Undo/Redo

    Architecture :
    - history : Liste immutable de toutes les modifications
    - undo_stack : Stack des modifications à annuler
    - redo_stack : Stack des modifications à refaire
    """

    def __init__(self):
        self.history: List[Modification] = []
        self.undo_stack: List[Modification] = []
        self.redo_stack: List[Modification] = []

    def append(self, modification: Modification):
        """Ajoute une modification et vide redo_stack"""
        self.history.append(modification)
        self.undo_stack.append(modification)
        self.redo_stack.clear()  # Effacer redo après nouvelle modification

    def undo(self) -> Optional[Modification]:
        """Annule la dernière modification"""
        if not self.undo_stack:
            return None

        modification = self.undo_stack.pop()
        self.redo_stack.append(modification)
        return modification

    def redo(self) -> Optional[Modification]:
        """Refait la dernière modification annulée"""
        if not self.redo_stack:
            return None

        modification = self.redo_stack.pop()
        self.undo_stack.append(modification)
        return modification

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0
```

---

### 4. Intégrer avec `GenomeStateManager`

**Fichier** : `Backend/Prod/sullivan/stenciler/genome_state_manager.py`

**Modifications** :

```python
class GenomeStateManager:
    def __init__(self, genome_path: str, modified_genome_path: Optional[str] = None):
        # ... (existant)

        # Ajouter ModificationLog
        self.modification_log = ModificationLog()

    def apply_modification(self, path: str, property: str, value: Any, ...) -> ModificationResult:
        # ... (existant)

        # 6. Log modification
        mod_id = modification_id or f"mod_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        modification = Modification(
            id=mod_id,
            timestamp=datetime.now(),
            path=path,
            property=property,
            old_value=old_value,
            new_value=value,
            semantic_attributes={}
        )
        self.modification_log.append(modification)

        # 7. Sauvegarde automatique sur disque
        self.save_to_file()

        return ModificationResult(...)

    def undo(self) -> Tuple[Optional[Dict], Optional[str]]:
        """Annule la dernière modification"""
        modification = self.modification_log.undo()

        if not modification:
            return None, "Aucune modification à annuler"

        # Appliquer l'ancienne valeur
        node, error = self._navigate_to_node(modification.path)
        if error:
            return None, error

        # Restaurer l'ancienne valeur
        node[modification.property] = modification.old_value

        # Sauvegarder
        self.save_to_file()

        return self.genome_current, None

    def redo(self) -> Tuple[Optional[Dict], Optional[str]]:
        """Refait la dernière modification annulée"""
        modification = self.modification_log.redo()

        if not modification:
            return None, "Aucune modification à refaire"

        # Appliquer la nouvelle valeur
        node, error = self._navigate_to_node(modification.path)
        if error:
            return None, error

        # Appliquer la nouvelle valeur
        node[modification.property] = modification.new_value

        # Sauvegarder
        self.save_to_file()

        return self.genome_current, None
```

---

### 5. Créer endpoints API

**Fichier** : `Backend/Prod/sullivan/stenciler/api.py`

```python
@router.post("/modifications/undo")
async def undo_modification():
    """Annule la dernière modification"""
    try:
        genome, error = genome_state_manager.undo()

        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

        return {
            "success": True,
            "genome": genome,
            "undo_available": genome_state_manager.modification_log.can_undo(),
            "redo_available": genome_state_manager.modification_log.can_redo()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur undo: {str(e)}"
        )


@router.post("/modifications/redo")
async def redo_modification():
    """Refait la dernière modification annulée"""
    try:
        genome, error = genome_state_manager.redo()

        if error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )

        return {
            "success": True,
            "genome": genome,
            "undo_available": genome_state_manager.modification_log.can_undo(),
            "redo_available": genome_state_manager.modification_log.can_redo()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur redo: {str(e)}"
        )
```

---

### 6. Documenter avec exemples

**Fichier à créer** : `docs/02-sullivan/mailbox/kimi/UNDO_REDO_BACKEND_READY.md`

**Contenu** :
- Description des endpoints
- Exemples curl
- Format requête/réponse
- Gestion d'erreurs
- Instructions pour KIMI (ÉTAPE 8)

---

## 🧪 Tests à Réaliser

### Test 1 : Undo simple

```bash
# 1. Faire modification
curl -X POST http://localhost:8000/api/modifications \
  -H "Content-Type: application/json" \
  -d '{"path": "n0[0]", "property": "accent_color", "value": "#NEW_COLOR"}'

# 2. Vérifier changement
curl http://localhost:8000/api/genome | jq -r '.genome.n0[0].accent_color'
# Résultat attendu : #NEW_COLOR

# 3. Undo
curl -X POST http://localhost:8000/api/modifications/undo

# 4. Vérifier retour
curl http://localhost:8000/api/genome | jq -r '.genome.n0[0].accent_color'
# Résultat attendu : <ancienne valeur>
```

---

### Test 2 : Redo simple

```bash
# Après undo ci-dessus

# 1. Redo
curl -X POST http://localhost:8000/api/modifications/redo

# 2. Vérifier réapplication
curl http://localhost:8000/api/genome | jq -r '.genome.n0[0].accent_color'
# Résultat attendu : #NEW_COLOR
```

---

### Test 3 : Undo multiple

```bash
# 1. Faire 3 modifications
curl -X POST http://localhost:8000/api/modifications \
  -d '{"path": "n0[0]", "property": "accent_color", "value": "#COLOR1"}'

curl -X POST http://localhost:8000/api/modifications \
  -d '{"path": "n0[0]", "property": "accent_color", "value": "#COLOR2"}'

curl -X POST http://localhost:8000/api/modifications \
  -d '{"path": "n0[0]", "property": "accent_color", "value": "#COLOR3"}'

# 2. Undo 3 fois
curl -X POST http://localhost:8000/api/modifications/undo
curl -X POST http://localhost:8000/api/modifications/undo
curl -X POST http://localhost:8000/api/modifications/undo

# 3. Vérifier état initial
curl http://localhost:8000/api/genome | jq -r '.genome.n0[0].accent_color'
```

---

### Test 4 : Nouvelle modification efface redo_stack

```bash
# 1. Faire modification
curl -X POST http://localhost:8000/api/modifications \
  -d '{"path": "n0[0]", "property": "accent_color", "value": "#NEW"}'

# 2. Undo
curl -X POST http://localhost:8000/api/modifications/undo

# 3. Faire nouvelle modification (efface redo)
curl -X POST http://localhost:8000/api/modifications \
  -d '{"path": "n0[0]", "property": "accent_color", "value": "#AUTRE"}'

# 4. Tenter redo (doit échouer)
curl -X POST http://localhost:8000/api/modifications/redo
# Résultat attendu : "Aucune modification à refaire"
```

---

## ⚠️ Points d'Attention

### 1. Immutabilité

Chaque undo/redo doit créer une **nouvelle copie** du Genome (via `copy.deepcopy()`), pas modifier l'existant.

### 2. Persistance

Les undo/redo doivent appeler `save_to_file()` pour persister l'état.

### 3. Limites

Définir une limite max pour `undo_stack` (ex: 50 modifications) pour éviter consommation mémoire excessive.

```python
class ModificationLog:
    MAX_UNDO_STACK = 50

    def append(self, modification: Modification):
        self.history.append(modification)
        self.undo_stack.append(modification)

        # Limiter taille stack
        if len(self.undo_stack) > self.MAX_UNDO_STACK:
            self.undo_stack.pop(0)  # Retirer plus ancienne

        self.redo_stack.clear()
```

---

## 📦 Livrables

### Code

- [ ] `Backend/Prod/sullivan/stenciler/modification_log.py` (nouveau)
- [ ] `Backend/Prod/sullivan/stenciler/genome_state_manager.py` (modifié)
- [ ] `Backend/Prod/sullivan/stenciler/api.py` (modifié)

### Documentation

- [ ] `docs/02-sullivan/mailbox/kimi/UNDO_REDO_BACKEND_READY.md` (nouveau)

### Tests

- [ ] Tests curl réussis (4 scénarios ci-dessus)
- [ ] Backend redémarré

---

## 🔄 Après ÉTAPE 7

**✋ KIMI PEUT DÉMARRER ÉTAPE 8**

KIMI implémentera :
- Boutons "↩️ Undo" et "↪️ Redo" dans header
- Raccourcis clavier `Ctrl+Z` et `Ctrl+Shift+Z`
- Appels API vers endpoints créés
- Rafraîchissement Canvas avec nouvel état

---

## ⏱️ Estimation

**Durée** : 1h
- 20min : Créer `ModificationLog`
- 20min : Intégrer avec `GenomeStateManager`
- 10min : Créer endpoints API
- 10min : Tests curl

**Complexité** : 🟡 Moyenne

---

## 📋 Checklist Validation

- [ ] `POST /api/modifications/undo` fonctionne
- [ ] `POST /api/modifications/redo` fonctionne
- [ ] Tests curl réussis (4 scénarios)
- [ ] Backend redémarré sans erreur
- [ ] Documentation KIMI créée
- [ ] ✋ Validation François-Jean

**Si OK** → KIMI démarre ÉTAPE 8

---

**Note** : Cette étape est marquée "SI TEMPS" car le minimum viable (ÉTAPES 1-6) doit être terminé en priorité.

---

**Créé le** : 12 février 2026, 16:00
**Par** : Claude Sonnet 4.5 (Backend Lead)
