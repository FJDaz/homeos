# Support BYOK/BYOC dans Homeos

**Date** : 27 janvier 2025  
**Statut** : ✅ **IMPLÉMENTÉ**

---

## 🎯 Concept BYOK/BYOC

**BYOK** = Bring Your Own Key (Apportez votre propre clé API)  
**BYOC** = Bring Your Own Cursor/Claude (Utilisez votre abonnement existant)

Les utilisateurs peuvent utiliser **l'une ou l'autre** de ces options selon ce qu'ils possèdent :

### **Option 1 : BYOK (Clé API Claude)**
- Utilisez votre propre **clé API Claude** (pay-per-use)
- Coûts : ~$0.021 par plan (à votre charge)
- Qualité : Excellente, contrôle total

### **Option 2 : BYOC (Abonnement Cursor Pro)**
- Utilisez votre **abonnement Cursor Pro** existant (20-30€/mois)
- Coûts : 0€ supplémentaire (utilise votre abonnement)
- Qualité : Excellente, via Claude Code

### **Option 3 : BYOC (Abonnement Claude Pro/MAX)**
- Utilisez votre **abonnement Claude.ai** existant (Claude Pro ou Claude MAX)
- Coûts : Utilise votre quota d'abonnement Claude.ai
- Qualité : Excellente, via API Claude avec votre abonnement

**Important** : Ce sont des **options parallèles**, pas des alternatives mutuellement exclusives. Vous pouvez choisir celle qui correspond à ce que vous possédez déjà. Si vous n'avez aucune de ces options, le système utilise Gemini 3 Pro par défaut (inclus dans l'abonnement Homeos).

---

## 📋 Support dans les Offres

### **Homeos PLAY (5€/mois) - "BYOK Intelligent"**

**Par défaut** : Gemini 3 Pro (économique, inclus)

**Options** (vous pouvez choisir l'une ou l'autre selon ce que vous possédez) :
- ✅ **BYOK** : Utiliser sa propre clé Claude API (coûts Claude à la charge de l'utilisateur, ~$0.021/plan)
- ✅ **BYOC (Cursor Pro)** : Utiliser son abonnement Cursor Pro (gratuit si déjà abonné, 20-30€/mois)
- ✅ **BYOC (Claude Pro/MAX)** : Utiliser son abonnement Claude.ai (utilise votre quota d'abonnement)

**Valeur** : "Soit 3x plus de plans qu'avec Claude seul"

### **Homeos CREATE (9,90€/mois)**

**Par défaut** : Gemini 3 Pro (économique, inclus)

**Options d'inférence par abonnement** :

#### **Solution #1 : Cursor Rules (0 installation utilisateur)**
- **Gratuit** si vous avez déjà Cursor Pro
- Ajoutez `homeos-rules.md` dans votre repo
- Tapez "HomeOS Phase X" → Plan généré automatiquement via Claude Code
- **Usage** : 500-1000 tâches/mois avec votre abonnement Cursor Pro existant
- **Coût** : 0€ supplémentaire (utilise votre Cursor Pro)

#### **Solution #2 : HomeOS Studio Web (Idéal commercial)**
- **Prix** : 9,90€/mois (accès web + 500 plans Claude Code optimisés)
- Portail web unique (`homeos.studio`)
- Connexion Cursor Pro via OAuth (1-clic)
- Génération de plans via Claude Code en arrière-plan
- Historique des plans, métriques, analytics
- **Valeur** : Transforme vos 500 messages Claude Pro en 1000+ tâches complètes/mois

#### **Solution #3 : CLI Magic Command (Mac uniquement)**
- Installation globale : `npm install -g @homeos/cli`
- Commande unique : `homeos plan phase1`
- Utilise votre Cursor Pro existant (spawn Cursor headless)
- **Coût** : 0€ supplémentaire (utilise votre Cursor Pro)

**Options d'inférence (vous pouvez choisir l'une ou l'autre)** :

#### **Option A : BYOK (Clé API Claude)**
- ✅ Utiliser sa propre clé Claude API
- Coûts : ~$0.021 par plan (à votre charge, pay-per-use)
- Qualité : Excellente, contrôle total

#### **Option B : BYOC (Abonnement Cursor Pro)**
- ✅ Utiliser son abonnement Cursor Pro existant
- Coûts : 0€ supplémentaire (utilise votre abonnement 20-30€/mois)
- Qualité : Excellente, via Claude Code
- Solutions : Cursor Rules, Studio Web, ou CLI Magic (voir ci-dessus)

#### **Option C : BYOC (Abonnement Claude Pro/MAX)**
- ✅ Utiliser son abonnement Claude.ai existant (Claude Pro ou Claude MAX)
- Coûts : Utilise votre quota d'abonnement Claude.ai
- Qualité : Excellente, via API Claude avec votre abonnement

---

## 🔧 Implémentation Technique

### **1. Détection Automatique**

Le système détecte automatiquement les clés API disponibles :

```python
# FallbackManager.check_api_keys_available()
availability = {
    "claude_api": bool(settings.anthropic_api_key valide),
    "gemini": bool(settings.google_api_key valide),
    "deepseek": bool(settings.deepseek_api_key valide),
    "claude_code": True  # Toujours disponible (Cursor)
}
```

### **2. Sélection du Planificateur**

**Pour les clients** :
- Si pas de clé Claude ni d'abonnement → Gemini par défaut (économique, inclus)
- Si a une clé Claude API → Peut choisir Claude API (BYOK)
- Si a un abonnement Cursor Pro → Peut choisir Claude Code (BYOC)
- Si a un abonnement Claude Pro/MAX → Peut choisir Claude API avec son abonnement (BYOC)
- **Les options sont parallèles** : vous pouvez utiliser celle que vous possédez déjà

**Pour vous (développeur)** :
- Choix dans le chat : "utilise ma clé Claude" → BYOK
- Choix dans le chat : "utilise Cursor" → BYOC
- Choix dans le chat : "utilise Gemini" → Planificateur par défaut

### **3. Détection dans le Chat**

La fonction `detect_planner_choice()` dans `claude_helper.py` détecte :

- **BYOK (Clé API)** : "ma clé claude", "byok", "claude api", "utilise ma clé claude"
- **BYOC (Cursor Pro)** : "cursor", "mon cursor", "mon abonnement cursor", "byoc", "claude code", "utilise cursor"
- **BYOC (Claude Pro/MAX)** : "mon abonnement claude", "claude pro", "claude max", "mon claude.ai"
- **Gemini** : "gemini", "utilise gemini"
- **DeepSeek** : "deepseek", "utilise deepseek"

---

## 💰 Coûts et Facturation

### **Option A : Avec BYOK (Clé API Claude)**

- **Coût Homeos** : 5€/mois (PLAY) ou 9,90€/mois (CREATE)
- **Coût Claude API** : À la charge de l'utilisateur (~$0.021 par plan, pay-per-use)
- **Avantage** : Qualité maximale, contrôle total, pas besoin d'abonnement
- **Pour qui** : Utilisateurs qui préfèrent payer à l'usage plutôt qu'un abonnement mensuel

### **Option B : Avec BYOC (Abonnement Cursor Pro) - Solutions d'abonnement**

#### **Solution #1 : Cursor Rules (Gratuit)**
- **Coût Homeos** : 5€/mois (PLAY) ou 9,90€/mois (CREATE)
- **Coût Cursor Pro** : Déjà payé par l'utilisateur (20-30€/mois)
- **Avantage** : Planification gratuite (via Cursor), qualité maximale, 0 installation
- **Usage** : Tapez "HomeOS Phase X" → Plan généré automatiquement

#### **Solution #2 : HomeOS Studio Web (9,90€/mois)**
- **Coût Homeos** : 9,90€/mois (CREATE)
- **Coût Cursor Pro** : Déjà payé par l'utilisateur (20-30€/mois)
- **Avantage** : Portail web, OAuth Cursor Pro, historique, métriques
- **Valeur** : Multiplie l'efficacité de votre Cursor Pro par 2x (500 messages → 1000+ tâches)

#### **Solution #3 : CLI Magic Command (Gratuit)**
- **Coût Homeos** : 5€/mois (PLAY) ou 9,90€/mois (CREATE)
- **Coût Cursor Pro** : Déjà payé par l'utilisateur (20-30€/mois)
- **Avantage** : Commande unique `homeos plan phase1`, Mac uniquement

### **Option C : Avec BYOC (Abonnement Claude Pro/MAX)**

- **Coût Homeos** : 5€/mois (PLAY) ou 9,90€/mois (CREATE)
- **Coût Claude.ai** : Utilise votre quota d'abonnement Claude Pro ou Claude MAX existant
- **Avantage** : Qualité maximale, utilise votre abonnement Claude.ai déjà payé
- **Pour qui** : Utilisateurs qui ont déjà un abonnement Claude Pro ou Claude MAX

### **Par défaut (Sans BYOK/BYOC)**

- **Coût Homeos** : 5€/mois (PLAY) ou 9,90€/mois (CREATE)
- **Coût planificateur** : Inclus (Gemini 3 Pro)
- **Avantage** : Tout inclus, pas de coûts supplémentaires
- **Pour qui** : Utilisateurs qui n'ont pas de clé API Claude ni d'abonnement Cursor/Claude

---

## 📊 Comparaison

| Option | Coût Homeos | Coût Planificateur | Qualité | Contrôle | Installation |
|--------|-------------|-------------------|---------|----------|--------------|
| **Par défaut (Gemini)** | 5€/mois | Inclus | Très bonne | Homeos | Aucune |
| **BYOK (Claude API)** | 5€/mois | ~$0.021/plan | Excellente | Utilisateur | Clé API |
| **BYOC Cursor #1 (Rules)** | 5€/mois | Déjà payé (20-30€/mois) | Excellente | Utilisateur | 0 installation |
| **BYOC Cursor #2 (Studio)** | 9,90€/mois | Déjà payé (20-30€/mois) | Excellente | Utilisateur | Web OAuth |
| **BYOC Cursor #3 (CLI)** | 5€/mois | Déjà payé (20-30€/mois) | Excellente | Utilisateur | npm install |
| **BYOC Claude Pro/MAX** | 5€/mois | Utilise quota abonnement | Excellente | Utilisateur | Clé API abonnement |

---

## 🎯 Messages Marketing

### **Pour utilisateurs SANS Claude/Cursor**
> "Avec Homeos, obtenez une planification de **qualité Claude** à **70% de réduction**. Notre moteur Gemini 3 Pro est classé #2 mondial, juste derrière Claude."

### **Pour utilisateurs AVEC Cursor Pro**
> "Vous payez déjà 20-30€/mois pour Cursor Pro ? **Multipliez son efficacité par 2-3x**. Homeos utilise Claude Code uniquement pour la planification critique et automatise le reste avec des modèles 10x moins chers. **3 solutions** : Cursor Rules (gratuit, 0 installation), HomeOS Studio Web (9,90€/mois, portail complet), ou CLI Magic (gratuit, Mac). Utilisez votre abonnement Cursor Pro existant (BYOC)."

### **Pour utilisateurs AVEC Claude Pro/MAX**
> "Vous payez déjà pour Claude Pro ou Claude MAX ? **Utilisez votre quota d'abonnement** pour la planification premium. Homeos utilise Claude uniquement pour la planification critique et automatise le reste avec des modèles 10x moins chers. Utilisez votre abonnement Claude.ai existant (BYOC) ou votre clé API Claude (BYOK)."

### **Pour utilisateurs AVEC clé API Claude**
> "Vous avez une clé API Claude ? **Utilisez-la directement** pour une planification premium. Coût : ~$0.021 par plan (pay-per-use). Qualité maximale, contrôle total. Utilisez votre clé Claude API (BYOK)."

---

## ✅ Implémentation Complète

- ✅ Détection automatique des clés API
- ✅ Support BYOK (Claude API - clé pay-per-use)
- ✅ Support BYOC (Cursor Pro - abonnement)
- ✅ Support BYOC (Claude Pro/MAX - abonnement)
- ✅ Détection dans le chat (distinction entre BYOK et BYOC)
- ✅ Fallback automatique si échec
- ✅ Documentation dans PRD Homeos
- ✅ Options parallèles (pas mutuellement exclusives)

---

**Dernière mise à jour** : 27 janvier 2025
