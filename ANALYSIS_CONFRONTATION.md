# Analyse de Confrontation - Genome Homeos

**Date d'analyse** : 6 février 2026  
**Méthode** : Confrontation 4 sources (Doc + Code + Inférence)  
**Analyste** : Kimi Code CLI  

---

## 1. Synthèse de Compréhension

**Qu'est-ce que Homeos ?**  
Homeos (nom interne AETHERFLOW) est une plateforme d'"homéostasie du code" qui orchestre des agents IA pour générer automatiquement des applications backend (Python/APIs) et frontend (HTML/CSS/JS). Le système maintient un équilibre entre qualité, performance et maintenabilité via des workflows structurés (PROTO/PROD).

**Pour qui ?**  
Initialement conçu pour les développeurs, Homeos s'adresse maintenant à un public plus large incluant les étudiants (DNMADE, BUT MMI) et enseignants via une interface pédagogique ("Mode Normal" HCI). Le "Studio" est l'interface graphique qui rend accessible la génération de code par IA.

**Comment ?**  
Via un parcours UX en 9 phases guidé par **Sullivan**, le kernel frontend intelligent :
1. **IR** : Analyse backend et inventaire des fonctions
2. **Arbiter** : Arbitrage des capacités avec traduction HCI (endpoints → "Pouvoirs Utilisateur")
3. **Genome** : Fixation de la topologie du produit
4. **Composants Défaut** : Génération de blueprints HTML neutres fonctionnels
5. **Upload** : Réception d'un PNG de design ou proposition de layouts
6. **Analyse** : Extraction visuelle (zones, style) via Gemini Vision
7. **Dialogue** : Collaboration Heureuse pour affiner (chat)
8. **Validation** : Accord final et vérification d'homéostasie
9. **Adaptation** : Génération finale par édition chirurgicale (Top-Bottom: Corps → Organe → Atome)

---

## 2. Table de Confrontation

| Phase UX | Intention utilisateur | Endpoints Code | Statut | Visual Hint |
|----------|----------------------|----------------|--------|-------------|
| **1. IR** | Inventorier les organes du backend | `/studio/reports/ir` | ✅ Codé + Doc | table |
| **1. IR** | Voir détail d'un organe | `/studio/drilldown` | ✅ Inféré + Doc | card |
| **2. Arbiter** | Décider des capacités (HCI) | `/studio/arbitrage/forms` | ✅ Codé + Doc | card |
| **2. Arbiter** | Valider l'arbitrage | `/studio/validate` | ✅ Codé + Doc | form |
| **2. Arbiter** | Voir vue technique (expert) | `/studio/reports/arbitrage` | ✅ Codé + Doc | table |
| **3. Genome** | Voir résumé du genome | `/studio/genome/summary` | ✅ Codé + Doc | dashboard |
| **3. Genome** | Voir JSON complet | `/studio/genome/enriched` | ✅ Codé + Doc | editor |
| **3. Genome** | Passer aux composants | `/studio/next/3` | ✅ Inféré + Doc | button |
| **4. Defaults** | Voir blueprints générés | `/studio/distillation/entries` | ✅ Codé + Doc | card |
| **4. Defaults** | Passer à personnalisation | `/studio/next/4` | ✅ Inféré + Doc | form |
| **5. Upload** | Uploader son PNG | `/studio/designer/upload` | ✅ Codé + Doc | upload/dropzone |
| **5. Upload** | Voir propositions layouts | `/studio/step/5/layouts` | ✅ Codé + Doc | grid |
| **5. Upload** | Sélectionner un layout | `/studio/step/5/select-layout/{id}` | ✅ Codé + Doc | button |
| **6. Analyse** | Voir calque analyse | `/studio/designer/upload` | ✅ Codé + Doc | preview |
| **7. Dialogue** | Discuter avec Sullivan | `/studio/majordome/chat` | ✅ Codé + Doc | chat/bubble |
| **8. Validation** | Voir récapitulatif | `/studio/step/8` | ⚠️ Inféré seul | dashboard |
| **8. Validation** | Passer à adaptation | `/studio/next/8` | ⚠️ Inféré seul | form |
| **9. Adaptation** | Naviguer Top-Bottom | `/studio/zoom/{level}/{id}` | ✅ Codé + Doc | editor |
| **9. Adaptation** | Remonter d'un niveau | `/studio/zoom/out` | ✅ Codé + Doc | breadcrumb |
| **9. Adaptation** | Finaliser le projet | `/studio/finalize` | ✅ Codé + Doc | form |
| **Transverse** | Navigation étapes | `/studio/next/{step}` | ✅ Codé + Doc | stepper |
| **Transverse** | Voir étape spécifique | `/studio/step/{step}` | ✅ Codé + Doc | tabs |

**Légende Statut** :
- ✅ = Confirmé par au moins 2 sources (Doc + Code)
- ⚠️ = Présent dans 1 source seule ou déduit logiquement
- ❓ = Mentionné mais contradictions non résolues

---

## 3. Points de Certitude Haute (confiance > 0.9)

Les N3 suivants sont confirmés par au moins 2 sources et sont essentiels au workflow :

| N3 Component | Endpoint | Sources | Justification |
|--------------|----------|---------|---------------|
| `comp_ir_report_view` | `/studio/reports/ir` | Doc + Code | Mentionné dans STATUS_REPORT comme opérationnel |
| `comp_stencil_card` | `/studio/arbitrage/forms` | Doc + Code + Implémentation HTML dans bundle A |
| `comp_arbiter_table` | `/studio/reports/arbitrage` | Doc + Code | Route clairement définie |
| `comp_upload_dropzone` | `/studio/designer/upload` | Doc + Code + Fragment HTML dans bundle A |
| `comp_layout_grid` | `/studio/step/5/layouts` | Doc + Code | Route et logique décrites |
| `comp_chat_bubble` | `/studio/majordome/chat` | Doc + Code | Mentionné comme opérationnel |
| `comp_zoom_view` | `/studio/zoom/{level}/{id}` | Doc + Code + Structure identity.py |
| `comp_breadcrumb_nav` | `/studio/zoom/out` | Doc + Code + SullivanNavigator class |

---

## 4. Points d'Incertitude (confiance < 0.7)

| Élément | Confiance | Raison de l'incertitude |
|---------|-----------|------------------------|
| Mode "Expert" de l'Arbiter | 0.65 | Mentionné comme toggle mais pas de route API spécifique dédiée |
| WebSocket `/ir-updates` | 0.40 | Listé comme "à faire" dans STATUS_REPORT, pas dans le code |
| Composants Phase C (HCI Intent Refactoring) | 0.35 | Marqués comme ❌ "à faire" dans STATUS_REPORT |
| Journal Narratif ML | 0.50 | Mentionné dans identity.py mais pas d'endpoint visible |
| Navigation "Ghost Mode" | 0.60 | Concept décrit mais implémentation HTMX non visible |
| Score Sullivan estimé en phase 9 | 0.55 | Logique d'évaluation présente mais pas clairement liée à l'UI finale |

---

## 5. Contradictions Majeures Non Résolues

| Élément | Source A dit | Source B dit | Mon arbitrage |
|---------|--------------|--------------|---------------|
| **Stack Frontend** | SvelteKit (doc PRD, STATUS_REPORT) | HTMX + HTML vanille (fragments dans doc, réalité perçue) | **HTMX est le réel** - STATUS_REPORT mentionne SvelteKit comme frontend-svelte mais les fragments fournis sont HTMX/Tailwind. Pour le Genome, je privilégie HTMX+DaisyUI. |
| **Phase C - HCI Intent Refactoring** | STATUS_REPORT: "à faire" (❌) | Fragments HTML détaillés dans doc | **Partiellement codé** - Les maquettes existent mais l'intégration complète n'est pas terminée. J'ai inclus les composants comme "à venir". |
| **Route /execute** | Définie comme endpoint API principal | Pas clairement liée à une phase UX | **Utilisée en arrière-plan** - C'est l'orchestrateur AETHERFLOW, pas une UI du Studio. Je l'ai mise dans "endpoints_unmapped". |
| **Mode "normal" vs "expert"** | Doc décrit un toggle | Pas de route dédiée visible | **Toggle UI, pas route** - C'est un état d'affichage côté client, pas un endpoint différent. |

---

## 6. Hypothèses Forçantes

Liste des suppositions que j'ai dû faire faute d'informations claires :

1. **Architecture Frontend** : J'ai assumé HTMX + Tailwind + DaisyUI comme stack principal, bien que SvelteKit soit mentionné. Les fragments fournis sont tous en HTMX.

2. **Organisation des routes** : Les routes `/studio/*` retournent des fragments HTMX (pas des pages complètes), injectés dans une colonne centrale du layout triptyque.

3. **Structure N0-N3** : J'ai organisé selon les 9 phases UX du Parcours Sullivan, bien que certaines phases (7-8) aient moins de détails techniques dans le code.

4. **États des composants** : Pour chaque N3, j'ai défini des états loading/empty/error basés sur les patterns usuels HTMX/DaisyUI, non explicitement documentés.

5. **Responsive Design** : J'ai assumé une approche mobile-first avec adaptations spécifiques (stack vs grid, modals en fullscreen mobile).

6. **Phase 8 (Validation)** : Peu de détails dans le code, j'ai inféré une structure logique cohérente avec les autres phases.

7. **Session/État** : J'ai assumé que l'état du workflow est géré côté serveur (session) avec les routes `/studio/session` et `/studio/next/{step}`.

---

## 7. Auto-Évaluation

| Critère | Score /5 | Justification |
|---------|----------|---------------|
| **Exhaustivité** | 4/5 | Les 9 phases sont couvertes, 22 endpoints mappés. Manque les détails de la Phase C (HCI Intent Refactoring) qui est marquée "à faire". |
| **Précision UI** | 4/5 | Visual hints spécifiques pour chaque N3 (pas de "generic"), états définis. Quelques hypothèses sur le responsive. |
| **Cohérence métier** | 4/5 | Respect du vocabulaire Sullivan (Corps/Organe/Atome), du parcours UX 9 phases, et de la philosophie HCI. |
| **Actionnable** | 4/5 | Un dev junior peut coder avec ça - endpoints clairs, descriptions UI précises. Manque les maquettes visuelles finales. |
| **Documentation des incertitudes** | 5/5 | Toutes les hypothèses et contradictions sont explicitement listées. |

### **Score Global : 17/20**

### Points forts :
- Structure N0-N3 complète couvrant tout le parcours UX
- Confrontation explicite entre documentation et code
- Aucun "generic" - tous les visual hints sont spécifiques
- Endpoints non mappés explicitement listés avec justification

### Points à améliorer :
- La Phase C (HCI Intent Refactoring) est incomplet dans les sources
- Manque de logs réels (Bundle C) pour valider les routes actives
- Certains composants de la phase 7-8 sont plus inférés que confirmés

### Recommandations pour utilisation :
1. **Valider avec les développeurs** les routes de la Phase 8 (Validation)
2. **Vérifier** l'état réel du WebSocket `/ir-updates`
3. **Confirmer** le choix HTMX vs SvelteKit pour le Studio
4. **Tester** les endpoints avec des appels réels pour valider les méthodes HTTP

---

## Annexes

### A. Mapping complet des endpoints par phase

```
Phase 1 (IR):          /studio/reports/ir
                       /studio/drilldown

Phase 2 (Arbiter):     /studio/arbitrage/forms
                       /studio/reports/arbitrage
                       /studio/validate

Phase 3 (Genome):      /studio/genome/summary
                       /studio/genome/enriched
                       /studio/next/3

Phase 4 (Defaults):    /studio/distillation/entries
                       /studio/next/4

Phase 5 (Upload):      /studio/designer/upload
                       /studio/step/5/layouts
                       /studio/step/5/select-layout/{id}

Phase 6 (Analysis):    /studio/designer/upload (POST)

Phase 7 (Dialogue):    /studio/majordome/chat

Phase 8 (Validation):  /studio/next/8
                       /studio/step/8 (inféré)

Phase 9 (Adaptation):  /studio/zoom/{level}/{target_id}
                       /studio/zoom/out
                       /studio/finalize

Navigation:            /studio/next/{current_step}
                       /studio/step/{step}
                       /studio/session
                       /studio/session/reset
```

### B. Structure de fichiers suggérée pour le frontend

```
Frontend/
├── templates/
│   ├── studio/
│   │   ├── phase_1_ir.html
│   │   ├── phase_2_arbiter.html
│   │   ├── phase_3_genome.html
│   │   ├── phase_4_defaults.html
│   │   ├── phase_5_upload.html
│   │   ├── phase_6_analysis.html
│   │   ├── phase_7_dialogue.html
│   │   ├── phase_8_validation.html
│   │   └── phase_9_adaptation.html
│   └── components/
│       ├── stencil_card.html
│       ├── blueprint_card.html
│       ├── chat_bubble.html
│       └── zoom_editor.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── htmx.min.js
└── index.html
```

---

*Document généré automatiquement par Kimi Code CLI - Mission Genome Inference v3.0*
