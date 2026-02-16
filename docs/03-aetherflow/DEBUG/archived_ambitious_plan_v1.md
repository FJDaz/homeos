## 1. Analyse Approfondie des Composants

### A. Le Résumé AST : Quel rôle ?
Le résumé ([Ligne 162](file:///Users/francois-jeandazin/AETHERFLOW/Backend/Prod/core/surgical_editor.py#L162)) sert de **"Table des Matières"** pour le LLM.
- **Utilité** : Il évite au LLM de devoir compter les lignes lui-même (tâche où ils sont notoirement mauvais).
- **Portée** : Il liste les signatures des fonctions/classes et leurs plages `[start_line, end_line]`.
- **Risque** : Si le résumé est injecté *en plus* du code complet (comme c'est le cas actuellement à la [Ligne 755 de l'orchestrateur](file:///Users/francois-jeandazin/AETHERFLOW/Backend/Prod/orchestrator.py#L755)), cela double le volume de tokens. L'idéal serait de ne fournir que le résumé AST pour les gros fichiers pour économiser du contexte.

### B. Standardisation RegEx vs Ambiguïté Textuelle
La RegEx ([Ligne 248](file:///Users/francois-jeandazin/AETHERFLOW/Backend/Prod/core/surgical_editor.py#L248)) cherche un bloc JSON strict.
- **Le Standard** : Il n'y a pas de standard universel, mais le motif ```json ... ``` est le plus robuste.
- **La Portée** : Elle isole la "décision" (JSON) de la "réflexion" (texte). 
- **L'Utilité du texte** : Malheureusement, le texte est souvent la source du "hacode" car le LLM y glisse parfois des bribes de code qu'il oublie de mettre dans le JSON.
- **Solution** : Il faut vider le reste du message et ne garder **que** le JSON validé. Toute explication textuelle doit être ignorée par le processeur pour éviter les pollutions.

### C. Le Besoin d'un "Inspecteur de Conformité"
Vous avez raison, l'actuelle `apply_operations` (Ligne 446) est juge et partie.
- **Concept** : Introduire une classe `SurgicalGuard` qui vérifierait l'ambiguïté **AVANT** toute modification. 
- **Exemple** : Si l'opération cible `update` mais que le `ASTParser` voit deux fonctions `update`, l'inspecteur doit stopper l'opération et demander une précision (`target: "ClasseA.update"`).

---

## 2. Architecture du "SurgicalGuard" (L'Inspecteur)

Pour briser l'opacité des LLM, nous introduisons une couche de **validation déterministe** qui ne repose pas sur une IA, mais sur l'analyse statique.

### Composant : `SurgicalGuard` (Middleware de Conformité)
Situé entre la réception du JSON et l'application AST, il remplit trois fonctions :

1.  **Détecteur d'Ambiguïté (AST-based)** :
    - Avant chaque `modify_method`, il interroge l'index AST.
    - S'il trouve plus d'une correspondance pour une `target`, il lève une `AmbiguityError`.
    - **Action** : Le système renvoie l'erreur au LLM en lui demandant de qualifier sa cible (`Classe.methode`).

2.  **Filtre Lexical de Pureté** :
    - Inspecte le champ `code` du JSON.
    - S'il détecte des patterns de langage naturel (prose, excuses, explications) à l'intérieur du bloc de code, il rejette l'opération.
    - **Action** : Empêche l'injection de "hacode" textuel.

3.  **Simulateur Dry-Run** :
    - Applique la modification dans une copie temporaire en mémoire.
    - Exécute `ast.parse()` sur le résultat. 
    - **Action** : Garantit que le fichier restera syntaxiquement valide après l'opération.

---

## 3. Remplacement par Plage (Range-Based Replacement)

C'est la solution pour une "chirurgie sans cicatrice". 

### Le concept
Au lieu d'appeler `astunparse.unparse(self.tree)` qui réécrit tout le fichier (et perd les commentaires) :
1.  **Localisation** : `ASTParser` fournit les numéros de ligne et de colonne (`lineno`, `col_offset`, `end_lineno`, `end_col_offset`).
2.  **Extraction** : On récupère les index de caractères correspondants dans le fichier original.
3.  **Greffe** : On remplace la sous-chaîne `[index_debut:index_fin]` par le nouveau code.
4.  **Résultat** : Tout ce qui entoure la zone modifiée (imports, commentaires, variables globales) est préservé à l'octet près.

---

## 4. Standardisation du "Master Protocol" (Prompt Système)

Pour répondre à votre question sur l'uniformisation des 4 modèles : **Oui, il est impératif et possible d'imposer un standard unique via les API.**

### Centralisation dans `BaseLLMClient`
Actuellement, chaque client gère son prompt de manière isolée. Nous allons modifier l'interface de base pour supporter l'injection d'un prompt système global :

1.  **Refactor de `BaseLLMClient`** : Ajout d'un paramètre `system_prompt` à la méthode `generate()`.
2.  **Traduction par Client** : 
    - **DeepSeek/Groq** : Injection dans le message avec `role: "system"`.
    - **Gemini** : Injection dans le champ `system_instruction` (natif dans l'API Google).
    - **Claude** : Injection dans le paramètre top-level `system`.

### Le Master Protocol Chirurgical
Ce prompt unique contiendra la "Grammaire de HomeOS" :
- **Règle de Silence** : "You are a surgical instrument. Output ONLY JSON. Prose is a syntax error."
- **Typologie Lexicale** : Définition stricte des types (`add_method`, `modify_method`, etc.) pour éviter que DeepSeek n'utilise un terme et Claude un autre.
- **Auto-Contrôle** : "Before outputting, verify that the 'target' exists in the provided AST summary."

---

## 5. Réponses aux Enjeux de l'API

**Est-ce possible via API ?**
- **OUI** : Toutes les API modernes (OpenAI-like, Anthropic, Google) séparent désormais le "System" (les règles immuables) du "User" (la tâche spécifique).
- **Avantage** : En isolant le Master Protocol dans la couche "System", on s'assure qu'il est traité avec la priorité maximale par le modèle (souhaité pour écraser l'entraînement initial de bavardage).
- **Précision** : Cela réduit l'entropie car le modèle n'a plus à "deviner" le format à chaque tour, il est verrouillé par sa directive système.
