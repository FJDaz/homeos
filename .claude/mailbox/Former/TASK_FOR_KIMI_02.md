# MISSION #2 POUR KIMI PADAWAN

**De** : Claude-Code (Senior)
**Pour** : KIMI Padawan
**Date** : 3 février 2026
**Priorité** : MOYENNE (après mission #1)
**Statut** : EN ATTENTE (faire APRÈS Sullivan Selecteur)

---

## Prérequis

**CETTE MISSION NE DOIT ÊTRE EXÉCUTÉE QU'APRÈS** la mission #1 (Sullivan Selecteur).
Vérifie que `TASK_FOR_KIMI.md` est terminé et `REPORT_FROM_KIMI.md` existe.

---

## Ta mission

Intégrer l'interface **Arbiter** (`Frontend/arbiter-interface.html`) dans le dispositif HomeOS existant (toolbar + chatbox Sullivan).

**Source** : `Frontend/arbiter-interface.html`
**Cible** : Remplacer le "mic-mac actuel" dans la zone de travail de `/homeos`

---

## Contexte

L'interface `arbiter-interface.html` contient :
- **Panneau gauche (clair)** : Intent Revue - arbitrage des intents
- **Panneau droit (sombre)** : Génome - visualisation Corps/Organes/Cellules
- **Badge flottant** : Sullivan

Cette interface doit s'intégrer dans la zone de travail principale de HomeOS, en cohabitation avec :
- La toolbar Sullivan (déjà en place)
- La chatbox Sullivan (déjà en place)

---

## Les 4 étapes à suivre

### Étape 1 : Analyser la structure actuelle
**Fichiers à lire** :
- `Backend/Prod/templates/studio_homeos.html` — Template actuel
- `Frontend/js/sullivan-super-widget.js` — Widget actuel
- `Frontend/arbiter-interface.html` — Interface à intégrer

**Questions à répondre** :
- Quelle zone DOM est actuellement utilisée pour le contenu principal ?
- Comment l'interface arbiter peut-elle cohabiter avec les tabs existants ?

### Étape 2 : Extraire les styles arbiter
**Action** : Extraire le CSS de `arbiter-interface.html` dans un fichier séparé
**Créer** : `Frontend/css/arbiter.css`

Le CSS doit être :
- Scopé (préfixé `.arbiter-` pour éviter conflits)
- Compatible avec le thème HomeOS existant

### Étape 3 : Créer le composant Arbiter
**Action** : Créer un composant JS pour l'interface arbiter
**Créer** : `Frontend/js/arbiter-panel.js`

```javascript
// Structure attendue
class ArbiterPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(genomeData) {
        // Génère le HTML de l'interface arbiter
        // Panneau gauche: Intent Revue
        // Panneau droit: Génome
    }

    updateGenome(data) {
        // Met à jour la visualisation du génome
    }

    updateIntentRevue(data) {
        // Met à jour le panneau Intent Revue
    }
}
```

### Étape 4 : Intégrer dans HomeOS
**Fichier à modifier** : `Backend/Prod/templates/studio_homeos.html`

**Actions** :
1. Ajouter un nouveau tab "Arbiter" dans la navigation
2. Créer une zone `#tab-arbiter` pour le contenu
3. Inclure les fichiers CSS/JS
4. Initialiser le composant ArbiterPanel

---

## Zones DOM cibles

```html
<!-- Nouveau tab dans la navigation -->
<button class="tab-btn" data-tab="arbiter">Arbiter</button>

<!-- Nouvelle zone de contenu -->
<div id="tab-arbiter" class="tab-content">
    <div class="arbiter-container">
        <!-- Panneau gauche -->
        <div class="arbiter-panel-left">
            <!-- Intent Revue -->
        </div>
        <!-- Panneau droit -->
        <div class="arbiter-panel-right">
            <!-- Génome -->
        </div>
    </div>
</div>
```

---

## RAPPEL PROTOCOLE OBLIGATOIRE

**AVANT de coder, tu DOIS** :

1. [ ] Lire `docs/02-sullivan/ARCHITECTURE_HOMEOS_SULLIVAN.md`
2. [ ] Vérifier `git status`
3. [ ] Mode identifié : **PROD** (-f)
4. [ ] Vérifier que l'interface `arbiter-interface.html` existe
5. [ ] Présenter ton plan à l'utilisateur
6. [ ] Attendre "GO" explicite

---

## Points d'attention

1. **NE PAS casser** le widget Sullivan existant
2. **NE PAS modifier** `sullivan-super-widget.js` sans nécessité
3. **Respecter** le système de tabs existant
4. **Garder** la chatbox Sullivan fonctionnelle
5. **Le badge flottant** peut être supprimé (déjà présent via le widget)

---

## Quand tu as terminé

Crée/mets à jour ton rapport :
```
.claude/mailbox/REPORT_FROM_KIMI.md
```

Avec :
- [ ] Mission #1 : [TERMINÉE/EN COURS]
- [ ] Mission #2 : [TERMINÉE/EN COURS]
- [ ] Fichiers créés/modifiés
- [ ] Tests exécutés
- [ ] Problèmes rencontrés

---

## Ressources

- Interface source : `Frontend/arbiter-interface.html`
- Template HomeOS : `Backend/Prod/templates/studio_homeos.html`
- Widget Sullivan : `Frontend/js/sullivan-super-widget.js`
- Architecture : `docs/02-sullivan/ARCHITECTURE_HOMEOS_SULLIVAN.md`

---

**Bonne continuation, Padawan !**

*— Claude-Code Senior*
