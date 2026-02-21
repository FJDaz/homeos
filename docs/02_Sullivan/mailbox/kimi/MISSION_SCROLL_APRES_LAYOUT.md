# 🎯 MISSION KIMI : Scroll Automatique après Validation Layout

**Date** : 10 février 2026
**Agent** : Kimi (Lead FRD)
**Mode** : Aetherflow Hybrid
**Priorité** : Haute
**Statut** : En attente

---

## 📋 Contexte

Le **Carrefour Créatif** (serveur 9998) permet actuellement à l'utilisateur de :
1. Visualiser le genome avec hiérarchie N0-N3
2. Sélectionner des composants (layouts, organes, cellules, atomes)
3. Cliquer sur "Valider (X)" quand la sélection est faite

**Problème** : Après validation, rien ne se passe. L'utilisateur ne sait pas quelle est la prochaine étape.

---

## 🎯 Objectif

Quand l'utilisateur clique sur le bouton **"Valider (X)"**, la page doit :

1. ✅ **Scroll automatiquement** vers le bas de la page
2. 🎨 **Afficher le step suivant** : "Choix du Style"
3. 🖼️ **Proposer 2 options** :
   - **Option A** : Upload d'une maquette (PNG/JPG)
   - **Option B** : Sélection parmi 8 styles par défaut

---

## 🏗️ Architecture (Niveau N2 → N3)

### N2 : Cellule concernée
- **`n2_validation`** : Cellule de validation du choix de layout

### N3 : Atomes à créer

#### 1. Bouton Valider (déjà existant)
- **ID** : `validate-btn`
- **Action actuelle** : Affiche le nombre d'éléments sélectionnés
- **Nouvelle action** : Au clic → `scrollToStyleChoice()`

#### 2. Section Style Choice (à créer)
- **ID** : `section-style-choice`
- **Contenu** :
  - Titre : "📐 Étape 2 : Choisir le Style"
  - 2 Cards :
    - **Card Upload** : Zone drag & drop + bouton "Parcourir"
    - **Card Styles** : Grille 4x2 de 8 miniatures de styles

---

## 💻 Code à Implémenter

### 1️⃣ Ajouter la section cachée dans le HTML

**Localisation** : [server_9998_v2.py:943](server_9998_v2.py#L943)
**Après** : La dernière section (Atomes)

```html
<!-- STEP 2: Style Choice (caché par défaut) -->
<div class="section" id="section-style-choice" style="display: none;">
    <div class="section-header">
        <span>📐 Étape 2 : Choisir le Style</span>
    </div>
    <div class="section-content">
        <div class="row" style="justify-content: center; gap: 32px;">

            <!-- Option A: Upload -->
            <div class="style-option-card">
                <div class="style-option-header">🖼️ Importer ma Maquette</div>
                <div class="upload-zone" id="upload-zone">
                    <span style="font-size: 48px; color: #cbd5e1;">📤</span>
                    <p style="font-size: 14px; color: #64748b; margin-top: 12px;">
                        Glisser-déposer ou cliquer
                    </p>
                    <input type="file" id="file-input" accept="image/*" style="display: none;">
                    <button class="btn-secondary" onclick="document.getElementById('file-input').click()">
                        Parcourir
                    </button>
                </div>
            </div>

            <!-- Option B: Styles par défaut -->
            <div class="style-option-card">
                <div class="style-option-header">🎨 Choisir un Style</div>
                <div class="styles-grid">
                    <!-- 8 miniatures de styles -->
                    <div class="style-card" data-style="minimal">Minimal</div>
                    <div class="style-card" data-style="corporate">Corporate</div>
                    <div class="style-card" data-style="creative">Créatif</div>
                    <div class="style-card" data-style="tech">Tech</div>
                    <div class="style-card" data-style="elegant">Élégant</div>
                    <div class="style-card" data-style="playful">Ludique</div>
                    <div class="style-card" data-style="dark">Dark</div>
                    <div class="style-card" data-style="colorful">Coloré</div>
                </div>
            </div>

        </div>
    </div>
</div>
```

### 2️⃣ Ajouter les styles CSS

**Localisation** : [server_9998_v2.py:819](server_9998_v2.py#L819)
**Avant** : `</style>`

```css
/* Style Choice Section */
.style-option-card {
    width: 450px;
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    transition: all 0.3s;
}
.style-option-card:hover {
    border-color: #7aca6a;
    box-shadow: 0 8px 24px rgba(122,202,106,0.15);
}
.style-option-header {
    font-size: 18px;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 20px;
    text-align: center;
}
.upload-zone {
    border: 2px dashed #cbd5e1;
    border-radius: 12px;
    padding: 40px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
}
.upload-zone:hover {
    border-color: #7aca6a;
    background: #f0fdf4;
}
.styles-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}
.style-card {
    height: 80px;
    background: #f8fafc;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    cursor: pointer;
    transition: all 0.2s;
}
.style-card:hover {
    border-color: #7aca6a;
    background: #7aca6a;
    color: white;
    transform: scale(1.05);
}
.style-card.selected {
    border-color: #7aca6a;
    background: #7aca6a;
    color: white;
}
.btn-secondary {
    margin-top: 12px;
    padding: 8px 24px;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    color: #475569;
    cursor: pointer;
    transition: all 0.2s;
}
.btn-secondary:hover {
    background: #e2e8f0;
}
```

### 3️⃣ Ajouter la fonction JavaScript

**Localisation** : [server_9998_v2.py:1007](server_9998_v2.py#L1007)
**Avant** : `</script>`

```javascript
// Fonction de scroll vers le choix de style
function scrollToStyleChoice() {
    const styleSection = document.getElementById('section-style-choice');
    if (styleSection) {
        // Afficher la section
        styleSection.style.display = 'block';

        // Scroll smooth vers la section
        setTimeout(() => {
            styleSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }, 100);
    }
}

// Gestion upload de fichier
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');

if (uploadZone && fileInput) {
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = '#7aca6a';
        uploadZone.style.background = '#f0fdf4';
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.style.borderColor = '#cbd5e1';
        uploadZone.style.background = 'transparent';
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });
}

function handleFileUpload(file) {
    console.log('Fichier uploadé:', file.name);
    // TODO: Envoyer à Gemini Vision pour analyse
    alert(`Maquette "${file.name}" uploadée ! (À implémenter: analyse Gemini)`);
}

// Gestion sélection de style
document.querySelectorAll('.style-card').forEach(card => {
    card.addEventListener('click', () => {
        // Désélectionner les autres
        document.querySelectorAll('.style-card').forEach(c => c.classList.remove('selected'));
        // Sélectionner celui-ci
        card.classList.add('selected');
        console.log('Style sélectionné:', card.dataset.style);
    });
});
```

### 4️⃣ Modifier le bouton Valider

**Localisation** : [server_9998_v2.py:878](server_9998_v2.py#L878)
**Remplacer** :

```html
<button id="validate-btn" class="validate-btn" disabled>Valider (0)</button>
```

**Par** :

```html
<button id="validate-btn" class="validate-btn" disabled onclick="scrollToStyleChoice()">
    Valider (0)
</button>
```

---

## ✅ Checklist d'Implémentation

- [ ] Ajouter la section HTML cachée `section-style-choice`
- [ ] Ajouter les styles CSS pour les cards de style
- [ ] Ajouter la fonction `scrollToStyleChoice()` au JavaScript
- [ ] Modifier le bouton "Valider" pour appeler la fonction
- [ ] Implémenter le drag & drop pour l'upload
- [ ] Implémenter la sélection des 8 styles par défaut
- [ ] Tester le scroll automatique
- [ ] Vérifier la responsivité mobile

---

## 🧪 Test Manuel

1. Lancer le serveur : `python3 server_9998_v2.py`
2. Ouvrir http://localhost:9998
3. Sélectionner au moins 1 composant
4. Cliquer sur "Valider (X)"
5. **Résultat attendu** : La page scroll vers le bas et affiche "Étape 2 : Choisir le Style"

---

## 📦 Livrable

- **Fichier modifié** : `server_9998_v2.py`
- **Version** : v7.0
- **Commentaire de commit** : `feat(layout): Ajout scroll automatique vers choix de style après validation`

---

**Mission créée par** : Claude (Architecte)
**À exécuter par** : Kimi (Lead FRD)
**Mode d'exécution** : Aetherflow Hybrid
