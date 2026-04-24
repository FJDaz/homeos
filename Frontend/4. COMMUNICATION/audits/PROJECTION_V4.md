# PROJECTION V4 — Maiathon / HoméOS

**Document maître.** Rédigé par Claude Opus 4.6, validé FJD 2026-04-15.
Source de vérité pour toute mission V4. À lire avant toute autre doc.

---

## 0. Contexte de décision

Le système actuel (V3, HoméOS) présente des défauts architecturaux fondamentaux accumulés par patchs successifs : double source de vérité DB/JSON, SQLite sync dans handlers async, absence de migrations versionnées, pas de vérification email, pas de RGPD, pas de plans, pas d'isolation tenant, pas d'observabilité.

**Décision FJD 2026-04-15 :** refonte V4 sur fondations solides, avec **Supabase comme backbone**, séquencée en phases de valeur démontrable, zéro budget initial, time-to-demo maximal 6 semaines.

**Ce document :**
- Définit les **phases de valeur** (0 → F) et leur ordre strict
- Liste toutes les **missions Phase 0-MVP et Phase A** (démo élève)
- Ébauche les **missions Phase B → F** (à détailler plus tard)
- Fixe les **garde-fous transverses** (invariants inviolables)
- Précise les **critères de sortie** de chaque phase (validation FJD)

**À lire en complément :** `ARCHITECTURE_V4.md` (stack, schéma DB, API, auth, deploy).

---

## 1. Stack V4 (zéro budget free-tier)

| Domaine | Service | Justification |
|---------|---------|---------------|
| DB + Auth + Storage + Realtime | **Supabase** (free 500MB + 1GB) | Postgres + JWT multi-rôles + email verif + reset + magic links + RLS + WebSockets + PITR 7j, tout en une ligne SDK |
| Email transactionnel | **Resend** (3000/mois free) | DKIM/SPF prêts, webhooks bounces |
| Hosting backend FastAPI | **Fly.io** ou **Railway** (free tiers) | Deploy depuis GitHub, env vars, logs |
| Hosting sites élèves/users | **Cloudflare Pages** (illimité free) | Publication statique, domaine custom plus tard |
| Error tracking | **Sentry** (5k events/mois free) | Stack traces + correlation ID |
| Uptime monitoring | **UptimeRobot** (50 checks free) | Alertes email |
| Code + CI/CD | **GitHub** + **Actions** (free) | Secrets, workflows, releases |
| Moteur LLM (existant) | **AetherFlow** (Backend/Prod/) simplifié | Réutilisation, pas de réécriture |

**Budget mensuel total : 0€** jusqu'à quelques centaines d'utilisateurs actifs. Au-delà, paliers payants progressifs (≈ 25€/mois à 1000 utilisateurs, ≈ 200€/mois à 10k).

---

## 2. Séquence des phases

**Règle fondamentale :** chaque phase est autonome, déployable, démontrable. Pas de démarrage Phase suivante sans **validation FJD** de la phase courante.

```
Phase 0-MVP   Fondation (bloquant total)              Semaines 1-2
Phase A       Demo Student (parcours élève E2E)       Semaines 3-5
Phase B       Parcours Teacher + notation             Semaines 6-8
Phase C       Parcours User (indépendant)             Semaines 9-10
Phase D       Cohabitation + double identité          Semaine 11
Phase 0-LAUNCH Pré-production publique                Semaines 12-13
Phase E       Stripe + plans free/Pro/Total           Semaines 14-16
Phase F       Ouverture hexagonale (ongoing)          Continu
```

### Phase 0-MVP — Fondation (bloquant total, Semaines 1-2)

**Objectif :** produire les fondations sur lesquelles tout le reste sera construit sans avoir à y revenir. Supabase assumé comme backbone, auth Supabase adoptée, système maison retiré.

**Livrables :**
- Projet Supabase créé avec schéma V4 complet appliqué via migrations Alembic
- Module `supabase_client.py` uniformisé, ancien auth maison supprimé
- Login racine superadmin (créé au boot)
- Mode inscription configurable (invite par défaut pour démo)
- Configuration Pydantic Settings, zéro secret hardcodé
- API `/api/v1/` avec format erreur uniforme
- Logs structurés JSON avec correlation IDs
- Storage abstraction (local dev → Supabase Storage prod)
- Job queue : interface `BackgroundJobs` (inline pour MVP, vraie queue plus tard)
- Seed de test (1 superadmin, 1 teacher, 2 classes, 5 élèves, 3 projets)
- Tests critiques : login, activation projet, déploiement statique
- Health check profond (`/api/v1/health`)

**Critère de sortie :** tout ci-dessus tourne sur DB vierge via `make seed`, login superadmin fonctionnel, email verif testé, 3 tests critiques verts. **Validation FJD requise.**

**Ce qui est exclu de Phase 0-MVP (reporté à Phase 0-LAUNCH) :**
- RGPD complet (consentement parental, export données, audit consents avancé)
- Sentry en production active (installé mais pas encore branché)
- Backup custom (PITR Supabase suffit en MVP)
- Modération de contenu (pas d'URL publique encore)
- i18n wrapper (français only assumé)
- Multi-tenant RLS complet (single-tenant pour démo, `organization_id` présent partout)

### Phase A — Demo Student (Semaines 3-5)

**Objectif produit :** un élève arrive sans compte, crée quelque chose, obtient une URL publique en moins de 10 minutes. C'est la seule mesure de succès qui compte.

**Parcours cible :**
1. Élève reçoit un code de classe (6 caractères) de son teacher
2. Arrive sur `/join` → entre code de classe + prénom
3. Supabase crée un compte (magic link optionnel ou anonyme)
4. Atterrit dans workspace minimaliste
5. Onboarding 3 étapes (nom projet → 3 écrans → liens)
6. Clic "publier" → backend génère HTML statique → push Cloudflare Pages → URL retournée
7. L'URL est affichée, copiable, partageable

**Livrables :**
- Page `/join` (code classe + prénom)
- Workspace simplifié (pas de FEE, pas de drills complexes)
- Éditeur Wire minimal (ajout écran, édition nom, ajout lien entre écrans)
- Preview live intégré
- Pipeline déploiement : génome projet → HTML statique → Cloudflare Pages
- URL publique stockée en DB et affichée
- Takedown rapide (`published = false`)

**Critère de sortie :** FJD (ou un testeur naïf) passe le parcours complet sur URL de prod Fly.io en moins de 10 minutes. URL publique accessible. Pas de bug bloquant. **Validation FJD requise.**

### Phase B — Teacher + notation (Semaines 6-8)

**Parcours cible :**
1. Teacher arrive, crée une classe → invite_code généré
2. Crée un sujet (titre, description, optionnel PDF de référentiel)
3. Attache le sujet à la classe
4. Les élèves de la classe voient le sujet lors de leur parcours (Phase A s'applique)
5. Teacher voit dashboard temps réel de progression
6. Élève publie → notation auto selon rubric (LLM check versus référentiel)
7. Teacher voit note + commentaire, peut ajuster manuellement

**Livrables :**
- Interface création classe + sujet
- Rubric JSON structurée
- Dashboard teacher (liste classes + progression élèves)
- Realtime Supabase : progression élève visible en direct (polling 5s acceptable au départ)
- Pipeline notation automatique (orchestration LLM via AetherFlow moteur simplifié)
- Interface ajustement manuel note + export

**Critère de sortie :** FJD teste le flow teacher complet avec 2 élèves de test, obtient 2 notes automatiques cohérentes avec la rubric. **Validation FJD requise.**

### Phase C — User (Semaines 9-10)

**Parcours cible :** identique à Phase A mais sans contexte classe. L'utilisateur s'inscrit librement (ou sur invitation selon mode), crée un projet, publie.

**Livrables :**
- Page `/signup` (email + password, vérification email)
- Mode inscription `open` activable dans config
- Workspace user (même UI que student, sans contexte sujet)
- Pas de dashboard teacher visible pour un user
- Projets user stockés avec `owner_user_id`, pas de `student_id`

**Critère de sortie :** un user invité via lien tokenisé arrive, crée un projet, publie, obtient URL. **Validation FJD requise.**

### Phase D — Cohabitation (Semaine 11)

**Règle produit fondamentale :** un élève peut aussi être un user à titre personnel. Même identifiant, rôles cumulés.

**Livrables :**
- Table `user_roles` fonctionnelle en multi-rôles
- Interface de sélection de contexte (switch entre "mode classe X" et "mode perso")
- Projets filtrés par contexte actif (projets classe vs projets perso)
- Permissions correctement appliquées (un élève-user ne voit pas les autres élèves de sa classe dans son mode user)

**Critère de sortie :** un compte de test avec rôles élève + user passe entre les deux contextes sans fuite de données. **Validation FJD requise.**

### Phase 0-LAUNCH — Pré-production publique (Semaines 12-13)

**Objectif :** tout ce qui n'était pas bloquant en MVP mais est obligatoire avant d'ouvrir à des utilisateurs réels (notamment mineurs).

**Livrables :**
- RGPD complet : consentement parental pour < 15 ans, export données `GET /api/v1/users/me/export`, suppression complète `DELETE /api/v1/users/me`, table `consents` opérationnelle
- Sentry branché en prod (erreurs non-sensibles uniquement)
- UptimeRobot configuré (health + homepage)
- Modération : endpoint `POST /api/v1/reports`, table `reports`, workflow admin basique, takedown rapide
- ToS + Privacy Policy hébergées (deux pages statiques, versionnées)
- Rate limiting en prod (login, register, reset)
- Backup strategy documentée (même si Supabase PITR suffit)
- Audit des routes publiques (aucune fuite de données)

**Critère de sortie :** pentest léger par FJD (ou un ami) ne trouve pas de faille évidente. Conformité RGPD vérifiée. **Validation FJD requise.**

### Phase E — Stripe + plans (Semaines 14-16)

**Objectif :** monétisation. Plans free / Pro / Total activables par utilisateur. Architecture extensible à N tiers futurs.

**Livrables :**
- Table `plans` seedée (free, Pro, Total)
- Table `subscriptions` liée à Stripe
- Intégration Stripe Checkout (paiement one-shot ou récurrent)
- Webhook Stripe sécurisé (`stripe-signature` vérifiée)
- Feature flags par plan (table `features` + matrix)
- Interface upgrade/downgrade dans l'UI
- Facturation (export invoices PDF, TVA FR)

**Critère de sortie :** FJD souscrit un plan Pro avec carte de test Stripe, webhook arrive, accès feature Pro débloqué, facture générée. **Validation FJD requise.**

### Phase F — Ouverture hexagonale (Continu)

Chaque feature est un hexagone extensible sans réécriture noyau.

**Candidats FEE :**
- Timeline GSAP UI (drag & drop keyframes)
- Asset manager (images, vidéos, fontes)
- Library de presets animations
- Import ScrollTrigger / Pin / Observer
- Export code clean (HTML + CSS + JS minifiés)

**Candidats Deploy :**
- Custom domains
- Staging URL vs production URL
- Analytics basiques (visites anonymisées)
- Preview par branche (Cloudflare Pages preview)

**Candidats Wire :**
- Collaboration temps réel (plusieurs élèves sur un projet)
- Version history (rollback)
- Commentaires sur screens

**Candidats Moteur AetherFlow :**
- LangGraph intégré (orchestration auto + fallback)
- Second architecte (Qwen/MIMO) intégré avec cascade
- Cost tracking par mission
- Métriques de qualité par agent

**Critère :** chaque extension doit pouvoir être conçue, développée, déployée, et si besoin désactivée sans affecter les phases précédentes. Chaque feature expose une **interface d'extension documentée** dans `docs/extensions/`.

---

## 3. Missions Phase 0-MVP (détaillées)

Chaque mission a un identifiant `V4-M0XX`, un ACTOR, des inputs, un livrable mesurable, un test de succès.

### V4-M001 — Setup projet Supabase + schéma de base
**ACTOR : CLAUDE** (code direct ou mission déléguée)
**DURÉE ESTIMÉE :** 1/2 journée
**DÉPENDANCES :** aucune (mission racine)

**Livrable :**
1. Projet Supabase créé (région europe-west)
2. Migrations Alembic initialisées dans `migrations/alembic/`
3. Migration `001_core_schema.sql` appliquée : tables `organizations`, `users`, `user_roles`, `plans` (voir ARCHITECTURE_V4.md section 3)
4. RLS activée sur toutes les tables (policies de base)
5. Seed plans free/pro/total dans la DB
6. Secrets Supabase dans `.env.example` (pas dans `.env`)

**Test de succès :** `alembic upgrade head` sur DB vierge produit le schéma. `alembic downgrade -1` rollback proprement. Seed plans visible via Supabase Studio.

**Garde-fous spécifiques :**
- Aucune colonne nullable non justifiée
- Toutes les FK ont `ON DELETE` explicite
- Tous les timestamps en `TIMESTAMPTZ`
- Tous les IDs en `UUID` (pas d'auto-increment)

### V4-M002 — Migration schéma content (classes, students, subjects, projects)
**ACTOR : CLAUDE**
**DÉPENDANCES :** V4-M001

**Livrable :**
- Migration `002_content_schema.sql` : tables `classes`, `students`, `subjects`, `subject_assignments`, `projects`, `screens`, `wirelinks`, `deployments`
- RLS policies correspondantes (voir ARCHITECTURE_V4.md section 4)
- Index de performance sur colonnes de lookup fréquent

**Test de succès :** création d'un record dans chaque table via Supabase SQL editor, RLS testée (teacher voit sa classe, pas celle d'un autre teacher).

### V4-M003 — Migration schéma compliance (consents, events, reports)
**ACTOR : CLAUDE**
**DÉPENDANCES :** V4-M002

**Livrable :**
- Migration `003_compliance_schema.sql` : `consents`, `events`, `reports`, `subscriptions`, `invoices`
- RLS policies strictes (seul admin lit events tous, user lit ses propres events)
- Triggers Postgres pour auto-log des actions sensibles dans `events`

**Test de succès :** UPDATE sur `users.display_name` déclenche une ligne dans `events` avec `event_type='user.updated'`.

### V4-M004 — Configuration Pydantic Settings
**ACTOR : CLAUDE**
**DÉPENDANCES :** V4-M001

**Livrable :**
- `Backend/Prod/config.py` avec `class Settings(BaseSettings)`
- Tous les secrets, URLs, feature toggles y sont déclarés avec types stricts
- Crash au boot si une variable requise manque
- `.env.example` exhaustif documenté
- `.env` ajouté à `.gitignore` si pas déjà fait (vérifier)

**Test de succès :** démarrage sans `.env` affiche un message d'erreur clair listant les variables manquantes. Démarrage avec `.env` valide charge propre.

**Garde-fous :** aucun `os.environ.get("X", "default")` dans le code métier après cette mission. Tout passe par `settings.X`.

### V4-M005 — Adoption auth Supabase (dépose l'ancien système)
**ACTOR : CLAUDE + GEMINI pour frontend**
**DÉPENDANCES :** V4-M001, V4-M004

**Livrable backend :**
- `Backend/Prod/auth/supabase_auth.py` : middleware FastAPI qui valide le JWT Supabase, extrait `user_id`, charge les rôles depuis `user_roles`
- Remplacement de `AuthMiddleware` dans `server_v3.py` (archivage de l'ancien)
- Helper `get_current_user(required_role=None)` en dépendance FastAPI
- Routes `/api/v1/auth/*` deviennent des proxies fins vers Supabase SDK (register, login, verify, reset)

**Livrable frontend :**
- Intégration `@supabase/supabase-js` dans les templates workspace + login
- `AuthManager.js` uniforme qui gère login/logout/session
- Retrait des anciennes cookies / localStorage maison (migration douce : lire ancien cookie → créer session Supabase équivalente → supprimer ancien)

**Test de succès :** le superadmin peut se connecter via email + mot de passe via l'UI, le JWT Supabase est stocké, une requête API authentifiée arrive avec le user_id correct injecté dans la dépendance FastAPI.

### V4-M006 — API v1 : structure + format erreur uniforme
**ACTOR : CLAUDE**
**DÉPENDANCES :** V4-M005

**Livrable :**
- Tous les routers existants préfixés `/api/v1/` (changement non rétrocompatible — ancien frontend mis à jour en conséquence)
- Handler d'exception global qui formate toutes les erreurs en `{ error: {code, message, detail} }`
- Codes d'erreur standardisés dans `Backend/Prod/errors.py` (enum)
- Suppression des routes non-/api/v1/ qui font du métier (exceptions : `/`, `/login`, `/workspace` = rendu HTML)

**Test de succès :** `curl /api/v1/nonexistent` retourne 404 au format standard. `curl` sur une route protégée sans token retourne 401 au format standard.

### V4-M007 — Logs structurés + correlation ID
**ACTOR : CLAUDE**
**DÉPENDANCES :** V4-M006

**Livrable :**
- Migration vers `structlog` (ou loguru configuré en JSON)
- Middleware qui génère un `correlation_id` par requête (uuid4) et l'attache au contexte logging
- Tous les appels à des services externes (Supabase, LLM) loguent avec ce correlation_id
- Logs JSON lisibles en dev (pretty print), JSON brut en prod

**Test de succès :** une requête qui fait 3 appels LLM produit 4 lignes de log (1 entrée + 3 sorties externes) toutes portant le même `correlation_id`.

### V4-M008 — Storage abstraction
**ACTOR : CLAUDE**
**DÉPENDANCES :** V4-M004

**Livrable :**
- Interface `Backend/Prod/storage/base.py` : `put(key, data)`, `get(key)`, `delete(key)`, `url_for(key)`, `list_prefix(prefix)`
- Implémentations : `LocalStorage` (dev, écrit dans `storage/` gitignore), `SupabaseStorage` (prod, Supabase Storage bucket)
- Choix via `settings.storage_backend`
- Buckets Supabase créés : `screens` (privé), `assets` (privé), `published-sites` (public-read)

**Test de succès :** en dev, un upload écrit dans `storage/`. En prod, même appel écrit dans Supabase Storage. Mêmes URLs retournées via `url_for()`.

**Garde-fous :** aucun code métier n'appelle directement `open()` ou `Path().write_bytes()` pour du contenu user. Tout passe par l'abstraction.

### V4-M009 — Job queue interface
**ACTOR : CLAUDE**
**DÉPENDANCES :** V4-M004

**Livrable :**
- Interface `Backend/Prod/jobs/base.py` : `enqueue(job_type, payload)`, `process_pending()`
- Implémentation MVP `InlineJobs` (exécute immédiatement en thread pool via `run_in_executor`)
- Stub `SupabaseQueueJobs` ou `ARQJobs` pour plus tard (interface vide, à implémenter en Phase F)
- Jobs définis : `deploy_project`, `grade_submission`, `send_email`
- Chaque job enregistre début/fin dans `events`

**Test de succès :** `enqueue("deploy_project", {...})` déclenche le deploy, retour HTTP immédiat, tâche visible dans `events` avec durée mesurée.

### V4-M010 — Login racine + seed de test
**ACTOR : CLAUDE**
**DÉPENDANCES :** V4-M005

**Livrable :**
- Script `scripts/seed.py` qui :
  1. Crée 1 organization `demo-school`
  2. Crée 1 superadmin via Supabase Auth (email, mot de passe temporaire affiché)
  3. Crée 1 teacher, attribue rôle, attache à l'org
  4. Crée 2 classes avec invite_codes
  5. Crée 5 élèves (users + students + user_roles)
  6. Crée 1 sujet, 3 projets exemples
- Commande `make seed` qui reset la DB puis exécute `seed.py`
- Au premier démarrage, si 0 superadmin existe : génère un mot de passe aléatoire fort, log une seule fois, force le changement

**Test de succès :** `make seed` sur DB vierge produit l'environnement complet. Login superadmin fonctionne. Password temporaire doit être changé à la première connexion.

### V4-M011 — Email transactionnel (Resend)
**ACTOR : CLAUDE**
**DÉPENDANCES :** V4-M004

**Livrable :**
- `Backend/Prod/email/resend_client.py` avec interface `send(to, template, data)`
- Templates (HTML + text) : `verification`, `password_reset`, `invitation_teacher`, `invitation_student`
- Supabase Auth configuré pour utiliser Resend comme SMTP custom (via option Supabase Dashboard)
- DKIM/SPF configurés sur le domaine (Resend guide)

**Test de succès :** inscription produit un email de vérification reçu en < 30s, cliquable, vérifie le compte correctement.

### V4-M012 — Health check profond + seed smoke test
**ACTOR : CLAUDE**
**DÉPENDANCES :** V4-M010, V4-M011

**Livrable :**
- Endpoint `GET /api/v1/health` qui retourne :
  ```json
  { "status": "ok" | "degraded" | "down",
    "checks": { "db": {...}, "storage": {...}, "email": {...}, "supabase_auth": {...} }
  }
  ```
- Script `scripts/smoke.py` qui effectue les 3 parcours critiques :
  1. Login superadmin → retourne 200
  2. Teacher crée classe → classe visible
  3. Élève login code classe → workspace accessible

**Test de succès :** `python scripts/smoke.py` passe sur une DB seed, tous tests verts. `/api/v1/health` retourne `status=ok`.

### V4-M013 — Suppression des squelettes V3 obsolètes
**ACTOR : CLAUDE** (code direct nettoyage)
**DÉPENDANCES :** V4-M005, V4-M006

**Livrable :** suppression ou archivage explicite des fichiers rendus obsolètes par la V4 :
- Ancien `AuthMiddleware` (server_v3.py) : retiré (remplacé par V4-M005)
- `routers/auth_router.py` : métier déplacé, ne reste que proxy Supabase
- Fichiers Stenciler V3 non utilisés par FEE : `Canvas.renderer.js`, `AtomRenderer.js`, `WireframeLibrary.js`, `stenciler_v3_main.js`, `stenciler_v3.html`, `stenciler_v3_additions.css`, `AtomPrototypes.js`, `GRID.js` (si pas importé ailleurs)
- `active_project.json` : supprimé (remplacé par DB)
- Templates obsolètes : `cadrage_alt.html.bak`, `bkd_frd.html` si non utilisé, imports `import_2026-04-*` déplacés dans `_archive/`

**Règle :** ne rien supprimer sans `grep -rn "<nom-fichier>"` préalable. Si un import existe encore, migrer l'import d'abord.

**Test de succès :** après suppression, `make smoke` passe toujours, `make test` passe, `grep -r` ne remonte aucune référence morte.

### V4-M014 — Documentation minimale pour Sonnet + Gemini
**ACTOR : CLAUDE**
**DÉPENDANCES :** V4-M001 → V4-M013

**Livrable :**
- `docs/SETUP.md` : comment installer, configurer Supabase, lancer en local
- `docs/ARCHITECTURE.md` : résumé (stack, flow auth, flow deploy, structure dossiers)
- `docs/CONTRIBUTING.md` : comment rédiger une mission, conventions, tests
- Mise à jour `API_CONTRACT.md` avec toutes les routes `/api/v1/` actives
- `CLAUDE.md` à la racine avec les garde-fous V4 résumés (ce que Claude et Sonnet doivent lire à chaque session)

**Test de succès :** un nouveau contributeur (ou Sonnet en session vierge) peut cloner, lire les 4 docs, et produire une mission V4 correcte.

---

## 4. Missions Phase A (détaillées)

### V4-M101 — Onboarding élève via code de classe
**ACTOR : GEMINI (frontend) + CLAUDE (backend)**
**DÉPENDANCES :** Phase 0-MVP validée

**Parcours :**
1. URL `/join` publique
2. Champ `code de classe` (6 caractères alphanumériques)
3. Champ `prénom` (display_name)
4. Validation : code existe → classe active ? → créer user + student + user_role `student`
5. Magic link envoyé ou session immédiate (à arbitrer : magic link plus sûr mais friction)
6. Redirection workspace

**Livrables backend :**
- `POST /api/v1/classes/join` avec `{invite_code, display_name, email?}`
- Création atomique user + student + role en transaction
- Email de bienvenue via Resend

**Livrables frontend :**
- Template `join.html` avec formulaire
- Gestion erreurs (code invalide, classe archivée)

### V4-M102 — Workspace simplifié (squelette)
**ACTOR : GEMINI**
**DÉPENDANCES :** V4-M101

Version dépouillée du workspace actuel : entête avec nom projet, zone principale Wire, sidebar minimaliste. Pas de FEE, pas de Stitch drill, pas d'audit. Juste : ajouter écran, éditer nom, voir liste.

### V4-M103 — Éditeur Wire minimal
**ACTOR : GEMINI + CLAUDE (backend persistence)**

- Créer un écran (titre + description)
- Lier deux écrans (click screen A → bouton "connecter à" → click screen B)
- Supprimer / renommer écran
- Sauvegarde auto toutes les 5s dans `screens` + `wirelinks`

### V4-M104 — Preview live
**ACTOR : GEMINI**

Affichage iframe du projet en cours de construction. Navigation entre écrans via clic sur liens wirelinks. Génération HTML côté client à partir des données.

### V4-M105 — Pipeline déploiement Cloudflare Pages
**ACTOR : CLAUDE**

- Job `deploy_project` :
  1. Lit `projects.manifest`, `screens`, `wirelinks`
  2. Génère N fichiers HTML statiques + 1 CSS + 1 JS de navigation
  3. Crée/met à jour un projet Cloudflare Pages via API
  4. Upload les fichiers
  5. Récupère l'URL finale, met à jour `deployments`
- Endpoint `POST /api/v1/projects/{id}/publish` qui enqueue le job et retourne 202

**Secrets requis :** `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`.

### V4-M106 — Flow démo complet testé
**ACTOR : CLAUDE (tests E2E) + FJD (validation humaine)**

- Test E2E Playwright : parcours complet `/join` → publish → URL accessible
- Démo manuelle par FJD sur prod Fly.io
- Critère : < 10 minutes du code à l'URL partageable

---

## 5. Missions Phase B → F (ébauches)

À détailler par Sonnet après validation Phase A.

### Phase B — Teacher
- V4-M201 : Création classe + invite_code
- V4-M202 : Création sujet + upload référentiel PDF
- V4-M203 : Attachement sujet ↔ classe
- V4-M204 : Dashboard teacher (classes, élèves, progression)
- V4-M205 : Realtime Supabase (progression live)
- V4-M206 : Notation auto via AetherFlow (LLM + rubric)
- V4-M207 : Ajustement manuel + commentaires
- V4-M208 : Export notes CSV

### Phase C — User
- V4-M301 : Page signup publique
- V4-M302 : Mode inscription configurable
- V4-M303 : Workspace user (copie workspace sans contexte classe)
- V4-M304 : Projets user

### Phase D — Cohabitation
- V4-M401 : user_roles multi-contextes
- V4-M402 : Selector contexte (mode classe X ↔ mode perso)
- V4-M403 : Filtrage projets par contexte actif
- V4-M404 : Tests croisés (pas de fuite entre rôles)

### Phase 0-LAUNCH
- V4-M501 : Consentement parental RGPD (< 15 ans)
- V4-M502 : Export données utilisateur
- V4-M503 : Suppression compte complète
- V4-M504 : Sentry branché en prod
- V4-M505 : UptimeRobot + alertes
- V4-M506 : Modération + takedown
- V4-M507 : ToS + Privacy policy + versioning
- V4-M508 : Rate limiting prod

### Phase E — Stripe
- V4-M601 : Table plans + seed
- V4-M602 : Stripe Checkout intégration
- V4-M603 : Webhook Stripe sécurisé
- V4-M604 : Feature flags par plan
- V4-M605 : UI upgrade/downgrade
- V4-M606 : Facturation + export

### Phase F — Hexagonale
- V4-M701 : Timeline GSAP (FEE)
- V4-M702 : Asset manager (FEE)
- V4-M703 : Custom domains (Deploy)
- V4-M704 : Staging vs Prod (Deploy)
- V4-M705 : Collab temps réel (Wire)
- V4-M706 : Version history (Wire)
- V4-M707 : LangGraph (Moteur)
- V4-M708 : Second architecte (Moteur)

---

## 6. Garde-fous transverses (invariants V4)

Règles **inviolables**. À faire respecter à chaque mission, chaque code review. Toute violation = bloquant merge.

### 6.1 Code

- **Zéro secret hardcodé.** Tout secret vient de `settings`. Pas de `api_key = "sk-..."`.
- **Zéro SQL brut.** SQLAlchemy ou SDK Supabase uniquement. Les raw SQL passent en migration versionnée uniquement.
- **Zéro I/O sync dans handler async.** `async def` = zéro `sqlite3.connect`, zéro `open()`, zéro appel HTTP synchrone. Si besoin : `run_in_executor` explicite.
- **Zéro manipulation datetime naive.** Tout en `datetime.now(tz=UTC)` ou `TIMESTAMPTZ`. Conversion locale uniquement à l'affichage.
- **Zéro monolithe > 400 lignes.** Au-delà, split en modules. Exception justifiée par commentaire en tête de fichier.
- **Zéro emoji dans les fichiers** (sauf UI user-facing strings si le design l'impose).
- **Zéro commentaire qui paraphrase le code.** Un commentaire explique le "pourquoi" non évident, pas le "quoi".

### 6.2 Database

- **Toutes les FK ont `ON DELETE` explicite** (`CASCADE`, `SET NULL`, `RESTRICT`). Jamais implicite.
- **Toutes les tables ont `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`**.
- **Aucun `ALTER TABLE` manuel.** Toute modification passe par une nouvelle migration Alembic.
- **Soft delete uniquement** (`deleted_at TIMESTAMPTZ`) pour `users`, `projects`. Hard delete via job RGPD explicite uniquement.
- **RLS activée sur toutes les tables publiques.** Pas d'exception.
- **Index systématique sur colonnes de lookup** (toute colonne utilisée dans WHERE sur > 1000 rows).

### 6.3 API

- **Tout endpoint métier est préfixé `/api/v1/`**. Pas d'exception.
- **Tout endpoint qui lit des données user est authentifié** par défaut. Opt-out explicite pour routes publiques.
- **Format erreur uniforme** : `{ "error": { "code": "...", "message": "...", "detail": {...} } }`.
- **Pagination** : toute route qui liste > 100 items doit paginer (cursor ou offset).
- **Validation Pydantic** : tout body, tout query param, typé.

### 6.4 Auth & Sécurité

- **Pas de rôle dans l'URL** (pas de `/admin/users`). Le rôle est vérifié côté serveur depuis le JWT.
- **Pas de `user_id` en query param** quand le JWT en donne un. Toujours utiliser celui du JWT authentifié.
- **Rate limiting** sur toutes les routes `/auth/*`.
- **Logs auth** : toute tentative de login (succès ou échec) logue dans `events`.

### 6.5 Tests

- **3 tests critiques** toujours verts avant merge : login superadmin, création projet end-to-end, déploiement projet.
- **Coverage minimum** : 60% sur les modules métier (pas sur l'infra).
- **CI GitHub Actions** : bloque le merge si tests rouges.

### 6.6 Workflow

- **Toute mission** a un identifiant `V4-MXXX`, un ACTOR, des dépendances listées, un test de succès mesurable.
- **Toute mission** mentionne explicitement les garde-fous spécifiques qu'elle applique.
- **Aucune mission ne modifie plusieurs phases à la fois.** Si nécessaire : split en sous-missions.
- **Aucune mission ne casse les phases précédentes.** Si régression : rollback immédiat.

### 6.7 Observabilité

- **Tout job long** enregistre début/fin/durée dans `events`.
- **Toute erreur 5XX** est capturée par Sentry (en prod).
- **Tout déploiement user** logue succès/échec dans `deployments` avec raison.

### 6.8 RGPD (dès Phase 0-LAUNCH)

- **Consentement explicite** stocké dans `consents` avec version des ToS/Privacy.
- **Droit à la portabilité** : endpoint `GET /api/v1/users/me/export` fonctionnel.
- **Droit à l'oubli** : endpoint `DELETE /api/v1/users/me` qui supprime réellement (avec délai 30j optionnel).
- **Consentement parental** pour mineurs : validation explicite représentant légal avant activation compte.

---

## 7. Dépendances inter-missions (graphe)

```
V4-M001 (Supabase init)
  └→ V4-M002 (schema content)
      └→ V4-M003 (schema compliance)

V4-M001 ─┬→ V4-M004 (Pydantic Settings)
         └→ V4-M008 (Storage) → V4-M011 (Email)

V4-M004 ─┬→ V4-M005 (Auth Supabase)
             └→ V4-M006 (API v1) → V4-M007 (Logs)
                                    └→ V4-M012 (Health)

V4-M009 (Jobs) ←─ V4-M004

V4-M010 (Seed) ←─ V4-M005
V4-M013 (Nettoyage) ←─ tous Phase 0
V4-M014 (Docs) ←─ tous Phase 0

Phase A :
V4-M101 (Join) ─→ V4-M102 (Workspace) ─→ V4-M103 (Wire)
                                           └→ V4-M104 (Preview) ─→ V4-M105 (Deploy) ─→ V4-M106 (E2E)
```

**Parallélisation possible :**
- V4-M002, V4-M003, V4-M004 en parallèle après V4-M001
- V4-M008, V4-M009, V4-M011 en parallèle après V4-M004
- V4-M007 après V4-M006 mais V4-M010 + V4-M012 peuvent démarrer avant

---

## 8. Indicateurs de succès globaux

**Phase 0-MVP :**
- Temps de setup local (clone → `make seed` → serveur démarre) : < 5 min
- Nombre de tests critiques passants : ≥ 3
- Couverture de code métier : ≥ 60%
- Erreurs Sentry en dev : 0

**Phase A :**
- Temps de parcours élève (code classe → URL publique) : < 10 min
- Taux de complétion du parcours : 100% sur 5 testeurs naïfs
- Taille moyenne HTML généré par projet : < 100 KB
- Temps de build + deploy Cloudflare : < 30s

**Phase B-C-D :**
- Latence realtime teacher dashboard : < 2s
- Précision notation auto vs humaine : ≥ 70% corrélation
- Fuite de données entre rôles (test pentest) : 0

**Phase E :**
- Conversion free → Pro (objectif 6 mois après launch) : ≥ 2%
- Churn mensuel Pro : ≤ 5%

---

## 9. Ce que ce document N'EST PAS

- **Pas un planning engagé en jours/heures.** Les durées sont estimations. Le tempo réel dépend des disponibilités FJD + Gemini + autres agents.
- **Pas figé.** Les phases B-F sont ébauchées, Sonnet ou Claude détailleront missions quand leur phase arrive.
- **Pas un remplaçant de la Constitution V3.** La Constitution reste la règle sociale (DA, architecte, ouvrier). Ce document est la règle technique.
- **Pas la fin de V3.** Certaines parties V3 restent actives en transition (FEE, moteur AetherFlow). La V4 ne redémarre pas à zéro.

---

## 10. Validation & activation

Ce document est **validé FJD 2026-04-15** (moment de sa rédaction, premier passage).
Toute modification majeure (ajout phase, changement de stack, ajout garde-fou inviolable) requiert nouvelle validation FJD.

**Activation :**
- Mission V4-M001 prête à être exécutée
- ROADMAP.md mis à jour pour pointer vers ce document
- Toute nouvelle mission HoméOS fait référence à `PROJECTION_V4.md` en en-tête

**Fin de document.**
