# SULLIVAN_INTERACTIONS — Référence Tailwind Animations & Patterns JS

> Fichier d'input obligatoire pour toute mission Sullivan impliquant des interactions JS.
> Version : 1.0 | 2026-03-17

---

## 1. Transitions Tailwind (classes à utiliser systématiquement)

```html
<!-- Classe de base : toujours ajouter sur l'élément qui se transforme -->
transition-all duration-200 ease-in-out

<!-- Variantes selon la propriété animée -->
transition-opacity       <!-- opacité seule -->
transition-transform     <!-- scale/translate/rotate -->
transition-colors        <!-- background/border/text color -->
transition-[max-height]  <!-- collapse/expand (voir §3) -->

<!-- Durées -->
duration-100  duration-150  duration-200  duration-300  duration-500

<!-- Easing -->
ease-in  ease-out  ease-in-out  ease-linear
```

---

## 2. Visibility Toggle (show/hide)

### Méthode A — classList toggle (simple, sans animation)
```js
// Toggle un seul élément
el.classList.toggle('hidden');

// Forcer visible / caché
el.classList.remove('hidden');
el.classList.add('hidden');
```

### Méthode B — Opacity + pointer-events (fade in/out animé)
```html
<!-- HTML : état initial caché -->
<div id="my-panel"
     class="opacity-0 pointer-events-none transition-opacity duration-200">
  ...
</div>
```
```js
// Ouvrir
el.classList.remove('opacity-0', 'pointer-events-none');
el.classList.add('opacity-100');

// Fermer
el.classList.add('opacity-0', 'pointer-events-none');
el.classList.remove('opacity-100');
```

---

## 3. Collapse / Expand (max-height animé)

**Pattern obligatoire pour tout collapse.** Ne pas utiliser `height: auto` animé (non supporté CSS).

```html
<!-- HTML -->
<div id="collapsible"
     class="overflow-hidden transition-[max-height] duration-300 ease-in-out"
     style="max-height: 0;">
  <div class="p-4"> <!-- padding sur wrapper interne, pas sur collapsible -->
    contenu
  </div>
</div>
```
```js
function toggleCollapse(el) {
  if (el.style.maxHeight && el.style.maxHeight !== '0px') {
    el.style.maxHeight = '0';
  } else {
    el.style.maxHeight = el.scrollHeight + 'px';
  }
}

// Usage
document.getElementById('btn-toggle').addEventListener('click', () => {
  toggleCollapse(document.getElementById('collapsible'));
});
```

### Variante `<details>` / `<summary>` (sans JS si animation non requise)
```html
<details class="border rounded p-2">
  <summary class="cursor-pointer select-none font-medium">Titre section</summary>
  <div class="mt-2 text-sm">contenu</div>
</details>
```
> ⚠ `<details>` n'est pas animable nativement. Si animation requise → utiliser le pattern max-height ci-dessus.

---

## 4. Accordion (un seul item ouvert à la fois)

```html
<div id="accordion">
  <div class="accordion-item">
    <button class="accordion-trigger w-full text-left py-2 font-medium">Section A</button>
    <div class="accordion-content overflow-hidden transition-[max-height] duration-200 ease-in-out" style="max-height:0">
      <div class="py-2 text-sm">Contenu A</div>
    </div>
  </div>
  <!-- répéter pour B, C... -->
</div>
```
```js
document.querySelectorAll('.accordion-trigger').forEach(btn => {
  btn.addEventListener('click', () => {
    const content = btn.nextElementSibling;
    const isOpen = content.style.maxHeight !== '0px' && content.style.maxHeight !== '';

    // Fermer tous
    document.querySelectorAll('.accordion-content').forEach(c => {
      c.style.maxHeight = '0';
    });

    // Ouvrir le cliqué si était fermé
    if (!isOpen) content.style.maxHeight = content.scrollHeight + 'px';
  });
});
```

---

## 5. Slide In / Out (panel latéral ou drawer)

```html
<!-- Panel qui slide depuis la droite -->
<div id="drawer"
     class="fixed right-0 top-0 h-full w-72 bg-white shadow-lg
            translate-x-full transition-transform duration-300 ease-in-out z-50">
  ...
</div>
```
```js
const drawer = document.getElementById('drawer');

function openDrawer() {
  drawer.classList.remove('translate-x-full');
  drawer.classList.add('translate-x-0');
}
function closeDrawer() {
  drawer.classList.remove('translate-x-0');
  drawer.classList.add('translate-x-full');
}
```

---

## 6. Loading / Spinner

```html
<!-- Spinner CSS-only Tailwind -->
<div class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"></div>

<!-- Pulse skeleton -->
<div class="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
```

---

## 7. Bouton avec état actif (toggle group)

```html
<div id="mode-tabs" class="flex gap-1">
  <button data-mode="multiplex" class="mode-btn active-mode">MULTIPLEX</button>
  <button data-mode="council" class="mode-btn">COUNCIL</button>
</div>
```
```js
// CSS : .mode-btn { padding: 4px 10px; border-radius: 4px; font-size: 11px; cursor: pointer; }
//       .active-mode { background: var(--text-primary); color: var(--bg-primary); }

document.querySelectorAll('.mode-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active-mode'));
    btn.classList.add('active-mode');
    setMode(btn.dataset.mode);
  });
});
```

---

## 8. Toast / Notification éphémère

```html
<div id="toast"
     class="fixed bottom-4 right-4 bg-gray-900 text-white text-sm px-4 py-2 rounded shadow
            opacity-0 pointer-events-none transition-opacity duration-200 z-50">
</div>
```
```js
function showToast(msg, duration = 2500) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.remove('opacity-0', 'pointer-events-none');
  t.classList.add('opacity-100');
  setTimeout(() => {
    t.classList.add('opacity-0', 'pointer-events-none');
    t.classList.remove('opacity-100');
  }, duration);
}
```

---

## Règles Sullivan — Interactions

1. **Transition toujours sur l'élément qui se transforme**, pas sur le trigger.
2. **Collapse = max-height**, jamais `height: auto` en CSS.
3. **Fade = opacity + pointer-events-none** (pas `display: none` en milieu d'animation).
4. **`<details>` = acceptable** si pas d'animation requise. Si animation → max-height pattern.
5. **Pas de librairie externe** (Framer, GSAP, Alpine.js) — Tailwind + vanilla JS uniquement.
6. **Z-index BRS/FRD** : content = default | modals = 40 | toasts = 50 | Sullivan panel = 30.
