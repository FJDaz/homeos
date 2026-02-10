# MISSION : Implémentation du Système de Vigilance (Aetherflow V2)

**Agent** : KIMI / AetherFlow
**Inspiration** : `docs/04-homeos/HOMEOS V2/Aetherflow V2 - Système de Vigilance et Orchestration de Bouquet.md`

## 🛠 Tâches Prioritaires

### 1. Le "Canari" de Surveillance (`Backend/Prod/core/monitor.py`)
- Créer une classe `ServiceVigilance` qui teste périodiquement les providers (DeepSeek, Gemini, Anthropic).
- Mesurer : Latence (ms), Success Rate (%), et Coût estimé.
- Stocker les résultats dans un fichier `cache/vigilance_status.json`.

### 2. Le "Friction-Killer" (UI Injection)
- Créer un composant HTML `Backend/Prod/templates/admin_vigilance.html`.
- Formulaire d'injection de Clefs API avec bouton "Test & Validate".
- Logique : Si l'admin colle une clef, Aetherflow lance immédiatement une requête `Hello World` pour valider la clef avant de l'enregistrer.

### 3. La Matrice de Comparaison (Benchmarking)
- Initialiser `Backend/Prod/core/pricing_matrix.py` avec les tarifs actuels.
- Prévoir la méthode `update_from_report(report_json)` pour permettre au futur agent BERT de mettre à jour les prix.

## 📊 Livrables attendus
- Script de healthcheck fonctionnel.
- Interface d'administration des clefs.
- Rapport de tests sur la bascule Local vs Cloud.

---
**Mission générée par Antigravity** - 10 février 2026
