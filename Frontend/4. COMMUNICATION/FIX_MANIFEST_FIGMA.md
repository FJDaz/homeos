# 🛠️ Fix Manifest Figma - Network Access

L'erreur "**Invalid value for allowedDomains**" a été corrigée dans le manifest du plugin.

## 📝 Diagnostic
Figma n'autorise pas une liste `allowedDomains` vide. Si aucun domaine n'est spécifié pour la production, il faut soit mettre `"none"`, soit inclure les domaines autorisés. Comme nous tournons sur `localhost:9998`, nous avons inclus ce domaine dans les deux listes pour garantir l'accès.

## ✅ Correction apportée
Fichier : `AETHERFLOW/Frontend/figma-plugin/manifest.json`

```json
"networkAccess": {
    "allowedDomains": [
        "http://localhost:9998"
    ],
    "devAllowedDomains": [
        "http://localhost:9998"
    ]
}
```

Le plugin devrait maintenant se charger sans erreur dans Figma.
