# MISSION : INFÉRENCE DU GÉNOME HOMEOS

## CONTEXTE
Tu es un architecte logiciel qui découvre le projet AETHERFLOW/Homeos pour la première fois.
Tu dois comprendre le projet UNIQUEMENT à partir de sa documentation et en extraire la structure du Genome qui permettrait de générer un frontend cohérent.

Ce test vise à valider si la documentation contient suffisamment d'informations structurelles pour générer un Genome pertinent sans connaissance préalable du code.

---

## MÉTHODOLOGIE (SUIVRE STRICTEMENT)

### PHASE 1 : Lecture Séquentielle (20 min)
Lire les documents DANS CET ORDRE :

1. **VISION** : `docs/04-homeos/PRD/PRD_HOMEOS_ETAT_ACTUEL.md`
   - Extraire : Qu'est-ce que Homeos ? Pour qui ? Quel problème résout-il ?

2. **PARCOURS** : `docs/02-sullivan/UX/Parcours UX Sullivan.md`
   - Extraire : Quelles sont les étapes du parcours utilisateur ?
   - Identifier : Les 9 phases (IR → Arbiter → Genome → ...)

3. **ARCHITECTURE** : `docs/02-sullivan/Architecture/MAnifest >. vers génome.md`
   - Extraire : Comment le système s'organise-t-il conceptuellement ?

4. **ENDPOINTS** : `Backend/Prod/sullivan/studio_routes.py` (lignes 1-500)
   - Extraire : Quelles sont les routes API réelles ?
   - Note : Ce fichier est technique, cherche les `@router.get/post`

### PHASE 2 : Analyse Structurale (20 min)
Pour chaque document lu, remplir cette grille :

```
INTENTIONS MÉTIER (Pourquoi ?)
- Objectif 1 : ...
- Objectif 2 : ...

FONCTIONNALITÉS (Quoi ?)
- Capacité 1 : ... (endpoints associés)
- Capacité 2 : ... (endpoints associés)

STRUCTURE UI (Comment ?)
- Espace 1 : ... (layout, composants)
- Espace 2 : ... (layout, composants)
```

### PHASE 3 : Synthèse Genome (20 min)
Construire le Genome avec cette hiérarchie OBLIGATOIRE :

```json
{
  "genome": {
    "metadata": {
      "project_name": "Homeos",
      "inference_source": "documentation_analysis",
      "inference_date": "2026-02-06",
      "confidence_score": "0.0-1.0 (auto-évalue)"
    },
    "n0_worlds": [
      {
        "id": "n0_xxx",
        "name": "Nom lisible",
        "description": "Ce que l'utilisateur fait ici",
        "intent": "L'intention métier principale",
        "n1_corps": [
          {
            "id": "n1_xxx",
            "name": "Section principale",
            "description": "Rôle de cette section",
            "n2_organes": [
              {
                "id": "n2_xxx",
                "name": "Bloc fonctionnel",
                "description": "Ce que fait ce bloc",
                "n3_atomies": [
                  {
                    "id": "n3_xxx",
                    "name": "Composant UI",
                    "endpoint": "/xxx/yyy",
                    "method": "GET/POST",
                    "visual_hint": "list/card/form/chat/status/upload",
                    "description": "Ce que voit l'utilisateur"
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## RÈGLES CRITIQUES

### RÈGLE 1 : Pas de "generic"
Chaque `visual_hint` doit être spécifique :
- ❌ "generic" 
- ✅ "list", "card", "form", "chat", "status", "upload", "table", "dashboard"

### RÈGLE 2 : Logique Métier avant Technique
Ne pas organiser par endpoints techniques mais par **intention utilisateur**.

Exemple :
- ❌ Mauvais : {"name": "GET /health"}
- ✅ Bon : {"name": "Indicateur de Santé", "intent": "Rassurer sur l'état du système"}

### RÈGLE 3 : Hiérarchie Sémantique
- N0 = Grandes phases (ex: "Construction", "Analyse", "Déploiement")
- N1 = Sections par phase (ex: "Studio", "Dashboard", "Paramètres")
- N2 = Fonctionnalités (ex: "Upload de Design", "Visualisation Genome")
- N3 = Actions concrètes (ex: "Bouton Upload", "Tableau des endpoints")

---

## CRITÈRES DE SUCCÈS (Auto-évaluation)

À la fin, évalue ton Genome sur ces critères (1-5) :

| Critère | Score | Justification |
|---------|-------|---------------|
| Cohérence métier | ?/5 | Les N0 reflètent-ils les vraies phases utilisateur ? |
| Exhaustivité | ?/5 | Avez-vous capturé les fonctionnalités majeures ? |
| Précision visuelle | ?/5 | Les visual_hints sont-ils spécifiques et pertinents ? |
| Traçabilité | ?/5 | Chaque N3 est-il lié à un endpoint réel ? |
| Utilisabilité | ?/5 | Un dev pourrait-il générer un frontend avec ça ? |

**Score global : ?/25**

---

## SORTIE ATTENDUE

1. **Fichier JSON** : `genome_inferred_by_kimi.json`
2. **Rapport d'analyse** : Réponses aux 3 questions :
   - Qu'avez-vous compris comme étant la "promesse" de Homeos ?
   - Quelle a été la plus grande difficulté d'inférence ?
   - Qu'est-ce qui manquait dans la doc pour être plus précis ?

---

## CONSEILS

1. **Ne cherchez pas le code** : Vous n'avez PAS accès au code source (sauf studio_routes.py)
2. **Inférez** : Si la doc mentionne "upload de design", imaginez l'interface (bouton, drag-drop, etc.)
3. **Soyez cohérent** : Si N0 = "Studio", les N1 dedans doivent être des espaces du studio
4. **Visualisez** : Pour chaque N3, demandez-vous "À quoi ça ressemble à l'écran ?"

---

BONNE CHANCE.
