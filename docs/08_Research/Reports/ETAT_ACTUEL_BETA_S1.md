# État Actuel AETHERFLOW - Beta S1 (1 semaine)

**Date** : 27 janvier 2025  
**Objectif** : Beta testable avec amis dans 1 semaine

---

## ✅ Ce qui EXISTE déjà

### **Backend AETHERFLOW**

#### **1. Orchestrator** ✅ **FONCTIONNEL**
- **Fichier** : `Backend/Prod/orchestrator.py`
- **Fonctionnalités** :
  - ✅ Exécution de plans JSON
  - ✅ Workflows PROTO (FAST → DOUBLE-CHECK)
  - ✅ Workflows PROD (FAST → BUILD → DOUBLE-CHECK)
  - ✅ Parallélisation des étapes indépendantes
  - ✅ Rate limiting par provider
  - ✅ Métriques complètes (temps, coûts, tokens)
  - ✅ Support RAG (enrichissement contexte)
  - ✅ Cache sémantique et prompt cache

#### **2. API FastAPI** ✅ **OPÉRATIONNELLE (basique)**
- **Fichier** : `Backend/Prod/api.py`
- **Endpoints existants** :
  - ✅ `POST /execute` : Exécute un plan JSON
  - ✅ `GET /health` : Health check
- **Fonctionnalités** :
  - ✅ Accepte `plan_path` (chemin vers fichier JSON)
  - ✅ Retourne résultats avec métriques
  - ✅ Gestion d'erreurs basique

#### **3. Workflows** ✅ **FONCTIONNELS**
- **Fichiers** :
  - `Backend/Prod/workflows/proto.py` : Workflow PROTO
  - `Backend/Prod/workflows/prod.py` : Workflow PROD
- **Fonctionnalités** :
  - ✅ PROTO : FAST → DOUBLE-CHECK (prototypage rapide)
  - ✅ PROD : FAST → BUILD → DOUBLE-CHECK (qualité maximale)

#### **4. Plan Reader** ✅ **FONCTIONNEL**
- **Fichier** : `Backend/Prod/models/plan_reader.py`
- **Fonctionnalités** :
  - ✅ Lecture et validation de plans JSON
  - ✅ Support schéma Pydantic
  - ✅ Gestion dépendances entre étapes

---

## ❌ Ce qui MANQUE pour la Beta S1

### **1. Frontend Homeos Studio** ❌ **À CRÉER**

**État actuel** :
- Dossier `Frontend/` existe mais vide (juste un README)
- Aucun fichier HTML/CSS/JS

**Besoin pour Beta S1** :
- ✅ Upload plan JSON (drag & drop)
- ✅ Affichage code généré avec syntax highlighting
- ✅ Métriques basiques (temps, coûts, tokens)
- ✅ Interface simple et fonctionnelle

**Stack recommandé** : HTML/CSS/JS Vanilla (compatibilité Mac 2016)

### **2. API - Upload de Plans** ❌ **À CRÉER**

**État actuel** :
- Endpoint `/execute` existe mais nécessite `plan_path` (chemin fichier local)
- Pas d'endpoint pour upload de fichiers JSON

**Besoin pour Beta S1** :
- ✅ `POST /upload-plan` : Upload fichier JSON
- ✅ Validation du schéma plan
- ✅ Stockage temporaire du plan
- ✅ Retourne `plan_id` pour exécution

### **3. API - Support JSON dans /execute** ⚠️ **À AMÉLIORER**

**État actuel** :
- `/execute` accepte seulement `plan_path` (chemin fichier)
- Nécessite que le fichier soit déjà sur le serveur

**Besoin pour Beta S1** :
- ✅ Option 1 : Accepter `plan_id` (après upload)
- ✅ Option 2 : Accepter `plan_json` directement (body JSON)
- ✅ Option 2 recommandée pour simplicité

### **4. Système de Comptes** ❌ **À CRÉER**

**État actuel** :
- Aucun système d'authentification
- Pas de gestion utilisateurs

**Besoin pour Beta S1** :
- ✅ Authentification basique (email/password)
- ✅ Stockage utilisateurs (SQLite pour simplicité)
- ✅ Sessions (JWT ou cookies)
- ✅ Endpoints : `/register`, `/login`, `/logout`
- ✅ Middleware auth pour protéger `/execute`

### **5. Système de Quota** ❌ **À CRÉER**

**Besoin pour Beta S1** :
- ✅ Tracking générations par utilisateur
- ✅ Limite : 500 générations par utilisateur
- ✅ Stockage dans base de données
- ✅ Vérification avant exécution
- ✅ Endpoint `/quota` pour voir quota restant

### **6. WebSocket (Optionnel pour Beta S1)** ⏳ **NICE TO HAVE**

**État actuel** :
- Pas de WebSocket
- Pas de streaming temps réel

**Pour Beta S1** :
- ⏳ Pas nécessaire (peut être ajouté après)
- ✅ L'utilisateur peut attendre la réponse complète

---

## 📋 Plan d'Action pour Beta S1 (1 semaine)

### **Jour 1-2 : Backend API**

#### **Tâche 1.1 : Endpoint Upload Plan**
```python
POST /upload-plan
- Accepte fichier JSON (multipart/form-data)
- Valide schéma avec PlanReader
- Stocke temporairement (ou en mémoire)
- Retourne plan_id
```

#### **Tâche 1.2 : Améliorer /execute**
```python
POST /execute
- Accepter soit plan_path (existant) soit plan_json (nouveau)
- Si plan_json fourni, utiliser directement
- Sinon, utiliser plan_path comme avant
```

#### **Tâche 1.3 : Système de Comptes**
```python
- Créer models/user.py (User model SQLite)
- Créer api/auth.py (endpoints register/login/logout)
- Créer middleware auth pour protéger /execute
- Utiliser JWT ou sessions simples
```

#### **Tâche 1.4 : Système de Quota**
```python
- Ajouter champ `generations_count` dans User model
- Vérifier quota avant exécution
- Incrémenter après exécution réussie
- Endpoint GET /quota pour voir quota restant
```

### **Jour 3-4 : Frontend Basique**

#### **Tâche 2.1 : Structure Frontend**
```
Frontend/
├── index.html          # Page principale
├── css/
│   └── styles.css      # Styles
├── js/
│   ├── app.js          # Logique principale
│   ├── api.js          # Appels API
│   └── syntax.js       # Syntax highlighting
└── assets/
    └── icons/
```

#### **Tâche 2.2 : Page Login/Register**
- Formulaire login (email/password)
- Formulaire register (email/password)
- Gestion sessions (localStorage ou cookies)

#### **Tâche 2.3 : Page Dashboard**
- Upload plan JSON (drag & drop)
- Sélection workflow (PROTO/PROD)
- Bouton "Générer"
- Affichage résultats avec syntax highlighting
- Métriques basiques (temps, coûts, tokens)
- Quota restant affiché

### **Jour 5 : Intégration et Tests**

#### **Tâche 3.1 : Intégration Frontend ↔ Backend**
- Tester upload plan
- Tester exécution
- Tester affichage résultats
- Tester quota

#### **Tâche 3.2 : Tests Utilisateurs**
- Tester avec 2-3 amis
- Vérifier que tout fonctionne
- Corriger bugs critiques

### **Jour 6-7 : Polish et Déploiement**

#### **Tâche 4.1 : Améliorations UX**
- Messages d'erreur clairs
- Loading states
- Feedback visuel

#### **Tâche 4.2 : Déploiement**
- Déployer backend (Railway, Render, ou VPS)
- Déployer frontend (Netlify, Vercel, ou même GitHub Pages)
- Configurer CORS
- Tester en production

---

## 🔧 Stack Technique Recommandée

### **Backend**
- ✅ FastAPI (déjà utilisé)
- ✅ SQLite (simplicité, pas besoin PostgreSQL pour beta)
- ✅ JWT ou sessions simples (pas besoin OAuth pour beta)
- ✅ python-multipart (pour upload fichiers)

### **Frontend**
- ✅ HTML/CSS/JS Vanilla (pas de framework lourd)
- ✅ Prism.js ou Highlight.js (syntax highlighting)
- ✅ Fetch API (appels HTTP)
- ✅ Pas de build step (fichiers statiques)

---

## 📊 Endpoints API à Créer

### **Authentification**
```
POST /register
POST /login
POST /logout
GET /me (info utilisateur actuel)
```

### **Plans**
```
POST /upload-plan (upload fichier JSON)
POST /execute (exécuter plan, avec plan_json ou plan_id)
GET /quota (quota restant)
```

### **Existant (à garder)**
```
GET /health
```

---

## 🎯 Critères de Succès Beta S1

- ✅ Un utilisateur peut créer un compte (email/password)
- ✅ Un utilisateur peut uploader un plan JSON
- ✅ Un utilisateur peut exécuter le plan
- ✅ Le code généré s'affiche avec syntax highlighting
- ✅ Les métriques s'affichent (temps, coûts, tokens)
- ✅ Le quota est tracké (500 générations max)
- ✅ Tout fonctionne en production (déployé)

---

## ⚠️ Ce qui N'EST PAS nécessaire pour Beta S1

- ❌ Stripe (paiement)
- ❌ Dashboard admin
- ❌ Certificat SSL (peut utiliser HTTP pour beta interne)
- ❌ WebSocket (streaming temps réel)
- ❌ Historique des exécutions (peut être ajouté après)
- ❌ Export de fichiers (peut être ajouté après)

---

## 🚀 Commandes pour Démarrer

### **Backend**
```bash
# Activer venv
source venv/bin/activate

# Installer dépendances si nécessaire
pip install fastapi uvicorn python-multipart sqlalchemy

# Lancer API (à créer script de démarrage)
python -m Backend.Prod.api
# ou
uvicorn Backend.Prod.api:app --host 0.0.0.0 --port 8000
```

### **Frontend**
```bash
# Servir fichiers statiques (simple serveur HTTP)
cd Frontend
python -m http.server 3000
# ou utiliser nginx/apache
```

---

## 📝 Notes Importantes

1. **Simplicité d'abord** : Pour la beta, on privilégie la simplicité et la rapidité
2. **SQLite OK** : Pas besoin PostgreSQL pour beta, SQLite suffit
3. **Pas de build** : Frontend vanilla, pas de webpack/vite
4. **Quota hardcodé** : 500 générations, peut être changé après
5. **Pas de sécurité avancée** : Auth basique suffit pour beta interne

---

**Dernière mise à jour** : 27 janvier 2025
