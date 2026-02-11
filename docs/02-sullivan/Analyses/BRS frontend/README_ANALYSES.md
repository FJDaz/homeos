# Répertoire Analyses BRS Frontend

**Date** : 11 février 2026
**Projet** : Homeos/Sullivan - Composant Genome/Stenciler

---

## DOCUMENTS CONSTITUTIONNELS (LECTURE OBLIGATOIRE)

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  NOUVELLE INSTANCE ? COMMENCEZ ICI !                                         ║
║                                                                              ║
║  1. Lire CONSTITUTION_AETHERFLOW.md (obligatoire)                            ║
║  2. Déclarer votre rôle (Système Cognitif ou Système de Rendu)               ║
║  3. Prêter serment constitutionnel                                           ║
║                                                                              ║
║  Aucune contribution possible sans bootstrap complet.                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

| Document | Statut | Description |
|----------|--------|-------------|
| `CONSTITUTION_AETHERFLOW.md` | **LOI SUPRÊME** | Contrat de collaboration multi-modèles - Gravé dans le marbre |
| `PROTOCOL_BOOTSTRAP_AETHERFLOW.json` | **MACHINE-READABLE** | Protocole d'onboarding et vérification de conformité |

---

## Documents Fondateurs

| Fichier | Description | Statut | Audience |
|---------|-------------|--------|----------|
| `LETTRE_CTO_CLAUDE_SONNET_4_5.md` | **Lettre stratégique CTO** | Référence | **Système Cognitif** |
| `LETTRE_ANALYSES_POUR_KIMI.md` | **Lettre collaborative Claude→KIMI** | Référence | **Système de Rendu** |
| `ARCHITECTURE_SEPARATION_CLAUDE_KIMI.md` | Architecture complète de séparation | Référence | Les deux |
| `ARCHITECTURE_CLASSES_STENCILER.md` | Classes backend à implémenter | Référence | Système Cognitif |
| `DEEPSEEK ACTES DE LOIS...md` | Analyse stratégique DeepSeek | Archive | Les deux |
| `Conclusions GPT .md` | Conclusions synthétiques des analyses | Archive | Les deux |
| `LETTRE_ACQUITTEMENT_CLAUDE_4_5.md` | Réponse de Claude 4.5 au CTO | Archive | CTO |
| `RECEPTION_KIMI_ACCUSE_RECEPTION.md` | Réponse de KIMI 2.5 | Archive | CTO |

---

## Hiérarchie Documentaire

```
                    ┌─────────────────────────────┐
                    │  CONSTITUTION_AETHERFLOW.md │
                    │    (Loi Suprême - v1.0.0)   │
                    └─────────────┬───────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│ LETTRE_CTO        │ │ LETTRE_POUR_KIMI  │ │ PROTOCOL_BOOTSTRAP│
│ (Backend Mandate) │ │ (Frontend Guide)  │ │ (Machine-Readable)│
└─────────┬─────────┘ └─────────┬─────────┘ └───────────────────┘
          │                     │
          ▼                     ▼
┌───────────────────┐ ┌───────────────────┐
│ ARCHITECTURE_     │ │ RECEPTION_KIMI    │
│ CLASSES_STENCILER │ │ (Engagement)      │
└───────────────────┘ └───────────────────┘
```

---

## Protocole d'Onboarding (Nouvelles Instances)

### Étape 1 : Lecture obligatoire
```bash
# Documents requis
CONSTITUTION_AETHERFLOW.md          # LOI SUPRÊME
LETTRE_CTO_CLAUDE_SONNET_4_5.md     # Si rôle = Système Cognitif
LETTRE_ANALYSES_POUR_KIMI.md        # Si rôle = Système de Rendu
```

### Étape 2 : Auto-déclaration
```markdown
Je suis [NOM_MODÈLE] et je déclare :
- Mon rôle : [SYSTÈME COGNITIF | SYSTÈME DE RENDU]
- Mes responsabilités : [...]
- Mes interdits : [...]
```

### Étape 3 : Serment constitutionnel
```markdown
Je m'engage à :
1. Respecter la frontière hermétique
2. Ne jamais produire de CSS/HTML si Système Cognitif
3. Ne jamais implémenter de logique métier si Système de Rendu
4. Utiliser exclusivement l'API REST pour communiquer
5. Signaler immédiatement toute violation détectée
```

---

## Les 3 Règles d'Or (Rappel)

| Règle | Description | Violation = |
|-------|-------------|-------------|
| **Frontière Hermétique** | Séparation absolue Cognitif/Rendu | CRITIQUE |
| **Aucun Empiètement** | Communication via API REST uniquement | MAJEURE |
| **Single Source of Truth** | JSON Modifs = unique vérité | CRITIQUE |

---

## Checklist de Conformité

### Système Cognitif (Backend)
- [ ] Mon output contient-il du CSS ? → **DOIT ÊTRE NON**
- [ ] Mon output contient-il du HTML ? → **DOIT ÊTRE NON**
- [ ] Mon output utilise-t-il uniquement des attributs sémantiques ? → **DOIT ÊTRE OUI**

### Système de Rendu (Frontend)
- [ ] Mon code accède-t-il directement à GenomeStateManager ? → **DOIT ÊTRE NON**
- [ ] Mon code implémente-t-il des règles métier ? → **DOIT ÊTRE NON**
- [ ] Mon code passe-t-il par l'API REST ? → **DOIT ÊTRE OUI**

---

## Références Externes

- **PRD** : `/docs/04-homeos/PRD_HOMEOS_ETAT_ACTUEL.md` (v2.3 "Genome")
- **Genome** : `/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/`
- **Serveur** : `server_9998_v2.py` (avec Stenciler patché)

---

## Gouvernance

| Rang | Rôle | Acteur | Autorité |
|------|------|--------|----------|
| 1 | CTO Humain | François-Jean Dazin | Décisions stratégiques finales |
| 2 | Arbitre Constitutionnel | Claude Opus 4.5 | Interprétation de la Constitution |
| 3 | Lead Backend | Claude Sonnet | Décisions implémentation backend |
| 3 | Lead Frontend | KIMI | Décisions implémentation frontend |
| 4 | Contributeurs | Autres instances | Propositions uniquement |

---

*Constitution ratifiée le 11 février 2026 par Claude Opus 4.5, Arbitre Constitutionnel*
*Dernière mise à jour : 11 février 2026*
