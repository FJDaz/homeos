Pour un étudiant de Master 2 en design graphique qui cherche la précision chirurgicale et la maîtrise totale du rendu (le "pixel-perfect" par le code), la bibliographie doit passer du "comment ça marche" au "comment le moteur de rendu respire".

Voici l'extension **"Niveau Expert"** de la base de connaissance Sullivan, classée par piliers méthodologiques.

---

### 1. La Bible des Standards (La Source de Vérité)

* **MDN Web Docs (Mozilla)** : Ce n'est pas un site, c'est la Constitution du Web.
* *Focus étudiant :* Les pages sur le **Visual Formatting Model**. C’est là qu’on apprend comment les boîtes sont calculées (Box Sizing, Stacking Contexts). Indispensable pour comprendre pourquoi un `z-index` ne fonctionne pas.


* **W3C CSS Specifications** : Pour l'étudiant vraiment pointilleux.
* *Focus :* Lire les "Editor's Drafts" sur les modules **Flexbox** et **Grid**. C'est le langage brut des créateurs du CSS.



### 2. Bibliographie : L'Ingénierie du Rendu

* **"CSS Secrets" – Lea Verou** :
* *Pourquoi :* Lea Verou est une experte du W3C. Son livre n'est pas une introduction, c'est une masterclass sur l'utilisation intelligente des propriétés CSS pour résoudre des problèmes de design complexes (bordures, formes, effets de verre dépoli) sans images. **C'est le livre de chevet du " Sullivan Mode ".**


* **"Resilient Web Design" – Jeremy Keith** :
* *Pourquoi :* Un livre court, gratuit et brillant sur la philosophie de la conception web. Il enseigne comment coder pour que le design survive à toutes les tailles d'écran et à toutes les conditions de réseau.


* **"DOM Enlightenment" – Cody Lindley** :
* *Pourquoi :* Pour maîtriser le Vanilla JS sans bibliothèques. Ce livre traite le DOM comme une API de rendu. Il apprend à manipuler les nœuds HTML comme on manipule des calques dans Illustrator.


* **"CSS Pocket Reference" – Eric A. Meyer** :
* *Pourquoi :* Eric Meyer est le pionnier du CSS. C'est le dictionnaire ultime pour vérifier la syntaxe exacte et les valeurs par défaut de chaque propriété.



### 3. Méthodologie et Architecture (L'Antidote à l'Entropie)

* **"Atomic Design" – Brad Frost** :
* *Pourquoi :* Pour comprendre comment passer d'un composant (atome) à une page (organisme). C’est la base théorique de la mutualisation dans AetherFlow.


* **"Object-Oriented CSS" (OOCSS) – Nicole Sullivan** (Concept) :
* *Pourquoi :* Apprendre à séparer la **structure** (la position) de la **peau** (les couleurs/typo). C'est exactement ce qui manque à ton bot actuel.



### 4. Webographie : Les "Maîtres du Pixel"

* **[Josh W. Comeau](https://www.joshwcomeau.com/)** : Ses articles (comme "The Joy of React" ou ses guides sur Flexbox) sont des modèles de pédagogie visuelle interactive. Pour un designer, c'est la référence absolue.
* **[Sara Soueidan](https://www.sarasoueidan.com/blog/)** : La papesse du SVG et de l'accessibilité. Si l'étudiant veut comprendre comment coder des icônes ou des illustrations complexes qui ne cassent jamais, c'est ici.
* **[A List Apart](https://alistapart.com/)** : Le journal historique du web design sérieux. Chercher les articles sur le "Responsive Design" original.
* **[Can I Use](https://caniuse.com/)** : L'outil de vérification pour savoir si une propriété (ex: `subgrid`) est prête pour la production. Un étudiant pointilleux ne code rien sans vérifier son support navigateur.
* **[Frontend Masters](https://frontendmasters.com/books/front-end-handbook/2019/)** : Le "Front-End Developer Handbook". Une vue d'ensemble massive et actualisée de tout l'écosystème.

---

### Le Conseil du Formateur pour l'étudiant pointilleux :

Je lui dirais : *"Le code n'est pas une traduction de ton design, c'est son matériau final. Tu ne dessines pas une boîte, tu écris les règles qui permettent à la boîte de s'auto-générer correctement partout."*

**Est-ce que cette liste te semble assez dense pour calmer sa soif de précision, ou faut-il que j'aille chercher des papiers de recherche sur les algorithmes de rendu des navigateurs (Webkit/Blink) ?**