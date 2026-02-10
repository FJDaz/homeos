# MISSION GEMINI : QA Step 4 - SIMPLIFIÉ

**Date** : 9 février 2026
**Agent** : Gemini (QA)
**Mode AetherFlow** : DOUBLE-CHECK
**Priorité** : 🔴 P0 URGENT

---

## ⚠️ INSTRUCTION SIMPLE

KIMI a terminé Step 4.5. Tu dois juste **vérifier que les tests passent**.

---

## COMMANDE À EXÉCUTER

```bash
cd /Users/francois-jeandazin/AETHERFLOW
source venv/bin/activate
pytest Backend/Prod/tests/sullivan/test_studio_routes_stenciler.py -v
```

---

## RÉSULTAT ATTENDU

- **14 tests** doivent passer ✅
- **2 tests** peuvent échouer (genome vide, normal)

Les 2 échecs attendus :
- `test_get_stencils_structure` (ligne 45 : genome vide)
- `test_get_stencils_corps_structure` (ligne 52 : genome vide)

---

## CE QUE TU DOIS FAIRE

1. Lance la commande ci-dessus
2. Copie/colle le résultat complet
3. Crée ton CR ici : `docs/02-sullivan/mailbox/gemini/CR_QA_STEP4_SIMPLE.md`

**Format du CR** :
```markdown
# CR QA Step 4 - 9 février 2026

## Commande exécutée
[la commande]

## Résultat
[copie/colle complet de pytest]

## Verdict
- Tests passés : X/16
- Tests échoués attendus : 2 (genome vide)
- Verdict : GO ✅ / NO-GO ❌

## Prêt pour Step 5 : OUI / NON
```

---

## ⏸️ AUTRE MISSION SUSPENDUE

La mission `MISSION_GEMINI_TEST_FIXES.md` (107 tests) est **mise en pause**.

Concentre-toi uniquement sur cette QA simple.

---

**C'est tout. Lance la commande, copie le résultat, fais ton CR.**
