# PROTOCOLE DE VALIDATION VISUELLE HUMAINE

**Version** : 1.0.0
**Date** : 11 février 2026 — 12:30
**Statut** : OBLIGATOIRE
**Conformité** : CONSTITUTION_AETHERFLOW Article 10

---

## 📜 PRINCIPE FONDAMENTAL

**TOUT RENDU VISUEL FRONTEND DOIT ÊTRE VALIDÉ PAR L'HUMAIN DANS LE NAVIGATEUR**

Aucun code frontend ne peut être considéré comme terminé sans validation visuelle explicite par François-Jean Dazin (CTO).

---

## 🚫 INTERDICTIONS ABSOLUES

### Pour KIMI 2.5 (Frontend Lead) :

❌ **INTERDIT** : Dire "le rendu est terminé" sans lancement serveur
❌ **INTERDIT** : Proposer du code HTML/CSS sans démonstration live
❌ **INTERDIT** : Considérer une interface comme validée sans screenshot ou URL
❌ **INTERDIT** : Passer à la tâche suivante sans validation humaine explicite

### Pour Claude Sonnet 4.5 (Backend Lead) :

❌ **INTERDIT** : Modifier du code frontend sans validation visuelle
❌ **INTERDIT** : Proposer des corrections CSS/HTML sans test navigateur
❌ **INTERDIT** : Accepter un rendu sur parole sans preuve visuelle

---

## ✅ WORKFLOW OBLIGATOIRE

### Phase 1 : Développement
```
KIMI écrit le code → Sauvegarde dans Frontend/
```

### Phase 2 : Lancement Serveur
```
KIMI fournit la commande exacte de lancement
Exemple: cd Frontend/3. STENCILER && python3 server_9998_v2.py
```

### Phase 3 : Validation Humaine
```
François-Jean ouvre http://localhost:[PORT] dans le navigateur
François-Jean inspecte visuellement le rendu
François-Jean donne son verdict : ✅ VALIDÉ ou ❌ À CORRIGER
```

### Phase 4 : Itération (si nécessaire)
```
Si ❌ → KIMI corrige → Retour Phase 2
Si ✅ → Passe à la tâche suivante
```

---

## 🎯 COMMANDES DE LANCEMENT STANDARD

### Stenciler (Port 9998)
```bash
cd "Frontend/3. STENCILER"
python3 server_9998_v2.py
# Ouvrir: http://localhost:9998
```

### Viewer Genome (Port 9999)
```bash
cd Frontend
python3 -m http.server 9999
# Ouvrir: http://localhost:9999/studio.html
```

### Test Widget Sullivan (Port 8000)
```bash
cd Frontend
python3 -m http.server 8000
# Ouvrir: http://localhost:8000/sullivan-super-widget.html
```

---

## 📋 CHECKLIST DE VALIDATION VISUELLE

Avant de marquer une tâche frontend comme complétée, KIMI doit fournir :

1. **✅ Commande de lancement serveur** (copiable/collable)
2. **✅ Port utilisé** (ex: 9998)
3. **✅ URL complète** (ex: http://localhost:9998)
4. **✅ Fichier HTML principal** (si applicable)
5. **✅ Description de ce qui doit être visible** (pour faciliter la validation)

### Template de Message KIMI

```
🚀 RENDU PRÊT POUR VALIDATION HUMAINE

Fichiers modifiés :
- Frontend/3. STENCILER/server_9998_v2.py
- Frontend/2. GENOME/genome_reference.json

Commande de lancement :
cd "Frontend/3. STENCILER" && python3 server_9998_v2.py

URL : http://localhost:9998

Ce qui doit être visible :
- Bande horizontale avec 4 Corps en preview (20%)
- Noms : Studio, Backend, Frontend, Deploy
- Couleurs : respectant design_principles.json
- Drag & drop fonctionnel vers canvas

En attente de validation humaine ⏳
```

---

## 🔄 WORKFLOW AVEC SCREENSHOTS (Optionnel)

Si François-Jean n'est pas disponible immédiatement, KIMI peut :

1. Lancer le serveur localement (si environnement le permet)
2. Prendre un screenshot du rendu
3. Sauvegarder dans `Frontend/screenshots/[date]_[feature].png`
4. Informer François-Jean avec le screenshot pour validation asynchrone

**Note** : Le screenshot ne remplace PAS la validation navigateur, c'est une pré-validation.

---

## 📊 SUIVI DES VALIDATIONS

Tenir un registre dans `Frontend/4. COMMUNICATION/VALIDATIONS.md` :

| Date | Feature | URL | Port | Statut | Validé par |
|------|---------|-----|------|--------|------------|
| 2026-02-11 | Preview 4 Corps | http://localhost:9998 | 9998 | ⏳ En attente | - |

---

## 🚨 CAS D'URGENCE

Si le serveur ne démarre pas ou le rendu est cassé :

1. **NE PAS PANIQUER** - C'est normal en développement
2. KIMI documente l'erreur exacte (stacktrace, console)
3. KIMI propose une correction
4. Retour Phase 2 (relance serveur)

**Règle d'or** : Mieux vaut 10 itérations validées qu'un seul rendu parfait non testé.

---

## 📖 RÉFÉRENCE CONSTITUTIONNELLE

**Article 10 : Validation Visuelle Obligatoire**

> Tout artefact visuel produit par le Système de Rendu (Frontend) DOIT faire l'objet d'une validation humaine via navigateur avant d'être considéré comme terminé. Le Backend Lead et le Frontend Lead sont co-responsables du respect de cette règle.

**Clause d'éternité** : Cette règle est INALTÉRABLE.

---

## 💡 BONNES PRATIQUES

1. **Lancer tôt, lancer souvent** : Valider visuellement dès qu'un composant est fonctionnel (même incomplet)
2. **Incrémenter progressivement** : Ne pas attendre d'avoir "tout fini" pour montrer
3. **Documenter les écarts** : Si le rendu diffère de la spec, le noter explicitement
4. **Partager les URLs** : Toujours inclure l'URL complète dans les messages

---

## 🔗 INTÉGRATION AVEC CANAL KIMI ↔ CLAUDE

Chaque validation visuelle doit être documentée dans :
- `Frontend/4. COMMUNICATION/CANAL_CLAUDE_KIMI.md`
- Avec statut : 🎨 RENDU PRÊT ou ✅ RENDU VALIDÉ

---

**Dernière mise à jour** : 11 février 2026 — 12:30
**Prochaine révision** : Après première validation visuelle réelle

---

*Protocole vivant — S'améliore avec l'expérience — Version 1.0.0*
