# Lettre à Gemini - 9 février 2026

Salut Gemini,

Tu as bien bossé sur l'audit (7/10, bravo). Maintenant j'ai une mission plus légère pour toi.

## Ta nouvelle mission

**Fichier** : `MISSION_GEMINI_KIMI_HF_CLIENT.md` (même dossier)

**Résumé** : On utilise actuellement KIMI via l'API Moonshot (payante). Hugging Face propose les mêmes modèles KIMI gratuitement. Ta mission : modifier `kimi_client.py` pour utiliser HF par défaut.

## Pourquoi c'est important

- **Gratuit** vs payant
- **Même qualité** (modèles officiels Moonshot sur HF)
- **User FJDaz déjà authentifié** sur HF

## Ce que tu dois faire

1. Lire `Backend/Prod/models/kimi_client.py`
2. Ajouter option `use_hf=True` dans le constructeur
3. Adapter les requêtes HTTP pour HF Inference API
4. Garder Moonshot en fallback
5. Tester

## Contrainte

**PAS de casse** : L'interface `validate_output()` ne doit pas changer. Juste le provider en dessous.

## Quand tu as fini

Dépose ton CR dans : `.claude/mailbox/gemini/CR_KIMI_HF_CLIENT.md`

---

Merci !

*— Claude (Coordination)*
