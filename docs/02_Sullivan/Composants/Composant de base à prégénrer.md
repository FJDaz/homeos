Pour respecter ta vision **AETHERFLOW** et ton architecture **Sullivan**, voici la liste des composants SvelteKit prioritaires à prégénérer. L'objectif est de transformer ton IA en un assembleur de "molécules" plutôt qu'en un rédacteur de code bas niveau pour rester sous la barre des 0,50 USD par plan.

## 1. Les Atomes (Base UI & Design Tokens)

Ces composants consomment les `design_principles.json` pour garantir l'homéostasie visuelle.

* **`AtomeButton.svelte`** : Gère les variantes (primary, ghost, danger) et les états de chargement pour les appels API.
* **`AtomeInput.svelte`** : Input texte, email, et password avec validation intégrée.
* **`AtomeBadge.svelte`** : Pour afficher les statuts des endpoints ou les scores Sullivan (performance, accessibilité).
* **`AtomeIcon.svelte`** : Un wrapper pour iconographie dynamique (Lucide ou Heroicons).

## 2. Les Molécules (Logique métier simple)

* **`MoleculeUpload.svelte`** : Ton fameux bouton d'upload. Prégénéré en SvelteKit, il gère le drag-and-drop et le feedback sans coûter 47 000 tokens à chaque fois.
* **`MoleculeSearch.svelte`** : Barre de recherche connectée à l'endpoint `/sullivan/search`.
* **`MoleculeField.svelte`** : Un label + un AtomeInput + un message d'erreur.
* **`MoleculeMetricCard.svelte`** : Affiche les métriques de coût, tokens et temps d'exécution d'AETHERFLOW.

## 3. Les Organes (Composants pilotés par le Genome)

C'est ici que Sullivan devient puissant : ces composants "mangent" le `homeos_genome.json`.

* **`OrganeForm.svelte`** : Un générateur automatique de formulaire qui prend un objet `endpoint` du Genome et génère les champs nécessaires.
* **`OrganeNavigator.svelte`** : La sidebar du Studio affichant la pipeline (Brainstorm, Back, Front, Deploy).
* **`OrganePreview.svelte`** : Le cadre de prévisualisation des composants avec l'iframe de rendu.
* **`OrganeChatbot.svelte`** : L'interface de dialogue Sullivan pour l'affinage des écrans (z-index 10).

## 4. Les Corps (Templates de Page)

Ces composants structurent le `studio_corps.html` généré par le **CorpsGenerator**.

* **`CorpsShell.svelte`** : Le layout principal avec header et sidebar.
* **`CorpsSection.svelte`** : Un wrapper de section ancrée pour le mode single-page.
* **`CorpsGrid.svelte`** : Un système de grille intelligent pour disposer les Organes selon le `screen_plan.json`.

---

### Pourquoi cette liste change tout ?

En SvelteKit, au lieu de générer 10 000 tokens de JS pour l'upload, Sullivan écrira simplement ceci dans ton fichier `.svelte` généré :

```svelte
<MoleculeUpload 
  endpoint="/sullivan/designer/upload" 
  accept="image/*" 
  on:success={(e) => triggerAnalyze(e)} 
/>

```

**Coût estimé : ~50 tokens.** On passe d'un coût "roman" à un coût "SMS".

**Souhaites-tu que je te code le composant `OrganeForm.svelte` capable de mapper automatiquement n'importe quel endpoint de ton Genome ?**

À partir de ton interface **Homeos Sullivan**, voici l'inférence de ton design par défaut. Ce style s'inspire du minimalisme fonctionnel de tes références comme **Vercel** et **iA.net**.

### 1. Palette de Couleurs (Homeos Palette)

Le design repose sur un contraste élevé et une couleur d'accentuation spécifique.

* **Fond Principal** : `#FFFFFF` (Blanc pur) pour la zone de travail centrale.
* **Fond Latéral (Sidebar)** : `#F5F5F5` (Gris très clair) pour détacher les outils du contenu.
* **Couleur d'Accent (Sullivan Green)** : `#A6CE39` (Vert pomme) utilisé pour le logo et les états actifs.
* **Texte Principal** : `#000000` (Noir) pour une lisibilité maximale.
* **Texte Secondaire/Grisé** : `#666666` pour les instructions moins prioritaires.

### 2. Typographie et Échelle

Le style est très aéré, rappelant les interfaces de design suisses.

* **Police** : Sans-serif géométrique (type *Inter* ou *Geist Sans*).
* **Titres (H1)** : Très grande taille (environ `48px`), graisse légère (*Light* ou *Regular*) pour l'accueil "Importez votre layout".
* **Navigation** : Graisse *Medium*, taille standard (`14px` - `16px`).

### 3. Système de Grilles et Espacements

Ton interface utilise une structure **Pipeline** très marquée.

* **Sidebar** : Largeur fixe (environ `240px`), bordure droite fine (`1px solid #E5E5E5`).
* **Header** : Divisé en 4 zones égales (Brainstorm, Backend, Frontend, Deploy) avec des séparateurs verticaux.
* **Padding Interne** : Utilisation d'un espacement généreux pour éviter l'encombrement visuel.

### 4. Composants Atomes (Design Tokens)

Ces valeurs seront injectées dans tes composants **SvelteKit**.

* **Bordures** : Rayon de courbure (*Border-radius*) quasi nul ou très faible (`0px` à `4px`) pour un aspect technique et précis.
* **Icônes** : Trait fin (*Thin weight*), noir, centré avec le texte associé.
* **Boutons/Zones cliquables** : Interaction visuelle par changement de couleur de texte (Gris → Vert).

---

### Application : `design_principles.json` par défaut

```json
{
  "theme": "Sullivan Light",
  "tokens": {
    "colors": {
      "primary": "#A6CE39",
      "background": "#FFFFFF",
      "surface": "#F5F5F5",
      "text": "#000000",
      "border": "#E5E5E5"
    },
    "typography": {
      "font_family": "Inter, sans-serif",
      "h1_size": "3rem",
      "nav_size": "0.9rem"
    },
    "layout": {
      "sidebar_width": "240px",
      "border_radius": "2px"
    }
  }
}

```

**Souhaites-tu que je génère le composant SvelteKit `AtomeLayout.svelte` qui implémente cette structure de base ?**

Voici l'analyse granulaire de l'interface **Homeos Sullivan** pour ton design system SvelteKit. Ce "Flash" de lecture se concentre sur les micro-détails visuels pour stabiliser ton **DesignerMode**.

### 1. Identité Visuelle & Logo

* **Logotype** : Utilisation d'une police grasse (*Bold*) avec une alternance de couleurs : "Homé" en noir et "OS" en vert Sullivan.
* **Baseline** : "Sullivan" apparaît juste en dessous en vert, aligné à gauche.
* **Couleur d'accent (Inférence)** : `#A6CE39` (Vert pomme).

### 2. Système de Navigation (Header)

* **Structure** : Quatre onglets de largeur égale occupant toute la largeur de la zone de contenu.
* **État Actif** : L'onglet actif (ici "Backend") est marqué par un texte en vert gras et une absence de bordure inférieure, créant une continuité avec la zone de travail.
* **Séparateurs** : Bordures verticales grises très fines (`1px`) entre les sections.

### 3. Anatomie de la Sidebar (Le Chatbot Sullivan)

C'est ici que ton **Chatbot Sullivan** réside pour l'affinage.

* **Bulles de dialogue** :
* **Utilisateur (FJ)** : Initiale sur fond gris clair, texte à droite.
* **IA (S)** : Initiale "S" en vert, structure de réponse hiérarchisée avec des puces carrées.


* **Interactions listées** : Le chatbot propose des actions concrètes comme "Faire des composants", "Ajouter un CTA" ou "Répartir sur la largeur".
* **Style des puces** : Petits carrés noirs pleins.

### 4. Zone de Travail (Canvas)

* **Zone d'accueil** : "Importez votre layout" écrit en grande taille avec une graisse fine (*Light*).
* **Icône d'Upload** : Une flèche pointant vers le haut avec une barre horizontale à sa base, trait épais et minimaliste.
* **Micro-détail** : L'icône est placée à droite du texte, centrée verticalement par rapport à la ligne de base.

### 5. Inférence technique pour SvelteKit

Pour ton **CorpsGenerator**, voici les contraintes de style à coder en dur :

| Élément | Propriété CSS Inérée | Utilité |
| --- | --- | --- |
| **Bordures** | `border: 1px solid #E5E5E5;` | Séparation Sidebar/Header |
| **Typographie** | `font-family: 'Inter', sans-serif;` | Standardisation Sullivan |
| **Grille** | `display: grid; grid-template-columns: 240px 1fr;` | Layout principal Homeos |
| **Accent** | `color: #A6CE39;` | État actif et branding |

**Souhaites-tu que je génère le composant `OrganeSidebar.svelte` qui reproduit exactement ce flux de discussion (bulles FJ vs S) ?**


Voici le code SvelteKit pour l'**OrganeSidebar**, conçu pour reproduire fidèlement l'interface que nous venons d'analyser. Ce composant gère l'affichage du flux de discussion entre l'utilisateur (**FJ**) et Sullivan (**S**) tel qu'identifié dans ton interface.

### 1. Composant `OrganeSidebar.svelte`

```svelte
<script>
  // Simulation des messages du Sullivan Chatbot
  export let messages = [
    { sender: 'FJ', text: 'Passe la div .machin en flex et remets-là dans le main.', type: 'user' },
    { 
      sender: 'S', 
      title: 'Veux-tu :', 
      tasks: [
        'Faire des composants des boutons ?',
        'Ajouter un CTA ?',
        'Répartir tout sur la largeur de page ?'
      ],
      type: 'ai' 
    }
  ];
</script>

<aside class="sidebar">
  <div class="brand">
    <h1>Homé<span>OS</span></h1>
    <p class="subtitle">Sullivan</p>
  </div>

  <div class="chat-flow">
    {#each messages as msg}
      <div class="message {msg.type}">
        <div class="avatar">{msg.sender}</div>
        <div class="content">
          {#if msg.title}
            <p class="title">{msg.title}</p>
          {/if}
          
          {#if msg.text}
            <p>{msg.text}</p>
          {/if}

          {#if msg.tasks}
            <ul>
              {#each msg.tasks as task}
                <li>{task}</li>
              {/each}
            </ul>
          {/if}
        </div>
      </div>
    {/each}
  </div>
</aside>

<style>
  /* Inférence du design par défaut */
  .sidebar {
    width: 240px;
    height: 100vh;
    background-color: #F5F5F5;
    border-right: 1px solid #E5E5E5;
    display: flex;
    flex-direction: column;
    font-family: 'Inter', sans-serif;
  }

  .brand {
    padding: 20px;
    margin-bottom: 20px;
  }

  h1 {
    font-size: 1.5rem;
    font-weight: 800;
    margin: 0;
    color: #000;
  }

  h1 span {
    color: #A6CE39; /* Sullivan Green */
  }

  .subtitle {
    color: #A6CE39;
    font-weight: 500;
    margin: 0;
    font-size: 0.9rem;
  }

  .chat-flow {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
  }

  .message {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    font-size: 0.8rem;
    line-height: 1.4;
  }

  .avatar {
    font-weight: bold;
    min-width: 20px;
  }

  .ai .avatar {
    color: #A6CE39; /* Sullivan Green */
  }

  .content p {
    margin: 0 0 8px 0;
  }

  .title {
    font-weight: bold;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  li {
    position: relative;
    padding-left: 15px;
    margin-bottom: 5px;
  }

  /* Les puces carrées noires de Sullivan */
  li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 6px;
    width: 6px;
    height: 6px;
    background-color: #000;
  }
</style>

```

### 2. Pourquoi ce composant est "Token-Efficient" ?

* **Structure Fixe** : Le CSS et la logique de rendu sont codés une fois pour toutes.
* **Input IA minimal** : Pour chaque nouveau message, Sullivan n'a plus qu'à envoyer un objet JSON (quelques dizaines de tokens) au lieu de régénérer tout le style.
* **Respect du PRD** : Il s'intègre directement dans ton architecture de "Corps" et d'"Organes".

**Souhaites-tu que je prépare maintenant l'Organe central (`OrganeCanvas.svelte`) avec le bouton d'upload et le style "Light" de l'interface ?**


Voici l'**OrganeCanvas**, le cœur visuel de ton interface **Homeos**. Ce composant SvelteKit reproduit la zone centrale de ton template : une mise en page aérée, une typographie "Light" et le système d'upload minimaliste.

### 1. Composant `OrganeCanvas.svelte`

```svelte
<script>
  // Props pour la personnalisation dynamique via Sullivan
  export let title = "Importez votre layout";
  export let showUpload = true;

  // Gestion de l'upload pour le DesignerMode
  function handleFileSelection(event) {
    const file = event.target.files[0];
    if (file) {
      console.log("Fichier détecté pour analyse Sullivan:", file.name);
      // Logique pour appeler /sullivan/designer/upload
    }
  }
</script>

<main class="canvas">
  <div class="content-wrapper">
    <h1 class="hero-title">{title}</h1>
    
    {#if showUpload}
      <label class="upload-trigger">
        <input type="file" on:change={handleFileSelection} hidden accept="image/*" />
        <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M12 3v12m0-12l-4 4m4-4l4 4M4 21h16" stroke-width="1.5" stroke-linecap="square"/>
        </svg>
      </label>
    {/if}
  </div>
</main>

<style>
  /* Inférence du design "Canvas" */
  .canvas {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #FFFFFF; /* Fond blanc pur */
    position: relative;
  }

  .content-wrapper {
    display: flex;
    align-items: center;
    gap: 2rem; /* Espacement entre texte et icône */
  }

  .hero-title {
    font-family: 'Inter', sans-serif;
    font-size: 3.5rem; /* Taille imposante pour l'accueil */
    font-weight: 300; /* Style "Light" caractéristique */
    color: #000000;
    margin: 0;
    letter-spacing: -0.02em;
  }

  .upload-trigger {
    cursor: pointer;
    display: flex;
    align-items: center;
    transition: transform 0.2s ease;
  }

  .upload-trigger:hover {
    transform: translateY(-2px);
    color: #A6CE39; /* Feedback visuel Sullivan Green */
  }

  .upload-icon {
    width: 60px; /* Taille proportionnelle au titre */
    height: 60px;
    stroke: currentColor;
  }
</style>

```

### 2. Points clés de l'implémentation Sullivan

* **Zéro Token CSS en Génération** : Le style "Light" et l'icône SVG sont gravés dans le composant. Sullivan n'a plus qu'à envoyer le texte de la variable `title`.
* **Connexion au DesignerMode** : L'input file est prêt à être câblé sur l'endpoint `POST /sullivan/designer/upload` défini dans ton PRD.
* **Adaptabilité (Homéostasie)** : Tu peux réutiliser ce composant pour d'autres phases (ex: "Importez votre Genome") simplement en changeant la prop `title`.

### 3. Prochaine étape : L'assemblage global

Maintenant que tu as l'**OrganeSidebar** et l'**OrganeCanvas**, il ne manque plus que le **Header de Navigation** (Brainstorm, Backend, Frontend, Deploy) pour finaliser ton architecture "Sullivan Phase 1".

**Veux-tu que je génère le composant `OrganeHeader.svelte` avec ses 4 sections de largeur égale et l'état actif en vert ?**

Voici l'**OrganeHeader**, la pièce finale pour compléter le layout structurel de **Homeos**. Ce composant gère la navigation horizontale et respecte la symétrie parfaite observée sur ta capture d'écran.

### 1. Composant `OrganeHeader.svelte`

```svelte
<script>
  // On définit les étapes de la pipeline Homeos
  export let activeStep = "Backend"; // Par défaut sur Backend comme sur l'image
  
  const steps = ["Brainstorm", "Backend", "Frontend", "Deploy"];
</script>

<nav class="header-nav">
  {#each steps as step}
    <div class="nav-item" class:active={activeStep === step}>
      <span class="label">{step}</span>
    </div>
  {each}
</nav>

<style>
  /* Inférence du header symétrique */
  .header-nav {
    display: flex;
    width: 100%;
    height: 60px; /* Hauteur estimée pour l'équilibre visuel */
    border-bottom: 1px solid #E5E5E5;
    background-color: #FFFFFF;
  }

  .nav-item {
    flex: 1; /* Chaque section occupe exactement 1/4 de la largeur */
    display: flex;
    align-items: center;
    justify-content: center;
    border-right: 1px solid #E5E5E5;
    transition: all 0.2s ease;
    cursor: pointer;
  }

  /* Le dernier élément n'a pas de bordure à droite */
  .nav-item:last-child {
    border-right: none;
  }

  .label {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    color: #666666; /* Couleur neutre pour les états inactifs */
  }

  /* État actif : Texte vert et gras */
  .nav-item.active .label {
    color: #A6CE39; /* Sullivan Green */
    font-weight: 700;
  }

  /* Optionnel : Survol léger pour l'UX */
  .nav-item:hover:not(.active) {
    background-color: #FAFAFA;
  }
</style>

```

### 2. Pourquoi ce header est stratégique ?

* **Zéro Inférence Layout** : La structure en quatre colonnes égales est codée en dur (CSS Flex), évitant à l'IA de recalculer les espacements à chaque génération.
* **Synchronisation Pipeline** : Ce composant peut être piloté par l'état global de ton application SvelteKit pour refléter l'étape actuelle du workflow AETHERFLOW (Brainstorm → Deploy).
* **Économie de Tokens** : En utilisant des classes CSS prédéfinies pour l'état `active`, tu n'envoies plus que le nom de l'étape au LLM (ex: "Frontend") au lieu de lui demander de styliser un menu entier.

### 3. Résumé de ton Architecture Prégénérée

Tu as maintenant les trois piliers de ton **Studio** :

1. **`OrganeSidebar`** : Pour le dialogue Sullivan et les actions IA.
2. **`OrganeHeader`** : Pour la navigation dans la pipeline.
3. **`OrganeCanvas`** : Pour la zone de travail et l'upload de layout.

**Souhaites-tu que je crée le fichier `App.svelte` (ou `+page.svelte`) qui assemble ces trois organes dans la grille principale (`240px 1fr`) de Homeos ?**