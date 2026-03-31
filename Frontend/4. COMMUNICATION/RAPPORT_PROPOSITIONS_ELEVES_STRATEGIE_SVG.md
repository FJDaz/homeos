# 📊 Rapport : État des Lieux & Stratégie d'Intégration (Propositions Élèves)

Ce rapport dresse un état des lieux de la hétérogénéité des livrables élèves et propose une trajectoire de normalisation via le **SVG Annoté** comme langage passerelle universel.

---

## 🔍 1. État des Lieux des Propositions (Le Florilège)

L'analyse des projets (ex: `Spinoza_Secours_HF`, `bergsonAndFriends_HF`, `3_PHI_HF`) révèle une architecture récurrente mais "hors-sol" par rapport au design system AetherFlow.

| Format | État des Lieux | Problématique AetherFlow |
| :--- | :--- | :--- |
| **PNG (Mockups)** | Conceptuels, souvent issus de captures Vision. | **Lossy** : La structure logique est perdue. |
| **HTML/CSS Vanilla** | Souvent un fichier unique (`index.html`). | Difficile à maintenir en composants réutilisables. |
| **React + Tailwind (CDN)** | Très fréquent via KIMI. Utilise des scripts `<script src="...">`. | **Fragile** : Dépendances externes, classes atomiques dures à "re-skinner". |
| **Python Backend** | FastAPI / Gradio (Mistral 7B). | **Siloté** : Les intents ne sont pas branchés sur le Genome global. |

---

## 🧩 2. Le Diagnostic : Le Gap des "Viewers"

Actuellement, les viewers AetherFlow (Stenciler, Template Viewer) peinent à "avaler" ces propositions car elles sont trop spécifiques.
- Le passage **Code Élève -> Code AetherFlow** est destructeur.
- Le passage **Genome (JSON) -> Code Élève** est approximatif esthétiquement.

---

## 💎 3. Recommandation : Le SVG Annoté (La Pierre de Rosette)

Pour stabiliser le process, nous devons élever le **SVG** au rang de **langage interfaciel radical**.

### Le Concept du "SVG Backplane"
Au lieu de passer d'un PNG à du code React instable, nous passons par une étape pivot en SVG "augmenté".

1.  **Capturation (PNG -> SVG)** : Utiliser Gemini Vision (Mission 39) pour générer un SVG qui reproduit la géométrie exacte de la proposition élève.
2.  **Annotation (SVG + Data)** : Chaque élément SVG est taggué avec des attributs `data-genome-id` et `data-intent`.
3.  **Traduction (SVG -> Any)** :
    - **En mode Design** : Directement manipulable dans Illustrator/Figma (via plugin).
    - **En mode Code** : KIMI traduit le SVG en HTML/CSS Vanilla ou React/Tailwind.

### Pourquoi le SVG est supérieur au JSON pour ce rôle :
- **Manipulation Visuelle** : C'est le format natif des graphistes.
- **Topologie** : Il fige les positions (x,y) là où le CSS est interprété.
- **Transversalité** : C'est le seul format qui se lit aussi bien sur le web, sur mobile, dans Figma et par les LLM.

---

## 🛠️ 4. Plan de Route : Mise en œuvre

1.  **Standardisation** : Définir le schéma d'annotation `af-metadata` dans le SVG (zones, intents, affectations Genome).
2.  **Plugin Figma Update** : Permettre l'import/export de ce SVG "intelligent" pour que l'aller-retour design-code soit sans perte.
3.  **KIMI "SVG-to-Component"** : Développer un pipeline où KIMI n'écrit pas le code à partir d'un prompt texte, mais "implémente" le SVG fourni.

---
**Verdict** : Le SVG Annoté agit comme le **Body** (corps physique) du **Genome** (esprit logique). C'est la garantie d'une "vibe" préservée entre l'idée de l'élève et la production industrielle.

**Auteur** : Antigravity Agent
**Date** : 13 Mars 2026
