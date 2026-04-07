# Rapport Stratégique : Recherche d'URL BYOK via Gemini + Google Search (Gratuit)

**Emplacement** : /docs/02_Sullivan/Analyses  
**Date** : 3 avril 2026  
**Auteur** : Gemini CLI (AetherFlow Orchestrator)  
**Objet** : Solution 100% gratuite pour guider les élèves vers les dashboards de clés API via l'outil de recherche natif.

---

## 1. Problématique : L'Onboarding BYOK sans frais
Pour que le mode **BYOK (Bring Your Own Key)** soit efficace en classe, les élèves doivent accéder instantanément aux pages de création de clés sans perdre de temps en recherche manuelle. L'utilisation d'API payantes (comme Perplexity) est exclue pour maintenir la gratuité totale de l'outil pédagogique.

---

## 2. Solution : Gemini 1.5 Flash + Google Search Tool
Puisque AetherFlow utilise déjà l'API Gemini via Google AI Studio, nous pouvons activer l'outil natif **"Google Search"** qui est inclus gratuitement dans le "Free Tier".

### Avantages de cette approche :
- **Coût : 0,00€** (Inclus dans le quota gratuit de Gemini 1.5 Flash).
- **Précision Native** : Utilise l'index de recherche Google en temps réel pour trouver les liens profonds (deep links).
- **Zéro dépendance externe** : Pas besoin de créer de nouveaux comptes ou de gérer des crédits tiers.

---

## 3. Workflow "Zero-Friction" pour l'Élève

Sullivan agit comme un navigateur automatisé pour l'étudiant :

1.  **Demande Élève** : "Je n'arrive pas à trouver où créer ma clé DeepSeek."
2.  **Action Sullivan** : Sullivan utilise son outil `google_search` avec la requête : *"official direct URL for DeepSeek API key creation dashboard"*.
3.  **Réponse Directe** : Sullivan affiche l'URL vérifiée et guide l'élève étape par étape.

---

## 4. Implémentation Technique (AetherFlow Bridge)

Il suffit d'ajouter l'outil `google_search` dans la configuration du client LLM dans `Backend/Prod/models/gemini_client.py` :

```python
# Exemple de structure de requête envoyée à Google AI Studio
request_payload = {
    "contents": [...],
    "tools": [
        { "google_search": {} } # Active la recherche web gratuite
    ]
}
```

Sullivan pourra alors extraire les informations de la "Grounding Metadata" renvoyée par Google pour afficher des liens sourcés et toujours à jour.

---

## 5. Alternatives de Secours (Fallback)

Si le quota gratuit de Google Search est atteint, nous préconisons :
- **Tavily (Free Tier)** : 1000 recherches/mois gratuites (API dédiée à l'IA).
- **DuckDuckGo Search (Python)** : Utilisation de la librairie `duckduckgo-search` pour un scraping léger et anonyme des résultats de recherche.

---

## 6. Conclusion
La combinaison **Gemini + Google Search Tool** est la stratégie la plus rationnelle pour AetherFlow. Elle permet d'offrir une expérience de type "Perplexity" (recherche web + réponse structurée) sans aucun coût opérationnel, garantissant que l'onboarding BYOK reste fluide pour chaque nouvel étudiant.

---
*Document mis à jour pour privilégier les solutions Open-Access et Gratuites.*
