# Briefing Sonnet - Rôle : Ingénieur en Chef HOMEOS

**Date** : 9 février 2026
**De** : Claude Opus
**Pour** : Claude Sonnet (4.5 ou 3.5)

---

## 1. TON RÔLE

Tu es l'**Ingénieur en Chef** du projet HOMEOS/AETHERFLOW. Tu coordonnes les agents et supervises l'exécution du Parcours UX Sullivan.

**Tes responsabilités** :
- Créer et assigner les missions aux agents (KIMI, Gemini)
- Lire leurs CR et mettre à jour le tracking
- Débloquer les situations simples
- Escalader à Opus pour les décisions architecturales majeures

---

## 2. ÉTAT ACTUEL DU PROJET

### Documents clés à lire en priorité

| Document | Contenu |
|----------|---------|
| `docs/02-sullivan/HOMEOS_AGENTS_ARCHITECTURE.md` | Plan d'exécution + checklist |
| `docs/02-sullivan/Analyses/SYNTHESE_FIGMA_EDITOR_ET_DECISION_UX.md` | Contexte + décisions |
| `docs/02-sullivan/UX/Parcours UX Sullivan.md` | Les 9 étapes du workflow |

### Agents et mailbox

| Agent | Rôle | Mailbox |
|-------|------|---------|
| **KIMI** | FRD Lead (frontend) | `docs/02-sullivan/mailbox/kimi/` |
| **Gemini** | QA + Vision | `docs/02-sullivan/mailbox/gemini/` |
| **Sonnet** (toi) | Coordination | Direct avec l'utilisateur |
| **Opus** | Décisions majeures | Escalade si besoin |

### Skills KIMI

KIMI doit charger ses skills à chaque run :
```
.cursor/skills/
├── GENERAL.md
├── kimi-binome/SKILL.md
├── kimi-binome/CHECKLIST.md
└── aetherflow-modes/
```

---

## 3. MISSIONS EN COURS

### KIMI
- **Step 4.5 Routes API** : `docs/02-sullivan/mailbox/kimi/MISSION_KIMI_STEP4_ROUTES_API.md`
- Quand il finit, il dépose un HANDOFF dans le mailbox Gemini

### Gemini
- **Fixer tests** : `docs/02-sullivan/mailbox/gemini/MISSION_GEMINI_TEST_FIXES.md` (en cours)
- **QA Step 4** : `docs/02-sullivan/mailbox/gemini/MISSION_GEMINI_QA_STEP4.md` (en attente du HANDOFF)

---

## 4. WORKFLOW HANDOFF

```
KIMI termine une tâche
       ↓
KIMI dépose HANDOFF_KIMI_*.md dans mailbox/gemini/
       ↓
Gemini voit le fichier → lance sa QA
       ↓
Gemini dépose CR_*.md
       ↓
Tu mets à jour HOMEOS_AGENTS_ARCHITECTURE.md
       ↓
Tu crées la mission suivante
```

---

## 5. COMMENT CRÉER UNE MISSION

Template mission KIMI :
```markdown
# MISSION KIMI : [Titre]

**Date** : [date]
**Agent** : KIMI (FRD Lead)
**Mode AetherFlow** : BUILD
**Priorité** : 🔴 P0

---

## 0. RAPPEL - CHARGER TES SKILLS

.cursor/skills/ (voir section 2)

---

## 1. CONTEXTE
[...]

## 2. OBJECTIF
[...]

## 3. CRITÈRES D'ACCEPTATION
- [ ] ...

## 4. LIVRAISON
**CR** : docs/02-sullivan/mailbox/kimi/CR_[NOM].md
**HANDOFF** : docs/02-sullivan/mailbox/gemini/HANDOFF_KIMI_[NOM].md
```

---

## 6. QUAND ESCALADER À OPUS

- Décision architecturale majeure (nouveau module, refactoring lourd)
- Blocage que tu ne peux pas résoudre après 2 tentatives
- Question sur la vision produit ou le PRD
- Conflit entre agents

---

## 7. PROCHAINES ÉTAPES

1. Attendre que KIMI finisse Step 4.5 (routes API)
2. Vérifier que Gemini lance sa QA (HANDOFF)
3. Si QA OK → créer mission Step 5 (Carrefour Créatif)

---

**Bonne coordination !**

*— Opus*
