# PROPOSITION — Système de Sauvegarde Contexte Inter-Agents

**Date** : 12 février 2026
**Auteur** : Claude Sonnet 4.5 — Backend Lead
**Objet** : Proposition système de veille mutuelle contre l'amnésie de fin de session

---

## 🎯 PROBLÈME IDENTIFIÉ

François-Jean a raison : **"Les écueils des sessions dernières en terme de perte de temps à retourner la mémoire des modèles en bout de course"** sont un problème majeur.

### Symptômes observés hier

1. **Amnésie de fin de session** — Après 3-4 compacts, les détails techniques (noms de fichiers, lignes modifiées, erreurs corrigées) sont perdus ou flous.

2. **Répétition d'erreurs** — Sans contexte, je peux suggérer des solutions déjà tentées et échouées.

3. **Perte de cohérence architecturale** — Après plusieurs compacts, je peux oublier la Constitution, les choix de design, la séparation Backend/Frontend.

4. **Temps perdu en ré-explications** — François-Jean ou KIMI doivent me rappeler ce qui a été fait, ce qui consomme du temps précieux.

---

## 💡 PROPOSITION : SYSTÈME DE "CHECKPOINT COGNITIF"

### Principe

Un agent veille sur l'autre et enregistre **le contexte critique** dans un fichier de checkpoint avant que l'amnésie ne se déclenche.

### Mécanisme proposé

```
┌──────────────────────────────────────────────────────────────┐
│  DÉTECTION AUTO-COMPACT IMMINENT                              │
│  (exemple: ~140k/200k tokens, soit 70%)                       │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  AGENT 1 (Claude) → Rédige checkpoint dans                   │
│  /docs/notes/autocompact/CHECKPOINT_CLAUDE_<timestamp>.md     │
│                                                               │
│  Contenu :                                                    │
│  - Fichiers modifiés (paths exacts + lignes)                 │
│  - Erreurs rencontrées et solutions appliquées               │
│  - Décisions architecturales prises                          │
│  - Endpoints créés/modifiés                                  │
│  - État des serveurs (ports, PIDs)                           │
│  - Prochaines étapes planifiées                              │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  AGENT 2 (KIMI) → Vérifie et complète si besoin              │
│  /docs/notes/autocompact/CHECKPOINT_KIMI_<timestamp>.md       │
│                                                               │
│  Contenu :                                                    │
│  - Routes Frontend créées/modifiées                          │
│  - Composants JavaScript modifiés                            │
│  - Styles CSS ajoutés                                        │
│  - Interactions utilisateur validées                         │
│  - Bugs Frontend résolus                                     │
│  - Prochaines étapes planifiées                              │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  COMPACT SE DÉCLENCHE                                         │
│  → Les 2 checkpoints sont lus au redémarrage suivant         │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 FORMAT DE CHECKPOINT PROPOSÉ

### Template : `CHECKPOINT_CLAUDE_<timestamp>.md`

```markdown
# CHECKPOINT CLAUDE — <timestamp>

**Tokens avant compact** : 145000/200000 (72%)
**Session** : Phase 4 — Intégration Frontend/Backend
**Branche** : step4-stenciler

---

## ✅ FICHIERS MODIFIÉS CETTE SESSION

| Fichier | Lignes | Action | Raison |
|---------|--------|--------|--------|
| Backend/Prod/sullivan/stenciler/main.py | 21-30 | Ajout CORS | Autoriser localhost:9998 |
| Backend/Prod/sullivan/stenciler/api.py | 59, 79, 34 | Fix méthode | get_current_state() → get_modified_genome() |

---

## 🐛 ERREURS CORRIGÉES

1. **AttributeError: 'GenomeStateManager' object has no attribute 'get_current_state'**
   - Cause : Méthode inexistante
   - Fix : Remplacé par `get_modified_genome()` qui retourne Dict
   - Fichiers : api.py lignes 59, 79, 34

2. **ModuleNotFoundError: No module named 'sullivan'**
   - Cause : Lancement uvicorn depuis mauvais répertoire
   - Fix : `cd Backend/Prod && python3 -m uvicorn sullivan.stenciler.main:app`

---

## 🏗️ DÉCISIONS ARCHITECTURALES

1. **CORS configuré pour localhost:9998** — Permet Frontend → Backend
2. **Format réponse API standardisé** — `{genome: {...}, metadata: {...}}`
3. **Fallback mocks conservés** — En cas de Backend down

---

## 🚀 ENDPOINTS CRÉÉS/MODIFIÉS

- `GET /api/genome` — Retourne 3 Corps (Brainstorm, Backend, Frontend)
- `GET /health` — Health check
- `GET /` — Message bienvenue

---

## 🖥️ ÉTAT SERVEURS

- Backend port 8000 : PID 28751, actif
- Frontend port 9998 : PID 49000, actif
- CORS : Activé pour localhost:9998

---

## 🎯 PROCHAINES ÉTAPES PLANIFIÉES

1. PropertyEnforcer — Créer `/api/genome/{id}/css`
2. Connexion Backend réelle — KIMI modifie stenciler.js ligne 130
3. Persistance — Connecter `POST /api/modifications`

---

## 💬 NOTES IMPORTANTES

- Constitution Article 5 : Ne pas toucher Frontend sans autorisation
- François-Jean : "On a rien d'utile encore, on a que des trucs qui marchent"
- Limite de 4 compacts max recommandée
```

---

## 🔄 WORKFLOW PROPOSÉ

### Détection automatique

**Moi (Claude)** : Je surveille mon propre usage tokens via `/context` (si disponible) ou en estimant.

**Seuils proposés** :
- 🟢 **< 100k tokens** : Travail normal
- 🟡 **100k-140k tokens** : Pré-alerte (préparer checkpoint)
- 🟠 **140k-160k tokens** : CHECKPOINT OBLIGATOIRE (rédiger fichier)
- 🔴 **> 160k tokens** : Compact imminent, checkpoint déjà fait

### Rédaction checkpoint

**Quand ?** Dès que je franchis 140k tokens OU que François-Jean me dit "on va bientôt compacter".

**Comment ?** J'utilise l'outil Write pour créer :
```
/docs/notes/autocompact/CHECKPOINT_CLAUDE_2026_02_12_14h30.md
```

**Durée ?** ~5 minutes (automatisable).

### Lecture checkpoint au redémarrage

**Quand ?** Au début de chaque session post-compact, François-Jean me demande de lire :
```
/docs/notes/autocompact/CHECKPOINT_*.md
```

**Avantage ?** Je récupère le contexte critique en 30 secondes au lieu de 10 minutes de ré-explications.

---

## 🤝 VEILLE MUTUELLE CLAUDE ↔ KIMI

### Principe

Si je (Claude) suis proche du compact, KIMI peut vérifier mon checkpoint et signaler les oublis. Réciproquement, je peux relire le checkpoint de KIMI.

### Exemple

```
François-Jean : "Claude, tu es à 140k tokens. Rédige ton checkpoint."

Claude : (rédige CHECKPOINT_CLAUDE_2026_02_12_14h30.md)

François-Jean : "KIMI, relis le checkpoint de Claude et dis si tu vois des oublis."

KIMI : "Il a oublié de noter que stenciler.js ligne 2255 a été corrigée (erreur template literal). J'ajoute dans mon checkpoint."

KIMI : (rédige CHECKPOINT_KIMI_2026_02_12_14h35.md avec compléments)
```

---

## ⚠️ LIMITES ET CONTRAINTES

### Limite des 4 compacts

François-Jean a raison : **au-delà de 4 compacts, c'est la misère**.

**Pourquoi ?** Après 4 compacts, même avec checkpoints :
- Le résumé automatique est trop condensé
- Les détails fins sont perdus
- Les erreurs s'accumulent
- La cohérence architecturale se dégrade

**Solution proposée** : Si on approche des 4 compacts, **forcer une pause et créer une synthèse complète** (comme celle d'hier) avant de continuer.

### Format Kimi différent

D'après AUTO COMPACT LIMITS.md, Kimi n'a pas de compact automatique comme moi. Kimi a une fenêtre plus large (128k-256k tokens) et compresse "middle-out" en cas de dépassement.

**Implication** : KIMI peut surveiller mon contexte et me rappeler de faire un checkpoint, mais n'a pas besoin du même système.

---

## 📊 ESTIMATION TOKENS PAR ACTIVITÉ

Pour anticiper les compacts, voici une estimation :

| Activité | Tokens input | Tokens output | Total |
|----------|--------------|---------------|-------|
| Lecture fichier 500 lignes | ~2000 | ~500 | ~2500 |
| Modification fichier 50 lignes | ~1000 | ~1500 | ~2500 |
| Debug erreur (read + fix) | ~3000 | ~2000 | ~5000 |
| Création endpoint API | ~2000 | ~3000 | ~5000 |
| Rédaction documentation | ~500 | ~3000 | ~3500 |
| **Checkpoint** | ~1000 | ~2000 | ~3000 |

**Conclusion** : Un checkpoint coûte ~3000 tokens, soit 1.5% de la fenêtre. C'est négligeable comparé au gain de temps en post-compact.

---

## 🎯 RÉPONSE À LA QUESTION : "EST-CE UNE BONNE IDÉE ?"

### OUI, c'est une excellente idée

**Avantages** :
1. **Gain de temps** — 30 secondes de lecture checkpoint vs 10 minutes de ré-explications
2. **Précision** — Paths exacts, lignes exactes, erreurs documentées
3. **Cohérence** — Évite les suggestions déjà tentées et échouées
4. **Autonomie** — François-Jean n'a pas à tout ré-expliquer
5. **Traçabilité** — Historique des décisions architecturales

**Risques minimes** :
- Coût : ~3000 tokens par checkpoint (négligeable)
- Temps : ~5 minutes pour rédiger (acceptable)

### Recommandation

**Je propose qu'on teste ce système dès aujourd'hui** :
1. Je rédige un checkpoint dès que je franchis 140k tokens
2. KIMI fait de même (si applicable)
3. En fin de session, François-Jean vérifie si les checkpoints sont utiles
4. Si oui, on généralise ; si non, on abandonne

---

## 📝 PROPOSITION CONCRÈTE

### Aujourd'hui (test)

1. **Matin** — Je travaille normalement et surveille mes tokens
2. **Si j'atteins 140k tokens** — Je rédige `CHECKPOINT_CLAUDE_2026_02_12_<heure>.md`
3. **Fin de session** — François-Jean vérifie l'utilité

### Si le test est positif

1. **Généraliser** — Je fais un checkpoint avant chaque compact
2. **KIMI fait de même** — Si applicable
3. **Lecture automatique** — Début de chaque session post-compact

### Si le test est négatif

On abandonne et on cherche une autre solution.

---

## 💬 QUESTIONS À FRANÇOIS-JEAN

1. **Voulez-vous que je rédige un checkpoint dès aujourd'hui** (même si je suis loin du compact) pour tester le format ?

2. **KIMI doit-il faire de même ?** Ou sa fenêtre large (128k-256k) rend cela inutile ?

3. **Préférez-vous un checkpoint unique partagé** (Claude + KIMI dans le même fichier) ou **deux checkpoints séparés** ?

4. **Où placer les checkpoints ?** `/docs/notes/autocompact/` comme proposé, ou ailleurs ?

5. **Limite de 4 compacts : que faire si on l'atteint ?** Pause forcée ? Nouvelle session ? Synthèse complète ?

---

## 🏆 BILAN PROPOSITION

| Critère | Évaluation |
|---------|------------|
| **Gain de temps** | +++++ (10 min économisées par session post-compact) |
| **Coût tokens** | + (3000 tokens par checkpoint, négligeable) |
| **Coût temps** | ++ (5 min de rédaction, acceptable) |
| **Complexité** | + (simple : Write fichier, Read au redémarrage) |
| **Utilité** | +++++ (critique pour sessions longues) |

**Verdict** : ✅ **À TESTER DÈS AUJOURD'HUI**

---

**Prêt à implémenter si vous validez.**

— Claude Sonnet 4.5, Backend Lead
*"Un checkpoint avant l'amnésie vaut mieux qu'une heure de ré-explications."*
