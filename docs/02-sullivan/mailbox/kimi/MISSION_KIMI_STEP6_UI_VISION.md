# MISSION KIMI : Step 6 - UI Designer Vision

**Date** : 9 février 2026
**Agent** : KIMI (FRD Lead)
**Mode AetherFlow** : BUILD
**Priorité** : 🟠 P1 (après Gemini termine vision_analyzer.py)

---

## 0. RAPPEL - CHARGER TES SKILLS + CHEMINS MAILBOX

```
.cursor/skills/
├── GENERAL.md
├── kimi-binome/SKILL.md
└── aetherflow-modes/
```

⚠️ **HANDOFF** : Dépose dans `docs/02-sullivan/mailbox/gemini/` (PAS `.claude/mailbox/`)

---

## 1. CONTEXTE

**Gemini** crée `vision_analyzer.py` (analyse PNG avec Vision API).

**Toi** : Créer l'UI pour afficher les résultats de l'analyse.

---

## 2. OBJECTIF

Créer :
1. Route API `/studio/step/6/analyze` (POST)
2. Template HTML `studio_step_6_analysis.html`
3. Affichage visuel du rapport :
   - PNG uploadé avec calque zones détectées
   - Style guide extrait (couleurs, typo, spacing)
   - Zones layout avec hypothèses Sullivan
4. Tests unitaires

---

## 3. SPÉCIFICATIONS DÉTAILLÉES

### 3.1 Route API

```python
@router.post("/studio/step/6/analyze")
async def analyze_uploaded_design(
    session_id: str = Query(None)
):
    """
    Déclenche l'analyse Gemini Vision du PNG uploadé.

    Returns:
        HTML fragment avec rapport visuel
    """

    # 1. Vérifier PNG existe
    upload_path = Path(f"~/.aetherflow/uploads/{session_id}/design.png").expanduser()

    if not upload_path.exists():
        raise HTTPException(400, "Aucun PNG trouvé. Uploadez d'abord à Step 5.")

    # 2. Analyser avec Gemini Vision
    from Backend.Prod.sullivan.vision_analyzer import analyze_design_png

    try:
        visual_report = await analyze_design_png(str(upload_path), session_id)
    except Exception as e:
        raise HTTPException(500, f"Erreur analyse Vision : {str(e)}")

    # 3. Retourner template HTML
    return templates.TemplateResponse("studio_step_6_analysis.html", {
        "request": request,
        "report": visual_report,
        "png_url": f"/uploads/{session_id}/design.png",
        "session_id": session_id
    })
```

### 3.2 Template HTML

Créer `Backend/Prod/sullivan/templates/studio_step_6_analysis.html` :

```html
<div id="studio-main-zone" class="p-8 max-w-7xl mx-auto">
    <h2 class="text-2xl font-bold text-slate-800 mb-6">Analyse de votre design</h2>

    <div class="grid grid-cols-2 gap-8">
        <!-- Colonne gauche : PNG + Calque zones -->
        <div class="relative">
            <h3 class="text-lg font-semibold mb-4">Zones détectées</h3>

            <div class="relative border border-slate-200 rounded-lg overflow-hidden">
                <!-- Image PNG -->
                <img src="{{ png_url }}" alt="Design uploadé" class="w-full">

                <!-- Calque SVG avec zones -->
                <svg class="absolute inset-0 w-full h-full pointer-events-none">
                    {% for zone in report.layout.zones %}
                    <rect
                        x="{{ zone.coordinates.x }}"
                        y="{{ zone.coordinates.y }}"
                        width="{{ zone.coordinates.w }}"
                        height="{{ zone.coordinates.h }}"
                        fill="rgba(99, 102, 241, 0.2)"
                        stroke="#6366f1"
                        stroke-width="2"
                        stroke-dasharray="5,5"
                    />
                    <text
                        x="{{ zone.coordinates.x + 10 }}"
                        y="{{ zone.coordinates.y + 25 }}"
                        fill="#1e293b"
                        font-weight="bold"
                        font-size="14"
                    >
                        {{ zone.hypothesis.label }}
                    </text>
                    {% endfor %}
                </svg>
            </div>

            <p class="text-sm text-slate-500 mt-2">
                Sullivan a détecté {{ report.layout.zones|length }} zones dans votre design.
            </p>
        </div>

        <!-- Colonne droite : Style Guide -->
        <div>
            <h3 class="text-lg font-semibold mb-4">Style Guide extrait</h3>

            <!-- Couleurs -->
            <div class="mb-6">
                <h4 class="font-medium text-slate-700 mb-2">Couleurs</h4>
                <div class="flex gap-3">
                    {% for name, color in report.style.colors.items() %}
                    <div class="text-center">
                        <div
                            class="w-16 h-16 rounded-lg border border-slate-200"
                            style="background-color: {{ color }};"
                        ></div>
                        <span class="text-xs text-slate-600 mt-1 block">{{ name }}</span>
                        <code class="text-xs text-slate-500">{{ color }}</code>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- Typographie -->
            <div class="mb-6">
                <h4 class="font-medium text-slate-700 mb-2">Typographie</h4>
                <p class="text-sm text-slate-600">
                    Famille : <code class="bg-slate-100 px-2 py-1 rounded">{{ report.style.typography.family }}</code>
                </p>
                <div class="mt-2 space-y-1">
                    {% for size, value in report.style.typography.sizes.items() %}
                    <p style="font-size: {{ value }};">
                        {{ size }} : {{ value }}
                    </p>
                    {% endfor %}
                </div>
            </div>

            <!-- Spacing -->
            <div class="mb-6">
                <h4 class="font-medium text-slate-700 mb-2">Espacements</h4>
                <ul class="text-sm text-slate-600 space-y-1">
                    <li>Border radius : <code>{{ report.style.spacing.border_radius }}</code></li>
                    <li>Padding : <code>{{ report.style.spacing.padding }}</code></li>
                    <li>Margin : <code>{{ report.style.spacing.margin }}</code></li>
                </ul>
            </div>

            <!-- Bouton suivant -->
            <button
                hx-get="/studio/step/7/dialogue"
                hx-target="#studio-main-zone"
                class="w-full bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
            >
                Continuer vers le Dialogue
            </button>
        </div>
    </div>
</div>
```

---

## 4. CRITÈRES D'ACCEPTATION

- [ ] Route POST `/studio/step/6/analyze` fonctionne
- [ ] Template HTML créé
- [ ] Affichage PNG + calque SVG zones
- [ ] Style guide affiché (couleurs, typo, spacing)
- [ ] Tests unitaires (minimum 6 tests) :
  - Analyse déclenche Gemini Vision
  - Erreur si PNG manquant
  - Template HTML rendu correctement
  - Zones SVG positionnées
  - Style guide parsé
  - Bouton "Continuer" présent

---

## 5. ATTENDEZ HANDOFF GEMINI

⚠️ **NE COMMENCE PAS** avant de voir ce fichier :

```
docs/02-sullivan/mailbox/gemini/HANDOFF_GEMINI_STEP6_UI.md
```

Gemini te dira quand `vision_analyzer.py` est prêt.

---

## 6. LIVRAISON

⚠️ **CHEMINS CORRECTS** :

**CR KIMI** : `docs/02-sullivan/mailbox/kimi/CR_STEP6_UI_VISION.md`

**HANDOFF pour Gemini QA** : `docs/02-sullivan/mailbox/gemini/HANDOFF_KIMI_STEP6_UI.md`

**PAS DANS** `.claude/mailbox/` !

---

**Attends le feu vert de Gemini, puis crée l'UI.**

*— Sonnet (Ingénieur en Chef)*
