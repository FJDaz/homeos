# Synthèse Stratégique : War Room de Brainstorm AetherFlow

## 🧠 Le Conseil des Bots (Trio Multimodal)

Pour maximiser la pertinence et minimiser les coûts, la Phase Brainstorm (BRS) repose sur trois instances pilotées en parallèle via API :

| Instance | Modèle | Rôle Stratégique | Coût |
| :--- | :--- | :--- | :--- |
| **Cerveau 1** | **Gemini 1.5 Pro** | **Le Scribe & RAG** : Analyse de contexte long, synthèse des PDF et du code existant. | **Gratuit** (Google Cloud) |
| **Cerveau 2** | **DeepSeek V3** | **L'Architecte** : Logique pure, structuration technique, précision du code et du JSON. | **Minimal** (Pay-as-you-go) |
| **Cerveau 3** | **Llama 3 (Groq)** | **Le Créatif Flash** : Vitesse fulgurante, ideation brute, réponse instantanée. | **Gratuit** (Groq Tier) |

---

## 🔄 Le Protocole HCI "Pristine" (Anti-Latence)

L'interaction est conçue pour transformer le temps d'attente IA en temps de réflexion utilisateur :

1.  **Le Dispatcher (Bouton Central)** : Envoie la requête simultanément aux 3 cerveaux + contexte Retro-Genome.
2.  **Le Buffering Sullivan** : Pendant l'inférence, Sullivan pose 2-3 questions de filtrage (ex: "Cible B2B/B2C ?", "Mobile-First ?").
3.  **Le Streaming Parallèle** : Les trois colonnes d'interface affichent les réponses "mot à mot" en temps réel via des flux SSE (Server-Sent Events).

---

## 🛠️ Architecture Technique

### Backend : La Route `/brainstorm`
*   **Mode** : Asynchrone (`asyncio.gather`).
*   **Entrée** : Intention utilisateur + Genome actuel.
*   **Sortie** : Triple flux streamé vers le Frontend.

### Frontend : Composants Atomes SVG
*   **Insight Cards** : Blocs visuels dédiés à chaque IA (Pas d'Iframe).
*   **Le Panier de Sullivan** : Zone de capture des "pépites" sémantiques.
*   **Capture Directe** : Chaque idée générée possède un bouton SVG "Capturer" pour alimenter le futur PRD.

---

## ✅ Objectif Final : Inférence de PRD
À la fin de la session, Sullivan compile toutes les pépites du panier pour générer automatiquement le fichier `PRD_BASIQUE.md` dans le répertoire `/docs`, prêt pour la Phase Backend.

> [!TIP]
> Ce workflow élimine le "Saut d'onglet" et garantit que chaque IA travaille avec le même niveau d'information sur le projet.
