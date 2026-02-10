# MISSION GEMINI : Migrer KIMI vers Hugging Face Inference

**Date** : 9 février 2026
**Agent** : Gemini (QA + Refactoring)
**Mode AetherFlow** : BUILD
**Priorité** : 🟠 P1

---

## 1. OBJECTIF

Remplacer le client KIMI Moonshot API (payant) par l'**Inference API Hugging Face** (gratuite).

Modèles disponibles sur HF :
- `moonshotai/Kimi-K2.5` - Vision + Text (456K downloads, trending)
- `moonshotai/Kimi-K2-Instruct` - Text only (274K downloads)

---

## 2. FICHIER À MODIFIER

**Cible** : `Backend/Prod/models/kimi_client.py`

### 2.1 État actuel

```python
# Moonshot API directe (payant)
self.api_url = settings.kimi_api_url  # https://api.moonshot.cn/v1/chat/completions
self.api_key = settings.kimi_api_key  # KIMI_KEY
self.model = settings.kimi_model      # moonshot-v1-8k
```

### 2.2 État cible

```python
# Hugging Face Inference API (gratuit)
self.api_url = "https://api-inference.huggingface.co/models/moonshotai/Kimi-K2-Instruct"
self.api_key = settings.hf_token  # HF_TOKEN (déjà existant ?)
self.model = "moonshotai/Kimi-K2-Instruct"
```

---

## 3. CHANGEMENTS REQUIS

### 3.1 Dans `kimi_client.py`

1. **Ajouter option HF** dans `__init__`:
```python
def __init__(self, use_hf: bool = True):
    if use_hf:
        self.api_url = "https://api-inference.huggingface.co/models/moonshotai/Kimi-K2-Instruct"
        self.api_key = settings.hf_token
        self.provider = "huggingface"
    else:
        # Fallback Moonshot
        self.api_url = settings.kimi_api_url
        self.api_key = settings.kimi_api_key
        self.provider = "moonshot"
```

2. **Adapter la requête HTTP** pour HF Inference API :
```python
# HF format différent de Moonshot
if self.provider == "huggingface":
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 200, "temperature": 0.1}
    }
else:
    payload = {
        "model": self.model,
        "messages": [...],
        "temperature": 0.1,
        "max_tokens": 200
    }
```

3. **Parser la réponse HF** :
```python
# HF retourne directement le texte généré
if self.provider == "huggingface":
    content = response.json()[0]["generated_text"]
else:
    content = response.json()["choices"][0]["message"]["content"]
```

### 3.2 Dans `settings.py`

Ajouter si absent :
```python
hf_token: str = Field(default="", alias="HF_TOKEN", description="Hugging Face API token")
use_kimi_hf: bool = Field(default=True, alias="USE_KIMI_HF", description="Use KIMI via HF (free)")
```

---

## 4. TESTS

Créer/modifier `Backend/Prod/tests/models/test_kimi_client.py` :

```python
@pytest.mark.asyncio
async def test_kimi_hf_validation():
    """Test KIMI validation via HuggingFace."""
    client = KimiClient(use_hf=True)

    # Skip si pas de HF_TOKEN
    if not client.available:
        pytest.skip("HF_TOKEN not configured")

    result = await client.validate_output(
        output="def hello(): print('world')",
        expected_language="python"
    )

    assert result["valid"] == True
```

---

## 5. CONTRAINTES

- **Backward compatible** : Garder l'option Moonshot en fallback
- **Variable d'env** : `USE_KIMI_HF=true` par défaut
- **Pas de breaking change** : L'interface `validate_output()` ne change pas

---

## 6. CRITÈRES D'ACCEPTATION

- [ ] `KimiClient` utilise HF Inference par défaut
- [ ] Fallback Moonshot si `USE_KIMI_HF=false`
- [ ] Tests passent avec HF
- [ ] Pas de régression sur le gate-keeper

---

## 7. LIVRAISON

**Fichier CR** : `.claude/mailbox/gemini/CR_KIMI_HF_CLIENT.md`

---

## 8. RESSOURCES

- Doc HF Inference API : https://huggingface.co/docs/api-inference
- Modèle : https://hf.co/moonshotai/Kimi-K2-Instruct
- User HF actuel : `FJDaz` (authentifié)
