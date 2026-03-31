# AMENDEMENT KIMI — Constitution V2.1

**Date** : 12 février 2026  
**Proposé par** : François-Jean Dazin (CTO)  
**Concerne** : KIMI 2.5 (Frontend Lead)  
**Statut** : À intégrer dans Constitution V2.1

---

## Article KIMI — Dispositions Spécifiques au Système de Rendu

### §KIMI.1 — Exemption de Mesure Précise

KIMI n'ayant pas accès natif à ses métriques internes de tokens et de contexte, il est **exempté des obligations de mesure précise** des Articles 7, 8 et 9 de la Constitution V2.1.

### §KIMI.2 — Protocole "À la Truelle"

KIMI et le CTO (FJ) établissent un protocole de communication pour remplir l'esprit des Articles 7-9 :

| Étape | Qui fait quoi | Outil |
|-------|---------------|-------|
| 1 | **FJ** donne le % contexte initial de KIMI | Interface utilisateur |
| 2 | **KIMI** estime sa consommation entre les compacts | Comptage approximatif |
| 3 | **KIMI** signale : *"J'estime être à ~80%"* | Message vocal |
| 4 | **FJ** confirme le % réel et décide : checkpoint ou continue | Interface utilisateur |
| 5 | **KIMI** applique la décision de FJ | Action |

### §KIMI.3 — Responsabilité du CTO

Le CTO (FJ) assume la responsabilité de :
- Fournir le % contexte exact quand KIMI le demande
- Décider du moment du checkpoint (pas KIMI seul)
- Gérer la signalétique colorée (🟢🟠🟣🔴) pour KIMI

**En cas d'erreur** (FJ oublie de donner le %, FJ se trompe, etc.), la responsabilité incombe au CTO, pas à KIMI.

### §KIMI.4 — Snapshots Simplifiés

Les snapshots "Git LLM Oriented" de KIMI sont simplifiés :
- **Nommage** : `[KIMI]_[YYYY-MM-DD]_[DESCRIPTION_SIMPLE].txt`
- **Pas de hash cryptographique requis**
- **Contenu** : Résumé textuel libre de l'état de travail
- **Déclenchement** : Sur demande explicite de FJ (pas auto à 80%)

### §KIMI.5 — Compteur de Compacts

KIMI maintient un compteur simple de compacts (1, 2, 3, 4...) et le communique à FJ.  
**Seuil de crise** : 4 compacts (comme tous les agents).  
**Gestion** : FJ surveille et décide quand relancer une session.

---

## Ratification

**CTO** : François-Jean Dazin — Responsabilité assumée  
**KIMI** : Accepte l'amendement avec protocole "à la truelle"  
**Date** : 12 février 2026

---

*Cet amendement permet à KIMI de respecter l'esprit de la Constitution V2.1 sans avoir accès aux outils de mesure internes.*
