# AetherFlow Adobe Bridge (Conceptual Design)

L'idée d'un plugin Adobe (Photoshop/Illustrator) agissant comme un **Watcher/Sender** est parfaitement réalisable via la plateforme **Adobe UXP (Unified Extensibility Platform)**.

## Architecture du Plugin

### 1. Le "Watcher" (Écouteur de modifications)
En UXP, nous pouvons écouter les événements du document. Dès qu'un calque est modifié, déplacé ou renommé, le plugin analyse si l'élément appartient à la hiérarchie Genome.

```javascript
// Exemple conceptuel de Watcher UXP
const { entrypoints } = require("uxp");
const app = require("photoshop").app;

// On surveille les changements de sélection ou de structure
app.eventListeners.add("select", (event) => {
    const activeLayer = app.activeDocument.activeLayers[0];
    if (activeLayer.name.startsWith("[N3]")) {
        console.log("Composant N3 détecté :", activeLayer.name);
        // Déclenche l'envoi vers le Genome
    }
});
```

### 2. Le "Sender" (Extraction & Transmission)
Le plugin extrait les propriétés critiques (x, y, w, h, couleurs, texte) et les envoie à l'API `localhost:9998`.

```javascript
async function pushToGenome(layer) {
    const payload = {
        id: layer.id,
        name: layer.name.replace("[N3] ", ""),
        x: layer.bounds.left,
        y: layer.bounds.top,
        w: layer.bounds.width,
        h: layer.bounds.height,
        visual_hint: "Extrait depuis Adobe"
    };

    await fetch('http://localhost:9998/api/ingest_component', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
}
```

## Compatibilité Genome
Pour assurer une compatibilité totale, le plugin Adobe utiliserait le même **Lexique de Design** que le Stenciler :
- **Identification** : Utilisation de préfixes de noms de calques (`[N1]`, `[N2]`, `[N3]`).
- **Styles** : Conversion des styles de calques Adobe en tokens CSS AetherFlow.
- **Export Assets** : Génération automatique de SVG/PNG depuis les calques Adobe pour alimenter le `template_latest.svg`.

## Avantages
- **Single Source of Truth** : Le designer travaille dans son outil favori, et le Genome se met à jour en temps réel.
- **Pristine Mode Loop** : Permet de réinjecter des designs haute-fidélité directement dans la boucle de décision du LLM Sullivan.
