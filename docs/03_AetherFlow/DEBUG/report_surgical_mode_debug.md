# Rapport Technique Avancé : Diagnostic & Architecture du Mode Chirurgical

Ce rapport approfondit l'analyse du `SurgicalEditor` en répondant aux enjeux d'ambiguïté et de propreté du code ("hacode").

## 1. Analyse des Mécanismes de Précision

### A. Le Résumé AST : La Vue en Coupe du Fichier
Le résumé généré à la **Ligne 162** est l'unique moyen pour le LLM de "voir" la structure sans se perdre dans les 2000 lignes de code.
- **Portée** : Il cartographie les signatures des fonctions et les plages de lignes `[début, fin]`.
- **Utilité** : Il sert de référentiel pour les cibles de modification. Sans lui, le LLM ferait des suppositions erronées sur l'emplacement des méthodes.

### B. Standardisation et Ambiguïté Textuelle
La RegEx de la **Ligne 248** est le filtre qui sépare le "bruit" (les explications textuelles) du "signal" (le JSON d'opérations).
- **Le Risque** : Les explications textuelles sont la première source d'ambiguïté. Le LLM peut y glisser des intentions de code mal formulées qui ne se retrouvent pas dans le JSON.
- **Solution Technique** : Il est impératif d'isoler strictement le bloc JSON et d'ignorer tout ce qui se trouve à l'extérieur. Le texte ne doit servir qu'au débuggage humain, jamais à l'application du code.

### C. L'Inspecteur de Conformité (SurgicalGuard)
Actuellement, la validation à la **Ligne 446** est limitée. Pour éviter les erreurs de placement :
- **Concept** : Un agent ou un module externe doit vérifier la **non-ambiguïté** des cibles. 
- **Règle** : Si une opération cible "update" mais que le fichier contient plusieurs méthodes du même nom, l'inspecteur doit bloquer l'opération avant toute tentative d'écriture.

---

## 2. Vers une "Chirurgie sans Cicatrice" (Rplacement par Plage)

Le point critique identifié à la **Ligne 484** (`astunparse.unparse`) est la cause racine du code "hacké" (perte de commentaires, reformatage sauvage).

### La Nouvelle Approche
Au lieu de régénérer tout le fichier, nous proposons de passer à un **système de remplacement par plage (Range-based replacement)** :

1. **Calcul des Coordonnées** : Utiliser l'AST uniquement pour trouver les index exacts des caractères (début/fin) de la fonction cible.
2. **Greffe Textuelle** : Effectuer un remplacement de sous-chaîne dans le texte original.
   - **Avantage** : 100% du code hors de la zone chirurgicale (commentaires, espaces, imports) reste strictement inchangé.
3. **Validation Lexicale** : Soumettre le fragment à insérer à un moteur de conformité pour s'assurer qu'il ne contient pas de "hacode" ou de résidus textuels du LLM.

---

## 3. Synthèse des Dysfonctionnements

| Symptôme | Cause Probable | Localisation Code |
| :--- | :--- | :--- |
| **Code en fin de fichier** | Échec de la chirurgie entraînant un "Fallback Append". | `orchestrator.py:889` |
| **Commentaires disparus** | Régénération totale par `astunparse`. | `surgical_editor.py:484` |
| **Modification mauvaise classe** | Ambiguïté de `ast.walk` non détectée. | `surgical_editor.py:694` |

---

## 4. Plan de Remédiation
- **Court terme** : Logger explicitement chaque "Fallback Append" pour alerter l'utilisateur.
- **Moyen terme** : Forcer le typage des cibles (`Classe.Methode`).
- **Long terme** : Implémenter le remplacement par plage textuelle indexée par AST pour préserver l'intégrité du fichier original.
