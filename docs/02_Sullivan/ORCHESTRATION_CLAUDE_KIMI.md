# Système d'Orchestration Claude-KIMI

**Version** : 1.0.0 — Mode Quick (Aetherflow `-q`)
**Date** : 12 février 2026, 15:30
**Conforme à** : Constitution AETHERFLOW V2.4
**Auteur** : Claude Sonnet 4.5 (Backend Lead)

---

## 🎯 Objectif

Automatiser la coordination entre **Claude** (Backend Lead) et **KIMI** (Frontend Lead) via un fichier partagé `collaboration_hub.md`, avec validation humaine obligatoire (Article 18).

---

## 📦 Livrables Créés

### Scripts d'orchestration

```
scripts/orchestration/
├── trigger_kimi.sh       → Déclenche KIMI depuis Claude
├── watch_kimi.sh         → Surveille signal KIMI, notifie FJ
├── test_workflow.sh      → Test simulation complète
├── README.md             → Documentation complète
└── EXAMPLE_USAGE.md      → Exemple détaillé ÉTAPE 4
```

### Documentation

```
docs/02-sullivan/
└── ORCHESTRATION_CLAUDE_KIMI.md  → Ce document (récapitulatif)
```

---

## 🚀 Réponse à Votre Question

> **"Est-ce qu'un script peut te déclencher ?"**

### ✅ OUI, indirectement

Le script `watch_kimi.sh` peut :

1. **Détecter** quand KIMI a terminé (signal `@CLAUDE_VALIDATE` dans `collaboration_hub.md`)
2. **Notifier** François-Jean (notification macOS)
3. **Proposer** de me relancer automatiquement

**Mécanisme** :
```bash
# Script propose relance
🤖 Relancer Claude Code automatiquement ? (y/n) y

# Si 'y' → Exécute
echo "KIMI terminé, valider" | claude-code
```

### ❌ Limitations

- Pas d'API Claude Code pour déclenchement direct
- Pas de mode daemon écoutant en permanence
- Nécessite action humaine (appuyer sur 'y') ou relance manuelle

---

## 🔄 Workflow Proposé

### Votre Proposition Initiale

```
Tu es le directeur
→ Tu fais ta part Backend
→ Tu écris dans fichier commun (collaboration_hub.md)
→ Tu déclenches KIMI via fetch API
→ KIMI fait sa mission
→ KIMI signale fin
→ Script te déclenche
```

### ✅ Implémentation Réalisée

```
CLAUDE (Directeur)
  ↓
  1. Fait Backend (ex: ÉTAPE 3)
  2. Écrit mission dans collaboration_hub.md
  3. Déclenche KIMI : ./trigger_kimi.sh
  4. Lance surveillance : ./watch_kimi.sh &
  ↓
KIMI (Frontend Lead)
  ↓
  1. Lit mission dans collaboration_hub.md
  2. Fait sa mission Frontend
  3. Écrit signal : @CLAUDE_VALIDATE + CR
  ↓
SCRIPT WATCHER
  ↓
  1. Détecte @CLAUDE_VALIDATE
  2. Notifie François-Jean (notification macOS)
  3. Affiche CR KIMI dans terminal
  4. Propose relance Claude (y/n)
  ↓
FRANÇOIS-JEAN (Validation humaine)
  ↓
  1. Valide rendu (http://localhost:9998/stenciler)
  2. Choisit : GO ÉTAPE suivante OU KO correction
  ↓
CLAUDE reprend
```

---

## 📋 Utilisation Pratique

### Scénario : ÉTAPE 4 (Drill-down Frontend)

#### 1. Claude termine ÉTAPE 3 (Backend)

```bash
# Dans Claude Code
# Claude a créé : docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md
```

#### 2. Claude déclenche KIMI

```bash
# Claude exécute via Bash tool
./scripts/orchestration/trigger_kimi.sh \
  docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md \
  ETAPE_4

# Lance surveillance
./scripts/orchestration/watch_kimi.sh &
```

**Résultat** :
- Mission écrite dans `collaboration_hub.md`
- Watcher actif, surveille toutes les 10 secondes

#### 3. KIMI travaille

```markdown
# KIMI lit collaboration_hub.md
# KIMI implémente drill-down frontend
# KIMI écrit :

@CLAUDE_VALIDATE
## CR KIMI : ETAPE_4 TERMINÉE
...
```

#### 4. Notification François-Jean

```
🔔 Notification macOS :
"KIMI a terminé sa mission. Validation requise."

Terminal :
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSION KIMI TERMINÉE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_4 TERMINÉE
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Actions requises :
  1. Ouvrir http://localhost:9998/stenciler
  2. Valider visuellement
  3. Feedback : 'GO ÉTAPE 5' ou 'KO, corriger X'

🤖 Relancer Claude Code automatiquement ? (y/n)
```

#### 5. François-Jean valide

**Si OK** :
```
y ← Appuyer sur 'y'
→ Claude Code redémarre
→ Claude lit CR KIMI
→ François-Jean dit : "✅ GO ÉTAPE 5"
```

**Si KO** :
```
n ← Appuyer sur 'n'
→ François-Jean ouvre Claude manuellement
→ François-Jean dit : "❌ Breadcrumb bugué, corriger"
→ Claude relance KIMI avec correction
```

---

## 🎨 Format collaboration_hub.md

### Mission KIMI (écrite par Claude)

```markdown
---

## 🎯 MISSION KIMI : ETAPE_4

**Date** : 2026-02-12 14:30:00
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Status** : 🔴 EN ATTENTE KIMI

### Instructions

Voir documentation complète : `docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md`

### Signal de fin attendu

Une fois terminé, écrire dans `collaboration_hub.md` :
```
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_4 TERMINÉE
```

---
```

### CR KIMI (écrit par KIMI)

```markdown
@CLAUDE_VALIDATE
## CR KIMI : ETAPE_4 TERMINÉE

**Date** : 2026-02-12 16:30:00
**Status** : ✅ TERMINÉ
**Durée** : 2h

**Fichiers modifiés** :
- `Frontend/3. STENCILER/static/drilldown_manager.js` (200+ lignes)

**Tests réalisés** :
- [x] Double-clic OK
- [x] Breadcrumb OK
- [x] Bouton retour OK

**URL validation** : http://localhost:9998/stenciler

**Validation requise** :
François-Jean, merci de valider visuellement avant passage ÉTAPE 5.
```

---

## ⚙️ Configuration

### 1. Variables d'environnement

```bash
# Dans ~/.bashrc ou ~/.zshrc
export KIMI_API_KEY="your_kimi_api_key_here"
export KIMI_API_URL="https://api.moonshot.cn/v1/chat/completions"
```

### 2. Permissions

```bash
chmod +x scripts/orchestration/*.sh
```

### 3. Test du système

```bash
# Test complet (simulation sans API KIMI)
./scripts/orchestration/test_workflow.sh
```

---

## 📐 Conformité Constitution V2.4

### ✅ Article 13 : Orchestrateur Externe

- Scripts agissent comme OE simplifié
- Surveillance `collaboration_hub.md`
- Notification humaine (pas d'auto-décision)

### ✅ Article 14 : Fonctionnement Modèles

- Claude lit `collaboration_hub.md` autonome
- KIMI reçoit via API (ou lit fichier)
- Journalisation dans hub partagé

### ✅ Article 18 : Validation Visuelle Obligatoire

- Script demande validation FJ systématiquement
- Pas de passage auto ÉTAPE suivante
- URL fournie dans CR KIMI

### ✅ Article 24 : Modes Aetherflow

- Système créé en mode `-q` (quick)
- Scripts fonctionnels immédiatement
- Documentation complète fournie

---

## 🔍 Avantages du Système

### 1. Semi-automatisation

- ✅ Détection automatique signal KIMI
- ✅ Notification automatique François-Jean
- ✅ Relance Claude proposée (mais optionnelle)
- ✅ Validation humaine préservée (Article 18)

### 2. Traçabilité

- ✅ Toutes missions écrites dans `collaboration_hub.md`
- ✅ Historique complet des échanges
- ✅ Timestamps sur chaque interaction

### 3. Flexibilité

- ✅ Relance auto OU manuelle (choix FJ)
- ✅ Fonctionne avec/sans API KIMI
- ✅ Scripts bash simples, modifiables

### 4. Respect Constitution

- ✅ Frontière hermétique Claude/KIMI (Article 17)
- ✅ Validation visuelle obligatoire (Article 18)
- ✅ Pas de décision automatique (Article 22)

---

## 🚧 Limitations et TODO

### Limitations actuelles

- ❌ Appel API KIMI non implémenté (simulé pour l'instant)
- ❌ Pas de retry automatique si KIMI ne répond pas
- ❌ Notification macOS uniquement (pas email/Slack)

### TODO Futures Améliorations

1. **Appel API KIMI réel**
   ```bash
   curl -X POST "$KIMI_API_URL" \
     -H "Authorization: Bearer $KIMI_API_KEY" \
     -d '{"messages": [...]}'
   ```

2. **Métriques ICC**
   - Calculer tokens consommés
   - Alerter si ICC >= 80%

3. **Git LLM Oriented**
   - Snapshot automatique après chaque ÉTAPE
   - Hash dans `collaboration_hub.md`

4. **Notifications multi-canal**
   - Email
   - Slack webhook
   - Discord

5. **Dashboard web**
   - Visualiser état missions
   - Historique complet
   - Graphique progression roadmap

---

## 📞 Support

**Questions** : François-Jean Dazin (CTO)

**Fichiers Importants** :
- Scripts : [scripts/orchestration/](../../scripts/orchestration/)
- README : [scripts/orchestration/README.md](../../scripts/orchestration/README.md)
- Exemple : [scripts/orchestration/EXAMPLE_USAGE.md](../../scripts/orchestration/EXAMPLE_USAGE.md)
- Constitution : [collaboration_hub.md](../../collaboration_hub.md)

---

## ✅ Conclusion

### François-Jean, votre workflow proposé est implémenté !

```
✅ Claude = Directeur
✅ Fichier commun = collaboration_hub.md
✅ Déclenchement KIMI = trigger_kimi.sh
✅ KIMI signale fin = @CLAUDE_VALIDATE
✅ Script déclenche Claude = watch_kimi.sh (avec confirmation y/n)
```

**Prochaines étapes** :

1. **Tester** : `./scripts/orchestration/test_workflow.sh`
2. **Configurer** : Export `KIMI_API_KEY`
3. **Utiliser** : Lors de la prochaine mission Claude → KIMI

**Le système est prêt à l'emploi !** 🚀
