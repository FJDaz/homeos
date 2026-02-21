# 04 - Principes HCI & Design (Sens & Culture)

Pour qu'un petit modèle LLM (3B-8B) produise un design "digne" et non générique, il doit être infusé de culture design via un système de RAG (Retrieval Augmented Generation).

## 1. La Sémantique au service de l'Ergonomie
L'IA ne doit jamais choisir une police ou une couleur. Elle doit choisir une **Intention**.
- **Erreur classique** : IA injecte `style="color: blue"`.
- **Modèle Aetherflow** : IA injecte `importance: "primary"`. L'Engine traduit cela en un bleu institutionnel précis, respectant les lois du design (accessibilité, contraste).

## 2. Le RAG Culturel (Design RAG)
Le système Sullivan Engine doit être nourri par des documents de référence (dans `/docs/design_system`) :
- **CONSTITUTION de l'élégance** : Principes de vides, de rythmes et de hiérarchie visuelle.
- **Référentiel Sullivan** : Guide de tonalité (Clarté, Discrétion, Efficacité).
- **Patrons HCI** : Liste des meilleures pratiques (Feedback immédiat, Loi de Fitts appliquée au tactile).

## 3. Le Seuil de Dignité (HCI)
Un service est jugé "digne" lorsqu'il anticipe le besoin sans être intrusif.
- **Micro-interactions** : Gérées par les Hooks (ex: légère vibration ou changement de curseur sur un Drag & Drop).
- **Transitions** : Navigation fluide (Smooth Scroll) pour maintenir le lien spatial entre N0 et N3.

---

## 🛠️ Implementation pour l'Agent Guardian
L'Agent Guardian utilise ce document comme **Grille d'Évaluation**. Si une proposition de KIMI viole un principe HCI (ex: bouton trop petit ou sémantique floue), le Guardian la refuse au nom de la "Dignité du Design".
