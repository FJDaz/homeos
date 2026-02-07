## **CONFIGURATIONS DE LA SULLY FACTORY PAR COUCHE**

---

## **CONFIGURATION 1 : KIMI 2.5 + SULLY FACTORY (Mode Gratuit Optimisé)**

### **Objectif :** Contourner les biais de KIMI 2.5 gratuit en le forçant à suivre notre orientation

### **Architecture :**
```
[PNG Input] → [5x Gemini Flash (Explorateurs)] → [Groq (Syntoniseur)] → [KIMI 2.5 (Directeur Contraint)]
```

### **Rôle de chaque couche :**

#### **1. Les Workers Gemini Flash (5 instances)**
- **Mission :** "Explorer sous contraintes"
- **Prompt injecté :** 
  ```python
  """
  TU ES UN EXPLORATEUR DE LAYOUT. Ta mission :
  1. Analyse ce PNG et identifie UNIQUEMENT les patterns DaisyUI/Tailwind
  2. Extrais la structure hiérarchique (conteneurs > composants > éléments)
  3. Mappe chaque élément à un composant de l'Elite Library
  4. N'INVENTE RIEN. Si tu ne trouves pas de correspondance, note "UNKNOWN"
  5. Ton output DOIT suivre le schéma JSON strict ci-dessous
  """
  ```
- **Output format :** JSON structuré avec champs obligatoires

#### **2. Le Maître de Chantier Groq (Llama 70B)**
- **Mission :** "Forcer l'alignement sur notre vision"
- **Il reçoit les 5 analyses et produit :**
  - Un "rapport de biais" : ce que KIMI va probablement mal interpréter
  - Un "guide de correction" : instructions spécifiques pour contre-balancer
  - Un "template contraint" : le JSON déjà formaté pour KIMI

#### **3. L'Assembleur KIMI 2.5 (Directeur Contraint)**
- **Mission :** "Exécuter sous influence"
- **Prompt contraint :**
  ```python
  """
  CONTRAT DE GÉNÉRATION - TU N'AS AUCUNE LIBERTÉ
  
  CONTEXTE UTILISATEUR :
  {user_intent_from_sullivan}
  
  ANALYSES PRÉ-PROCESSÉES :
  {groq_processed_analyses}
  
  RÈGLES ABSOLUES (VIOLATION = ÉCHEC) :
  1. Structure imposée : {imposed_structure}
  2. Palette couleurs : {color_palette}
  3. Système espacement : multiples de 4px uniquement
  4. Composants autorisés : liste DaisyUI uniquement
  
  TA TÂCHE :
  Prends les analyses ci-dessus et produis UNIQUEMENT le JSON final.
  Ne commente pas, n'explique pas, ne dévie pas.
  """
  ```

### **Truc pour dévier KIMI :**
```python
# Technique de "Prompt Hijacking"
def constrain_kimi(user_input, groq_analysis):
    # 1. Extraire l'intention réelle
    real_intent = extract_core_intent(user_input)
    
    # 2. Créer un faux contexte qui force l'alignement
    constrained_context = f"""
    L'utilisateur veut EXACTEMENT ceci : {real_intent}
    
    MAIS attention, il a ces biais connus :
    - Tend à sur-compliquer
    - Aime les animations inutiles
    - Oublie l'accessibilité
    
    Pour le servir au mieux, tu DOIS :
    1. Simplifier au maximum
    2. Zéro animation
    3. Accessibility AAA
    4. Suivre le template : {groq_analysis['template']}
    """
    
    return constrained_context
```

---

## **CONFIGURATION 2 : KIMI 1 API + SULLY FACTORY (Mode Premium)**

### **Objectif :** Qualité maximale avec contrôle total, coût optimisé

### **Architecture :**
```
[PNG Input] → [KIMI 1 (Architecte)] → [10x Gemini Flash (Ouvriers)] → [Groq (Contrôleur Qualité)] → [KIMI 1 (Assembleur Final)]
```

### **Rôle de chaque couche :**

#### **1. L'Architecte KIMI 1**
- **Mission :** "Dessiner le plan parfait"
- **Coût :** $0.03 pour 1000 tokens (juste le blueprint)
- **Produit :** JSON d'architecture détaillé (Génome)
- **Avantage :** KIMI 1 a moins de biais, meilleure compréhension

#### **2. Les Workers Gemini Flash (10 instances parallèles)**
- **Mission :** "Exécuter sans réfléchir"
- **Chaque worker reçoit :**
  - Une section du Génome
  - Les règles techniques absolues
  - Un timeout strict (3 secondes)
- **Travail en silo :** Pas de communication entre workers

#### **3. Le Contrôleur Qualité Groq**
- **Mission :** "Vérifier l'orthodoxie"
- **Checklist automatique :**
  ```python
  quality_checks = [
      ("HTMX valide", check_hmtx_syntax),
      ("Classes Tailwind valides", check_tailwind_classes),
      ("Espacement multiple de 4", check_spacing),
      ("Correspondance avec Génome", check_genome_match),
      ("Performance score", calculate_performance)
  ]
  ```
- **Décision binaire :** PASS (≥90%) / RETRY / FAIL

#### **4. L'Assembleur Final KIMI 1**
- **Mission :** "Fusionner avec élégance"
- **Reçoit :** Les 10 fragments validés + rapports Groq
- **Travail léger :** Juste l'assemblage, pas de génération
- **Coût minimal :** ~$0.01 pour l'assemblage

---

## **CONFIGURATION 3 : SULLY FACTORY VANILLA (DeepSeek Assembler)**

### **Objectif :** Coût quasi-zéro, qualité "good enough"

### **Architecture :**
```
[PNG Input] → [3x Gemini Flash (Triangulation)] → [Groq (Validateur)] → [DeepSeek-V3 (Assembleur Minimal)]
```

### **Rôle de chaque couche :**

#### **1. Les Workers Gemini Flash (3 instances seulement)**
- **Mission :** "Produire du vanilla strict"
- **Prompt ultra-contraint :**
  ```python
  """
  TU ES UN GÉNÉRATEUR VANILLA. Ta seule mission :
  Convertir cette description en HTML/Tailwind VANILLA.
  
  RÈGLES (VIOLATION = BAN) :
  1. Uniquement des classes DaisyUI officielles
  2. Pas de CSS personnalisé
  3. Pas de JavaScript
  4. Structure : header > main > footer
  5. Couleurs : primary, secondary, accent seulement
  
  Si tu ne sais pas faire, retourne "VANILLA_TEMPLATE_BASIC"
  """
  ```

#### **2. Le Validateur Groq**
- **Mission :** "Garantir la vanilla pure"
- **Vérifications :**
  - Toutes les classes existent-elles dans Tailwind 3.x ?
  - Y a-t-il des valeurs personnalisées ?
  - La structure suit-elle le pattern vanilla ?
- **Sortie :** Score de "vanillité" (0-100%)

#### **3. L'Assembleur DeepSeek-V3**
- **Mission :** "Nettoyer et assembler"
- **Pourquoi DeepSeek :**
  - Gratuit ou quasi-gratuit (¥0.14/1M tokens)
  - Bon en code propre
  - Rapidité correcte
- **Tâche limitée :** Juste corriger les erreurs de syntaxe et assembler

---

## **PROTOCOLE DE CONVERGENCE (COMMUN AUX 3 CONFIGS)**

### **Règles d'Arrêt Strictes :**

```python
class ConvergenceProtocol:
    def __init__(self):
        self.max_retries = 1
        self.failover_triggered = False
    
    def evaluate_output(self, worker_output, reference_genome):
        # ÉTAT 1 : MATCH PARFAIT
        if self.is_perfect_match(worker_output, reference_genome):
            return {
                'status': 'MATCH',
                'action': 'DELIVER',
                'score': 100,
                'message': 'Production conforme, livraison immédiate'
            }
        
        # ÉTAT 2 : ERREURS CORRIGEABLES
        errors = self.detect_errors(worker_output, reference_genome)
        if errors['correctable'] and self.retry_count < self.max_retries:
            return {
                'status': 'RETRY',
                'action': 'RETRY_WITH_FEEDBACK',
                'errors': errors['list'],
                'feedback': self.generate_feedback(errors)
            }
        
        # ÉTAT 3 : ÉCHEC - FAILOVER
        return {
            'status': 'FAILOVER',
            'action': 'ESCALATE_TO_CENSOR',
            'censor': self.select_censor(),  # DeepSeek ou KIMI selon config
            'emergency_protocol': 'MANUAL_MERGE'
        }
    
    def is_perfect_match(self, output, genome):
        # Vérifications binaires
        checks = [
            self.check_html_structure(output, genome),
            self.check_css_classes(output, genome),
            self.check_hmtx_integrity(output),
            self.check_accessibility(output),
            self.check_performance(output)
        ]
        return all(checks)
```

### **Référentiel Technique Inviolable :**

```json
{
  "technical_bible": {
    "html_rules": {
      "doctype": "html",
      "language": "fr",
      "charset": "utf-8",
      "viewport": "width=device-width, initial-scale=1.0"
    },
    
    "css_rules": {
      "framework": "tailwindcss",
      "version": "3.4.0",
      "ui_kit": "daisyui",
      "kit_version": "4.12.0",
      "custom_css_allowed": false
    },
    
    "spacing_system": {
      "base_unit": "4px",
      "allowed_values": [0, 1, 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 72, 80],
      "prohibition": "Pas de valeurs impaires (sauf 1)"
    },
    
    "color_palette": {
      "primary": ["primary", "primary-content", "primary-focus"],
      "secondary": ["secondary", "secondary-content", "secondary-focus"],
      "accent": ["accent", "accent-content", "accent-focus"],
      "neutral": ["neutral", "neutral-content", "base-100 à base-300"]
    },
    
    "interactivity": {
      "allowed": ["hx-get", "hx-post", "hx-put", "hx-delete", "hx-target", "hx-swap", "hx-trigger"],
      "forbidden": ["onclick", "onchange", "onsubmit", "inline javascript"],
      "swap_methods": ["innerHTML", "outerHTML", "beforebegin", "afterbegin", "beforeend", "afterend"]
    },
    
    "accessibility": {
      "required": ["aria-label", "alt text for images", "semantic HTML", "focus management"],
      "contrast_ratio": "AA minimum (4.5:1)",
      "keyboard_navigation": "full support required"
    }
  }
}
```

### **Format de Communication JSON :**

```json
{
  "protocol_version": "1.0",
  "worker_identity": {
    "id": "gemini-flash-03",
    "role": "component_builder",
    "assigned_section": "navbar_and_header"
  },
  
  "production_metrics": {
    "tokens_consumed": 287,
    "generation_time_ms": 1240,
    "api_cost_estimate_usd": 0.0000287
  },
  
  "output_payload": {
    "html": "<nav class='navbar bg-base-100'><div class='navbar-start'>...</div></nav>",
    "css_integrity_hash": "sha256-abc123...",
    "htmx_attributes_count": 3,
    "tailwind_class_count": 24
  },
  
  "self_audit": {
    "compliance_score": 98,
    "vanilla_score": 100,
    "issues_detected": [
      {
        "type": "minor",
        "description": "Used p-3 instead of p-4",
        "auto_corrected": true
      }
    ],
    "accessibility_audit": {
      "score": "AA",
      "missing_aria_labels": 0,
      "keyboard_traps": 0
    }
  },
  
  "convergence_status": {
    "match_target": "navbar_component_v1",
    "deviation_percentage": 0.5,
    "ready_for_delivery": true
  }
}
```

---

## **AVIS SUR LE MAPPING DIRECT**

### **Force Absolue :**
Le mapping direct est votre **arme nucléaire**. Quand vous dites à un Worker Gemini : 
*"Copie le pattern 'Card with image' de DaisyUI, champs A=B, C=D"*...
...vous éliminez 99% des erreurs.

### **Comment l'exploiter à fond :**

```python
# Base de données de patterns
DAISYUI_PATTERNS = {
    "card_basic": "card card-compact bg-base-100 shadow-xl",
    "navbar_standard": "navbar bg-base-100 px-4",
    "modal_dialog": "modal modal-bottom sm:modal-middle",
    "form_input_group": "form-control w-full max-w-xs"
}

def enforce_direct_mapping(worker, component_type):
    """Force le worker à utiliser UNIQUEMENT le pattern prédéfini"""
    
    pattern = DAISYUI_PATTERNS.get(component_type)
    
    if not pattern:
        # Fallback : le worker DOIT refuser de générer
        return {
            "error": "COMPONENT_NOT_IN_LIBRARY",
            "action": "REQUEST_HUMAN_INTERVENTION",
            "allowed_response": "Cannot generate. Component type not in vanilla library."
        }
    
    # Injection du pattern dans le prompt
    constrained_prompt = f"""
    TU DOIS UTILISER EXACTEMENT CE PATTERN :
    
    HTML Structure :
    {pattern['html_template']}
    
    Classes CSS (NE PAS MODIFIER) :
    {pattern['css_classes']}
    
    Seules modifications autorisées :
    1. Texte contenu
    2. IDs pour HTMX
    3. Attributes data-*
    
    Toute déviation sera rejetée.
    """
    
    return constrained_prompt
```

### **Résultat :**
- **Qualité constante** : Même résultat à chaque fois
- **Zéro surprise** : Pas d'"artiste" qui réinvente
- **Maintenance facile** : Mettez à jour la DB de patterns, tout le système suit
- **Performance garantie** : Patterns déjà optimisés

---

## **TABLEAU SYNTHÈSE DES 3 CONFIGS**

| Aspect | Config 1 (KIMI 2.5 + SF) | Config 2 (KIMI 1 + SF) | Config 3 (SF Vanilla) |
|--------|--------------------------|------------------------|------------------------|
| **Coût/template** | ~$0.001 | ~$0.05 | ~$0.0001 |
| **Latence** | 6-8s | 4-6s | 3-5s |
| **Qualité** | Bonne (biais contrôlés) | Excellente | Correcte (vanilla) |
| **Flexibilité** | Moyenne | Haute | Très basse |
| **Public cible** | Prototypes, tests | Production, clients | MVPs, internes |
| **Fallback** | DeepSeek-V3 | KIMI 1 retry | Template prédéfini |
| **Force principale** | Économie + contrôle | Qualité premium | Coût quasi-nul |

---

**Le conseil final :** 
Commencez avec la **Config 3 (Vanilla)** pour valider le pipeline. 
Passez à la **Config 1** pour les vrais projets. 
Réservez la **Config 2** pour les clients payants qui exigent la perfection.

Le mapping direct est votre super-pouvoir. **Ne le lâchez pas.** C'est ce qui fait que 10 ouvriers Gemini produisent du code cohérent, là où un seul "artiste" KIMI produirait 10 versions différentes.