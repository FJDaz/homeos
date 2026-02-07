# MISSION KIMI V3 : INFÉRENCE GENOME FRONTEND - RUN COMPLET

## 🎯 OBJECTIF FINAL
Produire un **Genome Spatialisé N0-N3** qui permette à un développeur frontend de générer l'interface utilisateur de Homeos **sans connaissance préalable du projet**.

Ce n'est pas une description technique. C'est un **cahier des charges UI exécutable**.

---

## 📦 INPUTS FOURNIS (4 sources)

Tu as accès à ces 4 bundles (dans l'ordre de priorité) :

### 1️⃣ BUNDLE A : Documentation (Intention/Vision)
**Fichier**: `bundle_A_documentation.md` (1700+ lignes)
**Contient**:
- PRD_HOMEOS_ETAT_ACTUEL.md → Vision produit, users, scope
- Parcours UX Sullivan.md → Les 9 étapes du workflow
- STATUS_REPORT_HOMEOS.md → État actuel opérationnel

**⚠️ RÈGLE D'OR - "Dernier Qui Parle A Raison"**:
Ce projet a évolué. En cas de contradiction entre documents :
- **STATUS_REPORT_HOMEOS.md** (31 jan 2026) > PRD (plus ancien)
- Mentionne "SvelteKit" mais LE FRONTEND RÉEL utilise HTMX (HTML+JS vanilla)
- Privilégie toujours l'état "opérationnel" vs "planifié"

### 2️⃣ BUNDLE B : Code Backend (Implémentation)
**Fichier**: `bundle_B_endpoints.txt` (22 endpoints)
**Contient**: Les routes API réellement définies (`@router.get/post`)

**⚠️ ATTENTION**:
- Un endpoint défini dans le code ≠ forcément implémenté/testé
- Un endpoint dans la doc ≠ forcément codé
- C'est ta référence technique brute

### 3️⃣ BUNDLE C : Logs (Réalité d'exécution)
**Fichier**: À extraire si disponible
**Contient**: Les appels HTTP réels (200 = fonctionne, 404 = inexistant)

**⚠️ RÈGLE**:
- Logs > Code > Doc
- Si logs disent 404 sur une route définie → route non active

### 4️⃣ BUNDLE D : Toi-même (Inférence)
Tu dois **inférer** ce qui manque :
- Les composants UI entre les endpoints
- Les états de l'interface (loading, error, empty)
- Les transitions entre écrans

---

## 🔬 MÉTHODOLOGIE (5 PHASES)

### PHASE 1 : Lecture Séquentielle (30 min)
Lire les bundles DANS CET ORDRE STRICT :

1. **STATUS_REPORT_HOMEOS.md** (priorité max)
   - Note : "Ce qui est fait" vs "Ce qui est à faire"
   - Identifie les 9 phases UX

2. **Parcours UX Sullivan.md**
   - Comprendre le flow utilisateur étape par étape
   - Identifier les "intentions" à chaque phase

3. **PRD_HOMEOS_ETAT_ACTUEL.md**
   - Contexte général (ne pas s'y attarder, peut être obsolète)

4. **bundle_B_endpoints.txt**
   - Liste brute des capacités techniques
   - Mapper mentalement vers les phases UX

### PHASE 2 : Table de Confrontation (20 min)
Créer ce tableau (markdown) dans ta réponse :

```markdown
| Phase UX | Intention utilisateur | Endpoints Code | Statut | Visual Hint |
|----------|----------------------|----------------|--------|-------------|
| 1. IR | Inventorier | /studio/reports/ir | ✅ Codé + Doc | list |
| 2. Arbiter | Décider | /studio/arbitrage/forms | ✅ Codé | card |
| 9. Adaptation | Zoom Atome | /studio/zoom/atome/{id} | ⚠️ Codé mais ? | detail_panel |
```

**Légende Statut**:
- ✅ = Confirmé par au moins 2 sources (Doc + Code, ou Code + Logs)
- ⚠️ = Présent dans 1 source seule (risque d'hallucination)
- ❓ = Mentionné mais contradictions non résolues

### PHASE 3 : Extraction N0-N3 (30 min)
Structurer selon cette hiérarchie obligatoire :

```
N0 (World/Phase) → Les 9 étapes du parcours UX
  └── N1 (Section/Espace) → Grands espaces de l'UI
       └── N2 (Feature/Fonctionnalité) → Capacités concrètes
            └── N3 (Component/Atome) → Éléments UI rendables
```

**Contraintes N3 (CRITIQUE)**:
Chaque N3 DOIT avoir :
- `endpoint` : URL exacte (ex: "/studio/reports/ir")
- `method` : GET/POST/PUT/DELETE
- `visual_hint` : Type de composant (voir liste ci-dessous)
- `layout_hint` : grid/flex/stack
- `interaction_type` : click/hover/submit/drag
- `description_ui` : "L'utilisateur voit... et peut..."

**Liste des Visual Hints autorisés** (sois précis, pas de "generic"):
- **list** : Liste verticale d'items
- **card** : Carte avec header/body/footer
- **form** : Formulaire avec inputs + bouton submit
- **table** : Tableau de données
- **upload/dropzone** : Zone de drag & drop
- **chat/bubble** : Interface conversationnelle
- **preview** : Aperçu visuel (image/code)
- **dashboard** : Grille de métriques
- **editor** : Éditeur avec toolbar
- **breadcrumb** : Navigation hiérarchique
- **modal/dialog** : Fenêtre modale
- **tabs** : Onglets
- **accordion** : Contenu pliable
- **stepper** : Indicateur d'étapes
- **status/indicator** : Indicateur d'état (LED, badge)

### PHASE 4 : Validation Frontend (20 min)
Pour chaque N3, demande-toi :
- "Un dev junior peut-il coder ça sans me poser de question ?"
- "Quelles classes Tailwind/DaisyUI utiliser ?"
- "Que se passe-t-il en mobile ?"
- "Quel état loading ? Quel état error ?"

Si tu ne sais pas → Marque "uncertain" et justifie.

### PHASE 5 : Rapport d'Incertitudes (10 min)
Lister explicitement :
- Ce que tu n'as pas compris
- Les contradictions non résolues
- Les endpoints mentionnés mais sans visualisation claire
- Les hypothèses que tu as dû faire

---

## 📋 FORMAT DE SORTIE ATTENDU

### Fichier 1 : `genome_inferred_complete.json`
Structure strictement conforme à ce template :

```json
{
  "genome_version": "3.0-confronted",
  "inference_method": "4-source-confrontation",
  "project": "Homeos",
  "date": "2026-02-06",
  
  "metadata": {
    "confidence_global": "0.0-1.0",
    "sources_used": ["doc", "code", "inference"],
    "unresolved_conflicts": ["liste des contradictions"],
    "assumptions_made": ["hypothèses nécessaires"]
  },
  
  "n0_phases": [
    {
      "id": "phase_1_ir",
      "name": "Intent Refactoring",
      "description": "Phase 1-3 : Inventaire, Arbitrage, Genome",
      "order": 1,
      "confidence": 0.95,
      "n1_sections": [
        {
          "id": "section_ir_inventory",
          "name": "Inventaire",
          "description": "Visualisation du rapport d'inventaire",
          "n2_features": [
            {
              "id": "feature_ir_report",
              "name": "Rapport IR",
              "description": "Affichage des organes détectés",
              "n3_components": [
                {
                  "id": "comp_ir_list",
                  "name": "Liste Organes",
                  "endpoint": "/studio/reports/ir",
                  "method": "GET",
                  "visual_hint": "list",
                  "layout_hint": "flex-column",
                  "interaction_type": "click-select",
                  "description_ui": "Liste verticale des organes avec verdicts colorés (vert/jaune/rouge). Clic pour détails.",
                  "states": {
                    "loading": "skeleton-list",
                    "empty": "message-empty",
                    "error": "alert-error"
                  },
                  "responsive": "full-width-mobile"
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  
  "endpoints_unmapped": [
    {
      "endpoint": "/execute",
      "method": "POST",
      "reason": "Présent dans le code mais pas clairement lié à une phase UX"
    }
  ]
}
```

### Fichier 2 : `ANALYSIS_CONFRONTATION.md`
Rapport d'analyse structuré :

```markdown
# Analyse de Confrontation - Genome Homeos

## 1. Synthèse de Compréhension
(En 5 phrases : Qu'est-ce que Homeos ? Pour qui ? Comment ?)

## 2. Table de Confrontation
(Voir template PHASE 2)

## 3. Points de Certitude Haute (confiance > 0.9)
- Liste des N3 confirmés par au moins 2 sources

## 4. Points d'Incertitude (confiance < 0.7)
- Liste des éléments déduits, inférés ou contradictoires

## 5. Contradictions Majeures Non Résolues
| Élément | Source A dit | Source B dit | Mon arbitrage |
|---------|--------------|--------------|---------------|
| Stack Frontend | SvelteKit (doc) | HTMX (réalité perçue) | ??? |

## 6. Hypothèses Forçantes
(Liste des suppositions que tu as dû faire faute d'info claire)

## 7. Auto-Évaluation
| Critère | Score /5 | Justification |
|---------|----------|---------------|
| Exhaustivité | ? | ... |
| Précision UI | ? | ... |
| Cohérence métier | ? | ... |
| Actionnable | ? | Un dev peut-il coder avec ça ? |

**Score Global : ?/20**
```

---

## ⚠️ PIÈGES À ÉVITER

1. **Ne pas copier bêtement les endpoints**
   - Un endpoint technique n'est pas un composant UI
   - Traduis : "POST /studio/validate" → "Formulaire de validation avec bouton submit"

2. **Ne pas inventer de fonctionnalités**
   - Si ce n'est ni dans la doc, ni dans le code → n'en parle pas
   - Marque "uncertain" plutôt que d'halluciner

3. **Attention au vocabulaire**
   - "BRS/BKD/FRD/DPL" = concept obsolète (4 piliers)
   - "9 phases" = concept actuel (parcours UX)
   - Privilégie "phases" sur "piliers"

4. **HTMX vs SvelteKit**
   - La doc mentionne SvelteKit
   - L'état réel (si tu vois les templates) est HTMX (HTML+JS vanilla)
   - Pour le frontend : privilégie les composants DaisyUI + HTML
   - Ignore React/Svelte/Angular

5. **Les "step" du parcours UX**
   - Step 1-3 = IR (Inventaire, Arbitrage, Genome)
   - Step 4 = Composants défaut
   - Step 5-6 = Personnalisation (Upload/Analyse)
   - Step 7-8 = Dialogue/Validation
   - Step 9 = Adaptation (Corps/Organe/Atome)
   - Si un endpoint contient "step/9" → c'est la phase d'adaptation

---

## ✅ CHECKLIST AVANT LIVRAISON

- [ ] J'ai lu les 3 bundles dans l'ordre
- [ ] J'ai créé la table de confrontation
- [ ] Chaque N3 a un visual_hint spécifique (pas "generic")
- [ ] J'ai identifié les endpoints non mappés
- [ ] J'ai listé mes hypothèses et incertitudes
- [ ] J'ai auto-évalué mon travail (score /20)
- [ ] Le JSON est valide (vérifie avec un linter)
- [ ] Le rapport d'analyse est complet

---

BON COURAGE.

Ce test vise à savoir si un LLM "innocent" peut comprendre un projet complexe à partir de sa documentation et produire une spécification UI actionnable.

La qualité de ton genome déterminera la facilité avec laquelle un développeur frontend pourra implémenter l'interface.
