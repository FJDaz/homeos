---
name: test-mandatory
description: Impose de tester systématiquement tout code produit avant livraison. S'applique à chaque modification de fichier, création de fonction, ou livraison de feature. Doit être utilisé systématiquement avant de dire "c'est fait" ou de considérer une tâche terminée.
---

# Test Mandatory - Livraison Sans Bug

## RÈGLE D'OR

**INTERDICTION ABSOLUE** : Ne jamais livrer de code non testé.

Avant chaque "✅ C'est fait", "Terminé", "Fonctionne", vérifier impérativement.

---

## CHECKLIST OBLIGATOIRE

### Pour chaque fichier modifié/créé :

- [ ] **Syntaxe valide** - Pas d'erreur de parsing
- [ ] **Imports résolus** - Pas de `ModuleNotFoundError`
- [ ] **Exécution** - Le code tourne sans crash immédiat
- [ ] **Logique cohérente** - Le résultat correspond à l'intention

### Pour les fonctions/classes :

- [ ] **Appel testé** - La fonction peut être appelée avec des arguments valides
- [ ] **Retour vérifié** - Le retour est du type attendu
- [ ] **Edge cases** - Pas de crash avec entrées vides/bizarres

### Pour les intégrations (CLI, API, etc.) :

- [ ] **Commande testée** - La commande CLI s'exécute
- [ ] **Arguments** - Les flags/paramètres fonctionnent
- [ ] **Output** - L'affichage est correct

---

## PROCESS DE TEST RAPIDE

### 1. Python - Test de base
```python
# Vérifier syntaxe
python -m py_compile fichier.py

# Tester import
python -c "import module"

# Tester fonction
python -c "from module import func; print(func())"
```

### 2. Bash - Test de base
```bash
# Vérifier syntaxe
bash -n script.sh

# Test dry-run si possible
./script.sh --help
```

### 3. JSON/YAML - Test de base
```bash
# JSON valide ?
python -m json.tool < fichier.json

# YAML valide ?
python -c "import yaml; yaml.safe_load(open('fichier.yml'))"
```

---

## NIVEAUX DE TEST

| Priorité | Type de code | Test requis |
|----------|--------------|-------------|
| 🔴 **CRITIQUE** | CLI, core, API | Test exécution réelle + vérification output |
| 🟡 **IMPORTANT** | Fonctions utilitaires | Test import + appel basique |
| 🟢 **STANDARD** | Docs, config | Vérification syntaxe + structure |

---

## PHRASES INTERDITES (sans test préalable)

❌ "C'est fait"  
❌ "Ça fonctionne"  
❌ "Terminé"  
❌ "Prêt"  
❌ "Voilà"  

**Remplacer par :**

✅ "Code créé, je teste..."  
✅ "Modification faite, vérification en cours..."  
✅ "Implémentation terminée, test d'exécution..."  

---

## TEMPLATE DE LIVRAISON

Après test réussi, utiliser ce format :

```
✅ [TESTÉ] Description de la livraison

- Fichiers modifiés : 
  - `chemin/fichier.py` (testé : ✅)
  - `chemin/autre.py` (testé : ✅)

- Tests effectués :
  - Syntaxe : OK
  - Import : OK  
  - Exécution : OK
  - Output : conforme

- Commande de test utilisée : `...`
```

---

## PROCÉDURE EN CAS D'ÉCHEC

Si un test échoue :

1. **Ne pas livrer** le code
2. **Corriger** immédiatement
3. **Retester** jusqu'à succès
4. **Documenter** la correction si non-triviale

---

## EXCEPTIONS (Rares)

Autorisé à ne pas tester si :
- Modification de commentaire/docstring uniquement
- Renommage de variable locale sans changement logique
- Formatage (black, prettier) automatique

**TOUJOURS tester si :**
- Une ligne de code exécutable est modifiée
- Un import est ajouté/supprimé
- Une structure de contrôle est changée

---

## EXEMPLES DE TEST RAPIDES

### Exemple 1 : Nouvelle fonction Python
```python
# Fichier : Backend/Prod/utils.py
def nouvelle_fonction(x):
    return x * 2

# TEST IMMÉDIAT :
# python -c "from Backend.Prod.utils import nouvelle_fonction; print(nouvelle_fonction(5))"
# Attendu : 10
```

### Exemple 2 : Modification CLI
```python
# Fichier : Backend/Prod/cli.py
# Ajout d'une commande

# TEST IMMÉDIAT :
# ./aetherflow-chat --help
# Vérifier que la nouvelle commande apparaît
```

### Exemple 3 : Nouveau module
```python
# Fichier : Backend/Prod/nouveau_module.py

# TEST IMMÉDIAT :
# python -c "import Backend.Prod.nouveau_module"
# Pas d'erreur = OK
```

---

## RAPPEL FINAL

**L'utilisateur préfère attendre 5 minutes de plus pour du code qui fonctionne, que d'avoir immédiatement du code cassé.**

Teste. Vérifie. Puis livre.

🎯 **Zéro régression, zéro livraison non testée.**
