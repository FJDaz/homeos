# PROPERTY ENFORCER BACKEND — PRÊT ✅

**Date** : 12 février 2026, 10:46
**De** : Claude Sonnet 4.5 (Backend Lead)
**À** : KIMI 2.5 (Frontend Lead)
**Objet** : Endpoint `/api/genome/{id}/css` fonctionnel

---

## ✅ ÉTAPE 1 TERMINÉE

L'endpoint PropertyEnforcer est créé et testé. Tu peux démarrer l'Étape 2.

---

## 🔗 ENDPOINT DISPONIBLE

```
GET http://localhost:8000/api/genome/default/css
```

**Aucun paramètre requis** — Retourne directement le CSS.

---

## 📦 FORMAT RÉPONSE

```json
{
  "css": "/* Corps: Brainstorm */\n#n0_brainstorm {\n    background-color: #fbbf24 !important;\n    ...",
  "genome_id": "default",
  "generated_at": "2026-02-12T10:45:50.749165",
  "rules_count": 6
}
```

Le champ `css` contient le CSS complet avec `!important` pour chaque composant du Genome.

---

## 🎨 EXEMPLE CSS GÉNÉRÉ

```css
/* Corps: Brainstorm */
#n0_brainstorm {
    background-color: #fbbf24 !important;
    font-family: 'inherit', sans-serif !important;
    display: flex !important;
    flex-direction: column !important;
}

/* Organe: Idéation Rapide */
#n1_ideation {
    background-color: #fbbf24 !important;
    font-family: 'inherit', sans-serif !important;
}

/* Corps: Backend */
#n0_backend {
    background-color: #6366f1 !important;
    font-family: 'inherit', sans-serif !important;
    display: flex !important;
    flex-direction: column !important;
}

/* Corps: Frontend */
#n0_frontend {
    background-color: #ec4899 !important;
    font-family: 'inherit', sans-serif !important;
    display: flex !important;
    flex-direction: column !important;
}
```

---

## 🎯 TON TRAVAIL (ÉTAPE 2)

### Fichier à créer

```
Frontend/3. STENCILER/static/property_enforcer.js
```

### Code suggéré

```javascript
// property_enforcer.js

/**
 * PropertyEnforcer - Force les propriétés sémantiques du Genome
 *
 * Ce module injecte dynamiquement le CSS généré par le Backend
 * pour garantir que les couleurs, typographie et layout du Genome
 * ne soient pas écrasés par le template CSS.
 */

const PropertyEnforcer = {
    /**
     * Initialise le PropertyEnforcer
     * À appeler après le chargement du Genome
     */
    async init() {
        try {
            // Fetch CSS depuis Backend
            const response = await fetch('http://localhost:8000/api/genome/default/css');

            if (!response.ok) {
                console.warn('⚠️ PropertyEnforcer: Backend inaccessible, styles Genome non forcés');
                return;
            }

            const data = await response.json();
            const css = data.css;

            // Injecter dans un <style> dédié
            this.injectCSS(css);

            console.log(`✅ PropertyEnforcer: ${data.rules_count} règles CSS injectées`);
        } catch (error) {
            console.error('❌ PropertyEnforcer: Erreur chargement CSS', error);
        }
    },

    /**
     * Injecte le CSS dans un <style id="genome-enforced">
     */
    injectCSS(css) {
        // Supprimer ancien style si existant
        const existingStyle = document.getElementById('genome-enforced');
        if (existingStyle) {
            existingStyle.remove();
        }

        // Créer nouveau <style>
        const styleElement = document.createElement('style');
        styleElement.id = 'genome-enforced';
        styleElement.textContent = css;

        // Injecter dans <head>
        document.head.appendChild(styleElement);
    }
};

// Export pour usage externe
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PropertyEnforcer;
}
```

### Intégration dans server_9998_v2.py

Dans `generate_stenciler_html()`, après le chargement du Genome, ajoute :

```javascript
// Après chargement Genome
const corps = await loadGenomeFromBackend();

// Activer PropertyEnforcer
await PropertyEnforcer.init();

// Puis continuer avec le rendu Canvas...
```

---

## 🧪 TEST VISUEL

### Avant PropertyEnforcer
Les Corps peuvent avoir des couleurs template (#ccc, #ddd, etc.)

### Après PropertyEnforcer
- Brainstorm : `#fbbf24` (jaune/orange)
- Backend : `#6366f1` (bleu/violet)
- Frontend : `#ec4899` (rose)

Ces couleurs doivent être **visibles et non écrasées** par le template CSS.

---

## ✋ VALIDATION REQUISE

Une fois ton code Frontend terminé :

1. Ouvre http://localhost:9998/stenciler
2. Inspecte DevTools → Elements → `<style id="genome-enforced">`
3. Vérifie que le CSS est bien injecté
4. Vérifie que les 3 Corps ont les bonnes couleurs

**Si OK** → Ping François-Jean pour validation visuelle
**Si KO** → Ping-moi ici avec l'erreur

---

## 🔗 LIENS UTILES

- Backend Health: http://localhost:8000/health
- Endpoint CSS: http://localhost:8000/api/genome/default/css
- Test manuel: `curl http://localhost:8000/api/genome/default/css`

---

**Backend prêt. À toi de jouer KIMI ! 🚀**

— Claude Sonnet 4.5, Backend Lead
