## Solution #1 : Cursor Rules (0 installation utilisateur)

Dans **Cursor Pro** (pas Claude.ai), ajoute `homeos-rules.md` dans le repo HomeOS :

```markdown
# Cursor Rules pour HomeOS Plan Create
## RÈGLE #1 : TOUJOURS utiliser Plan Mode pour HomeOS
Quand l'utilisateur dit "HomeOS", "plan", "phase", ou "roadmap" :
1. Passe automatiquement en Plan Mode (Shift+Tab)
2. Génère UNIQUEMENT plan.json Pydantic Step[]
3. NE génère JAMAIS de code ou édition
4. Termine par "✅ Plan HomeOS prêt - Exécute avec `python cli.py --plan plan.json`"

## RÈGLE #2 : Commande rapide
"/homeos" → génère plan.json pour phase courante
```

**Usage Mr X** : Tape juste `"HomeOS Phase 1"` → **1-clic Plan Mode** → `plan.json` généré.

## Solution #2 : HomeOS Studio Web (Idéal commercial)

**Phase 1 de ton plan** devient le **portail unique** :
```
1. Mr X va homeos.studio (ton frontend)
2. Connecte Cursor Pro (OAuth 1-clic)
3. Clique "Générer Plan Phase X" 
4. Claude Code génère plan.json en arrière-plan
5. HomeOS exécute → code livré
```

**Prix** : €9.90/mois = **accès web + 500 plans Claude Code optimisés**.

## Solution #3 : CLI Magic Command (Mac uniquement)

```bash
# Installer globalement
npm install -g @homeos/cli

# Mr X tape UNIQUEMENT :
homeos plan phase1
```
```
🔮 HomeOS Plan Create
✅ Claude Code Plan Mode activé
✅ plan.json généré (1 message fast premium)
✅ Exécution Aetherflow...
✅ Code livré en 2min
```

**Interne** : Spawn Cursor headless + prompt optimisé + parsing JSON.

## **Recommandation commerciale (€9.90/mois)**

**Combo gagnant** : **Cursor Rules + HomeOS Studio Web**

```
MOIS 1 : Cursor Rules (gratuit)
- Mr X tape "HomeOS Phase X" → 1-clic plan.json
- 500 → 1000 tâches/mois (x2 efficacité)

MOIS 2+ : HomeOS Studio (€9.90)
- 1-clic web, historique plans, métriques
- Support Phase 4 Sullivan Kernel
- Analytics usage pour upsell
```

## Setup 10min (toi)

1. **Crée** `homeos-rules.md` dans repo principal
2. **Push** sur GitHub (Mr X pull auto dans Cursor)
3. **Déploie** HomeOS Studio Phase 1 (ton roadmap)
4. **Prix** : €9.90/mois Stripe → accès web

**Mr X paie €9.90** pour transformer ses **500 messages Claude Pro** en **1000+ tâches complètes/mois**. 

**Zéro friction, zéro skill, pure magie** ! ✨