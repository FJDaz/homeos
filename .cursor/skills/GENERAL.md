# 📋 RÈGLES GÉNÉRALES DES SKILLS CURSOR

**Version** : 1.0  
**Date** : 3 février 2026  
**Portée** : Tous les skills du projet

---

## 🎯 PRINCIPE FONDAMENTAL

> "Un skill n'est utile que s'il est utilisé systématiquement et correctement."

Ces règles s'appliquent à **tous** les skills définis dans `.cursor/skills/`.

---

## 📁 STRUCTURE DES SKILLS

### Arborescence obligatoire

```
.cursor/skills/
├── [nom-skill]/
│   ├── SKILL.md          # Documentation principale (OBLIGATOIRE)
│   ├── CHECKLIST.md      # Checklist exécutable (OPTIONNEL mais recommandé)
│   └── TEMPLATES/        # Templates réutilisables (OPTIONNEL)
│       └── *.md
└── GENERAL.md            # Ce fichier - règles transverses
```

### Règles de nommage

- **Nom du dossier** : `kebab-case` (ex: `kimi-binome`, `aetherflow-modes`)
- **Fichier principal** : toujours `SKILL.md`
- **Checklist** : toujours `CHECKLIST.md`
- **Templates** : `UPPERCASE_SNAKE_CASE.md` ou descriptif

---

## 🚨 UTILISATION OBLIGATOIRE

### Quand consulter un skill ?

| Situation | Skill à utiliser | Obligatoire |
|-----------|------------------|-------------|
| Implémentation HomeOS/Sullivan | `kimi-binome/` | ✅ OUI |
| Choix mode AetherFlow | `aetherflow-modes/` | ✅ OUI |
| Test agent IA | `test-mandatory/` | ✅ OUI |
| Autre tâche | Aucun / Contexte | ❌ Non |

### Comment utiliser un skill ?

1. **Lire** `SKILL.md` en entier avant toute action
2. **Copier** `CHECKLIST.md` au début de la réponse
3. **Remplir** tous les champs obligatoires
4. **Suivre** le workflow décrit
5. **Valider** avec l'utilisateur avant implémentation

---

## 📝 FORMAT DES SKILLS

### SKILL.md - Sections obligatoires

```markdown
# [Titre du skill]

**Version** : X.Y.Z
**Date** : JJ/MM/AAAA
**Statut** : [OBLIGATOIRE/OPTIONNEL/DÉPRÉCIÉ]

## 🚨 RÈGLE D'OR (si applicable)
[La règle la plus importante - violation = rejet]

## 📋 CHECKLIST (si applicable)
[Liste à cocher obligatoire]

## [Contenu spécifique au skill]
...

## 🔗 LIENS
[Références croisées]
```

### CHECKLIST.md - Structure

```markdown
# ✅ CHECKLIST [NOM]

## PRÉ-ACTION
- [ ] Item 1
- [ ] Item 2

## POST-ACTION
- [ ] Item 3
- [ ] Item 4

## TEMPLATES
[Voir TEMPLATES/*.md]
```

---

## 🔄 MAINTENANCE DES SKILLS

### À chaque modification de code

Si vous modifiez une architecture/pattern couvert par un skill :

1. **Mettre à jour** le skill concerné
2. **Incrémenter** la version (semver)
3. **Documenter** les changements
4. **Notifier** l'équipe

### Versioning (Semver)

- **MAJEUR (X)** : Changement breaking dans le workflow
- **MINEUR (Y)** : Ajout fonctionnalité, règle optionnelle
- **PATCH (Z)** : Correction, clarification, exemple

### Exemple

```
v1.0.0 → v1.1.0 : Ajout d'une règle optionnelle
v1.1.0 → v1.1.1 : Correction typo, ajout exemple
v1.1.1 → v2.0.0 : Changement workflow obligatoire
```

---

## ⚠️ ERREURS À ÉVITER

### ❌ Mauvaises pratiques

- Ignorer un skill marqué "OBLIGATOIRE"
- Modifier un skill sans mettre à jour la version
- Copier une checklist sans la remplir
- Sauter des étapes du workflow
- Implémenter sans validation "GO"

### ✅ Bonnes pratiques

- Lire le skill systématiquement
- Remplir la checklist honnêtement
- Valider chaque étape avant de passer à la suivante
- Demander clarification si ambiguïté
- Mettre à jour les skills quand nécessaire

---

## 🎓 FORMATION

### Nouveau contributeur ?

1. Lire `GENERAL.md` (ce fichier)
2. Lire `kimi-binome/SKILL.md`
3. Lire `aetherflow-modes/SKILL.md`
4. Faire un exercice test avec supervision

### Validation compétence

Un contributeur est validé quand :
- ✅ Il applique correctement les skills 3 fois de suite
- ✅ Il met à jour les skills quand nécessaire
- ✅ Il forme d'autres contributeurs

---

## 🔍 AUDIT ET QUALITÉ

### Vérification automatique

Les skills peuvent être audités pour :
- Complétude des sections obligatoires
- Cohérence des liens
- Version à jour
- Checklist exécutable

### Score de conformité

| Critère | Poids |
|---------|-------|
| SKILL.md complet | 40% |
| CHECKLIST.md présent | 30% |
| TEMPLATES pertinents | 20% |
| Version à jour | 10% |

---

## 📞 SUPPORT

### Questions fréquentes

**Q : Je ne comprends pas une règle du skill ?**  
R : Demandez clarification à l'utilisateur avant de continuer.

**Q : Le skill semble obsolète ?**  
R : Vérifiez la date et la version, proposez une mise à jour.

**Q : Peut-on ignorer un skill dans certains cas ?**  
R : Seulement si explicitement marqué "OPTIONNEL" ou avec approbation.

**Q : Comment proposer un nouveau skill ?**  
R : Créez-le suivant ce template et soumettez-le pour validation.

---

## 📝 HISTORIQUE DES MODIFICATIONS

| Date | Version | Modification | Auteur |
|------|---------|--------------|--------|
| 2026-02-03 | 1.0 | Création initiale | Kimi |

---

**Mainteneur** : Équipe AetherFlow  
**Dernière mise à jour** : 3 février 2026

---

*"Un skill bien utilisé vaut mieux qu'une documentation parfaite ignorée."*
