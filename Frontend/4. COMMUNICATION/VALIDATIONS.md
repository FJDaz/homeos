# REGISTRE DES VALIDATIONS VISUELLES

**Protocole** : PROTOCOLE_VALIDATION_VISUELLE.md  
**Responsable** : KIMI 2.5 (Frontend) + François-Jean (Validation)  
**Statut** : 🟢 ACTIF

---

## 📋 VALIDATIONS EN COURS

| Date | Feature | Fichiers Modifiés | URL | Port | Statut | Validé par |
|------|---------|-------------------|-----|------|--------|------------|
| 2026-02-11 | Structure initiale | `server_9998_v2.py` (basique) | http://localhost:9998 | 9998 | ✅ VALIDÉ | François-Jean |
| 2026-02-11 | **Genome corrigé** | `genome_reference.json` (4 Corps) | - | - | ✅ **CORRIGÉ** | KIMI |
| 2026-02-11 | Mock données 4 Corps | `mocks/corps_previews.json` | - | - | ✅ **CRÉÉ** | KIMI |
| 2026-02-11 | **Layout Viewer** | `server_9998_v2.py` + chemin corrigé | http://localhost:9998 | 9998 | ✅ **VALIDÉ** | François-Jean |
| 2026-02-11 | **Workflow "Trois Clics"** | `server_9998_v2.py` + connexion API Backend | http://localhost:9998/stenciler | 9998/8000 | ✅ **ALL VALIDÉ** | François-Jean |

---

## 🎯 VALIDATIONS À VENIR (Phase 4)

| Feature | Description | Priorité | Statut |
|---------|-------------|----------|--------|
| ~~Bande previews 3 Corps~~ | ~~Affichage horizontal avec drag~~ | ~~🔴 Haute~~ | ✅ **VALIDÉ** 11/02 |
| ~~Canvas Fabric.js~~ | ~~Zone de drop et manipulation~~ | ~~🔴 Haute~~ | ✅ **VALIDÉ** 11/02 |
| ~~Connexion API Backend~~ | ~~Fetch localhost:8000/api/genome~~ | ~~🔴 Haute~~ | ✅ **VALIDÉ** 11/02 |
| PropertyEnforcer | Forcer styles Genome sans écrasement | 🟡 Moyenne | ⏳ En attente |
| Drill-down N1 | Double-clic → affichage Organes | 🟡 Moyenne | ⏳ En attente |
| Sidebar breadcrumb | Fil d'Ariane + bouton retour | 🟡 Moyenne | ⏳ En attente |
| Persistance modifs | POST /api/modifications | 🟢 Basse | ⏳ En attente |

---

## ✅ VALIDATION COMPLÉTÉES

### 2026-02-11 — Structure existante vérifiée

**Fichier** : `server_9998_v2.py`  
**Commande** : `cd Frontend/3. STENCILER && python3 server_9998_v2.py`  
**URL** : http://localhost:9998  
**Résultat** : ✅ Viewer Genome fonctionnel  
**Validé par** : François-Jean

---

### 2026-02-11 — Workflow "Trois Clics" + Connexion API Backend

**Fichiers** :
- `Frontend/3. STENCILER/server_9998_v2.py`
- `Backend/Prod/sullivan/stenciler/main.py`

**Commandes** :
```bash
# Terminal 1 — Backend
cd Backend/Prod && python3 -m uvicorn sullivan.stenciler.main:app --host 0.0.0.0 --port 8000

# Terminal 2 — Frontend
cd Frontend/3. STENCILER && python3 server_9998_v2.py
```

**URLs** :
- Genome Viewer : http://localhost:9998/
- Stenciler : http://localhost:9998/stenciler
- API Backend : http://localhost:8000/api/genome

**Workflow validé** :
- [x] Clic 1 : Sélection composants → "Valider" → scroll style picker
- [x] Clic 2 : Choix style (Minimal) → localStorage → redirect `/stenciler`
- [x] Clic 3 : Stenciler charge → fetch API Backend (:8000) → scroll auto
- [x] 3 Corps affichés (Brainstorm, Backend, Frontend)
- [x] Console : `🧬 Genome chargé via API Backend: 3 corps`
- [x] Aucune erreur CORS
- [x] Aucune erreur JavaScript

**Verdict** : ✅ **ALL VALIDÉ**  
**Validé par** : François-Jean  
**Commentaires** : Workflow complet fonctionnel. Prêt pour Phase 4 suite (PropertyEnforcer, Drill-down).

---

## 📝 TEMPLATE DE VALIDATION

```markdown
### YYYY-MM-DD — [Nom de la Feature]

**Fichiers** :
- `Frontend/3. STENCILER/[fichier].py`
- `Frontend/2. GENOME/[fichier].json`

**Commande** :
cd "Frontend/3. STENCILER" && python3 server_9998_v2.py

**URL** : http://localhost:9998

**Ce qui doit être visible** :
- [ ] Élément 1
- [ ] Élément 2
- [ ] Élément 3

**Screenshots** : `Frontend/screenshots/YYYYMMDD_feature.png`

**Verdict** : ⏳ En attente / ✅ Validé / ❌ À corriger
**Validé par** : [Nom]
**Commentaires** : [Si corrections nécessaires]
```

---

*Registre vivant — Mis à jour à chaque validation*
