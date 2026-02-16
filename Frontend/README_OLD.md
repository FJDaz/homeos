# Interface HTML - Sullivan Kernel

Interface web simple pour rechercher et gérer des composants via Sullivan Kernel.

## 🚀 Démarrage rapide

### 1. Démarrer l'API

```bash
cd /Users/francois-jeandazin/AETHERFLOW
python -m Backend.Prod.api
```

L'API sera disponible sur `http://127.0.0.1:8000`

### 2. Ouvrir l'interface HTML

Ouvrez simplement `frontend/index.html` dans votre navigateur.

**Note** : Pour éviter les problèmes CORS, vous pouvez aussi servir les fichiers statiques via l'API FastAPI (voir ci-dessous).

### 3. Utiliser l'interface

1. **Rechercher un composant** :
   - Entrez une description du composant recherché (ex: "Un bouton de connexion avec validation")
   - Optionnellement, spécifiez un User ID
   - Cliquez sur "Rechercher"

2. **Voir les résultats** :
   - Le composant trouvé s'affiche avec ses scores (Sullivan, Performance, Accessibilité, etc.)
   - Un badge indique où le composant a été trouvé (Cache Local, Elite Library, ou Généré)

3. **Consulter les composants disponibles** :
   - Cliquez sur l'onglet "Cache Local" ou "Elite Library"
   - Cliquez sur "Actualiser" pour recharger la liste
   - Cliquez sur un composant pour remplir automatiquement le champ de recherche

## 📁 Structure

```
frontend/
├── index.html          # Page principale
├── css/
│   └── styles.css      # Styles CSS
├── js/
│   └── app.js          # Logique JavaScript
└── README.md           # Ce fichier
```

## 🔌 API Endpoints utilisés

### POST `/sullivan/search`
Recherche un composant par intention.

**Request** :
```json
{
  "intent": "Un bouton de connexion avec validation",
  "user_id": "default_user"
}
```

**Response** :
```json
{
  "success": true,
  "component": {
    "name": "component_bouton_connexion",
    "sullivan_score": 75.0,
    "performance_score": 80,
    "accessibility_score": 70,
    "ecology_score": 75,
    "popularity_score": 60,
    "validation_score": 80,
    "size_kb": 10,
    "created_at": "2026-01-27T22:00:00",
    "user_id": "default_user"
  },
  "found_in": "generated",
  "message": "Component found in generated"
}
```

### GET `/sullivan/components`
Liste tous les composants disponibles.

**Query Parameters** :
- `user_id` (optionnel) : Filtrer par utilisateur

**Response** :
```json
{
  "local_cache": [
    {
      "name": "component_1",
      "sullivan_score": 75.0,
      ...
    }
  ],
  "elite_library": [
    {
      "name": "component_2",
      "sullivan_score": 90.0,
      ...
    }
  ]
}
```

## 🎨 Personnalisation

### Changer l'URL de l'API

Modifiez la constante `API_BASE_URL` dans `js/app.js` :

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000';  // Changez ici
```

### Styles

Les styles sont dans `css/styles.css`. Vous pouvez modifier :
- Les couleurs (gradient dans `body`, couleurs des badges)
- La mise en page (grid, flexbox)
- Les tailles de police

## 🐛 Dépannage

### Erreur CORS

Si vous voyez des erreurs CORS, assurez-vous que :
1. L'API FastAPI est démarrée avec CORS activé (déjà configuré dans `api.py`)
2. Vous ouvrez l'interface depuis `http://127.0.0.1:8000` si vous servez les fichiers via FastAPI

### L'API ne répond pas

1. Vérifiez que l'API est démarrée : `curl http://127.0.0.1:8000/health`
2. Vérifiez les logs de l'API pour voir les erreurs
3. Assurez-vous que Sullivan Kernel est correctement initialisé

### Les composants ne s'affichent pas

1. Vérifiez que des composants existent dans `~/.aetherflow/components/` (cache local)
2. Vérifiez que des composants existent dans `components/elite/` (elite library)
3. Utilisez la recherche pour générer un premier composant

## 📝 Notes

- L'interface est en HTML/CSS/JS vanilla (pas de framework) pour compatibilité Mac 2016
- Les composants sont stockés en JSON dans le système de fichiers
- Le score Sullivan est calculé avec les poids : Performance 30%, Accessibilité 30%, Écologie 20%, Popularité 10%, Validation 10%
