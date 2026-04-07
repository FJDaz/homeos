# HoméOS — Les Lois de l'Animation (Physics Engine)

## 🏛️ Philosophie du Mouvement
Le mouvement dans HoméOS n'est pas un artifice décoratif. C'est une **physique de l'intention**. Rien ne doit apparaître ou disparaître sans une trajectoire logique et une inertie ressentie.

### 1. Courbes Standard (Eases)
- **Ouverture (Panneaux, Modales)** : `Power4.out` — Départ fulgurant, amortissement luxueux.
- **Micro-interactions (Boutons, Hovers)** : `Back.out(1.7)` — Effet rebond léger pour une sensation de matière.
- **Transitions (Switchers)** : `Expo.inOut` — Fluidité maximale.

## 🤖 Moteurs Techniques
### GSAP (GreenSock Animation Platform)
- **Standard** : Toute animation complexe doit passer par GSAP pour garantir le respect de l'orthographe temporelle.
- **Inertie** : Utilisation du plugin Draggable pour une manipulation naturelle des panneaux.

### SPLITTING.JS (Rythme Typographique)
- **Apparition des Titres** : Chaque caractère doit émerger avec un décalage (`stagger`) de 0.05s.
- **Effet Signature** : Opacité 0 -> 1 + Translation Y 10px -> 0px.

## 🎨 Signatures Visuelles
- **Magnétisme** : Le dot grid (8px) exerce une attraction subtile sur les éléments lors du déplacement.
- **Flou de Mouvement** : Légère désactivation du contenu pendant les transitions rapides (filtre blur 2px).
- **Elasticité** : Les bordures des cartes "glass" peuvent tressaillir lors d'un choc ou d'un redimensionnement.

---
*Dernière mise à jour : Mission 210 — Réorganisation Documentaire*
