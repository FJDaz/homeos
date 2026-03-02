# Compilation de la Logique AetherFlow (Démarche PA-I)

## 1. Vision Stratégique : L'Architecture en "Costume"
La démarche repose sur une séparation hermétique entre la **Structure** (Squelette JS/DOM) et le **Rendu** (Costume CSS). 
- **Objectif** : Atteindre un niveau industriel où le Front-End est une injection dynamique pilotée par un Lexique immuable.
- **Rôle Gemini-PAI** : Garantir la pureté des "Slots" (Conteneurs). Pas de double-balise, pas de wrapper inutile. Le DOM doit être un miroir exact du Lexique.

## 2. Le "Triple Lock" (Verrouillage)
Pour stabiliser HomeOS, trois niveaux de vérité sont synchronisés :
1. **LEXICON_DESIGN.json** : Le code génétique (Naming Convention).
2. **Lexicon.js** : La passerelle logicielle qui distribue ces gènes aux features.
3. **stenciler_v3.html** : La cellule hôte (les Slots vides).

## 3. Méthodologie du "Sondage Technique" (Technical Probe)
Le mode AetherFlow rejette l'essai-erreur visuel flou (Eye-balling).
- **Principe** : L'agent interroge le DOM(`querySelector`) et l'API (`fetch`) pour obtenir des faits cliniques (Nombre d'enfants, Status Code).
- **Raisonnement** : Si le sondage révèle 0 enfant dans un slot alors que le JS est chargé, le blocage est structurel ou infrastructurel.

## 4. Gestion de la Latence et Infrastructure
La répétition actuelle a révélé que la **latence de premier token** et le **caching agressif** sont les ennemis du développement agentique.
- **Décision** : En cas de blocage lié aux serveurs ou au Service Worker, l'acteur PAI (Structure) doit passer le relais à l'acteur Infrastructure (Claude). Vouloir tout faire "au talent" brise la Constitution et corrompt la spécialisation des rôles.

## 5. Conclusion pour la Phase FRD
Pour un utilisateur lambda, la complexité doit être masquée derrière un **Roadmap Operator**. L'utilisateur change une intention dans un document, et l'essaim d'agents s'aligne via ces sondages techniques pour livrer une interface fonctionnelle, belle, et conforme "à l'aveugle".
