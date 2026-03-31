**Claude Code Sonnet 4.5** dispose d'un mécanisme d'*auto-compaction* automatique du contexte dans les interfaces comme Claude Code ou l'SDK Agent Python, déclenché quand l'usage des tokens dépasse un seuil configurable (ex. 5k-100k tokens, défaut ~100k sur 200k fenêtre). [platform.claude](https://platform.claude.com/cookbook/tool-use-automatic-context-compaction)

## Déclencheur et fréquence chez Claude

- **Déclencheur principal** : Seuil de tokens input + output + cache atteint (ex. 5 000 tokens pour workflows itératifs comme traitement de tickets).
  - Surveille après chaque tour : input cumulatif + sortie + cache KV.  
  - UI affiche "Context left until auto-compact: X%" ou "Context low (Y% remaining) · Run /compact". [github](https://github.com/anthropics/claude-code/issues/9636)
- **Fréquence** : Pas fixe (périodique), mais *par tour* quand seuil dépassé ; reset l'historique en remplaçant par un résumé généré par le modèle (balisé <summary>). [platform.claude](https://platform.claude.com/cookbook/tool-use-automatic-context-compaction)
- **À surveiller** : Logs UI ("Context low"), comptage tokens (/context commande), cumul input avant API call. Anticipe en trackant tokens via SDK ou tokenizer.

## Chez Kimi (K2 / K2.5)

Pas de commande *auto-compact* native/fixe documentée comme chez Claude ; gestion contextuelle via **compression manuelle ou auto sur providers** (ex. OpenRouter). [kimi-ai](https://kimi-ai.chat/guide/manages-context-windows/)

- **Déclencheur** : Dépassement limite fenêtre (128k-256k tokens) → erreur API ou auto-compression "middle-out" (condense milieu du prompt, préserve débuts/fins).
  - Logs : "Context size increased during condensing" ou "Failed to condense context".
- **Fréquence** : Au dépassement (pas périodique), ou implémentée manuellement (résumé ancien contexte).
- **À surveiller** : Token count avant envoi API (Moonshot/OpenRouter), erreurs overflow. Anticipe avec chunking/summarization proactif ou YaRN pour long-context. [kimi-ai](https://kimi-ai.chat/guide/manages-context-windows/)

En résumé, Claude est plus "automatique" par seuil configurable en agentic workflows ; Kimi repose sur provider/infra pour overflow, avec emphase sur fenêtre native large (moins besoin). [kimi-ai](https://kimi-ai.chat/guide/manages-context-windows/)