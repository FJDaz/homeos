# MISSION KIMI : Chat Majordome Widget

**De** : Claude-Code Senior
**Pour** : KIMI Padawan
**Date** : 5 fevrier 2026
**Priorite** : MOYENNE

---

## Objectif

Creer un widget chat "Majordome" integrable dans le studio.
Le chat route les requetes vers le bon provider selon le type de tache.

## Architecture du routage (CRITIQUE)

```
User message
    |
    v
[Classification rapide - Groq 20ms]
    |
    ├── Commande courte/navigation → Groq (20-100ms)
    ├── Raisonnement/architecture  → DeepSeek (200-500ms)
    ├── Analyse document/image     → Gemini (300-800ms)
    └── Analyse UI/template PNG    → KIMI K2.5 via HF (400-1000ms)
```

Le Majordome utilise Groq comme CLASSIFIEUR + repondeur rapide.
Il ne passe aux autres que si necessaire.

## Ce que tu dois creer

### Fichier : `Frontend/majordome-chat.html`

Widget chat standalone, style DaisyUI dark theme.

### Structure HTML

```html
<!-- Barre fixe en bas ou sidebar droite -->
<div id="majordome-widget">
  <div id="majordome-header">
    🎩 Majordome
    <span id="majordome-provider">groq</span>
    <button onclick="toggleMajordome()">_</button>
  </div>
  <div id="majordome-messages">
    <!-- Messages ici -->
  </div>
  <div id="majordome-input">
    <input type="text" placeholder="Que puis-je faire ?"
           onkeydown="if(event.key==='Enter') sendMessage()">
    <button onclick="sendMessage()">Envoyer</button>
  </div>
</div>
```

### Backend : route dans studio_routes.py

```python
@router.post("/majordome/chat")
async def majordome_chat(request: Request):
    """Chat Majordome avec routage intelligent."""
    import json
    body = await request.json()
    message = body.get("message", "")

    # Classification rapide via heuristiques (PAS de LLM pour classifier)
    provider = classify_message(message)

    # Appel au bon provider
    response = await call_provider(provider, message)

    return JSONResponse({
        "response": response,
        "provider": provider,
        "latency_ms": elapsed
    })


def classify_message(message: str) -> str:
    """Classifie par heuristiques simples - ZERO appel API."""
    msg = message.lower()

    # Navigation / commandes courtes → Groq
    if any(w in msg for w in ["va", "ouvre", "montre", "liste", "status",
                                "aide", "help", "next", "retour"]):
        return "groq"

    # Analyse code / architecture → DeepSeek
    if any(w in msg for w in ["analyse", "refactor", "bug", "code",
                                "architecture", "pourquoi", "explique"]):
        return "deepseek"

    # Documents / images → Gemini
    if any(w in msg for w in ["document", "fichier", "image", "pdf",
                                "screenshot", "png"]):
        return "gemini"

    # UI / template → KIMI
    if any(w in msg for w in ["template", "composant", "ui", "design",
                                "layout", "figma"]):
        return "kimi"

    # Default → Groq (le plus rapide)
    return "groq"
```

### Appel providers (reutiliser les clients existants)

Les clients existent deja dans `Backend/Prod/models/` :
- `groq` → pas de client existant, appel direct API
- `deepseek` → `deepseek_client.py`
- `gemini` → `gemini_client.py`
- `kimi` → `kimi_vision_client.py` (si cree) ou HF Router direct

Pour Groq, appel simple :
```python
async def call_groq(message: str) -> str:
    import httpx
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "Tu es un majordome concis. Reponds en 1-2 phrases."},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 150,
                "temperature": 0.3
            }
        )
        return response.json()["choices"][0]["message"]["content"]
```

## Style du widget

- Position : fixed bottom-right ou integre dans la sidebar
- DaisyUI classes : chat, chat-bubble, btn, input
- Theme sombre coherent (#1a1a1a, #7cb342)
- Afficher le provider utilise en petit a cote de chaque reponse
- Indicateur de latence

## Contraintes

- Le classifieur est 100% heuristique (ZERO appel API pour classifier)
- Groq est le defaut — le plus rapide
- Max 150 tokens par reponse Majordome (c'est un assistant concis)
- Le widget doit etre LEGER (pas un framework JS)

## Test

```
http://localhost:8080/majordome-chat.html  (standalone)
http://localhost:8000/studio/drilldown     (integre)
```

---

*— Claude-Code Senior*
