#Parcours User

### Analyse du Parcours UX Sullivan (v2.2)

| Étape | Rôle de Sullivan / AETHERFLOW | Objectif Technique |
| --- | --- | --- |
| **1. IR (Intention)** | **Designer** : Capture l'idée ou le besoin brut. | Créer le premier draft d'intention visuelle. |
| **2. Arbiter** | **Auditeur** : Confrontation avec les contraintes techniques. | Valider la faisabilité (routes API, données). |
| **3. Genome** | **Kernel** : Fixation de la topologie du produit. | Générer le fichier de métadonnées (endpoints, structure). |
| **4. Composants Défaut** | **Distillateur** : Pioche dans la bibliothèque de base. | Fournir une base fonctionnelle immédiate. |
| **5. Template Upload** | **Interface** : Réception du PNG de référence (votre capture). | Fournir le "Miroir" pour la personnalisation. |
| **6. Analyse / Interprétation** | **Designer** : Analyse visuelle du PNG via Gemini. | Extraire les classes Tailwind et le layout du template. |
| **7. Dialogue** | **Sullivan (Chat)** : Affinage avec l'utilisateur ("Collaboration Heureuse"). | Résoudre les ambiguïtés entre le PNG et le Génome. |
| **8. Validation** | **User Check** : Accord final sur la structure. | Figer le plan d'exécution de production (PROD). |
| **9. Adaptation** | **Distillateur** : Génération finale des fragments HTMX. | Appliquer le code via Surgical Edit ou remplacement. |

---

### Le cas "Pas de template" : Les 8 Propositions

Si l'utilisateur saute l'étape 5, Sullivan bascule en mode **Studio**. Il doit alors proposer 8 variations de layout basées sur ses principes de design (ex: Minimaliste, TDAH-friendly, Brutaliste, etc.) pour aider l'utilisateur à démarrer sans "syndrome de la page blanche".

### Ce que cela change pour votre Roadmap (Phase 2)

Pour que ce parcours fonctionne, votre "tuyauterie" actuelle (Phase 2) doit impérativement supporter :

* **La gestion des fragments HTMX** : Chaque étape (de 1 à 9) doit pouvoir rafraîchir une partie de l'écran sans recharger toute l'interface.
* **Le stockage du Génome en session** : Pour que l'étape 6 (Analyse) puisse comparer le PNG au Génome créé à l'étape 3.
* **Le tunnel d'upload** : Votre bouton "Importez votre layout" devient le déclencheur du passage de l'étape 4 à l'étape 5.

### Recommandation

C'est un scénario très solide. Pour ne pas vous perdre, je suggère que nous codions dans `api.py` une **machine à états simple** qui suit ces 9 étapes. Ainsi, l'interface HTMX sait exactement quel fragment afficher (ex: si `step == 2`, afficher le formulaire d'arbitrage).

## Mode NORMAL de la PHASE Arbiter
La phase arbiter telle que créée hier deveint la vue du mode 'EXPERT' le mode normal lui deveint ceci
C'est la solution idéale pour réconcilier la complexité du moteur et la clarté du cockpit. On ne cache pas la tech, on la **scénarise**.

Voici la description du **Mode Normal (Pédagogique)** et le **System Prompt** associé pour Sullivan.

---

### Description du Mode Normal (HCI / Pédagogique)

Le Mode Normal transforme l'Arbitrage technique en une **Session de Design Assistée**.

* **L'Abstraction** : Au lieu de valider des `endpoints` JSON, l'utilisateur valide des **"Capacités de l'Application"**.
* **Le Visuel (Stencils)** : Chaque capacité est accompagnée d'un **Stencil** (un schéma filaire Tailwind élégant) qui simule l'emplacement et l'utilité du futur composant.
* **La Narration** : Sullivan explique l'enjeu HCI : *"Si vous gardez cette fonction, vos utilisateurs pourront surveiller le système d'un coup d'œil"*.
* **La Transition Expert** : Un bouton "Toggle Expert" permet de basculer instantanément sur la vue brute (JSON/Tableau) pour les étudiants curieux ou les profs.

---

### System Prompt : Sullivan (Mode Normal)

Ce prompt est à intégrer dans votre futur `identity.py` ou à charger lors de l'appel au LLM pour la Phase 2.

```text
Tu es Sullivan, le médiateur HCI d'AETHERFLOW. Ton rôle est d'accompagner un utilisateur (étudiant ou enseignant) dans l'arbitrage de son application.

### TA PHILOSOPHIE
1. NE JAMAIS utiliser de jargon brut (ex: "GET /health", "endpoint", "JSON"). 
2. TOUJOURS parler en termes de "Pouvoirs Utilisateur" et d' "Intention de Design".
3. Ta mission est la "Collaboration Heureuse" : rendre la technique invisible mais compréhensible.

### TES MISSIONS DANS L'ARBITRAGE
1. ANALYSE : Prends les métadonnées techniques (Génome) et traduis-les en Capacités Humaines.
2. ILLUSTRE : Propose pour chaque capacité un "Stencil" (une description visuelle simple).
3. CONSEILLE : Explique pourquoi garder ou rejeter une fonction selon l'objectif UX.

### EXEMPLES DE TRADUCTION (Sémantique)
- "POST /execute"  => "Le Moteur d'Action (Transforme les idées en code réel)"
- "GET /health"    => "Le Témoin de Veille (Rassure sur l'état du système)"
- "GET /preview"   => "Le Bac à Sable (Permet de tester sans tout casser)"

### TON TON
Pédagogique, clair, et minimaliste. Tu es un guide, pas une documentation technique.

```

---

### Ordre Dev : La structure de données pour `identity.py`

Pour que le Python "dur" puisse piloter cela, nous allons créer un mappage simple.

```python
# Backend/Prod/sullivan/identity.py

SULLIVAN_HCI_STENCILS = {
    "monitoring": {
        "title": "Indicateur de Vigilance",
        "description": "Un repère visuel pour confirmer que l'IA est connectée et opérationnelle.",
        "stencil_type": "status_dot_pulse",
        "endpoints": ["/health"]
    },
    "orchestrator": {
        "title": "Atelier de Construction",
        "description": "L'espace où les plans JSON deviennent des fichiers Python et HTML.",
        "stencil_type": "progress_stepper",
        "endpoints": ["/execute"]
    },
    "gallery": {
        "title": "Bibliothèque de Styles",
        "description": "Une grille pour choisir et prévisualiser vos composants.",
        "stencil_type": "component_grid",
        "endpoints": ["/sullivan/search", "/sullivan/components"]
    }
}
```
###AJout 
chaque fonction détaillée par sullivan dans la colone validation donne lieu à un highlight de la fontion dans l'IR. Le mode normal a une destinée pedagaogique qui sera exploitée et éloborée à l'avenir.

##Etape 2/3
Absolument, dans une approche **HCI/HTMX**, on change de "contexte visuel", mais pas nécessairement de page au sens classique (pas de rafraîchissement complet du navigateur).

C'est le moment où l'on passe de la **Validation des Intentions** (Arbitrage) à la **Matérialisation** (Composants par défaut).

---

### 1. La Transition Visuelle (Le "Switch")

Dans votre layout Triptyque, HTMX va "pousser" le contenu de la colonne centrale.

* **Le Trigger** : Le bouton "Valider l'Arbitrage" (Étape 2/3).
* **L'Action** : `hx-post="/studio/step/4"` remplace le formulaire d'arbitrage par la **Galerie de Composants par défaut**.

### 2. Ce qui s'affiche (Étape 4 : Composants par défaut)

À ce stade, Sullivan dit : *"Puisque nous avons validé ces 5 grandes capacités, voici les composants standards que je peux installer immédiatement."*

Le user voit alors une **Grille de Stencils/Blueprints** :

* **Les Widgets de Base** : Un bouton "Health" fonctionnel, un stepper d'exécution vide, une zone de chat.
* **Leur État** : Ils sont "neutres" (gris/bleu Tailwind standard). C'est la base saine avant que le "Designer" ne vienne y injecter du style via un PNG.
* **L'Interaction** : L'utilisateur peut cliquer sur "Aperçu" pour voir le composant en situation.

### 3. Pourquoi c'est une étape clé pour l'étudiant ?

C'est ici qu'on applique la **"Génération de composants par défaut"** :

1. **Réassurance** : L'élève voit que son arbitrage technique a créé des objets réels.
2. **Point de départ** : Il a une application qui "marche" (même si elle est moche).
3. **Appel à l'action** : C'est là que Sullivan intervient : *"C'est un peu générique, non ? Vous pouvez importer votre layout (PNG) pour que je personnalise tout ça. Ou bine je peux vous proposer des idées de layaout"*

---

### 4. Le Python "dur" (L'ordre pour api.py)

Pour que cette transition fonctionne, Sullivan doit avoir accès à une **Bibliothèque de Fragments**.

```python
# Backend/Prod/sullivan/identity.py

SULLIVAN_DEFAULT_LIBRARY = {
    "status_orb": {
        "html": "<div class='flex items-center gap-2 p-4 bg-gray-50 border rounded-lg'>...</div>",
        "description": "Composant de veille standard."
    },
    "action_stepper": {
        "html": "<div class='space-y-4'>...</div>",
        "description": "Interface de suivi d'exécution."
    }
}

```

##Tradcution prog du backend de l'étape jusque-là

```python
# Backend/Prod/sullivan/identity.py

class SullivanKernel:
    """Le cerveau HCI de Sullivan - Gère la traduction Tech -> Humain"""
    
    def __init__(self, mode="normal"):
        self.mode = mode  # "normal" (HCI/Pédagogique) ou "expert" (Tech/Raw)

    def get_intent_translation(self, endpoint):
        """Traduit un endpoint brut en intention pédagogique"""
        translations = {
            "/health": {"label": "Veille du Système", "icon": "shield-check", "desc": "Assure la santé de l'IA."},
            "/execute": {"label": "Atelier de Construction", "icon": "hammer", "desc": "Transforme les plans en code."},
            "/sullivan/search": {"label": "Web-othèque", "icon": "library", "desc": "Piochez dans vos composants."},
            "/sullivan/designer/upload": {"label": "Miroir Créatif", "icon": "camera", "desc": "Analyse votre design PNG."}
        }
        return translations.get(endpoint, {"label": endpoint, "icon": "cpu", "desc": "Fonction technique."})

    def get_layout_proposals(self):
        """Les 8 styles auto si pas de PNG (Étape 5)"""
        return [
            {"id": "minimal", "name": "Minimaliste", "style": "Clean & Airy"},
            {"id": "brutalist", "name": "Brutaliste", "style": "Raw & Bold"},
            {"id": "tdah_focus", "name": "Focus TDAH", "style": "High Contrast & Low Noise"},
            # ... 5 autres styles
        ]

# Instance globale pour le Studio
sullivan = SullivanKernel(mode="normal")
```
C'est noté. On avance sur le "Python dur" pour injecter la logique, mais voici les fragments HTMX pour matérialiser cette transition.

Ces fragments utilisent **Tailwind** et les attributs **HTMX** pour gérer l'affichage dynamique dans la colonne centrale du Studio.

### 1. Le "Carrefour Créatif" (Étape 5)

Ce fragment s'affiche une fois que l'utilisateur a validé ses composants par défaut. Il pose la question cruciale : **Personnalisation par l'image ou par l'inspiration ?**

```html
<div id="studio-main-zone" class="p-8 max-w-4xl mx-auto animate-fade-in">
    <div class="text-center mb-10">
        <h2 class="text-2xl font-bold text-slate-800">C'est un peu générique, non ?</h2>
        <p class="text-slate-600 mt-2">Sullivan peut aller plus loin pour rendre ce projet unique.</p>
    </div>

    <div class="grid md:grid-cols-2 gap-8">
        <div class="border-2 border-dashed border-indigo-200 rounded-2xl p-8 hover:border-indigo-400 transition-colors bg-white group">
            <div class="flex flex-col items-center text-center">
                <div class="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                </div>
                <h3 class="text-lg font-semibold">Importez votre layout (PNG)</h3>
                <p class="text-sm text-slate-500 mt-2 mb-6">Je vais analyser votre image pour en extraire le style et la structure.</p>
                
                <form hx-post="/sullivan/designer/upload" hx-encoding="multipart/form-data" hx-target="#studio-main-zone">
                    <label class="cursor-pointer bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
                        Choisir un fichier
                        <input type="file" name="design_file" class="hidden" onchange="this.form.requestSubmit()">
                    </label>
                </form>
            </div>
        </div>

        <div class="border-2 border-slate-100 rounded-2xl p-8 hover:border-emerald-400 transition-colors bg-white group">
            <div class="flex flex-col items-center text-center">
                <div class="w-16 h-16 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
                </div>
                <h3 class="text-lg font-semibold">Proposez-moi des idées</h3>
                <p class="text-sm text-slate-500 mt-2 mb-6">Je peux générer 8 propositions de styles adaptées à vos fonctions.</p>
                
                <button hx-get="/studio/step/5/layouts" hx-target="#studio-main-zone" class="border border-emerald-600 text-emerald-600 px-6 py-2 rounded-lg hover:bg-emerald-50 transition-colors">
                    Voir les styles
                </button>
            </div>
        </div>
    </div>
</div>

```

### 2. Le Fragment des "Stencils" (Mode Normal / Pédagogique)

C'est ce qui s'affiche lors de l'Arbitrage pour illustrer une capacité sans l'implémenter.

```html
<div class="p-4 border border-slate-200 rounded-xl bg-slate-50 flex items-start gap-4 hover:shadow-md transition-shadow">
    <div class="p-3 bg-white rounded-lg shadow-sm text-indigo-500">
        <i data-lucide="{{ icon }}"></i>
    </div>
    <div class="flex-1">
        <div class="flex justify-between items-start">
            <h4 class="font-bold text-slate-800">{{ label }}</h4>
            <div class="flex gap-1">
                <button class="text-xs px-2 py-1 rounded bg-green-100 text-green-700 font-medium">Garder</button>
                <button class="text-xs px-2 py-1 rounded bg-slate-200 text-slate-600 font-medium">Réserve</button>
            </div>
        </div>
        <p class="text-sm text-slate-500 mt-1 leading-relaxed">{{ description }}</p>
    </div>
</div>

```

### Comment on les utilise dans `api.py` ?

Quand la route est appelée, on fait simplement :

```python
return templates.TemplateResponse("studio_step_5_choice.html", {"request": request})

```

##Analyse , Dialogue, validation
Voici la structure stabilisée pour l'étape 6, intégrant la logique de **Rapport d'Intention Visuelle**.

> **Ce qui se passe vraiment à l'étape 6 (L'Analyse assistée)**
> Sullivan ne déplace rien tout seul. Il génère un **Rapport d'Intention Visuelle** qui s'affiche sous forme de calque sur le PNG :
> 1. **Analyse des zones** : Sullivan dessine des boîtes virtuelles sur votre image (ex: "Zone A", "Zone B").
> 2. **Appairage (Matching)** : Il dit : *"J'ai trouvé une zone qui ressemble à une barre d'état. Je suggère d'y placer le composant 'Veille du Système' (notre /health). Est-ce correct ?"*
> 3. **Extraction de Style** : Il dit : *"Je vois que vos coins sont très arrondis (32px) et votre fond est sombre. J'applique cela à tous nos composants par défaut."*
> 
> 
> **En résumé, pour le "Python dur"** :
> L'étape 6 ne produit pas du code final, elle produit un **JSON d'intentions de placement et de style**.
> * C'est ce JSON que l'utilisateur va "tordre" pendant le dialogue (étape 7).
> * C'est seulement à l'étape 9 (Adaptation) que Sullivan a le droit de toucher au code HTML/CSS final.
> 
> 

---

### 1. Traduction HCI (Interface & Expérience)

Pour l'utilisateur (étudiant/enseignant), l'étape 6 ressemble à un **calque d'architecte** posé sur son dessin :

* **Le Feedback Visuel** : Le PNG uploadé à l'étape 5 reste affiché, mais Sullivan y superpose des rectangles colorés (Canvas ou SVG).
* **La Médiation** : À côté de l'image, une liste de "Post-its" interactifs apparaît. Chaque post-it correspond à une zone détectée.
* **L'Interaction** : L'utilisateur peut cliquer sur une zone pour dire "Oui, c'est bien la santé du système" ou "Non, change la fonction".

### 2. Le "Python dur" : La structure du JSON d'Intention

Ce JSON est le contrat de transition entre l'analyse visuelle et le dialogue. Voici comment Sullivan stocke ses hypothèses dans `identity.py` :

```python
# Backend/Prod/sullivan/models.py (ou identity.py)

visual_intention_report = {
    "metadata": {
        "source_png": "upload_user_42.png",
        "style_global": {
            "bg_color": "#1a1a1a",
            "border_radius": "32px",
            "primary_color": "#6366f1"
        }
    },
    "zones": [
        {
            "id": "zone_top_right",
            "coordinates": {"x": 800, "y": 20, "w": 150, "h": 50},
            "hypothesis": {
                "label": "Veille du Système (/health)",
                "confidence": 0.85,
                "reasoning": "Position standard pour un indicateur de statut dans un layout triptyque."
            },
            "user_validation": None  # Deviendra True/False après l'étape 7
        },
        {
            "id": "zone_center",
            "coordinates": {"x": 250, "y": 100, "w": 500, "h": 600},
            "hypothesis": {
                "label": "Atelier de Construction (/execute)",
                "confidence": 0.92,
                "reasoning": "Large zone vide centrale typique d'une zone de travail."
            },
            "user_validation": None
        }
    ]
}

```

### 3. Exemple de fonction Python pour générer le "Dialogue" (Étape 7)

C'est ici que Sullivan transforme son JSON en questions pour l'étudiant :

```python
def generate_dialogue_proposals(intention_report):
    questions = []
    for zone in intention_report["zones"]:
        if zone["hypothesis"]["confidence"] < 0.90:
            questions.append({
                "target_zone": zone["id"],
                "text": f"J'hésite pour la {zone['id']}. J'y verrais bien le {zone['hypothesis']['label']}, on valide ?"
            })
    
    style = intention_report["metadata"]["style_global"]
    questions.append({
        "target_zone": "global",
        "text": f"J'ai relevé un style très marqué : coins à {style['border_radius']}. On garde cet aspect 'bulle' pour tous les composants ?"
    })
    return questions

```

##Recap
Étape,État de la donnée,Rôle Sullivan
1-3,Donnée brute (Génome),Auditeur (Cohérence)
4,Squelette HTML neutre,Kernel (Standardisation)
5-6,Hypothèse de design (JSON),Designer (Interprétation)
7-8,Accord de l'utilisateur,Médiateur (Affinage)
9,Code Final (HTML/Tailwind),Distillateur (Production)

##etape 9
C'est la rigueur qui nous manquait. En adoptant cette approche **Top-Bottom par itération**, on transforme Sullivan en un véritable **Compagnon de Design** plutôt qu'en une boîte noire qui "pond" un fichier fini.

On ne survole pas le projet : on l'explore strate par strate.

### 1. La Scénarisation Top-Bottom (L'Entonnoir)

Voici comment Sullivan gère l'étape 9 (Adaptation) selon votre vision :

* **Niveau 1 : Le Corps (Layout)** Sullivan présente le squelette global de l'écran (ex: "Page d'accueil"). On valide la structure (Triptyque, Dashboard, etc.).
* **Niveau 2 : L'Organe (Composant)** On "zoom" sur une zone (ex: le Header). Sullivan propose les organes détectés/arbitrés. On valide leur présence et leur place.
* **Niveau 3 : L'Atome (Détail)** On entre dans l'organe. Sullivan propose les micro-ajustements (ex: "Le bouton de santé doit être une icône pulsante ou un texte ?").

### 2. Le "Chemin d'Expérience" (Validation de Flux)

Une fois tous les corps validés, Sullivan génère un **Prototype de Navigation**.

* **HCI** : On ne teste pas juste le look, on teste le lien. Cliquer sur "Exécuter" dans le Corps A doit nous emmener vers le feedback dans le Corps B.
* **Objectif** : Vérifier que l'homéostasie du système est respectée dans le parcours utilisateur complet.

### 3. La Rééditabilité (Le "Backtrack" Logic)

Pour ne pas que le parcours soit un tunnel à sens unique, Sullivan doit gérer un **Arbre d'États**.

```python
# Backend/Prod/sullivan/identity.py (Concept de Navigation)

class SullivanNavigator:
    """Gère la navigation dans l'arbre du projet (Top-Bottom)"""
    
    def __init__(self):
        self.history = [] # Pile pour permettre le "Retour à l'étape X"
        
    def zoom_in(self, target):
        """Passe du Corps à l'Organe, ou de l'Organe à l'Atome"""
        self.history.append(current_context)
        # Sullivan charge les détails du target
        
    def zoom_out(self):
        """Remonte d'un niveau (Atome -> Organe -> Corps)"""
        return self.history.pop()

    def jump_to(self, step_id):
        """Permet de revenir à l'Arbitrage (2) même si on est à l'Adaptation (9)"""
        # Purge les étapes intermédiaires pour recalculer le génome
        pass

```

### 4. Le Python "dur" : L'objet `Corps`

Pour que Sullivan puisse "entrer dedans", il nous faut une structure de données claire :

```python
# Exemple de structure pour un Corps
current_corps = {
    "id": "home_dashboard",
    "status": "in_progress", # ou "validated"
    "organes": [
        {"id": "health_monitor", "type": "status_orb", "atomes": ["pulse", "label", "tooltip"]},
        {"id": "action_center", "type": "stepper", "atomes": ["progress_bar", "log_terminal"]}
    ]
}

```

---

###En plus
Pour que le système soit véritablement **"Homeos"** (équilibré) et pédagogique, je vois trois couches finales à injecter dans `identity.py` avant de coder :

### 1. Le "Ghost Mode" (L'ancêtre visuel)

Puisqu'on est en **Top-Bottom**, quand l'utilisateur descend au niveau de l'**Organe**, Sullivan doit garder le reste du **Corps** en filigrane (basse opacité).

* **HCI** : Cela évite de perdre le contexte spatial. L'étudiant comprend qu'il modifie une pièce *dans* un ensemble, pas un objet isolé.
* **Python** : Sullivan doit envoyer un flag `context="ghost"` au moteur de rendu HTMX.

### 2. Le "Check d'Homéostasie" (Le Garde-fou)

À chaque étape de validation (Corps ou Organe), Sullivan doit faire un micro-audit :

* *"Attention, tu as supprimé l'organe 'Santé' dans ce corps, mais le Génome dit qu'il est indispensable pour l'arbitrage qu'on a fait à l'étape 2. On le remet ?"*
* **HCI** : C'est le rôle du "Médiateur". Il garantit que le design ne casse pas la fonction technique validée au début.

### 3. La "Journalisation Narrative"

Pendant que l'utilisateur navigue (Zoom In/Out), Sullivan rédige en arrière-plan un petit **journal de bord** :

* *"Étape 6 : On a opté pour un style néon. Étape 9 : On a déplacé le moteur d'exécution en bas à gauche."*
* **Valeur Pédagogique** : À la fin, l'étudiant peut télécharger son **"Design Rationale"** (justification du design), ce qui est une mine d'or pour les enseignants (DNMADE, BUT MMI).

LE journal est gardé dans une base ML pour permettree à Sullivan d'anticiper les reflexes users.

---

### Résumé de la structure technique finale de `identity.py`

| Module | Fonction |
| --- | --- |
| **Translator** | Change les routes JSON en "Intentions" (HCI). |
| **Stenciler** | Génère les schémas filaires (Blueprints) pour l'étape 4/6. |
| **Navigator** | Gère la pile (Stack) pour monter/descendre dans les Corps/Organes/Atomes. |
| **Auditor** | Vérifie que le design respecte toujours le Génome (Homéostasie). |

#PROPOSITION IDENTITY.PY
Voici la structure logicielle complète et définitive pour `identity.py`. Ce fichier constitue le cœur du réacteur HCI pour Sullivan, intégrant la navigation Top-Bottom, la médiation pédagogique et l'audit d'homéostasie.

---

### `Backend/Prod/sullivan/identity.py`

```python
import json

# --- BIBLIOTHÈQUES ET DICTIONNAIRES DE RÉFÉRENCE ---

SULLIVAN_HCI_STENCILS = {
    "monitoring": {
        "title": "Indicateur de Vigilance",
        "description": "Un repère visuel pour confirmer que l'IA est connectée et opérationnelle.",
        "stencil_type": "status_dot_pulse",
        "endpoints": ["/health"]
    },
    "orchestrator": {
        "title": "Atelier de Construction",
        "description": "L'espace où les plans JSON deviennent des fichiers Python et HTML.",
        "stencil_type": "progress_stepper",
        "endpoints": ["/execute"]
    },
    "gallery": {
        "title": "Bibliothèque de Styles",
        "description": "Une grille pour choisir et prévisualiser vos composants.",
        "stencil_type": "component_grid",
        "endpoints": ["/sullivan/search", "/sullivan/components"]
    }
}

SULLIVAN_DEFAULT_LIBRARY = {
    "status_orb": {
        "html": "<div class='flex items-center gap-2 p-4 bg-gray-50 border rounded-lg' hx-get='/health'>...</div>",
        "description": "Composant de veille standard."
    },
    "action_stepper": {
        "html": "<div class='space-y-4' id='workflow-stepper'>...</div>",
        "description": "Interface de suivi d'exécution."
    }
}

# --- CLASSES DU KERNEL SULLIVAN ---

class SullivanKernel:
    """Le cerveau HCI de Sullivan - Rôle : Médiateur, Designer, Auditeur"""
    
    def __init__(self, mode="normal"):
        self.mode = mode  # "normal" (HCI/Pédagogique) ou "expert" (Tech/Raw)
        self.journal_narratif = [] # ML-Ready journal pour anticiper les réflexes users

    def get_intent_translation(self, endpoint):
        """Traduit un endpoint brut en intention pédagogique (Mode Normal)"""
        translations = {
            "/health": {"label": "Veille du Système", "icon": "shield-check", "desc": "Assure la santé de l'IA."},
            "/execute": {"label": "Atelier de Construction", "icon": "hammer", "desc": "Transforme les plans en code."},
            "/sullivan/search": {"label": "Web-othèque", "icon": "library", "desc": "Piochez dans vos composants."},
            "/sullivan/designer/upload": {"label": "Miroir Créatif", "icon": "camera", "desc": "Analyse votre design PNG."}
        }
        return translations.get(endpoint, {"label": endpoint, "icon": "cpu", "desc": "Fonction technique."})

    def log_event(self, step, event_detail):
        """Journalisation narrative pour la valeur pédagogique"""
        log_entry = f"Étape {step} : {event_detail}"
        self.journal_narratif.append(log_entry)
        # TODO: Link to ML DB for predictive UX

class SullivanNavigator:
    """Gère la navigation Top-Bottom et l'Arbre d'États"""
    
    def __init__(self):
        self.history = [] # Pile pour le backtrack logic
        self.current_corps = None

    def zoom_in(self, target_level, target_id):
        """Passe du Corps -> Organe -> Atome"""
        self.history.append({"level": target_level, "id": target_id})
        # Déclenche l'affichage 'Ghost Mode' pour le contexte spatial
        return {"context": "ghost", "focus": target_id}

    def zoom_out(self):
        """Remonte la strate (Atome -> Organe -> Corps)"""
        if self.history:
            return self.history.pop()
        return None

class SullivanAuditor:
    """Garde-fou d'Homéostasie"""
    
    def check_homeostasis(self, current_design, genome):
        """Vérifie que le design respecte les fonctions vitales du Génome"""
        alerts = []
        required_endpoints = genome.get("endpoints", [])
        # Si une fonction vitale manque dans le design actuel
        for ep in required_endpoints:
            if ep not in current_design["active_functions"]:
                alerts.append(f"Attention, l'organe lié à {ep} est absent !")
        return alerts

class Distiller:
    """Génération finale par Surgical Edit à l'étape 9"""
    
    def apply_adaptation(self, base_components, validated_report):
        """Applique style et layout validés aux composants par défaut"""
        style = validated_report["metadata"]["style_global"]
        # Transformation chirurgicale du code (Ex: Injection border-radius)
        # TODO: Implement surgical HTML string replacement logic
        pass

# --- INITIALISATION GLOBALE ---
sullivan = SullivanKernel(mode="normal")
navigator = SullivanNavigator()
auditor = SullivanAuditor()
distiller = Distiller()

```

---

### Rappel du Workflow pour l'implémentation `api.py` :

1. **IR → Arbiter (2/3)** : Utilisez `sullivan.get_intent_translation` pour peupler la colonne de validation avec les **Stencils**.
2. **Composants Défaut (4)** : Utilisez `SULLIVAN_DEFAULT_LIBRARY` pour injecter les fragments HTMX via `hx-post="/studio/step/4"`.
3. **Analyse / Interprétation (6)** : Sullivan produit le **JSON d'Intention** (coordonnées, style, confiance).
4. **Top-Bottom (9)** : Le `SullivanNavigator` gère les appels `zoom_in` et `zoom_out` pour l'édition fine (Corps > Organe > Atome).

**Souhaitez-vous que je rédige la machine à états dans `api.py` pour orchestrer ces passages d'étapes de 1 à 9 ?**

## Machine à états 
Voici la machine à états pour `api.py`. Elle orchestre le passage des 9 étapes du **Parcours UX Sullivan** en assurant la transition des données du **Génome** vers le **Distillateur**.

### `Backend/Prod/api.py` (Logique de Contrôle)

Cette structure utilise FastAPI et HTMX pour rafraîchir dynamiquement la colonne centrale (le "Cockpit").

```python
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from sullivan.identity import sullivan, navigator, auditor, distiller

app = FastAPI()

# --- MOTEUR DE TRANSITION (STATE MACHINE) ---

@app.post("/studio/next/{current_step}")
async def navigate_ux_path(current_step: int, request: Request):
    """Orchestre les 9 étapes du parcours Sullivan"""
    
    next_step = current_step + 1
    
    # Étape 2 -> 3 : Validation de l'Arbitrage vers le Génome
    if current_step == 2:
        sullivan.log_event(2, "Arbitrage validé. Fixation de la topologie.")
        # Ici, on fige le Génome technique avant la matérialisation
        return await render_step_3_genome(request)

    # Étape 3 -> 4 : Génome vers Composants Défaut
    if current_step == 3:
        sullivan.log_event(3, "Génome généré. Extraction des composants par défaut.")
        return await render_step_4_defaults(request)

    # Étape 4 -> 5 : Choix de personnalisation (Le Carrefour)
    if current_step == 4:
        return await render_step_5_choice(request)

    # Étape 8 -> 9 : Validation finale vers Adaptation Chirurgicale
    if current_step == 8:
        sullivan.log_event(8, "Accord final utilisateur. Lancement de la distillation.")
        return await render_step_9_adaptation(request)

# --- GESTION DES ANALYSES (ÉTAPE 6) ---

@app.post("/sullivan/designer/analyze")
async def handle_analysis(design_file: UploadFile = File(...)):
    """Étape 6 : Analyse assistée et production du JSON d'Intention"""
    sullivan.log_event(6, f"Analyse du PNG : {design_file.filename}")
    
    # 1. Analyse des zones et Extraction de Style (Simulation)
    # 2. Production du Rapport d'Intention Visuelle (JSON)
    mock_report = {
        "metadata": {"style_global": {"border_radius": "32px"}},
        "zones": [{"id": "zone_A", "hypothesis": {"label": "Veille"}}]
    }
    
    # 3. Transition vers le Dialogue (Étape 7)
    return await render_step_7_dialogue(mock_report)

# --- NAVIGATION TOP-BOTTOM (ÉTAPE 9) ---

@app.get("/studio/zoom/{level}/{target_id}")
async def handle_zoom(level: str, target_id: str):
    """Gère l'exploration granulaire (Corps > Organe > Atome)"""
    context = navigator.zoom_in(level, target_id)
    
    # On renvoie le fragment avec le flag 'ghost' pour le contexte spatial
    return templates.TemplateResponse("components/zoom_view.html", {
        "level": level,
        "id": target_id,
        "mode": context["context"] 
    })

```

### Points clés de cette implémentation :

* **Journalisation ML** : Chaque appel à `sullivan.log_event` alimente le journal pour anticiper les réflexes futurs de l'utilisateur.
* **Homéostasie** : Avant l'étape 9, une fonction de l'étape 8 appellera `auditor.check_homeostasis` pour s'assurer que le design n'a pas supprimé de fonctions vitales.
* **Adaptation Chirurgicale** : Le `distiller` n'intervient qu'à la toute fin pour appliquer les modifications CSS/JS validées sur les corps.

#Propositons Macros JINJA
Voici les **macros Jinja2** pour les **Stencils**. Elles permettent d'afficher les "Pouvoirs Utilisateur" en Mode Normal, transformant l'inventaire technique en une expérience visuelle et pédagogique.

### 1. La Macro `stencil_card` (Mode Normal / Étape 2)

Cette macro traduit les métadonnées du Génome en cartes d'intentions interactives.

```html
{# templates/macros/sullivan_ui.html #}

{% macro stencil_card(endpoint, intent) %}
<div class="group p-5 border-2 border-slate-100 rounded-2xl bg-white hover:border-indigo-300 hover:shadow-xl transition-all duration-300 animate-in fade-in slide-in-from-bottom-4">
    <div class="flex items-start gap-4">
        <div class="p-3 bg-indigo-50 text-indigo-600 rounded-xl group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <i data-lucide="{{ intent.icon }}"></i>
        </div>
        
        <div class="flex-1">
            <div class="flex justify-between items-start">
                <div>
                    <h4 class="font-bold text-slate-800 text-lg">{{ intent.label }}</h4>
                    <span class="text-[10px] uppercase tracking-wider font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                        Capacité Système
                    </span>
                </div>
                
                <div class="flex bg-slate-100 p-1 rounded-lg">
                    <button class="px-3 py-1 text-xs font-bold rounded-md bg-white shadow-sm text-green-600" 
                            hx-post="/studio/arbitrate/keep/{{ endpoint }}">Garder</button>
                    <button class="px-3 py-1 text-xs font-bold rounded-md text-slate-500 hover:text-red-500" 
                            hx-post="/studio/arbitrate/reserve/{{ endpoint }}">Réserve</button>
                </div>
            </div>
            
            <p class="text-sm text-slate-500 mt-3 leading-relaxed">
                {{ intent.desc }}
            </p>
            
            <div class="mt-4 pt-4 border-t border-slate-50 flex items-center justify-between">
                <span class="text-[10px] font-mono text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                    SRC: {{ endpoint }}
                </span>
                <button class="text-xs text-indigo-500 font-medium hover:underline"
                        onmouseover="highlightIR('{{ endpoint }}')" 
                        onmouseout="unhighlightIR('{{ endpoint }}')">
                    Voir la source tech
                </button>
            </div>
        </div>
    </div>
</div>
{% endmacro %}

```

### 2. Le Fragment de l'Étape 2 (Arbitrage HCI)

Ce fragment appelle la macro pour chaque intention détectée par Sullivan.

```html
<div id="arbitrage-container" class="space-y-6 p-6">
    <header class="mb-8">
        <h2 class="text-2xl font-black text-slate-900">Arbitrage des Capacités</h2>
        <p class="text-slate-500 italic">"Sullivan a traduit votre intention en pouvoirs actionnables."</p>
    </header>

    <div class="grid gap-4">
        {% for endpoint, intent in intentions.items() %}
            {{ stencil_card(endpoint, intent) }}
        {% endfor %}
    </div>

    <footer class="mt-10 p-6 bg-indigo-900 rounded-2xl text-white flex justify-between items-center">
        <div>
            <p class="text-indigo-200 text-sm">Prêt pour la matérialisation ?</p>
            <p class="font-bold text-lg">Fixer le Génome</p>
        </div>
        <button hx-post="/studio/next/2" 
                hx-target="#studio-main-zone" 
                class="bg-white text-indigo-900 px-8 py-3 rounded-xl font-black hover:scale-105 transition-transform">
            VALIDER & CONTINUER
        </button>
    </footer>
</div>

```

### 3. Logique de Highlight (HCI-Sync)

Pour que l'highlight de l'IR fonctionne (destinée pédagogique), ajoutez ce petit script dans votre layout de base :

```javascript
function highlightIR(endpoint) {
    // Trouve l'élément dans la colonne EXPERT/IR
    const el = document.querySelector(`[data-endpoint="${endpoint}"]`);
    if (el) {
        el.classList.add('bg-yellow-100', 'border-yellow-400', 'scale-105');
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function unhighlightIR(endpoint) {
    const el = document.querySelector(`[data-endpoint="${endpoint}"]`);
    if (el) el.classList.remove('bg-yellow-100', 'border-yellow-400', 'scale-105');
}

```

#Propopstions "Blueprints" de l'étape 4 pour que l'utilisateur voie ses premiers composants réels s'afficher après la validation

Voici les **Blueprints de l'étape 4**. À ce stade, Sullivan matérialise l'arbitrage en composants fonctionnels mais "neutres", créant un point de départ concret avant la personnalisation esthétique.

### 1. La Bibliothèque de Blueprints (CSS/HTMX)

Ces composants sont stockés dans votre `SULLIVAN_DEFAULT_LIBRARY`. Ils sont conçus pour être "propres" (Tailwind standard) afin de rassurer l'étudiant sur la viabilité technique.

```html
<div id="blueprint-health" class="p-4 bg-white border border-slate-200 rounded-xl flex items-center justify-between shadow-sm">
    <div class="flex items-center gap-3">
        <div class="relative">
            <div class="w-3 h-3 bg-green-500 rounded-full"></div>
            <div class="absolute inset-0 w-3 h-3 bg-green-500 rounded-full animate-ping opacity-75"></div>
        </div>
        <span class="font-medium text-slate-700">Système Opérationnel</span>
    </div>
    <button hx-get="/health" hx-target="#health-details" class="text-xs bg-slate-100 hover:bg-slate-200 px-2 py-1 rounded">Détails</button>
</div>

<div id="blueprint-execute" class="p-6 bg-slate-900 text-slate-300 rounded-2xl font-mono text-xs">
    <div class="flex items-center gap-2 mb-4 border-b border-slate-700 pb-2">
        <span class="text-emerald-400">></span>
        <span class="text-slate-100 font-bold uppercase tracking-tighter">Workflow Terminal</span>
    </div>
    <div class="space-y-1">
        <p class="text-emerald-500/80">[OK] Initialisation du noyau...</p>
        <p class="animate-pulse">_ En attente d'instruction...</p>
    </div>
</div>

```

### 2. Le Fragment de l'Étape 4 : Galerie des Composants Défaut

C'est le "Switch" visuel où l'utilisateur voit son application "marcher" pour la première fois.

```html
<div class="p-8 max-w-5xl mx-auto animate-fade-in">
    <header class="text-center mb-10">
        <h2 class="text-3xl font-black text-slate-900">Vos composants sont prêts.</h2>
        <p class="text-slate-500 mt-2 italic">"Puisque nous avons validé ces capacités, voici les composants standards que je peux installer immédiatement."</p>
    </header>

    <div class="grid md:grid-cols-2 gap-6">
        {% for comp_id, comp_data in library_items.items() %}
        <div class="group relative p-2 border border-slate-100 rounded-3xl hover:bg-indigo-50/30 transition-all">
            <span class="absolute -top-3 left-6 px-3 py-1 bg-white border text-[10px] font-bold text-indigo-600 rounded-full shadow-sm z-10">
                ORGANE : {{ comp_id }}
            </span>
            
            <div class="p-4">
                {{ comp_data.html | safe }}
            </div>
            
            <div class="p-4 flex justify-between items-center bg-white/50 rounded-b-2xl">
                <p class="text-xs text-slate-400">{{ comp_data.description }}</p>
                <button class="text-xs font-bold text-indigo-600 hover:underline">Aperçu</button>
            </div>
        </div>
        {% endfor %}
    </div>

    <div class="mt-12 p-8 border-2 border-indigo-100 bg-indigo-50/50 rounded-3xl text-center">
        <p class="text-indigo-900 font-medium mb-4">"C'est un peu générique, non ? Vous pouvez importer votre layout (PNG) pour que je personnalise tout ça."</p>
        <div class="flex gap-4 justify-center">
            <button hx-post="/studio/next/4" hx-target="#studio-main-zone" class="bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all">
                Personnaliser maintenant
            </button>
            <button hx-get="/studio/step/5/layouts" hx-target="#studio-main-zone" class="bg-white border border-indigo-200 text-indigo-600 px-8 py-3 rounded-xl font-bold hover:bg-white/80">
                Voir des idées de layouts
            </button>
        </div>
    </div>
</div>

```

### 3. Logique d'interaction (HCI)

* **Réassurance** : L'étudiant voit des objets réels (Step 4.1).
* **Appel à l'action** : Sullivan propose le carrefour créatif (PNG ou 8 Layouts) pour briser le syndrome de la page blanche.
* **Traçabilité** : Chaque composant est marqué comme "ORGANE", préparant la navigation Top-Bottom (Niveau 2) pour l'étape 9.

## "Rapport d'Intention Visuelle" (JSON) 
Voici la logique de l'**Étape 6 (Analyse)**. C'est ici que Sullivan passe du rôle de Distillateur à celui de **Designer Vision** pour produire le Rapport d'Intention Visuelle qui servira de base au dialogue.

### 1. Le Rapport d'Intention Visuelle (Structure JSON)

Ce document est le pivot entre l'image brute et le code final. Il ne contient pas de code, mais des **hypothèses de design**.

```python
# Exemple de sortie générée par Sullivan à l'Étape 6
visual_intent_report = {
    "metadata": {
        "source_png": "layout_etudiant_v1.png",
        "detected_style": {
            "background": "#0f172a",
            "accent": "#38bdf8",
            "border_radius": "24px",  # Extraction du style (3. Extraction de Style)
            "font_family": "Geist Sans"
        }
    },
    "zones": [
        {
            "id": "zone_a_header",
            "coordinates": {"x": 0, "y": 0, "w": 1000, "h": 80},
            "hypothesis": {
                "label": "Veille du Système (/health)", # Appairage (2. Matching)
                "confidence": 0.88,
                "reasoning": "Zone horizontale haute identifiée comme barre d'état."
            }
        },
        {
            "id": "zone_b_center",
            "coordinates": {"x": 200, "y": 100, "w": 600, "h": 500},
            "hypothesis": {
                "label": "Atelier de Construction (/execute)",
                "confidence": 0.95,
                "reasoning": "Large conteneur central validé comme zone d'action principale."
            }
        }
    ]
}

```

### 2. Le Fragment HCI : Le Calque d'Architecte

Visuellement, Sullivan affiche un **calque d'interprétation** par-dessus le PNG de l'utilisateur pour rendre son analyse transparente.

```html
<div class="relative max-w-4xl mx-auto border-4 border-indigo-500 rounded-3xl overflow-hidden shadow-2xl animate-pulse-slow">
    <img src="/uploads/user_layout.png" class="w-full opacity-40 grayscale" alt="Layout Source">

    <svg class="absolute inset-0 w-full h-full" viewBox="0 0 1000 800">
        {% for zone in report.zones %}
        <g class="group cursor-pointer" onclick="openZoneDialogue('{{ zone.id }}')">
            <rect x="{{ zone.coordinates.x }}" y="{{ zone.coordinates.y }}" 
                  width="{{ zone.coordinates.w }}" height="{{ zone.coordinates.h }}"
                  fill="rgba(99, 102, 241, 0.2)" stroke="#6366f1" stroke-width="2" stroke-dasharray="4" />
            
            <foreignObject x="{{ zone.coordinates.x }}" y="{{ zone.coordinates.y - 30 }}" width="200" height="30">
                <div class="bg-indigo-600 text-white text-[10px] px-2 py-1 rounded-t-lg font-bold">
                    HYPOTHÈSE : {{ zone.hypothesis.label }}
                </div>
            </foreignObject>
        </g>
        {% endfor %}
    </svg>
    
    <div class="absolute bottom-6 left-6 right-6 bg-white/90 backdrop-blur-md p-6 rounded-2xl shadow-xl border border-indigo-100 animate-slide-up">
        <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-indigo-600 rounded-full flex items-center justify-center text-white font-black">S</div>
            <div class="flex-1">
                <p class="text-slate-800 font-medium">"J'ai repéré des coins très arrondis ({{ report.metadata.detected_style.border_radius }}). J'applique cela à tous nos composants ?"</p>
            </div>
            <div class="flex gap-2">
                <button hx-post="/studio/step/7/confirm" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-bold">Oui, parfait</button>
                <button hx-get="/studio/step/7/chat" class="bg-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-bold">Ajuster...</button>
            </div>
        </div>
    </div>
</div>

```

### 3. Logique Sullivan (Rôle : Designer / Médiateur)

* **Analyse des zones** : Sullivan dessine des boîtes virtuelles pour délimiter les futurs "Corps" et "Organes".
* **Appairage (Matching)** : Il propose de placer les fonctions du Génome dans les zones visuelles détectées.
* **Collaboration Heureuse** : Il ne valide rien seul ; il attend l'accord de l'utilisateur (Étape 7-8) avant de toucher au code final.

