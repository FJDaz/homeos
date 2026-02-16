# 06 - Résilience Offline & Local-First

L'objectif d'Aetherflow est d'offrir une expérience de création fluide, même en l'absence de réseau, en déplaçant la logique de l'interface vers le client (Navigateur).

## 1. La Stratégie du "Local-First"
Contrairement au modèle "Cloud-First" où tout dépend du serveur, le "Local-First" considère le serveur comme une simple sauvegarde.

- **Persistance Immédiate** : Chaque modification (événement) est enregistrée dans l'**IndexedDB** du navigateur. En cas de crash du serveur ou de coupure réseau, le travail n'est pas perdu.
- **Synchronisation Différée** : Le `offline_sync.js` surveille l'état de la connexion. Dès que le serveur Python redevient disponible, il pousse la pile d'événements en attente.

## 2. Service Workers (Disponibilité Statique)
En externalisant le HTML et le JavaScript, nous pouvons utiliser un **Service Worker** pour mettre en cache l'application. 
- **Bénéfice** : L'interface s'ouvre instantanément même sans internet.
- **Autonomie** : Le moteur de rendu (Sullivan Engine) fonctionne de manière autonome tant qu'il a le Genome chargé en mémoire locale.

## 3. Le Pont Adaptatif
Le Pont sémantique (`bridge_core.js`) intègre une logique de "File d'attente" :
1. L'utilisateur fait une action.
2. Le pont valide le schéma localement (Vigilance JS).
3. L'action est ajoutée à la file d'attente (Offline Queue).
4. Le rendu est mis à jour immédiatement (Optimistic UI).
5. La file est vidée dès que le serveur répond.

---

## 🏗️ Impact Architectural
Cette approche transforme le navigateur en un véritable **nœud système** complet, et non plus en simple visualiseur passif. C'est l'atout majeur pour un système conçu pour être utilisé partout, tout le temps (l'esprit HomeOS).
