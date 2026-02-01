# Guide d'intégration IntentTranslator/STAR

Ce guide explique comment utiliser et intégrer le système STAR (Situation, Transformation, Abstraction, Réalisation) avec IntentTranslator dans Sullivan Kernel.

## Table des matières

- [Qu'est-ce que STAR ?](#quest-ce-que-star)
- [Utilisation d'IntentTranslator](#utilisation-dintenttranslator)
- [Intégration dans nouveaux modules](#intégration-dans-nouveaux-modules)
- [Structure star_mappings.json](#structure-star_mappingsjson)
- [Best practices](#best-practices)
- [Exemples concrets](#exemples-concrets)

---

## Qu'est-ce que STAR ?

STAR est un framework qui permet de représenter les intentions utilisateur et leurs transformations en composants UI de manière structurée.

### Les 4 éléments STAR

1. **Situation** : Contexte dans lequel l'intention est exprimée
   - Pattern name (ex: "Toggle Visibility")
   - Variants (ex: "show/hide", "toggle", "expand/collapse")
   - Description sémantique

2. **Transformation** : Action ou changement appliqué à la situation
   - Terme utilisateur → Terme technique
   - Mapping sémantique

3. **Abstraction** : Niveau d'abstraction de l'intention
   - Nom de l'abstraction
   - Description conceptuelle

4. **Réalisation** : Implémentation concrète de l'intention
   - Template HTML
   - Code JavaScript
   - Structure CSS

### Exemple de chaîne STAR

```
Situation: "Toggle Visibility" (show/hide, toggle)
    ↓
Transformation: "toggle" → "aria-expanded", "hidden"
    ↓
Abstraction: "Interactive Disclosure Pattern"
    ↓
Réalisation: <button aria-expanded="false">...</button>
```

---

## Utilisation d'IntentTranslator

### Initialisation

```python
from Backend.Prod.sullivan.intent_translator import IntentTranslator

# Créer instance (charge star_mappings.json automatiquement)
intent_translator = IntentTranslator()
```

### Recherche de situation

```python
# Rechercher situations similaires avec embeddings
situations = intent_translator.search_situation("bouton pour afficher/masquer", limit=5)

for situation in situations:
    print(f"Pattern: {situation.pattern_name}")
    print(f"Description: {situation.description}")
    print(f"Variants: {situation.variants}")
```

**Méthode** : `search_situation(query: str, limit: int = 5) -> List[Situation]`
- Utilise embeddings (sentence-transformers) pour similarité sémantique
- Fallback sur comptage de mots si embeddings non disponibles
- Retourne les N meilleures situations triées par score

### Propagation STAR

```python
# Propager STAR depuis une situation
situation = situations[0]  # Meilleure situation trouvée
realisation = intent_translator.propagate_star(situation)

if realisation:
    print(f"Template: {realisation.template}")
    print(f"Code: {realisation.code}")
    print(f"JavaScript: {realisation.javascript}")
```

**Méthode** : `propagate_star(situation: Situation) -> Optional[Realisation]`
- Construit la chaîne STAR complète
- Retourne la réalisation avec templates et code

### Score de mapping

```python
# Évaluer la pertinence d'un mapping
score = intent_translator.score_mapping("bouton toggle", situation)
print(f"Score: {score:.2f}")
```

**Méthode** : `score_mapping(query: str, situation: Situation) -> float`
- Score entre 0.0 et 1.0
- Utilise embeddings pour similarité cosinus
- Fallback sur comptage de mots

---

## Intégration dans nouveaux modules

### Exemple 1 : ComponentGenerator

Intégrer STAR dans `_enrich_context()` :

```python
def _enrich_with_star(self, intent: str) -> Optional[str]:
    """Enrichit le contexte avec patterns STAR."""
    try:
        from ..intent_translator import IntentTranslator
        
        intent_translator = IntentTranslator()
        situations = intent_translator.search_situation(intent, limit=3)
        
        star_info = []
        for situation in situations:
            realisation = intent_translator.propagate_star(situation)
            if realisation:
                star_info.append(
                    f"STAR Pattern: {situation.pattern_name}\n"
                    f"  Situation: {situation.description}\n"
                    f"  Realisation: {realisation.description}\n"
                    f"  Template: {realisation.template or 'N/A'}"
                )
        
        if star_info:
            return f"\n=== Patterns STAR ===\n" + "\n\n".join(star_info)
            
    except Exception as e:
        logger.warning(f"Error enriching with STAR: {e}")
    
    return None
```

### Exemple 2 : PatternAnalyzer

Intégrer STAR dans `analyze_patterns()` :

```python
def analyze_patterns(self) -> Dict[str, Any]:
    """Analyse avec insights STAR."""
    insights = {
        "star_insights": {}
    }
    
    try:
        from ..intent_translator import IntentTranslator
        intent_translator = IntentTranslator()
        
        star_patterns_count = 0
        star_transformations = []
        
        for comp in components:
            intent = comp.name.replace("component_", "").replace("_", " ")
            situations = intent_translator.search_situation(intent, limit=1)
            
            if situations:
                star_patterns_count += 1
                realisation = intent_translator.propagate_star(situations[0])
                if realisation:
                    star_transformations.append(situations[0].pattern_name)
        
        insights["star_insights"] = {
            "components_with_star_patterns": star_patterns_count,
            "most_common_star_patterns": dict(Counter(star_transformations).most_common(5))
        }
    except Exception as e:
        logger.warning(f"STAR analysis failed: {e}")
    
    return insights
```

### Pattern d'intégration standard

```python
# 1. Lazy import pour éviter dépendances circulaires
try:
    from ..intent_translator import IntentTranslator
except ImportError:
    IntentTranslator = None

# 2. Créer instance si disponible
if IntentTranslator:
    intent_translator = IntentTranslator()
    
    # 3. Utiliser search_situation() et propagate_star()
    situations = intent_translator.search_situation(query, limit=3)
    for situation in situations:
        realisation = intent_translator.propagate_star(situation)
        # Utiliser realisation.template, realisation.code, etc.
    
    # 4. Gérer erreurs avec fallback
except Exception as e:
    logger.warning(f"STAR not available: {e}. Using fallback.")
    # Fallback vers comportement normal
```

---

## Structure star_mappings.json

Le fichier `Backend/Prod/sullivan/knowledge/star_mappings.json` contient les mappings STAR.

### Structure

```json
{
  "mappings": [
    {
      "pattern_name": "Toggle Visibility",
      "category": "interaction",
      "variants": ["show/hide", "toggle", "expand/collapse"],
      "transformations": {
        "user_term": "toggle",
        "tech_term": "aria-expanded"
      },
      "abstraction": {
        "name": "Interactive Disclosure",
        "description": "Pattern pour afficher/masquer du contenu"
      },
      "realisation": {
        "template": "<button aria-expanded=\"false\">...</button>",
        "code": "<button>Toggle</button>",
        "javascript": "element.addEventListener('click', () => {...})"
      }
    }
  ]
}
```

### Ajouter un nouveau pattern

1. Ouvrir `Backend/Prod/sullivan/knowledge/star_mappings.json`
2. Ajouter un nouvel objet dans le tableau `mappings` :

```json
{
  "pattern_name": "Mon Nouveau Pattern",
  "category": "navigation",
  "variants": ["variant1", "variant2"],
  "transformations": {
    "user_term": "terme utilisateur",
    "tech_term": "terme technique"
  },
  "abstraction": {
    "name": "Nom Abstraction",
    "description": "Description de l'abstraction"
  },
  "realisation": {
    "template": "<div>...</div>",
    "code": "Code HTML",
    "javascript": "Code JS"
  }
}
```

3. Redémarrer l'application pour charger le nouveau pattern

---

## Best practices

### 1. Lazy import

Toujours utiliser lazy import pour éviter dépendances circulaires :

```python
try:
    from ..intent_translator import IntentTranslator
    STAR_AVAILABLE = True
except ImportError:
    STAR_AVAILABLE = False
    IntentTranslator = None
```

### 2. Gestion d'erreurs

Toujours prévoir un fallback si STAR n'est pas disponible :

```python
try:
    intent_translator = IntentTranslator()
    situations = intent_translator.search_situation(intent)
    # Utiliser STAR
except Exception as e:
    logger.debug(f"STAR not available: {e}")
    # Fallback vers comportement normal sans STAR
```

### 3. Embeddings

IntentTranslator utilise automatiquement `EmbeddingModelSingleton` pour les embeddings :
- Modèle : `sentence-transformers/all-MiniLM-L6-v2`
- Chargé une seule fois (singleton)
- Fallback sur comptage de mots si non disponible

### 4. Performance

- `search_situation()` avec `limit` raisonnable (3-5)
- Créer instance IntentTranslator une seule fois si possible
- Utiliser STAR uniquement si nécessaire (pas pour chaque requête)

### 5. Logging

Logger les utilisations de STAR pour monitoring :

```python
logger.debug(f"Enriched context with {len(star_info)} STAR patterns")
logger.info(f"STAR pattern '{pattern_name}' matched for intent: {intent}")
```

---

## Exemples concrets

### Exemple 1 : Enrichissement contexte génération

```python
# Dans ComponentGenerator._enrich_context()
def _enrich_with_star(self, intent: str) -> Optional[str]:
    try:
        from ..intent_translator import IntentTranslator
        intent_translator = IntentTranslator()
        
        situations = intent_translator.search_situation(intent, limit=3)
        star_info = []
        
        for situation in situations:
            realisation = intent_translator.propagate_star(situation)
            if realisation:
                star_info.append(
                    f"STAR Pattern: {situation.pattern_name}\n"
                    f"  Template: {realisation.template}"
                )
        
        return "\n=== STAR Patterns ===\n" + "\n\n".join(star_info) if star_info else None
    except Exception as e:
        logger.debug(f"STAR enrichment failed: {e}")
        return None
```

### Exemple 2 : Analyse patterns Elite Library

```python
# Dans PatternAnalyzer.analyze_patterns()
star_patterns_count = 0
star_transformations = []

for comp in components:
    intent = comp.name.replace("component_", "").replace("_", " ")
    situations = intent_translator.search_situation(intent, limit=1)
    
    if situations:
        star_patterns_count += 1
        realisation = intent_translator.propagate_star(situations[0])
        if realisation:
            star_transformations.append(situations[0].pattern_name)

insights["star_insights"] = {
    "components_with_star_patterns": star_patterns_count,
    "most_common_star_patterns": dict(Counter(star_transformations).most_common(5))
}
```

### Exemple 3 : Recommandation avec STAR

```python
# Dans ContextualRecommender.recommend()
if self.intent_translator:
    situations = self.intent_translator.search_situation(intent, limit=3)
    for situation in situations:
        realisation = self.intent_translator.propagate_star(situation)
        if realisation:
            # Enrichir recommandations avec templates STAR
            recommendations.append({
                "component": comp,
                "star_template": realisation.template,
                "star_score": self.intent_translator.score_mapping(intent, situation)
            })
```

---

## Références

- Fichier source : `Backend/Prod/sullivan/intent_translator.py`
- Mappings STAR : `Backend/Prod/sullivan/knowledge/star_mappings.json`
- Embeddings : `Backend/Prod/cache/semantic_cache.py` (EmbeddingModelSingleton)
- Exemples d'intégration :
  - `Backend/Prod/sullivan/generator/component_generator.py` (méthode `_enrich_with_star`)
  - `Backend/Prod/sullivan/analyzer/pattern_analyzer.py` (méthode `analyze_patterns`)
  - `Backend/Prod/sullivan/recommender/contextual_recommender.py` (méthode `recommend`)
