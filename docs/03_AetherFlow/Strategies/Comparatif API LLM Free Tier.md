##Tableau comparatif exhaustif des **offres IA/LLM gratuites ou quasi-gratuites** (free tiers)
Voici un résumé 2026 basé sur les données actuelles. J'ai priorisé les LLM accessibles via API, adaptés à tes projets dev (React/Python, agents multimodaux), avec quotas utilisables sans CB. [llmpricing](https://llmpricing.dev/fr/)

## Comparatif API LLM Free Tier
| Provider | Modèles phares | Input/Output Gratuit (/M tokens) | Quotas Free | Contexte Max | Multimodal ? | OpenAI Compatible |
|----------|----------------|---------------------------|-------------|--------------|--------------|-------------------|
| Google AI Studio  [llmpricing](https://llmpricing.dev/fr/) | Gemini 2.5 Flash/Lite | $0 / $0 (free tier) | 15-60 RPM, ~millions tokens/jour | 1M | Oui (img/vidéo/audio) | Non (mais SDK simple) |
| Groq  [hypereal](https://hypereal.tech/a/free-open-source-llm-apis) | Llama 3.3 70B, DeepSeek R1 | $0 (free) | 30 req/min, 14k/jour | 128k | Non | Oui |
| OpenRouter  [hypereal](https://hypereal.tech/a/free-open-source-llm-apis) | Llama, Mistral, Gemma (free models) | $0 pour modèles gratuits | Varie (illimité low-volume) | Varie | Partiel | Oui |
| Hugging Face Inference  [visionvix](https://visionvix.com/best-free-llm-api/) | Llama 3, Mistral, Qwen | $0 (rate-limited) | Haut volume bas, illimité slow | 128k+ | Oui (HF models) | Oui (lite) |
| Together AI  [hypereal](https://hypereal.tech/a/free-open-source-llm-apis) | Llama 3.3, Qwen 2.5 | $5 crédit gratuit | 60 req/min | 128k | Non | Oui |
| Fireworks AI  [hypereal](https://hypereal.tech/a/free-open-source-llm-apis) | Llama 3.3, Mixtral | $1 crédit gratuit | 10 req/min | 128k | Non | Oui |
| Cloudflare Workers AI  [perplexity](https://www.perplexity.ai/search/b67baf2b-f737-4828-bc87-0def97b6a497) | Mixtral, Llama | $0 (quotas généreux) | Illimité edge low-vol | 128k | Non | Oui |
| Mistral (La Plateforme)  [perplexity](https://www.perplexity.ai/search/b67baf2b-f737-4828-bc87-0def97b6a497) | Mistral Nemo/Large | Free tier limité | Quotas/jour | 128k | Non | Oui |

**Notes** : Prix paid indicatifs (~0.1-0.5$/M input pour Flash models) ; free tiers sans CB pour la plupart (sauf crédits initiaux). Pour tes setups Kimi/DeepSeek, Groq/OpenRouter excellent en vitesse/coût. [visionvix](https://visionvix.com/best-free-llm-api/)

## Autres Offres IA Gratuites Populaires
Pour élargir (agents, embeddings, etc.) :

| Catégorie | Outils | Quotas Free | Usage Typique |
|-----------|--------|-------------|---------------|
| Agents Multimodaux  [jedha](https://www.jedha.co/formation-ia/meilleurs-agents-ia-gratuits) | CrewAI (open source), Dify Cloud | 50 workflows/mois ; 200 appels OpenAI | Automatisation RAG/vision |
| Embeddings | Google Gemini Embed  [llmpricing](https://llmpricing.dev/fr/), OpenAI text-embedding-3-small | $0 free tier ; ~62k pages/$ | Recherche sémantique |
| Images/Vidéo | Hugging Face Stable Diffusion | Illimité slow | Génération avatars/infographies  [perplexity](https://www.perplexity.ai/search/71f95bf8-8c3f-40c8-a1cb-fbbbbdc1ae1f) |

**Source exhaustive** : llmpricing.dev pour simulateur coûts ; publicapis.io pour +1000 API non-LLM. Si tu veux filtrer (e.g. vision only, self-hosted, ou inclure Kimi/Claude Pro), dis-moi pour un tableau custom ! [publicapis](https://publicapis.io)