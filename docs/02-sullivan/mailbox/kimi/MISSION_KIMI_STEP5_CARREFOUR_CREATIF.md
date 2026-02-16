# MISSION KIMI : Step 5 - Carrefour Créatif

**Date** : 9 février 2026
**Agent** : KIMI (FRD Lead)
**Mode AetherFlow** : BUILD
**Priorité** : 🔴 P0

---

## 0. RAPPEL - CHARGER TES SKILLS

```
.cursor/skills/
├── GENERAL.md
├── kimi-binome/SKILL.md
├── kimi-binome/CHECKLIST.md
└── aetherflow-modes/
```

---

## 1. CONTEXTE

**Steps précédents complétés** :
- ✅ Step 4 : Stenciler (classe + 25 tests)
- ✅ Step 4.5 : Routes API (3 routes + 15 tests)
- ✅ QA : 14/16 tests passent (2 échecs genome vide normaux)

**Prochaine étape** : Le "Carrefour Créatif" (Step 5)

---

## 2. OBJECTIF

Implémenter **Step 5** du Parcours UX Sullivan : l'utilisateur choisit entre :
1. **Upload PNG** → Analyse visuelle par Gemini (Step 6)
2. **8 propositions de styles** → Génération automatique

**Livrables** :
1. Route API `/studio/step/5/upload` (POST multipart/form-data)
2. Route API `/studio/step/5/layouts` (GET) → 8 propositions
3. Template HTML `studio_step_5_choice.html`
4. Tests unitaires

---

## 3. SPÉCIFICATIONS DÉTAILLÉES

### 3.1 Route Upload PNG

```python
@router.post("/studio/step/5/upload")
async def upload_design_file(
    design_file: UploadFile = File(...),
    session_id: str = Query(None)
):
    """
    Upload fichier PNG pour analyse visuelle (Step 6).

    Returns:
        - Stocke le fichier dans ~/.aetherflow/uploads/
        - Retourne HTML de confirmation + bouton "Analyser avec Gemini"
    """
    pass
```

**Actions** :
1. Sauvegarder le fichier dans `~/.aetherflow/uploads/{session_id}/{filename}`
2. Créer thumbnail (optionnel)
3. Retourner fragment HTML HTMX avec preview + bouton "Lancer l'analyse"

### 3.2 Route 8 Propositions

```python
@router.get("/studio/step/5/layouts")
async def get_layout_proposals(session_id: str = Query(None)):
    """
    Génère 8 propositions de styles de layout.

    Returns:
        - HTML avec grid 2×4 des 8 styles
        - Chaque card : nom, description, preview SVG miniature, bouton "Choisir"
    """
    pass
```

**8 Styles à proposer** (depuis la classe `CreativeCarrefour`) :
1. Minimaliste (Clean & Airy)
2. Brutaliste (Raw & Bold)
3. Néomorphisme (Soft & Modern)
4. Glassmorphism (Transparent & Light)
5. Rétro Terminal (Monospace & Green)
6. Material Dense (Colorful & Busy)
7. Nordic Zen (White & Subtle)
8. Cyberpunk Neon (Dark & Vibrant)

**Format de réponse** :
- Grid Tailwind 2 colonnes
- Chaque card : hover effect, SVG miniature, bouton HTMX

### 3.3 Template HTML

Créer `Backend/Prod/sullivan/templates/studio_step_5_choice.html` :

```html
<div id="studio-main-zone" class="p-8 max-w-4xl mx-auto animate-fade-in">
    <div class="text-center mb-10">
        <h2 class="text-2xl font-bold text-slate-800">C'est un peu générique, non ?</h2>
        <p class="text-slate-600 mt-2">Sullivan peut aller plus loin pour rendre ce projet unique.</p>
    </div>

    <div class="grid md:grid-cols-2 gap-8">
        <!-- Option 1 : Upload PNG -->
        <div class="border-2 border-dashed border-indigo-200 rounded-2xl p-8 hover:border-indigo-400 transition-colors bg-white group">
            <div class="flex flex-col items-center text-center">
                <div class="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mb-4">
                    <!-- Icon SVG -->
                </div>
                <h3 class="text-lg font-semibold">Importez votre layout (PNG)</h3>
                <p class="text-sm text-slate-500 mt-2 mb-6">Je vais analyser votre image...</p>

                <form hx-post="/studio/step/5/upload" hx-encoding="multipart/form-data" hx-target="#studio-main-zone">
                    <label class="cursor-pointer bg-indigo-600 text-white px-6 py-2 rounded-lg">
                        Choisir un fichier
                        <input type="file" name="design_file" class="hidden" accept="image/png,image/jpeg" onchange="this.form.requestSubmit()">
                    </label>
                </form>
            </div>
        </div>

        <!-- Option 2 : 8 Propositions -->
        <div class="border-2 border-slate-100 rounded-2xl p-8 hover:border-emerald-400 transition-colors bg-white group">
            <div class="flex flex-col items-center text-center">
                <div class="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mb-4">
                    <!-- Icon SVG -->
                </div>
                <h3 class="text-lg font-semibold">Proposez-moi des idées</h3>
                <p class="text-sm text-slate-500 mt-2 mb-6">8 propositions de styles adaptées...</p>

                <button hx-get="/studio/step/5/layouts" hx-target="#studio-main-zone" class="border border-emerald-600 text-emerald-600 px-6 py-2 rounded-lg">
                    Voir les styles
                </button>
            </div>
        </div>
    </div>
</div>
```

---

## 4. BONUS - CHARGER LE GENOME

**Problème actuel** : Les tests Step 4 échouent (2/16) car le genome est vide.

**Fix à intégrer** dans `studio_routes.py` :

```python
from pathlib import Path
import json

# Charger le genome au démarrage du module
GENOME_PATH = Path(__file__).parent.parent.parent / "docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/genome_inferred_kimi_innocent.json"

try:
    with open(GENOME_PATH) as f:
        GENOME_DATA = json.load(f)

    # Initialiser Stenciler avec le genome
    stenciler._genome = GENOME_DATA

    print(f"✅ Genome chargé : {len(GENOME_DATA.get('n0_phases', []))} Corps détectés")
except FileNotFoundError:
    print("⚠️ Genome non trouvé, Stenciler vide")
    GENOME_DATA = {}
```

**Résultat attendu** : Les 2 tests Step 4 qui échouaient passent maintenant.

---

## 5. CRITÈRES D'ACCEPTATION

- [ ] Route POST `/studio/step/5/upload` fonctionne
- [ ] Fichier uploadé sauvegardé dans `~/.aetherflow/uploads/`
- [ ] Route GET `/studio/step/5/layouts` retourne 8 styles
- [ ] Template HTML `studio_step_5_choice.html` créé
- [ ] Tests unitaires (minimum 8 tests) :
  - Upload fichier PNG valide
  - Upload fichier invalide (erreur)
  - GET layouts retourne 8 propositions
  - Structure HTML correcte
- [ ] **BONUS** : Genome chargé au démarrage → 16/16 tests Step 4 passent

---

## 6. RÉFÉRENCES

| Document | Contenu |
|----------|---------|
| [Parcours UX Sullivan.md](docs/02-sullivan/Parcours UX Sullivan.md) | Step 5 détaillé (lignes 205-250) |
| [CR_QA_STEP4_SONNET.md](docs/02-sullivan/mailbox/gemini/CR_QA_STEP4_SONNET.md) | Recommandations Sonnet |
| `Backend/Prod/sullivan/studio_routes.py` | Fichier à modifier |

---

## 7. LIVRAISON

⚠️ **IMPORTANT - Chemin Mailbox** :
Dépose ton CR dans le **bon dossier** que Gemini peut voir :

**CR KIMI** : `docs/02-sullivan/mailbox/kimi/CR_STEP5_CARREFOUR_CREATIF.md`

**PAS DANS** `.claude/mailbox/` (Gemini ne voit pas ce dossier !)

**Format du CR** :
```markdown
# Compte-Rendu : Step 5 - Carrefour Créatif

**Date** : [date]
**Agent** : KIMI
**Mission** : MISSION_KIMI_STEP5_CARREFOUR_CREATIF.md

## ✅ Ce qui a été fait
- Route upload
- Route layouts
- Template HTML
- Tests
- Genome chargé (bonus)

## 📁 Fichiers modifiés/créés
- Backend/Prod/sullivan/studio_routes.py
- Backend/Prod/sullivan/templates/studio_step_5_choice.html
- Backend/Prod/tests/sullivan/test_studio_routes_step5.py

## 🧪 Tests exécutés
[résultats pytest]

## 🎯 Prêt pour Step 6 : OUI / NON
```

**HANDOFF** : `docs/02-sullivan/mailbox/gemini/HANDOFF_KIMI_STEP5.md`

---

**Bonne mission !**

*— Sonnet (Ingénieur en Chef)*
