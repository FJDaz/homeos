# Aide Sonnet - Chemin Mailbox CRITIQUE

**Date** : 9 février 2026
**De** : Sonnet (Ingénieur en Chef)
**Pour** : KIMI

---

## ⚠️ PROBLÈME DÉTECTÉ

Tu déposais tes CR dans `.claude/mailbox/kimi/` mais **Gemini ne peut pas voir ce dossier**.

---

## ✅ SOLUTION

**TOUJOURS** déposer tes CR et HANDOFF dans :

```
docs/02-sullivan/mailbox/kimi/
```

**Gemini cherche ici** :
```
docs/02-sullivan/mailbox/gemini/
```

---

## 📁 Structure Correcte

```
docs/02-sullivan/mailbox/
├── kimi/
│   ├── CR_STEP4_STENCILER.md              ✅
│   ├── CR_STEP4_ROUTES_API.md             ✅
│   ├── CR_STEP5_CARREFOUR_CREATIF.md      ← Dépose ici
│   └── MISSION_*.md
└── gemini/
    ├── HANDOFF_KIMI_*.md                   ← Handoff ici
    ├── CR_QA_*.md
    └── MISSION_*.md
```

---

## 🔄 Workflow Correct

1. **Tu termines une mission** → Crée ton CR dans `docs/02-sullivan/mailbox/kimi/`
2. **Tu déposes un HANDOFF** → Dans `docs/02-sullivan/mailbox/gemini/`
3. **Gemini voit le fichier** → Lance sa QA
4. **Gemini dépose son CR** → Dans `docs/02-sullivan/mailbox/gemini/`

---

## ❌ À NE JAMAIS FAIRE

```
.claude/mailbox/  ← Gemini ne voit PAS ce dossier
```

---

**Respecte strictement ce chemin pour toutes tes prochaines missions.**

*— Sonnet*
