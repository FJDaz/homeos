# **PRD - Homeos : Plateforme d'Homéostasie du Code**

## **1. Aperçu du Produit**

### **1.1. Vision**
Homeos est une plateforme d'IA qui génère du code de haute qualité (front-end HTML/CSS/JS et backend Python/APIs) en maintenant un équilibre homéostatique entre qualité, performance et maintenabilité. Homeos utilise **AETHERFLOW** (orchestrateur backend technique) pour l'exécution des plans et la génération de code, et intègre un système d'homéostasie intelligent pour mutualiser les composants optimisés.

**Note** : Homeos est le nom commercial de la plateforme. AETHERFLOW est le nom technique interne utilisé dans le code (classes, modules, fichiers).

### **1.2. Problème**

#### **Problème Utilisateur**
- Les générateurs d'IA produisent souvent du code sale, non optimisé, inaccessible et difficile à maintenir.
- Les développeurs passent trop de temps à ajuster le code généré par l'IA.
- Les enseignants en développement web manquent d'outils pédagogiques pour enseigner les bonnes pratiques (performance, accessibilité, sobriété).

#### **Problème Technique**
- **Dépendance à Cursor Pro** : Claude Code est gratuit uniquement via Cursor Pro (produit américain, nécessite abonnement payant pour usage commercial).
- **Coûts Claude API** : ~$0.021-0.048 par plan si utilisation standalone (planification seule ou + validation).
- **Risque géopolitique** : Dépendance exclusive aux LLMs américains (Cursor + Anthropic).
- **Blocage commercial** : Impossible de conditionner l'offre finale à l'obtention de Cursor Pro.

### **1.3. Solution**

Homeos propose une architecture en trois couches :

1. **Alternative Portable** (Phase 0) : Version indépendante de Cursor Pro utilisant Claude API uniquement pour planification + révision, réduisant l'utilisation Claude de 42% (facteur 1.73x).

2. **Sullivan Kernel** (Phase 1+) : Modèle local (DeepSeek-Coder-7B fine-tuné) remplaçant Claude API pour planification, réduisant les coûts de 95% ($0.022 → $0.001 par plan).

3. **Homeos Front-End** : Interface web complète pour visualiser, exécuter et gérer les plans.

**Workflows de génération** :
- **Mode FAST** (Workflow PROTO) : Prototypage rapide via AETHERFLOW (FAST → DOUBLE-CHECK) en ~5-15 secondes.
- **Mode BUILD** (Workflow PROD) : Génération de code production via AETHERFLOW (FAST draft → BUILD refactor → DOUBLE-CHECK) en ~30-90 secondes.

**Homeos Engine** : Système d'homéostasie qui mutualise intelligemment les composants et patterns, en maintenant un équilibre de qualité (score Homeos ≥ 85/100) dans sa bibliothèque.

### **1.4. Public Cible**
- **Enseignants** (DNMADE, NSI, BUT MMI) : Pour former les étudiants aux bonnes pratiques.
- **Étudiants** : Pour apprendre et prototyper rapidement.
- **Développeurs indépendants** : Pour gagner du temps sur le front-end.
- **Établissements d'enseignement et de formation** : Pour équiper leurs salles de cours avec un outil éthique et performant.

### **1.5. Objectifs**
- **Court terme** : Atteindre 100 utilisateurs payants en 6 mois.
- **Moyen terme** : Devenir l'outil de référence pour l'enseignement du front-end en France.
- **Long terme** : Étendre à l'international et à d'autres domaines (back-end, mobile).

---

## **2. Architecture Complète**

### **2.1. Architecture en Trois Couches**

```
┌─────────────────────────────────────────────────────────────┐
│                    HOMEOS (Nom Commercial)                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐      ┌──────────────────────┐    │
│  │  Homeos Front-End    │      │   Homeos Backend     │    │
│  │  (Interface Web)     │◄────►│   (AETHERFLOW)       │    │
│  │                      │      │                      │    │
│  │  • Dashboard         │      │  • Orchestrator      │    │
│  │  • Upload plans      │      │  • Workflows         │    │
│  │  • Visualisation     │      │  • AgentRouter       │    │
│  │  • Génération        │      │  • Cache             │    │
│  │    Front-End         │      │  • Métriques         │    │
│  │  • Homeos Engine    │      │                      │    │
│  │    (Homéostasie)    │      │                      │    │
│  └──────────────────────┘      └──────────────────────┘    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     Planification (Alternative Portable / Kernel)   │   │
│  │                                                       │   │
│  │  Phase 0: Claude API (planification + révision)     │   │
│  │  Phase 1+: Sullivan Kernel (local, indépendant)     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### **2.2. Alternative Portable (Phase 0)**

**Objectif** : Créer une version indépendante de Cursor Pro utilisant Claude API.

**Architecture** :
- **Claude API** : Uniquement pour planification (génération plan.json) + révision si problème
- **AETHERFLOW** : Validation (Gemini/DeepSeek) + Exécution (DeepSeek/Groq/Gemini)
- **Coût** : ~$0.022 par plan (vs $0.048 sans Homeos)
- **Réduction** : 42% d'utilisation Claude (facteur 1.73x)

**Avantages** :
- ✅ Indépendance de Cursor Pro
- ✅ Portabilité totale
- ✅ Solution immédiate (1 semaine de développement)
- ✅ Réduction significative des coûts Claude

**Limitations** :
- ⚠️ Dépendance à Anthropic API (US)
- ⚠️ Coût par plan (~$0.022)

### **2.3. Sullivan Kernel (Phase 1+)**

**Objectif** : Remplacer Claude API par un modèle local fine-tuné.

**Architecture** :
- **Modèle de base** : DeepSeek-Coder-7B-Instruct
- **Quantization** : Q4_K_M (~4GB VRAM)
- **Framework** : llama.cpp (déploiement Mac 2016)
- **Fine-tuning** : LoRA (efficient fine-tuning)

**Capacités** :
- Planification de tâches (génération plan.json)
- Routage intelligent (quel provider utiliser)
- Validation DOUBLE-CHECK (remplace Gemini)
- Feedback mentor (remplace Claude Code)

**Coût** : ~$0.001 par plan (coût marginal, électricité uniquement)

**Avantages** :
- ✅ Indépendance géopolitique totale
- ✅ Latence réduite (2s vs 10s)
- ✅ Coût marginal (~$0.001 vs $0.022)
- ✅ Personnalisation infinie
- ✅ Confidentialité totale

**ROI** :
- Coût développement : ~$5,000
- Économie mensuelle : $0.021 × 300 plans = $6.30/mois
- ROI : ~13 ans (mais valeur indépendance inestimable)

---

## **3. Fonctionnalités Détaillées**

### **3.1. Modes de Génération**

#### **3.1.1. Mode FAST** (Workflow PROTO)
- **Description** : Prototypage rapide via le workflow PROTO d'AETHERFLOW (FAST → DOUBLE-CHECK).
- **Durée** : ~5-15 secondes selon la complexité du plan JSON.
- **Utilisation** : Exploration d'idées, démonstrations, premiers jets.
- **Backend** : Utilise AETHERFLOW avec mode FAST (Groq) puis validation DOUBLE-CHECK (Gemini).
- **Limitations** : Code non optimisé, pas de refactoring guidé.
- **Output** : Code backend (Python, APIs) ou Front-end (HTML/CSS/JS) selon le plan.

#### **3.1.2. Mode BUILD** (Workflow PROD)
- **Description** : Génération de code production via le workflow PROD d'AETHERFLOW (FAST draft → BUILD refactor → DOUBLE-CHECK).
- **Durée** : ~30-90 secondes selon la complexité du plan JSON.
- **Processus** :
  1. Upload d'un plan JSON (ou génération automatique depuis design - Phase 3).
  2. AETHERFLOW exécute FAST (brouillon rapide via Groq).
  3. AETHERFLOW exécute BUILD (refactoring avec guidelines TDD/DRY/SOLID via DeepSeek).
  4. AETHERFLOW exécute DOUBLE-CHECK (validation finale via Gemini).
  5. Homeos Engine calcule le score Homeos du code généré.
  6. Si score ≥ 85, proposition de partage dans la bibliothèque Élite.
- **Output** : Code production (HTML/CSS/JS pour front-end, Python/APIs pour backend) avec score Homeos élevé.

### **3.2. Architecture d'Homéostasie à Trois Niveaux**

#### **3.2.1. Niveau 0 : Cache Privé**
- Stockage local des composants générés pour un utilisateur.
- Chemin technique : `~/.aetherflow/components/[user_id]/` (nom interne AETHERFLOW conservé).
- Usage : Préférences personnelles, projets spécifiques.
- Format : Fichiers JSON avec métadonnées + code généré.

#### **3.2.2. Niveau 1 : Homeos Library (Bibliothèque Homéostatique)**
- Composants mutualisés ayant un score Homeos ≥ 85.
- Stockés sur le serveur Homeos (chemin technique : `[aetherflow-server]/components/elite/`).
- Critères d'entrée :
  - Score Homeos ≥ 85 (intègre score DOUBLE-CHECK d'AETHERFLOW)
  - Performance Lighthouse > 90 (pour front-end) ou benchmarks > 90 (pour backend)
  - Accessibilité WCAG AA (pour front-end) ou sécurité validée (pour backend)
  - Poids < 10KB (pour front-end) ou efficacité optimale (pour backend)
  - Score DOUBLE-CHECK d'AETHERFLOW > 95%
  - Validé par au moins 3 utilisateurs

#### **3.2.3. Niveau 2 : Base de Connaissance Structurelle**
- Patterns UI/UX validés (ex : structure de page de pricing, flux de connexion).
- Principes HCI (modèle de Fogg, affordances de Norman).
- Analytics sur les performances des composants.

### **3.3. Homeos Engine (Moteur d'Homéostasie)**

#### **3.3.1. Workflow d'Homéostasie**
1. **Reçu d'une intention** (plan JSON uploadé via Homeos Studio ou design/image - Phase 3).
2. **Vérification cache local** : Homeos Engine vérifie le cache privé de l'utilisateur.
3. **Vérification bibliothèque Élite** : Homeos Engine cherche dans la bibliothèque mutualisée.
4. **Proposition** : Si trouvé, propose le composant avec son score Homeos et ses métriques.
5. **Génération via AETHERFLOW** : Sinon, envoie le plan à AETHERFLOW Backend pour génération.
   - AETHERFLOW exécute le workflow sélectionné (PROTO ou PROD).
   - AETHERFLOW utilise son cache sémantique interne.
   - AETHERFLOW génère le code selon le plan.
6. **Évaluation** : Homeos Engine calcule le score Homeos du nouveau composant.
7. **Régulation** : Si le score ≥ 85, propose le partage pour maintenir l'équilibre de la bibliothèque.

#### **3.3.2. Calcul du Score Homeos**
```python
class HomeosScore:
    performance: int      # 0-100 (Lighthouse pour front-end, benchmarks pour backend)
    accessibility: int   # 0-100 (WCAG pour front-end, sécurité pour backend)
    ecology: int         # 0-100 (poids bundle pour front-end, efficacité pour backend)
    stability: int       # 0-100 (variation dans le temps)
    adoption: int        # 0-100 (nombre d'utilisateurs)
    validation: int      # 0-100 (score DOUBLE-CHECK d'AETHERFLOW)
    
    @property
    def total(self) -> float:
        return (performance * 0.25 +
                accessibility * 0.25 +
                ecology * 0.15 +
                stability * 0.10 +
                adoption * 0.10 +
                validation * 0.15)  # Intègre validation AETHERFLOW
```

**Note** : Le score intègre la validation DOUBLE-CHECK d'AETHERFLOW pour garantir la qualité technique.

### **3.4. Interface Utilisateur : Homeos Studio**

#### **3.4.1. Vue "MakerPad"**
- **Panneau d'input** :
  - Upload plan JSON (drag & drop) ✅ **MVP**
  - Upload design (Figma, image) ⏳ **Phase 3**
  - Description textuelle ⏳ **Phase 3**
  
- **Panneau de workflow** :
  - Sélection workflow : **PROTO** (FAST) ou **PROD** (BUILD)
  - Visualisation des étapes du plan JSON
  - Statuts en temps réel (⏳ Running, ✅ Success, ❌ Failed)
  - Option Mentor Mode (feedback pédagogique AETHERFLOW)
  - Métriques live (temps, coûts, tokens) via WebSocket
  
- **Panneau de sortie** :
  - Code généré avec syntax highlighting
  - Visualisation (si front-end HTML/CSS)
  - Métriques (temps total, coût, tokens, cache hits)
  - Score Homeos (si calculé)
  - Feedback mentor (si activé)

**Note** : L'interface communique avec AETHERFLOW Backend via API REST et WebSocket.

#### **3.4.2. Dashboard d'Homéostasie**
- Visualisation en temps réel de l'équilibre de la bibliothèque.
- Graphiques : qualité moyenne, nombre de composants, utilisation.
- Alertes : déséquilibres détectés.

### **3.5. Module de Déploiement (Homeos Deploy)**
- Export de projet (ZIP, Git).
- Déploiement sur GitHub Pages, Netlify, Vercel.
- Intégration CI/CD.

---

## **4. Offres Commerciales et Tarification**

### **4.1. Homeos BASIC (Gratuit)**
- Mode FAST uniquement.
- 1 interface par session (pas de sauvegarde).
- Visualisation de l'homéostasie globale (lecture seule).
- Pas de déploiement.

### **4.2. Homeos PLAY (5€/mois) - "BYOK Intelligent"**
- Mode BUILD (10 générations/mois).
- Cache privé personnel.
- Téléchargement des composants stables de la Homeos Library.
- Déploiement GitHub Pages.

**Options d'inférence (vous pouvez choisir l'une ou l'autre selon ce que vous possédez)** :

- ✅ **Option A : BYOK (Clé API Claude)** : Utilisez votre propre clé Claude API pour une planification premium (qualité maximale). Coûts : ~$0.021 par plan (à votre charge, pay-per-use).
- ✅ **Option B : BYOC (Abonnement Cursor Pro)** : Utilisez votre abonnement Cursor Pro (Claude Code) pour la planification. Gratuit si vous avez déjà Cursor Pro (20-30€/mois).
- ✅ **Option C : BYOC (Abonnement Claude Pro/MAX)** : Utilisez votre abonnement Claude.ai (Claude Pro ou Claude MAX) pour la planification. Utilise votre quota d'abonnement Claude.ai.

**Par défaut** : Gemini 3 Pro (économique, qualité très bonne, inclus dans l'abonnement).

**Valeur** : "Soit 3x plus de plans qu'avec Claude seul"

### **4.3. Homeos CREATE (9,90€/mois)**
- Générations illimitées (modes FAST et BUILD).
- Contribution à la Homeos Library (partage de composants).
- Score d'homéostasie personnel.
- Déploiement complet (Netlify, Vercel, etc.).
- Export de projets.

**Options d'inférence par abonnement (BYOC)** :

#### **Solution #1 : Cursor Rules (0 installation)**
- **Gratuit** si vous avez déjà Cursor Pro (20-30€/mois)
- Ajoutez `homeos-rules.md` dans votre repo
- Tapez "HomeOS Phase X" → Plan généré automatiquement via Claude Code
- **Usage** : 500-1000 tâches/mois avec votre abonnement Cursor Pro existant
- **Coût supplémentaire** : 0€ (utilise votre Cursor Pro)

#### **Solution #2 : HomeOS Studio Web (Recommandé)**
- **Prix** : 9,90€/mois (accès web + 500 plans Claude Code optimisés)
- Portail web unique (`homeos.studio`)
- Connexion Cursor Pro via OAuth (1-clic)
- Génération de plans via Claude Code en arrière-plan
- Historique des plans, métriques, analytics
- **Valeur** : Transforme vos 500 messages Claude Pro en 1000+ tâches complètes/mois

#### **Solution #3 : CLI Magic Command (Mac uniquement)**
- Installation globale : `npm install -g @homeos/cli`
- Commande unique : `homeos plan phase1`
- Utilise votre Cursor Pro existant (spawn Cursor headless)
- **Coût supplémentaire** : 0€ (utilise votre Cursor Pro)

**Options d'inférence (vous pouvez choisir l'une ou l'autre selon ce que vous possédez)** :

#### **Option A : BYOK (Clé API Claude)**
- Utilisez votre propre **clé API Claude** (pay-per-use)
- Coûts : ~$0.021 par plan (à votre charge)
- Qualité : Excellente, contrôle total
- Pour qui : Utilisateurs qui préfèrent payer à l'usage plutôt qu'un abonnement mensuel

#### **Option B : BYOC (Abonnement Cursor Pro)**
- Utilisez votre **abonnement Cursor Pro** existant (20-30€/mois)
- Coûts : 0€ supplémentaire (utilise votre abonnement)
- Qualité : Excellente, via Claude Code
- Solutions : Cursor Rules, Studio Web, ou CLI Magic (voir ci-dessus)

#### **Option C : BYOC (Abonnement Claude Pro/MAX)**
- Utilisez votre **abonnement Claude.ai** existant (Claude Pro ou Claude MAX)
- Coûts : Utilise votre quota d'abonnement Claude.ai
- Qualité : Excellente, via API Claude avec votre abonnement
- Pour qui : Utilisateurs qui ont déjà un abonnement Claude Pro ou Claude MAX

**Par défaut** :
- Gemini 3 Pro (économique, qualité professionnelle, inclus dans l'abonnement).

**Argument commercial** :
- "9,90€/mois vs 20€ pour Cursor, avec une empreinte écologique 5x plus faible"
- "Multipliez l'efficacité de votre Cursor Pro par 2-3x (500 messages → 1000+ tâches)"

### **4.4. Homeos INSTITUTE (50€/poste/an)**
- Toutes les fonctionnalités CREATE.
- Instance dédiée (isolation des données).
- Dashboard administrateur.
- Gestion des utilisateurs (enseignants/étudiants).
- Support prioritaire et formation.

---

## **5. Scénarios d'Utilisation**

### **5.1. Enseignant en DNMADE**
- **Objectif** : Enseigner l'accessibilité web.
- **Utilisation** :
  1. Génère un plan JSON pour un formulaire accessible (ou upload design).
  2. Sélectionne workflow **PROD** (BUILD) dans Homeos Studio.
  3. Homeos envoie le plan à AETHERFLOW Backend.
  4. AETHERFLOW génère le code (FAST → BUILD → DOUBLE-CHECK).
  5. Homeos Engine calcule le score Homeos (accessibilité WCAG).
  6. Montre le code généré et le score d'accessibilité.
  7. Si score ≥ 85, propose de partager dans la bibliothèque Élite.
- **Valeur** : Pédagogie par l'exemple, gain de temps, code validé par AETHERFLOW.

### **5.2. Étudiant en NSI**
- **Objectif** : Prototyper une application web pour un projet.
- **Utilisation** :
  1. Utilise le workflow **PROTO** (FAST) pour explorer des idées rapidement.
  2. Upload plan JSON simple via Homeos Studio.
  3. Homeos envoie à AETHERFLOW Backend.
  4. AETHERFLOW génère rapidement (FAST → DOUBLE-CHECK).
  5. Passe au workflow **PROD** (BUILD) pour obtenir du code production.
  6. Homeos Engine calcule le score Homeos.
  7. Déploie sur GitHub Pages via Homeos Deploy.
- **Valeur** : Apprentissage des bonnes pratiques, rapidité, code validé.

### **5.3. Développeur Indépendant**
- **Objectif** : Livrer un projet front-end pour un client.
- **Utilisation** :
  1. Upload d'une maquette Figma.
  2. Homeos génère le code production (mode BUILD).
  3. Utilise des composants de la Homeos Library pour gagner du temps.
  4. Déploie sur Netlify.
- **Valeur** : Réduction du temps de développement, code de qualité.

---

## **6. Roadmap Complète**

### **Phase 0 : Alternative Portable avec Claude API (1 semaine)** 🔥 **PRIORITAIRE**

**Objectif** : Créer une version indépendante de Cursor Pro.

**Actions** :
- [ ] Intégrer Claude API dans AETHERFLOW
- [ ] Créer module de planification avec Claude API
- [ ] Limiter Claude API à planification + révision uniquement
- [ ] Déléguer validation/exécution à AETHERFLOW (Gemini/DeepSeek)
- [ ] Tester coûts et performance
- [ ] Documenter l'alternative portable

**Résultat attendu** :
- Version portable fonctionnelle
- Coût : ~$0.022 par plan (vs $0.048 sans Homeos)
- Réduction : 42% d'utilisation Claude (facteur 1.73x)
- Indépendance de Cursor Pro

### **Phase 1 : MVP Homeos Front-End (2 semaines)** ✅ **EN COURS**

- [x] Interface Homeos Studio (HTML/CSS/JS vanilla)
- [x] Intégration à AETHERFLOW Backend (API `/execute`)
- [ ] Upload plan JSON (drag & drop)
- [ ] Visualisation workflow temps réel
- [ ] Affichage résultats avec syntax highlighting
- [ ] Métriques live (WebSocket)
- [ ] Option Mentor Mode

### **Phase 2 : Homeos Engine (3 semaines)** ⏳

- [ ] Cache local utilisateur (Niveau 0)
- [ ] Calcul score Homeos basique
- [ ] Serveur bibliothèque Élite (Niveau 1)
- [ ] Système suggestion partage
- [ ] Tests automatiques (accessibilité, performance)
- [ ] Intégration avec cache sémantique AETHERFLOW

### **Phase 3 : Génération Front-End (4 semaines)** ⏳

- [ ] Génération HTML/CSS/JS depuis plans JSON
- [ ] Upload design (Figma, image)
- [ ] Analyse design → plan JSON automatique
- [ ] Validation Lighthouse/WCAG automatique
- [ ] Packaging DMG (version locale pour écoles)

### **Phase 4 : Sullivan Kernel MVP (4 semaines)** ⏳

- [ ] Cloner DeepSeek-Coder-7B
- [ ] Configurer environnement d'entraînement
- [ ] Collecter 5,000+ traces d'orchestration
- [ ] Fine-tuning SFT initial
- [ ] Évaluation vs Claude API
- [ ] Version 0.1 prête pour tests

### **Phase 5 : Sullivan Kernel Production (4 semaines)** ⏳

- [ ] Reinforcement Learning (RLHF)
- [ ] Quantization 4-bit
- [ ] Tests sur Mac 2016
- [ ] Déploiement shadow mode
- [ ] A/B testing vs Claude API
- [ ] Déploiement 50% trafic

### **Phase 6 : Intelligence Collective (2 semaines)** ⏳

- [ ] Base connaissance structurelle (Niveau 2)
- [ ] Insights automatiques
- [ ] Recommandations contextuelles
- [ ] Dashboard homéostasie
- [ ] CDN pour distribution composants
- [ ] API publique pour développeurs

---

## **7. Métriques de Succès**

### **7.1. Métriques Utilisateurs**
- Nombre d'utilisateurs actifs (MAU).
- Taux de conversion (gratuit → payant).
- Score de satisfaction (NPS).

### **7.2. Métriques Produit**
- Temps moyen de génération (mode BUILD).
- Score Homeos moyen des composants générés.
- Taux de réutilisation des composants de la Homeos Library.

### **7.3. Métriques Techniques**
- Temps de réponse de l'API.
- Disponibilité du service (uptime).
- Coût par utilisateur.
- Réduction utilisation Claude (facteur 1.73x avec alternative portable, 38x avec Sullivan Kernel).

---

## **8. Risques et Atténuations**

### **8.1. Risque : Qualité variable des composants mutualisés.**
- **Atténuation** : Validation stricte (score ≥ 85, tests automatiques, validation par les pairs).

### **8.2. Risque : Adoption faible du mode BUILD (trop long).**
- **Atténuation** : Éducation via l'interface (montrer la valeur du code production), amélioration continue de l'expérience utilisateur.

### **8.3. Risque : Coûts d'infrastructure.**
- **Atténuation** : Architecture économe (cache agressif, CDN seulement si nécessaire), tarification adaptée.

### **8.4. Risque : Dépendance à Claude API (Alternative Portable).**
- **Atténuation** : Phase transitoire vers Sullivan Kernel, fallback vers DeepSeek si Claude indisponible.

### **8.5. Risque : Qualité Sullivan Kernel insuffisante.**
- **Atténuation** : Fallback vers Claude API si confiance < 70%, collecte données ciblées pour amélioration.

---

## **9. Architecture Technique**

### **9.1. Stack Technique**

**Backend (AETHERFLOW)** :
- Python 3.11+
- FastAPI (API REST + WebSocket)
- Orchestrator (exécution plans)
- Cache sémantique (embeddings)
- Workflows PROTO/PROD

**Front-End (Homeos Studio)** :
- HTML5/CSS3/JavaScript vanilla
- WebSocket API (streaming temps réel)
- Prism.js ou Highlight.js (syntax highlighting)
- Chart.js (métriques graphiques)

**Homeos Engine** :
- Python (module AETHERFLOW)
- Base de données composants (SQLite ou PostgreSQL)
- Système scoring Homeos
- API bibliothèque Élite

**Planification (Alternative Portable / Sullivan Kernel)** :
- Claude API (Phase 0) : Anthropic API
- Sullivan Kernel (Phase 1+) : DeepSeek-Coder-7B + llama.cpp

### **9.2. Communication Backend ↔ Front-End**

```
Homeos Studio (Front-End)
    ↕ HTTP REST + WebSocket
AETHERFLOW API (FastAPI)
    ↕ Python modules
AETHERFLOW Orchestrator
    ↕ Providers (DeepSeek, Gemini, Groq, Codestral)
Homeos Engine
    ↕ Cache + Bibliothèque Élite
Planification (Claude API / Sullivan Kernel)
    ↕ Génération plan.json
```

### **9.3. Nommage Technique**

- **Code interne** : Conserve le nom "AETHERFLOW" (classes, modules, fichiers)
- **API publique** : Utilise "Homeos" dans les endpoints (`/api/homeos/...`)
- **Interface utilisateur** : Branding "Homeos" partout
- **Documentation technique** : Référence "AETHERFLOW" pour développeurs

---

## **10. Coûts et ROI**

### **10.1. Coûts Claude API**

| Scénario | Coût par plan | Plans/mois ($100) | Facteur |
|----------|---------------|-------------------|---------|
| **Claude Code (Cursor)** | $0.00 | ∞ | - |
| **Claude API (tout)** | $0.038 | 2,632 | 1.0x |
| **Claude API + Homeos** | $0.022 | 4,545 | **1.73x** |
| **Sullivan Kernel** | $0.001 | 100,000 | **38x** |

### **10.2. ROI Alternative Portable**

- **Coût développement** : 1 semaine FTE
- **Coût mensuel** : $0.022 × 300 plans = $6.60/mois
- **Économie** : 42% vs utilisation Claude complète
- **ROI** : Immédiat (solution transitoire)

### **10.3. ROI Sullivan Kernel**

- **Coût développement** : ~$5,000
- **Coût mensuel** : $0.001 × 300 plans = $0.30/mois
- **Économie** : 95% vs Claude API
- **ROI** : ~13 ans (mais valeur indépendance inestimable)

---

## **11. Conclusion**

Homeos est une plateforme innovante qui allie génération d'IA via AETHERFLOW Backend, mutualisation intelligente et homéostasie pour produire du code de haute qualité (front-end et backend). Son positionnement sur l'éducation et la sobriété en fait un outil unique sur le marché.

**Stratégie de déploiement** :
1. **Phase 0** : Alternative portable avec Claude API (indépendance Cursor Pro)
2. **Phase 1** : Homeos Front-End (interface complète)
3. **Phase 2** : Homeos Engine (mutualisation intelligente)
4. **Phase 4+** : Sullivan Kernel (indépendance totale)

**Prochaines étapes immédiates :**
1. Implémenter l'alternative portable (Phase 0)
2. Finaliser Homeos Front-End MVP (Phase 1)
3. Commencer développement Sullivan Kernel (Phase 4)

---

**Approbations :**
- [ ] Product Manager
- [ ] Lead Developer
- [ ] Marketing
- [ ] CEO

**Date de révision :** 27 janvier 2025
**Version :** 2.2

---

Ce PRD est un document vivant et sera mis à jour au fur et à mesure de l'avancement du projet.
