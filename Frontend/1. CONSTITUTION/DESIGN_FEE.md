# DESIGN_FEE.md — Contrat d'Interaction FEE
**Version :** 1.0.0
**Autorité :** FJD (DA) — seule personne habilitée à modifier ce fichier.
**Usage :** Contrat d'animation et d'interaction pour le mode Front-End Engineering (FEE).
S'applique aux **screens projets élèves** uniquement — pas à l'UI système HoméOS.
Complète `DESIGN.md`, ne le remplace pas.

> **Réf :** `docs/02_Sullivan/FEE/GSAP_INTEGRATION_MCP.md`
> **Réf :** `docs/02_Sullivan/FEE/PEDAGOGIE_GSAP_VISUELLE.md`
> **RAG Live :** `https://gsap.com/llms.txt` — Sullivan consulte avant toute génération FEE.

---

## Bibliothèques autorisées

| Lib | Version | Usage |
|---|---|---|
| **GSAP** | 3.x (CDN) | Animations, timelines, interactions |
| **ScrollTrigger** | plugin GSAP | Animations au scroll |
| **SplitText** | plugin GSAP | Animations typographiques lettre/mot |
| **Lenis** | latest (CDN) | Smooth scroll — remplace le scroll natif |

### Chargement
```html
<!-- GSAP core -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<!-- Plugins selon besoin -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>
<!-- Lenis -->
<script src="https://cdn.jsdelivr.net/npm/@studio-freight/lenis@1/bundled/lenis.min.js"></script>
```

Tout code GSAP est injecté dans `projects/{uuid}/logic.js` — jamais inline dans le HTML.

---

## Effets autorisés

### Glossaire étudiant → technique

| Intention étudiant | Effet GSAP | Pattern de base |
|---|---|---|
| "l'un après l'autre" | **Stagger** | `gsap.to('.card', { opacity:1, y:0, stagger: 0.15 })` |
| "collé à la souris" | **Magnetic** | `mousemove` + `gsap.to(el, { x, y, ease:'power2.out' })` |
| "lié à la molette" | **Scrub** | `ScrollTrigger` avec `scrub: 1` |
| "le bloc se fige" | **Pinning** | `ScrollTrigger` avec `pin: true` |
| "effet élastique" | **Elastic/Bounce** | `ease: 'elastic.out(1, 0.3)'` |
| "texte qui s'écrit" | **SplitText** | `new SplitText(el)` + stagger sur `chars` |

---

## Durées et eases

### Durées
| Contexte | Durée recommandée | Max autorisé |
|---|---|---|
| Micro-interaction (hover, focus) | `0.15s` | `0.3s` |
| Entrée d'élément | `0.4s` | `0.8s` |
| Transition de page | `0.6s` | `1.2s` |
| Animation héro / scroll narrative | `1.0s` | `2.0s` |

Durée > `2s` interdit sans validation FJD.

### Eases recommandées
```js
// Entrées douces
ease: 'power2.out'      // standard — la majorité des cas
ease: 'power3.out'      // plus marqué

// Effets organiques
ease: 'elastic.out(1, 0.3)'   // élastique subtil
ease: 'back.out(1.7)'         // légère surdépassement

// Scroll
ease: 'none'            // pour scrub (indexé sur scroll)
```

Eases interdites : `bounce` (cartoonesque), `steps()` sauf typographie intentionnelle.

---

## Smooth Scroll (Lenis)

Initialisation standard dans `logic.js` :
```js
const lenis = new Lenis({ duration: 1.2, easing: t => Math.min(1, 1.001 - Math.pow(2, -10 * t)) });
function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
requestAnimationFrame(raf);

// Synchronisation avec ScrollTrigger
lenis.on('scroll', ScrollTrigger.update);
gsap.ticker.add(time => lenis.raf(time * 1000));
gsap.ticker.lagSmoothing(0);
```

---

## Patterns de production

### Reveal à l'entrée (Stagger)
```js
gsap.from('.card', {
    opacity: 0, y: 30,
    duration: 0.5, stagger: 0.12,
    ease: 'power2.out',
    scrollTrigger: { trigger: '.card-grid', start: 'top 80%' }
});
```

### Pinning section narrative
```js
ScrollTrigger.create({
    trigger: '.hero',
    start: 'top top',
    end: '+=600',
    pin: true,
    anticipatePin: 1
});
```

### Magnetic button
```js
el.addEventListener('mousemove', e => {
    const rect = el.getBoundingClientRect();
    const x = (e.clientX - rect.left - rect.width / 2) * 0.3;
    const y = (e.clientY - rect.top - rect.height / 2) * 0.3;
    gsap.to(el, { x, y, duration: 0.3, ease: 'power2.out' });
});
el.addEventListener('mouseleave', () => gsap.to(el, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.3)' }));
```

### SplitText reveal
```js
const split = new SplitText('.headline', { type: 'words,chars' });
gsap.from(split.chars, { opacity: 0, y: 10, stagger: 0.02, duration: 0.4, ease: 'power2.out' });
```

---

## Règles absolues FEE

- `gsap.killTweensOf('*')` interdit — cibler précisément les éléments
- `ScrollTrigger.refresh()` obligatoire après tout changement de layout dynamique
- `gsap.context()` obligatoire si composant monté/démonté (évite les fuites mémoire)
- Pas d'animation sur `width` ou `height` — toujours `scaleX` / `scaleY` (perf GPU)
- `will-change: transform` à ajouter sur les éléments animés fréquemment
- `MorphSVG` et `DrawSVG` : plugins payants GSAP — vérifier la licence avant usage

---

## Sullivan en mode FEE

Avant toute génération de code GSAP, Sullivan :
1. Consulte `gsap.com/llms.txt` pour la syntaxe à jour
2. Identifie l'effet dans le glossaire étudiant → technique
3. Demande : *"vitesse lente ou rapide ?"* et *"au chargement ou au scroll ?"*
4. Injecte dans `logic.js` uniquement — jamais inline dans le HTML
5. Ajoute un commentaire `// FEE — [nom effet] — Sullivan [date]` sur chaque bloc

---

## Librairies avancées (usage artistique)

`P5.js`, `Three.js`, `Pixi.js` sont **autorisées** avec intention artistique claire.

> FJD : on forme des artistes. Une interface avec P5.js en pièce centrale et un narratif qui vit autour, c'est exactement dans le scope. Ne pas brider ça.

- Usage : élément central de la composition, pas gadget décoratif
- Validation FJD requise avant intégration dans un projet élève
- Sullivan ne génère pas de code P5/Three/Pixi seul — il assiste, l'étudiant pilote

---

## Interdit en FEE

- `anime.js`, `Velocity.js` — remplacés par GSAP
- CSS `animation` complexes dans les screens — déléguer à GSAP
- Effets > `2s` sans validation FJD
- Parallaxe agressive (facteur > 0.5) — donne le mal de mer
