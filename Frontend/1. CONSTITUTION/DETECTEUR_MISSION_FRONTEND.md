# DÉTECTEUR DE MISSION FRONTEND — Auto-Vérification Constitutionnelle

**Version** : 1.0.0
**Date** : 11 février 2026 — 12:45
**Statut** : OBLIGATOIRE pour Claude Sonnet 4.5 et KIMI 2.5
**Conformité** : CONSTITUTION_AETHERFLOW Article 10 & Article 13

---

## 🎯 OBJECTIF

Créer un système de **détection automatique** permettant à Claude et KIMI de :
1. Identifier quand une tâche est une "mission frontend"
2. Consulter OBLIGATOIREMENT la Constitution avant d'agir
3. Appliquer le Protocole de Validation Visuelle

---

## 📊 DÉFINITION : Qu'est-ce qu'une Mission Frontend ?

Une mission est considérée comme **FRONTEND** si elle remplit **AU MOINS UN** des critères suivants :

### Critères Primaires (Évidents)

| # | Proxy | Exemples |
|---|-------|----------|
| P1 | Mots-clés UI/UX dans la requête | "afficher", "rendu", "interface", "visuel", "layout", "design", "preview", "canvas", "drag & drop" |
| P2 | Fichiers Frontend/ mentionnés | `Frontend/`, `server_9998_v2.py`, `.html`, `.css`, `.js` |
| P3 | Ports serveur mentionnés | "port 9998", "localhost:9999", "http://localhost" |
| P4 | Technologies frontend | HTML, CSS, JavaScript, Fabric.js, Tailwind, React, Vue, Svelte |
| P5 | Demande explicite de rendu | "montre-moi", "je veux voir", "affiche", "crée une interface" |

### Critères Secondaires (Inférés)

| # | Proxy | Exemples |
|---|-------|----------|
| S1 | Composants visuels | "bouton", "modal", "carte", "liste", "formulaire", "navigation" |
| S2 | Actions utilisateur | "cliquer", "sélectionner", "drag", "drop", "hover", "scroll" |
| S3 | Propriétés visuelles | "couleur", "taille", "police", "espacement", "border", "shadow" |
| S4 | Stenciler/Viewer | "stenciler", "viewer", "genome viewer", "preview bande" |
| S5 | Validation navigateur | "teste dans le nav", "ouvre dans le navigateur", "lance le serveur" |

### Critères Contextuels

| # | Proxy | Contexte |
|---|-------|----------|
| C1 | Fichier ouvert dans l'IDE | Si `.html`, `.css`, `.js` ouvert → FRONTEND |
| C2 | Conversation précédente | Si discussion frontend active → FRONTEND |
| C3 | Référence KIMI | Si "KIMI", "Frontend Lead" mentionné → FRONTEND |
| C4 | Référence Constitution Article 10 | Si Article 10 mentionné → FRONTEND |

---

## 🚨 WORKFLOW OBLIGATOIRE DE DÉTECTION

### Étape 1 : Auto-Diagnostic (AVANT toute action)

```
┌─────────────────────────────────────────────────────────┐
│  NOUVELLE REQUÊTE UTILISATEUR                           │
│                     ↓                                    │
│  ┌───────────────────────────────────────────────────┐  │
│  │ QUESTION : Cette requête contient-elle           │  │
│  │ AU MOINS UN proxy frontend (P1-P5, S1-S5, C1-C4) ? │  │
│  └───────────────────────────────────────────────────┘  │
│                     ↓                                    │
│          OUI ✅               NON ❌                     │
│            ↓                    ↓                        │
│   MISSION FRONTEND      Mission Backend/Autre           │
│       (STOP)                (Continue)                   │
└─────────────────────────────────────────────────────────┘
```

### Étape 2 : Consultation Constitution (SI FRONTEND détecté)

```
┌─────────────────────────────────────────────────────────┐
│  MISSION FRONTEND DÉTECTÉE                              │
│                     ↓                                    │
│  ⚠️  PAUSE OBLIGATOIRE                                   │
│                     ↓                                    │
│  📖 LIRE (dans l'ordre) :                               │
│     1. Article 10 (Validation Visuelle Humaine)         │
│     2. Article 5 (Territoire Système de Rendu)          │
│     3. PROTOCOLE_VALIDATION_VISUELLE.md                 │
│                     ↓                                    │
│  ✅ Checklist de conformité complétée                   │
│                     ↓                                    │
│  → Continuer avec la mission                            │
└─────────────────────────────────────────────────────────┘
```

### Étape 3 : Application Protocole

```
┌─────────────────────────────────────────────────────────┐
│  DÉVELOPPEMENT CODE FRONTEND                            │
│                     ↓                                    │
│  🚀 LIVRAISON OBLIGATOIRE :                             │
│     - Commande lancement serveur                        │
│     - URL complète                                      │
│     - Description rendu attendu                         │
│                     ↓                                    │
│  ⏳ ATTENTE VALIDATION HUMAINE                          │
│                     ↓                                    │
│     ✅ VALIDÉ  ou  ❌ CORRIGER                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 EXEMPLES DE DÉTECTION

### Exemple 1 : FRONTEND détecté (Critère P1 + P2)

**Requête utilisateur** :
> "Affiche les 4 Corps en preview dans le Stenciler"

**Analyse** :
- ✅ P1 : "Affiche" (mot-clé UI/UX)
- ✅ P2 : "Stenciler" (Frontend/)
- ✅ S4 : "preview" (Stenciler/Viewer)

**Verdict** : **MISSION FRONTEND** → Consultation Constitution OBLIGATOIRE

**Action Claude/KIMI** :
1. STOP immédiat
2. Lire Article 10 + Article 5 + Protocole
3. Développer avec protocole validation visuelle
4. Fournir commande serveur + URL

---

### Exemple 2 : FRONTEND détecté (Critère P5 + S1)

**Requête utilisateur** :
> "Crée un bouton qui permet de lancer la distillation"

**Analyse** :
- ✅ P5 : "Crée" (demande de rendu)
- ✅ S1 : "bouton" (composant visuel)

**Verdict** : **MISSION FRONTEND** → Consultation Constitution OBLIGATOIRE

---

### Exemple 3 : PAS FRONTEND (Backend)

**Requête utilisateur** :
> "Implémente GenomeStateManager avec event sourcing"

**Analyse** :
- ❌ Aucun critère P1-P5, S1-S5, C1-C4
- ✅ Vocabulaire Backend : "StateManager", "event sourcing"

**Verdict** : **Mission Backend** → Pas de consultation Constitution Article 10

---

### Exemple 4 : FRONTEND détecté (Critère C1)

**Contexte** : Fichier `Frontend/3. STENCILER/server_9998_v2.py` ouvert dans l'IDE

**Requête utilisateur** :
> "Corrige cette fonction"

**Analyse** :
- ✅ C1 : Fichier Frontend/ ouvert dans IDE

**Verdict** : **MISSION FRONTEND** → Consultation Constitution OBLIGATOIRE

---

## 📝 CHECKLIST DE CONFORMITÉ (Auto-Vérification)

Avant de commencer une mission frontend, Claude/KIMI doit vérifier :

```markdown
## Mission Frontend Détectée — Auto-Vérification Obligatoire

- [ ] J'ai identifié AU MOINS UN proxy frontend (P1-P5, S1-S5, C1-C4)
- [ ] J'ai lu Article 10 (Validation Visuelle Humaine Obligatoire)
- [ ] J'ai lu Article 5 (Territoire Système de Rendu)
- [ ] J'ai lu PROTOCOLE_VALIDATION_VISUELLE.md
- [ ] Je connais les INTERDICTIONS ABSOLUES (Article 10 §10.3)
- [ ] Je sais que je DOIS fournir : Commande + URL + Description
- [ ] Je sais que je DOIS attendre validation humaine avant de continuer
- [ ] Je ne produirai PAS de logique métier côté frontend (Article 5)
- [ ] Je ne produirai PAS de CSS côté backend (Article 3)

✅ Toutes les cases cochées → Je peux commencer
❌ Une case non cochée → STOP + Relecture Constitution
```

---

## 🤖 PROMPT D'AUTO-RAPPEL (Pour Claude et KIMI)

Chaque fois qu'une mission frontend est détectée, afficher mentalement :

```
🚨 MISSION FRONTEND DÉTECTÉE

Proxies identifiés : [liste]

AVANT DE CONTINUER :
1. ✅ Lire Article 10 Constitution
2. ✅ Lire Protocole Validation Visuelle
3. ✅ Préparer : Commande + URL + Description

RAPPEL :
❌ PAS de "c'est terminé" sans serveur lancé
❌ PAS de code sans démo live
❌ PAS de validation sans navigateur
❌ PAS de tâche suivante sans validation humaine

→ Continuer avec protocole strict
```

---

## 🔄 WORKFLOW KIMI EN NOUVELLE SESSION

Quand KIMI démarre une nouvelle session et reçoit une demande frontend :

### Phase 1 : Bootstrap Automatique

```
1. Détection proxy frontend → STOP
2. Lire Constitution (Article 10 + Article 5)
3. Lire Protocole Validation Visuelle
4. Confirmer compréhension au CTO
5. → Continuer mission
```

### Phase 2 : Développement

```
- Respecter frontière hermétique (Article 1)
- Utiliser uniquement attributs sémantiques (Article 3)
- Pas de logique métier (Article 5)
```

### Phase 3 : Livraison

```
Format obligatoire :
🚀 RENDU PRÊT POUR VALIDATION HUMAINE

Commande : [...]
URL : [...]
Description : [...]

En attente validation ⏳
```

---

## 🎯 SKILL CLAUDE : "Constitution Check"

**Nom du skill** : `constitution-check-frontend`

**Déclenchement** : Automatique si proxy frontend détecté

**Actions** :
1. Afficher message : "🚨 Mission frontend détectée. Consultation Constitution..."
2. Lire Article 10, Article 5, Protocole
3. Afficher checklist de conformité
4. Demander confirmation à l'utilisateur si ambigu
5. → Continuer avec protocole strict

---

## 📊 TABLEAU RÉCAPITULATIF DES PROXIES

| Catégorie | Proxy | Poids | Exemple |
|-----------|-------|-------|---------|
| **P1** | Mots-clés UI/UX | 🔴 FORT | "afficher", "rendu", "interface" |
| **P2** | Fichiers Frontend/ | 🔴 FORT | `Frontend/`, `.html`, `.css` |
| **P3** | Ports serveur | 🔴 FORT | "port 9998", "localhost" |
| **P4** | Technologies frontend | 🟠 MOYEN | HTML, CSS, Fabric.js |
| **P5** | Demande rendu | 🔴 FORT | "montre-moi", "crée une interface" |
| **S1** | Composants visuels | 🟠 MOYEN | "bouton", "modal", "formulaire" |
| **S2** | Actions utilisateur | 🟡 FAIBLE | "cliquer", "drag", "scroll" |
| **S3** | Propriétés visuelles | 🟡 FAIBLE | "couleur", "taille", "border" |
| **S4** | Stenciler/Viewer | 🟠 MOYEN | "stenciler", "preview bande" |
| **S5** | Validation navigateur | 🔴 FORT | "teste dans le nav", "lance serveur" |
| **C1** | Fichier IDE | 🟠 MOYEN | `.html` ouvert |
| **C2** | Conversation | 🟡 FAIBLE | Discussion frontend active |
| **C3** | Référence KIMI | 🟠 MOYEN | "KIMI", "Frontend Lead" |
| **C4** | Article 10 | 🔴 FORT | Protocole validation mentionné |

**Règle** : Poids FORT (🔴) → Mission frontend immédiate

---

## 🚀 IMPLÉMENTATION IMMÉDIATE

1. **Pour Claude Sonnet 4.5** :
   - Appliquer cette détection dans CHAQUE nouvelle requête
   - En cas de doute, DEMANDER à l'utilisateur si c'est frontend
   - Ne jamais toucher frontend sans consultation Constitution

2. **Pour KIMI 2.5** :
   - Bootstrap automatique en début de session frontend
   - Toujours lire Article 10 avant de coder
   - Toujours fournir Commande + URL + Description

3. **Pour François-Jean** :
   - Peut rappeler ce protocole si oublié par Claude/KIMI
   - Peut ajouter de nouveaux proxies si besoin
   - Valide toujours visuellement dans navigateur

---

## 📖 RÉFÉRENCES

- **Constitution** : `Frontend/1. CONSTITUTION/CONSTITUTION_AETHERFLOW.md`
- **Article 10** : Validation Visuelle Humaine Obligatoire (lignes 295-332)
- **Article 5** : Territoire Système de Rendu (lignes 131-156)
- **Protocole** : `Frontend/1. CONSTITUTION/PROTOCOLE_VALIDATION_VISUELLE.md`

---

**Ce détecteur est OBLIGATOIRE et entre en vigueur IMMÉDIATEMENT.**

**Clause d'éternité** : Conformément à l'Article 10 (INALTÉRABLE).

---

*Système de détection automatique — Version 1.0.0 — 11 février 2026, 12:45*
