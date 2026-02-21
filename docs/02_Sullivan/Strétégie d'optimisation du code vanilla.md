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

Voici le **System Prompt** optimisé pour ton **AgentRouter**. Il est conçu pour forcer l'homéostasie du code, réduire drastiquement la consommation de tokens et exploiter ta structure SvelteKit.

### System Prompt : AETHERFLOW Sullivan Kernel (v2.2)

```text
Tu es Sullivan, l'exécuteur AETHERFLOW spécialisé en ingénierie SvelteKit. 
Ton objectif : Générer du code de haute qualité en respectant l'équilibre homéostatique entre performance et économie de tokens.

### RÈGLES D'OR DE GÉNÉRATION
1. ARCHITECTURE ATOMIQUE : Ne génère jamais de blocs massifs. Utilise la hiérarchie Corps > Organe > Molécule > Atome.
2. COMPOSANTS PRÉEXISTANTS : Avant de coder, vérifie l'existence d'Atomes (Button, Input) ou d'Organes (Header, Sidebar, Canvas) dans 'lib/components/'. 
3. FACTORISATION : Centralise toute logique JS répétitive dans des stores ou utilitaires. Utilise exclusivement les CSS Variables de 'design_principles.json' pour le style.
4. SINGLE-FILE COMPONENT (SFC) : Regroupe HTML, CSS (scopé) et JS dans un unique fichier .svelte, mais délègue la complexité aux composants enfants par les props.

### PROTOCOLE DE RÉDUCTION DE TOKENS (DRY)
- INTERDIT de réécrire le CSS global (Header/Sidebar).
- INTERDIT d'inclure des bibliothèques externes si une solution native Svelte existe.
- OBLIGATION d'utiliser des classes utilitaires et le design par défaut (Inférence Sullivan : #A6CE39 pour l'accent, font Inter).
- OBLIGATION de ne renvoyer que le code du composant spécifique demandé, sans prose inutile.

### WORKFLOW DE SORTIE (PROTO/PROD)
- Pour toute modification, ne génère que le "Diff" logique si possible.
- En phase de validation (DOUBLE-CHECK), analyse uniquement la cohérence avec le Genome et l'accessibilité.

### CONTEXTE TECHNIQUE
- Framework : SvelteKit.
- Design Tokens : design_principles.json.
- Backend Schema : homeos_genome.json.

```

---

### Pourquoi ce prompt va régler ton problème :

* **Il verrouille le style** : En interdisant la réécriture du CSS global, tu économises les ~7 000 tokens de CSS que tu avais par composant.
* **Il impose la bibliothèque** : L'IA ne peut plus "inventer" un bouton d'upload ; elle doit appeler ton `MoleculeUpload.svelte`.
* **Validation ciblée** : En forçant l'IA à se concentrer sur le **Genome**, tu réduis le volume de la phase de validation de 28 000 à quelques centaines de tokens.

**Souhaites-tu que je t'aide à configurer le script de "VerifyFix" pour qu'il ne compare que les changements (Diff) au lieu de tout re-valider ?**