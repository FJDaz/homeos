# 💎 Architecture : SVG "Interfacial" — La Pierre de Rosette d'AetherFlow

Ce document propose d'élever le SVG au rang de **langage interfacial primaire**, agissant comme une couche de vérité visuelle radicale (la "Pierre de Rosette") entre le Genome (JSON), les maquettes (PNG) et le code final (HTML/CSS/React/Tailwind).

---

## 🏗️ 1. Le Shift : Du JSON Logique au SVG Interfacial

Actuellement, le `manifest.json` est le juge de paix. Cependant, il est par nature **abstrait** (logique). Le passage au code par un LLM est souvent "lossy" car l'agent doit interpréter la mise en page.

**La Vision** : Utiliser le SVG non pas comme un *export de visualisation*, mais comme le **Backbone de Transmission**.

### Pourquoi le SVG ?
- **Topologie Mathématique** : Contrairement au CSS qui dépend du box-model et du flux, le SVG fige les coordonnées (x,y,w,h).
- **Format LLM-Native** : Les LLM (KIMI/Gemini) manipulent le XML/SVG avec une précision chirurgicale, là où le CSS devient souvent verbeux et fragile.
- **Zéro Ambiguité** : Un bouton en SVG a une forme, une couleur hex et une position absolue. C'est une instruction de design "Pristine".

---

## 🔄 2. La Pipeline "Pierre de Rosette"

Le cycle de vie d'une proposition graphique devient :

1. **PNG (Entrée Élève)** → **SVG (Vision Analyzer)**
   - L'analyzer (Mission 39) ne produit plus seulement un JSON, mais un **SVG Blueprint** qui décalque fidèlement la structure (zones, sidebar, boutons).
2. **SVG (Backbone)** ↔ **JSON (Genome)**
   - Le JSON reste la base de données (l'intellect), mais le SVG est son **incarnation physique**. Ils sont synchronisés par des attributs `data-genome-id` dans le SVG.
3. **SVG** → **Code Final (React/Tailwind/Vanilla)**
   - Un agent (KIMI) traduit le SVG en composants React. Puisqu'il a les coordonnées et les styles inline du SVG, la fidélité graphique est maintenue à 100%.

---

## 🛠️ 3. Mise en Œuvre Technique

### Le "Visual JSON"
Le SVG contiendra des méta-données riches :
```xml
<g class="af-organ" data-genome-id="n1_chat" data-intent="dialogue" data-style="glassmorphism">
  <rect x="10" y="50" width="380" height="200" fill="#ffffff" stroke="#d5d4d0" rx="10" />
  <!-- ... structure visuelle ... -->
</g>
```

### Avantages pour les Élèves
- **Édition Graphique** : On peut modifier le SVG dans Illustrator/Figma et le ré-importer. Le système détecte les changements de `data-genome-id` et met à jour le code automatiquement.
- **Stabilité** : Plus de "prose" ou d'hallucinations de layout. Si c'est dans le SVG, c'est dans l'interface.

---

## 🚀 4. Prochaines Étapes : Mission "SVG Backplane"

- [ ] **Mise à jour d' `analyzer.py`** : Ajouter une fonction `to_svg()` qui génère un blueprint à partir de l'analyse visuelle.
- [ ] **Refacto du Template Viewer** : Lui permettre de devenir l'éditeur (via Stenciler) qui manipule directement ces briques SVG.
- [ ] **KIMI Translator** : Créer un prompt spécialisé "SVG-to-React" qui prend le SVG comme source unique de vérité esthétique.

---
**Verdict** : Le SVG est effectivement notre maillon manquant pour garantir que la "vibe" graphique des élèves ne soit pas perdue dans la traduction vers le code.
