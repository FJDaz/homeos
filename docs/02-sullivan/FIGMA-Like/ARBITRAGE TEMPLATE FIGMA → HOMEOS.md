# ARBITRAGE TEMPLATE FIGMA → HOMEOS

## 🎯 CONTEXTE & OBJECTIF

**Scénario** : Un template Figma existant doit être intégré dans HomeOS. 
**Problème** : Comment mapper cette structure visuelle (Figma) à la sémantique métier (HomeOS IR) ?

**Objectif** : Réaliser un arbitrage intelligent qui :
1. Comprend la structure Figma
2. La mappe aux Intents de l'IR
3. Identifie les incohérences
4. Propose des corrections

## 🔄 WORKFLOW D'ARBITRAGE

```
[PHASE 0: IMPORT]
Template Figma (fichier .fig ou lien)
    ↓
Analyse structurelle Sullivan
    ↓
Extraction hiérarchique complète
    └─── FRAMES (Corps potentiels)
    └─── COMPONENT_SETS (Organes potentiels)  
    └─── COMPONENTS/INSTANCES (Atomes potentiels)
    ↓
[PHASE 1: ARBITRAGE PRINCIPAL]
```

## 📊 PHASE 1 : MAPPING SÉMANTIQUE

### ÉTAPE 1.1 - CORPS → FRAMES
```python
# Sullivan analyse chaque FRAME Figma
for frame in figma_frames:
    # Cherche un Intent correspondant dans l'IR
    matching_intent = find_matching_intent(frame, ir_intents)
    
    if matching_intent:
        # Mapping réussi : FRAME → Corps
        corps = create_corps_from_frame(frame, matching_intent)
        mapped_corps.append(corps)
    else:
        # FRAME orphelin : pas d'Intent correspondant
        orphaned_frames.append(frame)
```

### ÉTAPE 1.2 - ORGANES → COMPONENT_SETS
```python
for component_set in figma_component_sets:
    # Cherche une fonction métier correspondante
    matching_function = find_matching_function(component_set, ir_functions)
    
    if matching_function:
        # Mapping réussi : COMPONENT_SET → Organe
        organe = create_organe_from_component_set(component_set, matching_function)
        mapped_organes.append(organe)
    else:
        orphaned_component_sets.append(component_set)
```

### ÉTAPE 1.3 - ATOMES → COMPONENTS/INSTANCES
```python
for component in figma_components:
    # Cherche un élément d'interface correspondant
    matching_element = find_matching_element(component, ir_interface_elements)
    
    if matching_element:
        atome = create_atome_from_component(component, matching_element)
        mapped_atomes.append(atome)
    else:
        orphaned_components.append(component)
```

## ⚠️ PHASE 2 : DÉTECTION & ANALYSE DES ORPHELINS

### TYPES D'ORPHELINS
1. **FRAMES sans Intent** → Pages/écrans non prévus dans l'IR
2. **COMPONENT_SETS sans fonction** → Fonctionnalités non spécifiées  
3. **COMPONENTS sans élément** → UI non documentée
4. **HIÉRARCHIES brisées** → Parents/enfants incohérents

### RAPPORT D'ORPHELINS
```json
{
  "orphans_summary": {
    "frames": [
      {
        "id": "frame_123",
        "name": "Admin_Panel",
        "reason": "Aucun Intent 'admin' dans l'IR",
        "suggestions": [
          "Ajouter Intent 'Gestion administrateur'",
          "Fusionner avec Intent 'Dashboard'",
          "Supprimer ce frame (non nécessaire)"
        ]
      }
    ],
    "component_sets": [...],
    "components": [...]
  },
  "coverage_metrics": {
    "frames_mapped": "85%",
    "component_sets_mapped": "72%", 
    "components_mapped": "91%",
    "confidence_score": 0.76
  }
}
```

## 🔍 PHASE 3 : ÉVALUATION DE LA NÉCESSITÉ

### MATRICE DE DÉCISION
```
Élément orphelin → Analyse d'impact → Décision
    ↓                   ↓              ↓
[Criticité]      [Conséquences]   [Action]
```

#### CRITÈRES D'ÉVALUATION :
1. **Criticité fonctionnelle** (0-10)
   - Essentiel au flux utilisateur ?
   - Contient des données critiques ?
   - Impact sur d'autres éléments ?

2. **Complexité d'intégration** (0-10)
   - Nombre de dépendances
   - Spécificité technique
   - Effort de mapping

3. **Alignement stratégique** (0-10)
   - Correspond à la roadmap ?
   - Valeur utilisateur ?
   - Cohérence produit ?

### SCORING AUTOMATIQUE
```python
def evaluate_orphan_necessity(orphan):
    score = (
        functional_criticality(orphan) * 0.4 +
        integration_complexity(orphan) * 0.3 +
        strategic_alignment(orphan) * 0.3
    )
    
    if score >= 7.0:
        return "NÉCESSAIRE_ABSOLU"  # → Retour en brainstorm
    elif score >= 4.0:
        return "NÉCESSAIRE_CONDITIONNEL"  # → Ajustements mineurs
    else:
        return "NON_NÉCESSAIRE"  # → Suppression ou report
```

## 🔄 PHASE 4 : RETOUR EN BRAINSTORM (SI NÉCESSAIRE)

### CAS 1 : NÉCESSITÉ ABSOLUE DÉTECTÉE
```
Élément(s) orphelin(s) critiques identifiés
    ↓
[ALERTE] Retour en phase Brainstorm requis
    ↓
Session collaborative :
├── Participants : PO, Designer, Tech Lead, Sullivan
├── Durée : 45-90 min
├── Objectif : Réconcilier template Figma avec IR
└── Livrable : PRD amendé
```

### AGENDA BRAINSTORM
1. **Présentation des orphelins critiques** (5 min)
2. **Analyse root-cause** (15 min)
   - Pourquoi cet élément n'était-il pas dans l'IR ?
   - Omission ou choix délibéré ?
3. **Options de résolution** (20 min)
   - Option A : Ajouter à l'IR (étendre le scope)
   - Option B : Adapter le template (réduire le scope)
   - Option C : Solution hybride
4. **Décision & plan d'action** (10 min)

### AMENDEMENT DU PRD
```markdown
# PRD - AMENDEMENT #X
Date : [date]
Motif : Éléments Figma non couverts par l'IR

## AJOUTS :
- [Nouvel Intent] : Gestion administrateur
  - Justification : Présent dans template, valeur utilisateur haute
  - Impact : +2 sprints, +1 développeur

- [Nouvelle Fonction] : Export CSV
  - Justification : Implémenté dans template UI
  - Impact : +3 jours de dev

## SUPPRESSIONS :
- [Intent retiré] : Dashboard avancé
  - Justification : Duplique nouvelles fonctionnalités
  - Impact : -5 jours de dev

## ADJUSTEMENTS :
- [Intent modifié] : Reporting
  - Changements : Inclut maintenant l'export
  - Impact : +2 jours de dev
```

## 🏗️ PHASE 5 : REPRISE DU BACKEND (SI NÉCESSAIRE)

### IMPACT SUR L'ARCHITECTURE
```python
# Nouveau Genome généré
new_genome = generate_genome_from_amended_prd(
    original_genome,
    prd_amendments,
    figma_template
)

# Analyse d'impact backend
backend_impact = analyze_backend_impact(new_genome)

if backend_impact["requires_changes"]:
    print("⚠️  Reprise backend nécessaire")
    
    # Génération des migrations
    migrations = generate_backend_migrations(
        backend_impact["new_models"],
        backend_impact["modified_apis"],
        backend_impact["new_integrations"]
    )
    
    # Plan d'exécution
    execution_plan = create_backend_execution_plan(migrations)
```

### CHECKLIST REPRISE BACKEND
- [ ] Modèles de données mis à jour
- [ ] Schémas API révisés
- [ ] Endpoints nouveaux/modifiés
- [ ] Migrations de base de données
- [ ] Tests mis à jour
- [ ] Documentation technique

## 📈 PHASE 6 : NOUVEAU GENOME & VALIDATION

### GÉNÉRATION DU GENOME RÉVISÉ
```python
# Intégration des décisions du brainstorm
revised_genome = GenomeReviser(
    original_genome=initial_genome,
    prd_amendments=prd_amendments,
    figma_template=figma_template,
    orphan_decisions=orphan_decisions  # {"include": [...], "exclude": [...]}
).revise()

# Validation de cohérence
validation_report = GenomeValidator(revised_genome).validate()

if validation_report["is_valid"]:
    print("✅ Nouveau genome généré avec succès")
    save_genome(revised_genome, "genome_v2.json")
else:
    print("❌ Incohérences détectées")
    trigger_review(validation_report["issues"])
```

### CYCLE ITÉRATIF
```
Nouveau Genome → Validation Sullivan → Feedback
      ↓                               ↑
  Déploiement test ←───── Corrections
      ↓
  User testing
      ↓
  Ajustements fins
      ↓
  Version finale
```

## 🎯 PRINCIPES DE L'ARBITRAGE

### 1. **PRAGMATISME SUR PURISME**
- Accepter certains orphelins si valeur utilisateur élevée
- Prioriser l'expérience sur la perfection théorique

### 2. **TRANSPARENCE TOTALE**
- Documenter toutes les décisions d'arbitrage
- Traçabilité complète : Figma → IR → Genome

### 3. **ITÉRATION RAPIDE**
- Cycles courts d'arbitrage
- Feedback immédiat sur les décisions
- Ajustements incrémentaux

### 4. **COLLABORATION CROISÉE**
- Designers, développeurs, PO ensemble
- Sullivan comme facilitateur technique
- Décisions consensuelles documentées

## 📊 MÉTRIQUES DE SUCCÈS

### QUALITATIVES
- **Cohérence** : Mapping logique entre Figma et IR
- **Complétude** : Tous les éléments critiques couverts
- **Maintenabilité** : Decisions documentées et réversibles

### QUANTITATIVES
- **Taux de mapping** : % d'éléments Figma mappés
- **Orphelins critiques** : < 5% des éléments
- **Temps d'arbitrage** : < 2 jours pour un template moyen
- **Itérations nécessaires** : Objectif 1-2 cycles max

## 🚨 GESTION DES RISQUES

### RISQUE 1 : SCOPE CREEP
- **Solution** : Seuil strict pour "nécessité absolue"
- **Mitigation** : Backlog séparé pour les "nice-to-have"

### RISQUE 2 : INCOHÉRENCES TECHNIQUES
- **Solution** : Validation automatisée du genome
- **Mitigation** : Environnement de test pour chaque décision

### RISQUE 3 : CONFLITS DÉCISIONNELS
- **Solution** : Matrice de décision objective
- **Mitigation** : Escalation rapide avec données factuelles

---

**EN RÉSUMÉ** : L'arbitrage Figma → HomeOS est un processus **semi-automatisé, collaboratif et itératif** qui utilise Sullivan pour identifier les incohérences entre le template visuel et l'Intent Review, avec des mécanismes clairs pour gérer les éléments orphelins et ajuster le produit de manière structurée.