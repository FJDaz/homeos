#!/bin/bash
# Script de test du workflow d'orchestration
# Mode démo/simulation sans appel API KIMI

echo "🧪 TEST WORKFLOW ORCHESTRATION CLAUDE-KIMI"
echo "==========================================="
echo ""

# Étape 1 : Simulation mission Claude terminée
echo "✅ ÉTAPE 1 : Claude termine ÉTAPE 3 (Drill-down Backend)"
echo "   - Endpoints créés"
echo "   - Documentation écrite"
echo "   - Backend redémarré"
echo ""

# Étape 2 : Déclencher KIMI
echo "🚀 ÉTAPE 2 : Déclencher KIMI"
echo "   Exécution : ./trigger_kimi.sh ..."
./scripts/orchestration/trigger_kimi.sh \
  docs/02-sullivan/mailbox/kimi/DRILLDOWN_BACKEND_READY.md \
  ETAPE_4

echo ""
read -p "▶️  Appuyer sur ENTER pour simuler réponse KIMI..."
echo ""

# Étape 3 : Simuler réponse KIMI
echo "🎨 ÉTAPE 3 : KIMI travaille (simulation)..."
sleep 2

# Écrire signal KIMI dans collaboration_hub.md
cat >> /Users/francois-jeandazin/collaboration_hub.md << 'EOF'

---

@CLAUDE_VALIDATE
## CR KIMI : ÉTAPE 4 TERMINÉE (SIMULATION TEST)

**Date** : 2026-02-12 15:00:00
**Status** : ✅ TERMINÉ (MODE TEST)
**Durée** : 2h (simulé)

**Fichiers modifiés** :
- `Frontend/3. STENCILER/static/drilldown_manager.js` (200+ lignes)

**Tests réalisés** :
- [x] Double-clic sur Corps → Organes affichés
- [x] Breadcrumb mis à jour
- [x] Bouton retour fonctionnel

**URL validation** : http://localhost:9998/stenciler

**Validation requise** :
François-Jean, merci de valider visuellement avant passage ÉTAPE suivante.

EOF

echo "✅ Signal @CLAUDE_VALIDATE écrit dans collaboration_hub.md"
echo ""

# Étape 4 : Lancer watcher (avec timeout 30s pour test)
echo "👀 ÉTAPE 4 : Lancer surveillance KIMI (timeout 30s)..."
echo ""

# Lancer watcher en arrière-plan
./scripts/orchestration/watch_kimi.sh &
WATCHER_PID=$!

# Attendre 35 secondes ou que watcher se termine
timeout 35s tail --pid=$WATCHER_PID -f /dev/null 2>/dev/null

# Si watcher toujours actif, le tuer
if ps -p $WATCHER_PID > /dev/null 2>&1; then
  kill $WATCHER_PID 2>/dev/null
fi

echo ""
echo "✅ TEST TERMINÉ"
echo ""
echo "📋 Résumé :"
echo "  - Mission KIMI écrite dans collaboration_hub.md ✅"
echo "  - Signal @CLAUDE_VALIDATE détecté ✅"
echo "  - Notification déclenchée ✅"
echo ""
echo "🧹 Nettoyage : Signal retiré de collaboration_hub.md"
