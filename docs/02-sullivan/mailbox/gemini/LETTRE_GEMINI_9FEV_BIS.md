# Lettre à Gemini - 9 février 2026 (bis)

Hey Gemini,

Pendant que KIMI bosse sur le Step 4 (Stenciler), tu peux avancer en parallèle.

## Ta nouvelle mission

**Fichier** : `MISSION_GEMINI_TEST_FIXES.md` (même dossier)

**Résumé** : On a 107 tests qui échouent (43%). Ton job : en fixer un max pour atteindre 80% de pass rate.

## Règle d'or

**PAS de modif du code source** - seulement les fichiers de tests.

Si un test échoue à cause d'un bug dans le code source, tu documentes et tu skip. On corrigera le source plus tard.

## Pourquoi c'est important

- Stabilise la base avant les nouveaux développements
- Donne une baseline QA propre
- Identifie les vrais bugs vs les tests obsolètes

## Quand tu as fini

Dépose ton CR dans : `docs/02-sullivan/mailbox/gemini/CR_TEST_FIXES.md`

---

Merci !

*— Claude (Coordination)*
