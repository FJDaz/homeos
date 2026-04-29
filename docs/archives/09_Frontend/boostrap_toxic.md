Bootstrap JS est devenu "toxique"
  pour le développement moderne pour plusieurs raisons, surtout dans
  un cadre pédagogique où l'on veut apprendre de bonnes pratiques.

  1. Pourquoi est-il considéré comme "lourd" et problématique ?

   * Le poids mort : Le fichier bootstrap.bundle.min.js pèse environ
     80 Ko (minifié/gzipped). C'est énorme si vous n'utilisez qu'une
     modale et un menu déroulant. Vous embarquez du code pour le
     Carousel, les Tooltips, le Scrollspy, etc., dont vous n'avez
     souvent pas besoin.
   * La dépendance à Popper.js : Même s'ils ont supprimé jQuery,
     Bootstrap dépend toujours de Popper.js pour le positionnement des
     menus. C'est une couche de complexité en plus.
   * Manipulation directe du DOM : Bootstrap utilise une approche
     "impérative" (il va chercher les éléments et les modifie). Cela
     entre souvent en conflit avec les frameworks modernes (React,
     Vue) qui préfèrent une approche "déclarative".
   * L'accessibilité (A11y) : Bien qu'il s'améliore, faire une modale
     Bootstrap vraiment accessible demande souvent du code
     supplémentaire.

  ---

  2. Comment le "refactorer" (ou s'en débarrasser) ?

  Il existe trois stratégies pour s'alléger tout en gardant les
  fonctionnalités :

  Stratégie A : Utiliser le "Native HTML/CSS" (Le plus propre)
  Aujourd'hui, les navigateurs font nativement ce que Bootstrap JS
  faisait avant.
   * Les Modales : Utilisez la balise <dialog>. Elle gère le focus,
     l'accessibilité et l'affichage "au-dessus" nativement. 
       * JS requis : dialog.showModal() et dialog.close(). C'est tout.
   * Les menus déroulants / Popovers : Utilisez la nouvelle Popover
     API (disponible dans tous les navigateurs récents). Pas besoin de
     JS pour ouvrir/fermer un menu.
   * Les accordéons : Utilisez <details> et <summary>. Zéro ligne de
     JS.

  Stratégie B : Le "Tree-shaking" (Si vous voulez rester sur
  Bootstrap)
  Au lieu d'importer tout le JS de Bootstrap via un CDN, utilisez les
  modules ES (ESM). Si vos élèves utilisent un outil comme Vite ou
  Parcel (très simple à mettre en place avec GitHub Actions), ils ne
  peuvent importer que ce qu'ils utilisent :

   1 // Au lieu de tout importer :
   2 // import 'bootstrap'; 
   3
   4 // Importez uniquement le nécessaire :
   5 import Modal from 'bootstrap/js/dist/modal';
   6 import Dropdown from 'bootstrap/js/dist/dropdown';
   7
   8 // Vite ne gardera que le code de ces deux composants dans le
     fichier final.

  Stratégie C : Remplacer par Alpine.js (Idéal pour les élèves)
  Si vous voulez de l'interactivité (tabs, menus, modales) sans la
  lourdeur, Alpine.js est la solution parfaite pour l'éducation.
   * Poids : ~15 Ko.
   * Style : On écrit la logique directement dans le HTML.
   * Exemple de menu :

   1     <div x-data="{ open: false }">
   2         <button @click="open = !open">Ouvrir</button>
   3         <ul x-show="open" @click.away="open = false">
   4             <li>Lien 1</li>
   5         </ul>
   6     </div>
      C'est beaucoup plus lisible pour un élève qu'un script JS
  complexe caché ailleurs.

  ---

  3. Ma recommandation pour votre classe

  Si vos élèves utilisent Bootstrap pour le CSS (la grille, les
  boutons) mais que vous trouvez le JS toxique :

   1. Gardez le CSS de Bootstrap (ou passez à Tailwind CSS qui est
      plus moderne et n'a aucun JS).
   2. Interdisez le bootstrap.bundle.js.
   3. Apprenez-leur à utiliser <dialog> et <details> pour les
      composants d'interface.
   4. Introduisez Alpine.js pour tout ce qui nécessite un peu de
      logique (menus, filtres, onglets).

  Résultat :
   * Des sites qui chargent instantanément.
   * Un code plus proche des standards du Web actuel.
   * Moins de "magie noire" Bootstrap qu'ils ne comprennent pas.

  Est-ce que vous voulez un exemple de "Modale" moderne sans Bootstrap
  pour leur montrer la différence ?
  