#!/bin/bash
# Test appel API KIMI (Moonshot AI)
# Pour vérifier que l'intégration fonctionne

set -e  # Arrêt si erreur

echo "🧪 TEST API KIMI (Moonshot AI)"
echo "=============================="
echo ""

# Configuration
KIMI_API_URL="https://api.moonshot.cn/v1/chat/completions"
KIMI_API_KEY="${KIMI_API_KEY:-}"

# Vérifier clé API
if [ -z "$KIMI_API_KEY" ]; then
  echo "❌ KIMI_API_KEY non définie"
  echo ""
  echo "Pour définir la clé :"
  echo "  export KIMI_API_KEY='votre_cle_ici'"
  echo ""
  echo "Ou temporairement :"
  echo "  KIMI_API_KEY='votre_cle' ./test_kimi_api.sh"
  echo ""
  exit 1
fi

echo "✅ KIMI_API_KEY trouvée (${#KIMI_API_KEY} caractères)"
echo "🌐 API URL : $KIMI_API_URL"
echo ""

# Préparer prompt de test
PROMPT="Bonjour KIMI. Ceci est un test d'intégration depuis AETHERFLOW.

Tu es KIMI 2.5, Frontend Lead pour le projet Sullivan.

Mission de test : Réponds simplement 'TEST OK' suivi de la date/heure actuelle.

Ne génère pas de code, juste cette réponse de test."

echo "📤 Envoi requête API KIMI..."
echo ""

# Appel API (avec timeout 30s)
RESPONSE=$(curl -s --max-time 30 -X POST "$KIMI_API_URL" \
  -H "Authorization: Bearer $KIMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "moonshot-v1-8k",
    "messages": [
      {
        "role": "system",
        "content": "Tu es KIMI, assistant Frontend Lead pour AETHERFLOW."
      },
      {
        "role": "user",
        "content": "'"$PROMPT"'"
      }
    ],
    "temperature": 0.3,
    "max_tokens": 100
  }' 2>&1)

# Vérifier erreur curl
if [ $? -ne 0 ]; then
  echo "❌ Erreur curl : $RESPONSE"
  exit 1
fi

echo "📥 Réponse reçue"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Vérifier présence erreur
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
  ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message')
  echo "❌ Erreur API : $ERROR_MSG"
  exit 1
fi

# Extraire contenu réponse
CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content' 2>/dev/null)

if [ -z "$CONTENT" ] || [ "$CONTENT" = "null" ]; then
  echo "❌ Réponse vide ou format invalide"
  exit 1
fi

echo "✅ API KIMI fonctionnelle !"
echo ""
echo "📝 Réponse KIMI :"
echo "   $CONTENT"
echo ""

# Statistiques
TOKENS_USED=$(echo "$RESPONSE" | jq -r '.usage.total_tokens // "N/A"' 2>/dev/null)
echo "📊 Tokens utilisés : $TOKENS_USED"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ TEST RÉUSSI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "L'API KIMI est prête pour l'orchestration."
echo ""
echo "Prochaines étapes :"
echo "  1. Intégrer dans trigger_kimi.sh"
echo "  2. Tester workflow complet ÉTAPE 4"
echo "  3. Valider avec François-Jean"
