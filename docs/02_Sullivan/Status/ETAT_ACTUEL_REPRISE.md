# ÉTAT ACTUEL ET PLAN DE REPRISE

**Date** : 9 février 2026, 19:20
**Situation** : Point de clarification critique

---

## ⚠️ CLARIFICATION FONDAMENTALE

**LA RÉFÉRENCE UX/UI : PORT 9999**

Le travail qui a de la valeur pour les humains se trouve sur le **port 9999**.
Tout le reste est de la "tuyauterie technique" secondaire.

**SI ON PERD LE RENDU DU PORT 9999, ON PERD TOUT.**

---

## 📍 OÙ ON EN EST EXACTEMENT

### 1. Le Port 9999 - LA RÉFÉRENCE

**Localisation** :
```
/Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/
├── server_9999_v2.py (SERVEUR DYNAMIQUE - 681 lignes)
└── genome_inferred_kimi_innocent.json (29 composants)
```

**Ce qu'il fait** :
- Charge le genome JSON
- Génère des wireframes HTML/SVG dynamiques selon le `visual_hint`
- Affiche hiérarchie N0→N1→N2→N3 (Corps/Organe/Atome)
- Couleurs par méthode HTTP (GET=vert, POST=bleu...)
- Checkboxes de sélection + bouton "Valider (n)"

**Comment le lancer** :
```bash
cd /Users/francois-jeandazin/AETHERFLOW/docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06
python3 server_9999_v2.py
# → http://localhost:9999
```

**STATUT** : ✅ OPÉRATIONNEL, tourne actuellement (PID 49629)

---

### 2. Le Port 8000 - La Tuyauterie

**Localisation** :
```
/Users/francois-jeandazin/AETHERFLOW/Backend/Prod/
├── api.py (FastAPI)
├── sullivan/studio_routes.py (Steps 1-9)
└── sullivan/templates/studio_step_*.html
```

**Ce qu'il a** :
- ✅ Step 5 : Upload PNG + 8 styles
- ✅ Step 6 : Analyse Vision Gemini
- ✅ Step 7 : Dialogue Sullivan
- ❌ Step 8 : Validation (à faire)
- ❌ Step 9 : Adaptation Top-Bottom (à faire)

**PROBLÈME** : Le 8000 ne reproduit PAS le rendu visuel du 9999.

---

## 🎯 OBJECTIF IMMÉDIAT

**Partir du rendu Genome (port 9999) → Ajouter le Carrefour Créatif (Upload PNG / 8 Styles)**

Le flux utilisateur souhaité :
```
1. Utilisateur voit le Genome sur port 9999
2. En bas de page : "C'est un peu générique, non ? Sullivan peut personnaliser ce design"
3. Deux options :
   A) Upload PNG → Analyse Gemini → Dialogue
   B) 8 Styles → Choix style → Dialogue
4. Suite du workflow...
```

---

## 🔧 SOLUTION TECHNIQUE

### Option A : Enrichir le 9999 (RECOMMANDÉ)

**Principe** : Garder le rendu UX du 9999, ajouter juste les boutons de transition.

**Modifications à faire** :

1. **Ajouter au server_9999_v2.py** (ligne ~625, avant `</body>`) :

```html
<!-- Carrefour Créatif Fixe -->
<div style="position:fixed;bottom:0;left:0;right:0;background:white;
            border-top:2px solid #6366f1;padding:20px;box-shadow:0 -4px 12px rgba(0,0,0,0.1);
            display:flex;justify-content:space-between;align-items:center;z-index:10000;">

    <div style="max-width:400px;">
        <h3 style="font-size:18px;font-weight:700;color:#374151;margin-bottom:4px;">
            C'est un peu générique, non ?
        </h3>
        <p style="font-size:14px;color:#6b7280;">
            Sullivan peut personnaliser ce design pour vous.
        </p>
    </div>

    <div style="display:flex;gap:12px;">
        <!-- Option 1 : Upload PNG -->
        <button onclick="window.location.href='http://localhost:8000/studio/step/5/upload'"
                style="background:#6366f1;color:white;border:none;padding:12px 24px;
                       border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;">
            Importer votre layout (PNG)
        </button>

        <!-- Option 2 : 8 Styles -->
        <button onclick="window.location.href='http://localhost:8000/studio/step/5/layouts'"
                style="background:white;border:2px solid #6366f1;color:#6366f1;
                       padding:12px 24px;border-radius:8px;font-size:14px;font-weight:600;cursor:pointer;">
            Voir les 8 styles proposés
        </button>
    </div>
</div>

<!-- Padding pour éviter que le contenu soit caché par le footer fixe -->
<div style="height:100px;"></div>
```

2. **Vérifier que le port 8000 a bien les routes** :
   - `/studio/step/5/upload` (POST pour upload PNG)
   - `/studio/step/5/layouts` (GET pour 8 styles)

3. **Tester le flux** :
   - Genome (9999) → Click "Upload PNG" → Redirige vers 8000 → Upload → Analyse → Dialogue
   - Genome (9999) → Click "8 Styles" → Redirige vers 8000 → Choix style → Dialogue

---

### Option B : Migrer le rendu 9999 vers 8000

**Principe** : Un seul serveur (8000), recréer le rendu visuel du 9999 dans les templates Jinja2.

**Travail requis** :
1. Copier la logique `generate_component_wireframe()` du server_9999_v2.py
2. Créer un nouveau template `studio_genome_viewer.html` qui reproduit le rendu du 9999
3. Ajouter une route `/studio/genome-viewer` dans studio_routes.py
4. Faire pointer le workflow dessus

**Avantage** : Un seul serveur à gérer.
**Inconvénient** : Risque de perdre le rendu visuel exact du 9999 pendant la migration.

---

## 📋 PLAN D'ACTION IMMÉDIAT

### Étape 1 : Vérifier l'existant

```bash
# 1. Vérifier que le 9999 tourne bien
curl -s http://localhost:9999 | head -20

# 2. Vérifier que le 8000 a les routes Step 5
curl -s http://localhost:8000/studio/step/5/choice | head -20
```

### Étape 2 : Enrichir le 9999

Je modifie `server_9999_v2.py` pour ajouter le footer "Carrefour Créatif" avec les deux boutons.

### Étape 3 : Tester le flux complet

1. Ouvrir http://localhost:9999
2. Voir le Genome rendu
3. Cliquer sur "Importer PNG"
4. Vérifier que ça redirige vers le port 8000 Step 5 Upload
5. Uploader un PNG
6. Vérifier que l'analyse Vision fonctionne
7. Vérifier que le dialogue Sullivan fonctionne

---

## ❓ QUESTION POUR DÉCIDER

**Tu veux quelle option ?**

- **Option A** : Garder le 9999 comme base, ajouter juste les boutons de transition
  - ✅ Garde le rendu UX parfait
  - ✅ Modification minimale (10 lignes de HTML)
  - ❌ Deux serveurs à gérer (9999 + 8000)

- **Option B** : Migrer tout vers le 8000
  - ✅ Un seul serveur
  - ❌ Doit recréer le rendu visuel du 9999 (risque de perte)
  - ❌ Travail plus long

**MA RECOMMANDATION** : Option A, car on ne touche pas au rendu UX du 9999.

---

## 🚀 PRÊT À EXÉCUTER

Donne-moi juste le GO et je modifie le server_9999_v2.py pour ajouter les boutons.

**Temps estimé** : 5 minutes.
