# Analyse du Bug M361 (Extraction des Illustrations)

Suite à l'investigation du plantage de la fonction "analyser les illustrations" (timeout du poll après 90 secondes avec `design_tokens: null`), voici les 5 hypothèses, de la plus probable à la plus "créative/périphérique" :

### 1. [La plus probable] Le Hard-Timeout de 30 secondes court-circuite silencieusement l'extraction
Dans `design_token_extractor.py`, l'appel à la Vision est strictement limité à 30s : `await asyncio.wait_for(client.generate_with_image(...), timeout=30.0)`. Le nouveau modèle `gemini-3.1-pro-preview` via le SDK `google-genai` prend souvent plus de 30s pour décortiquer un écran UI complexe et ses bounding boxes. 
**Résultat :** Au bout de 30s, `asyncio` lève une exception `TimeoutError`. Elle est catchée par le `except asyncio.TimeoutError:`, la fonction retourne `{}`. La ligne `if not tokens: continue` force l'algorithme à zapper l'écran et à passer au suivant SANS rien inscrire dans le `manifest.json`. Les 4 écrans enchaînent des timeouts et à la fin, rien n'est sauvegardé.

### 2. [Très probable] Empoisonnement du Threadpool par les threads "zombies"
Dans `gemini_client.py`, tu utilises `asyncio.to_thread(call)` car le SDK google-genai est synchrone. Lorsqu'un timeout de 30s survient (Hypothèse 1), l'Event Loop abandonne la tâche... mais **le thread sous-jacent avec la requête HTTP n'est pas tué**. 
**Résultat :** Pour 4 écrans, tu vas accumuler 4 requêtes synchrones massives qui tournent dans le vide en arrière-plan. Quand la boucle lance l'écran 2, 3 et 4, les limitations au niveau des sockets HTTP, du threadpool Python ou du rate-limiting de l'API Gemini vont garantir que les écrans suivants échoueront ou timeront eux aussi.

### 3. [Probable] Résolution de l'Identity : le syndrome du projet "fantôme" (homéos-default)
La route `/api/imports/extract-tokens` reçoit un JWT : `sess.token`. La fonction `get_active_project_id(token)` dans `bkd_service.py` utilise `decode_access_token`. 
**Résultat :** Si un élément de configuration (secret JWT, import path) fait planter le décodage sans lever d'erreur bloquante (grace au fallback `except Exception`), la fonction renvoie `"homéos-default"`. L'extraction va alors s'exécuter dans le dossier d'imports de `homéos-default` (qui lui aussi existe !), modifier SON manifeste et échapper au poll du navigateur qui, lui, scrute `dnmade1-2026-blart-samuel`.

### 4. [Moins probable] Condition de course sur le Set `_ACTIVE_EXTRACTIONS` 
Le système de protection contre les clics intempestifs `_ACTIVE_EXTRACTIONS.add(active_id)` est en place. 
**Résultat :** Si le frontend envoie par inadvertance deux requêtes rapides, ou si une requête précédente est restée bloquée de manière non prévue (le `finally: discard()` n'a pas été appelé à cause d'une fermeture brutale), la route API retourne immédiatement `{"status": "already_running"}`. Le hic : le code frontend (`ManifestSullivan.js`) ignore royalement cette réponse, affiche "analyse en cours...", attend bêtement 15 secondes, et le poll tourne dans le vide pendant 90s.

### 5. [La plus créative] Surcompression Base64 pre-Gemini et fuite mémoire invisible
Dans `extract_tokens_for_screen`, l'image source est convertie en Base64 : `image_b64 = base64.b64encode(image_path.read_bytes())`. Les étudiants importent parfois des images en .png non optimisées.
**Résultat :** Si l'image fait 5 ou 10MB, le payload JSON vers l'API explose. Bien que les images actuelles dans le dossier de blart-samuel soient légères (< 200Ko), une seule image lourde peut provoquer un "Silent Death" du parser JSON ou du buffer mémoire Python au moment où httpx tente d'allouer la chaîne massive, tuant le thread d'extraction instantanément avant qu'il ne puisse écrire le manifeste.
