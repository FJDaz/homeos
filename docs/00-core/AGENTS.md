# Guide pour les Agents IA (Claude, Cursor, Kimi)

**Projet**: AetherFlow / Sullivan  
**Version**: 2.2  
**Date**: 2 février 2026

---

## ⚠️ RÈGLE D'OR : Implémentation par Mode

**AVANT TOUTE IMPLÉMENTATION**, consulter le skill:
```
.cursor/skills/aetherflow-modes/SKILL.md
```

> **Principe**: Toujours implémenter via l'intermédiaire d'un mode AetherFlow.  
> **Interdit**: Appeler directement les APIs LLM (Gemini, Groq, DeepSeek, Claude) sans passer par le router approprié.

---

## 🎯 Les Modes Disponibles

| Mode | Flag | Usage | Router/Provider |
|------|------|-------|-----------------|
| **PROTO** | `-q` | Rapide, POC, utilitaires | Groq |
| **PROD** | `-f` | Production, Surgical Edit | AgentRouter |
| **FRONTEND** | `-frd` | Frontend intelligent | FrontendRouter |
| **DESIGNER** | `designer` | Analyse design/maquettes | Gemini Vision |
| **DEV** | `dev` | Backend → Frontend | AgentRouter |
| **UPLOAD** | `upload` | Préprocessing images | Local (PIL) |

---

## ✅ Checklist Pré-Implémentation

- [ ] **Lire le skill** `.cursor/skills/aetherflow-modes/SKILL.md`
- [ ] **Identifier le mode** approprié selon l'algorithme de décision
- [ ] **Utiliser le mode** plutôt que d'appeler directement un LLM
- [ ] **Respecter les signatures** des méthodes de mode

---

## 📋 Décision Rapide

```
Frontend/UI/Visuel ?
  ├─ OUI → Analyse d'image ? 
  │        ├─ OUI → DesignerMode
  │        └─ NON → FrontendMode (-frd)
  │
  └─ NON → Modification fichier Python existant ?
           ├─ OUI → PROD (-f) avec Surgical Edit
           └─ NON → Rapide/utilitaire ? 
                    ├─ OUI → PROTO (-q)
                    └─ NON → PROD (-f)
```

---

## 📚 Documentation Clé

- **Skill Modes**: `.cursor/skills/aetherflow-modes/SKILL.md`
- **Mode emploi**: `docs/02-sullivan/MODE_EMPLOI_SULLIVAN_GENOME.md`
- **FrontendMode**: `docs/02-sullivan/FRONTEND_MODE.md`
- **Guide rapide**: `docs/01-getting-started/GUIDE_RAPIDE_AETHERFLOW.md`

---

## 🚨 Anti-Patterns (INTERDITS)

❌ `GeminiClient.generate()` direct pour du code → ✅ Utiliser `AgentRouter`  
❌ `GroqClient.generate()` direct pour dialogue → ✅ Utiliser `FrontendMode.dialogue()`  
❌ Implémenter preprocessing image from scratch → ✅ Utiliser `image_preprocessor.py`  
❌ Modifier fichier Python sans validation → ✅ Utiliser `-f` (Surgical Edit)  

---

**Mémo**: "Pas de code sans mode, pas de mode sans routeur."
