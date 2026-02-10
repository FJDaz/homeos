# MISSION KIMI : Step 4 - Stenciler (Composants Défaut)

**Date** : 9 février 2026
**Agent** : KIMI (FRD Lead)
**Mode AetherFlow** : BUILD + SURGICAL
**Priorité** : 🔴 P0

---

## 0. RAPPEL OBLIGATOIRE - CHARGER TES SKILLS

⚠️ **AVANT de commencer cette mission** :

1. **Charge tes skills** depuis `.cursor/skills/` :
   - `GENERAL.md` - Règles générales
   - `kimi-binome/SKILL.md` - Ton skill principal
   - `kimi-binome/CHECKLIST.md` - Checklist à suivre
   - `aetherflow-modes/` - Modes AetherFlow
2. **Lis la méthodologie** : `docs/02-sullivan/Methodologies/KIMI_INNOCENT_COMPLETE.md`
3. **Consulte le genome enrichi** : `docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/`

### Tes skills (à charger à chaque run)

```
.cursor/skills/
├── GENERAL.md                    # Règles globales
├── kimi-binome/
│   ├── SKILL.md                  # Ton skill principal
│   ├── CHECKLIST.md              # Checklist obligatoire
│   └── TEMPLATES/                # Templates de travail
├── aetherflow-modes/             # Modes PROTO/BUILD/PROD
├── aetherflow-quickstart/        # Quickstart
└── test-mandatory/               # Tests obligatoires
```

### Note importante

Tu es **KIMI Agent FRD** (dans Cursor), pas le client API Moonshot.

---

## 1. CONTEXTE

Tu es responsable de l'étape 4 du **Parcours UX Sullivan** :

```
Étape 4 : COMPOSANTS DÉFAUT (Stenciler)
→ Affichage des "Stencils" (schémas filaires)
→ Validation "Garder/Réserve" par capacité
```

Le Genome enrichi est prêt (`genome_inferred_kimi_innocent.json`).
Tu dois maintenant implémenter le module **Stenciler** dans `identity.py`.

---

## 2. OBJECTIFS

### 2.1 Créer le module Stenciler

**Fichier cible** : `Backend/Prod/sullivan/identity.py`

Le Stenciler doit :
1. Lire le Genome enrichi (29 composants hiérarchisés)
2. Générer des **schémas filaires SVG** pour chaque Corps (N0)
3. Permettre à l'utilisateur de marquer chaque composant :
   - ✅ **Garder** (inclus dans le design final)
   - 📦 **Réserve** (exclu mais disponible)

### 2.2 Interface attendue

```python
class Stenciler:
    """Génère les schémas filaires depuis le Genome."""

    def __init__(self, genome_path: str):
        """Charge le genome enrichi."""
        pass

    def get_corps(self) -> list[dict]:
        """Retourne la liste des 7 Corps (N0)."""
        pass

    def generate_stencil_svg(self, corps_id: str) -> str:
        """Génère le SVG wireframe pour un Corps donné."""
        pass

    def set_selection(self, component_id: str, status: str) -> None:
        """Marque un composant comme 'keep' ou 'reserve'."""
        pass

    def get_validated_genome(self) -> dict:
        """Retourne le genome filtré (seulement 'keep')."""
        pass
```

---

## 3. INPUTS DISPONIBLES

| Ressource | Chemin |
|-----------|--------|
| Genome enrichi | `docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/genome_inferred_kimi_innocent.json` |
| Wireframes SVG existants | `docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/server_9999_v2.py` (fonction `get_wireframe_svg`) |
| Hiérarchie | Corps (7) → Organes (5) → Cellules (9) → Atomes (3) |

---

## 4. OUTPUTS ATTENDUS

### 4.1 Fichiers à créer/modifier

1. **`Backend/Prod/sullivan/identity.py`**
   - Ajouter classe `Stenciler`
   - Méthodes comme décrit section 2.2

2. **`Backend/Prod/sullivan/studio_routes.py`** (si nécessaire)
   - Route `GET /studio/stencils` → Liste des Corps avec SVG
   - Route `POST /studio/stencils/select` → Marquer keep/reserve
   - Route `GET /studio/stencils/validated` → Genome filtré

### 4.2 Tests unitaires

Créer `Backend/Prod/tests/sullivan/test_stenciler.py` :
- Test chargement genome
- Test génération SVG
- Test sélection keep/reserve
- Test filtrage genome

---

## 5. CONTRAINTES

- **Vanilla JS** : Pas de framework React/Vue
- **SVG inline** : Pas de bibliothèque externe
- **Dimensions** : Desktop First (1440×900)
- **Persistance** : localStorage côté client OU session côté serveur

---

## 6. CRITÈRES D'ACCEPTATION

- [ ] Classe `Stenciler` créée dans `identity.py`
- [ ] Les 7 Corps sont listés avec leur SVG wireframe
- [ ] L'utilisateur peut marquer keep/reserve
- [ ] Le genome filtré ne contient que les composants "keep"
- [ ] Tests unitaires passent
- [ ] Route API fonctionnelle

---

## 7. LIVRAISON

Quand tu as terminé, crée un **compte-rendu** :

**Fichier** : `.claude/mailbox/kimi/CR_STEP4_STENCILER.md`

Contenu :
- Ce qui a été fait
- Fichiers modifiés
- Tests exécutés
- Blocages éventuels
- Prêt pour Step 5 ? (oui/non)

---

**Bonne mission !** 🚀
