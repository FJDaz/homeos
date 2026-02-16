// static/js/semantic_bridge.js
// CONSTITUTION AETHERFLOW - Frontière Hermétique Enforcement
// Intercepteur Fetch et validateurs constitutionnels pour prévenir les fuites CSS vers le backend

/**
 * CONSTITUTION AETHERFLOW - Article 3
 * Le Système Cognitif ne produit JAMAIS :
 * - Classes CSS (flex, justify-between, gap-4)
 * - Propriétés CSS (padding: 16px, display: flex)
 * - HTML (<div>, <button>)
 * - Tailwind (bg-blue-500, text-lg)
 */

class ConstitutionalViolationError extends Error {
    constructor(message, violationType, payload) {
        super(message);
        this.name = 'ConstitutionalViolationError';
        this.violationType = violationType;
        this.payload = payload;
        this.timestamp = new Date().toISOString();
    }
}

class SemanticBridge {
    constructor() {
        this.violationLog = [];
        this.isActive = true;
        this.originalFetch = window.fetch.bind(window);
        this.setupInterceptors();
        this.setupGlobalHandlers();

        console.log('🔒 Semantic Bridge activé - Frontière Hermétique en vigueur');
        console.log('📜 Constitution AETHERFLOW v1.0.0 - Article 3 en application');
    }

    // ==================== VALIDATEURS CONSTITUTIONNELS ====================

    /**
     * Validateur CSS - Article 3.2
     * Détecte les classes CSS/Tailwind dans les payloads
     */
    validateNoCSS(content) {
        const cssPatterns = [
            // Classes Tailwind
            /\b(bg|text|border|rounded|p|m|w|h|flex|grid|gap|justify|items|self|place)-[a-zA-Z0-9-]+\b/g,
            // Propriétés CSS
            /\b(padding|margin|width|height|display|position|top|left|right|bottom):\s*[^;]+;/g,
            // Classes CSS génériques
            /\b(container|row|col|btn|card|modal|navbar|sidebar|header|footer)\b/g,
            // Unités CSS
            /\b(\d+(?:\.\d+)?)(px|rem|em|vh|vw|%)\b/g
        ];

        const violations = [];

        cssPatterns.forEach((pattern, index) => {
            const matches = content.match(pattern);
            if (matches) {
                matches.forEach(match => {
                    violations.push({
                        type: 'CSS_VIOLATION',
                        pattern: pattern.toString(),
                        match: match,
                        severity: index === 0 ? 'CRITICAL' : 'MAJOR'
                    });
                });
            }
        });

        return violations;
    }

    /**
     * Validateur HTML - Article 3.2
     * Détecte les balises HTML dans les payloads
     */
    validateNoHTML(content) {
        const htmlPatterns = [
            /<[a-z][\s\S]*?>/gi, // Balises HTML
            /&[a-z]+;/gi, // Entités HTML
            /\b(class|id|style|href|src)=["'][^"']*["']/gi // Attributs HTML
        ];

        const violations = [];

        htmlPatterns.forEach(pattern => {
            const matches = content.match(pattern);
            if (matches) {
                matches.forEach(match => {
                    violations.push({
                        type: 'HTML_VIOLATION',
                        pattern: pattern.toString(),
                        match: match,
                        severity: 'CRITICAL'
                    });
                });
            }
        });

        return violations;
    }

    /**
     * Validateur d'attributs sémantiques - Article 3.1
     * Vérifie que seuls les attributs sémantiques autorisés sont utilisés
     */
    validateSemanticAttributes(payload) {
        const allowedAttributes = {
            layout_type: ['grid', 'flex', 'stack', 'absolute'],
            density: ['compact', 'normal', 'airy'],
            importance: ['primary', 'secondary', 'tertiary'],
            semantic_role: ['navigation', 'content', 'action', 'feedback', 'header', 'footer'],
            accent_color: 'string', // Hex color
            border_weight: 'number', // 0-10
            visibility: ['visible', 'hidden', 'collapsed']
        };

        const violations = [];

        // Fonction récursive pour parcourir l'objet
        const checkObject = (obj, path = '') => {
            for (const [key, value] of Object.entries(obj)) {
                const currentPath = path ? `${path}.${key}` : key;

                // Si c'est un attribut sémantique connu
                if (key in allowedAttributes) {
                    const allowed = allowedAttributes[key];

                    if (Array.isArray(allowed)) {
                        // Enumération
                        if (!allowed.includes(value)) {
                            violations.push({
                                type: 'SEMANTIC_VALUE_VIOLATION',
                                attribute: key,
                                value: value,
                                allowed: allowed,
                                path: currentPath,
                                severity: 'MINOR'
                            });
                        }
                    } else if (allowed === 'string') {
                        // Validation hex color pour accent_color
                        if (key === 'accent_color' && !/^#[0-9A-F]{6}$/i.test(value)) {
                            violations.push({
                                type: 'COLOR_FORMAT_VIOLATION',
                                attribute: key,
                                value: value,
                                expected: 'hex color (#RRGGBB)',
                                path: currentPath,
                                severity: 'MINOR'
                            });
                        }
                    } else if (allowed === 'number') {
                        // Validation range pour border_weight
                        if (key === 'border_weight' && (value < 0 || value > 10)) {
                            violations.push({
                                type: 'RANGE_VIOLATION',
                                attribute: key,
                                value: value,
                                min: 0,
                                max: 10,
                                path: currentPath,
                                severity: 'MINOR'
                            });
                        }
                    }
                } else if (typeof value === 'object' && value !== null) {
                    // Parcours récursif
                    checkObject(value, currentPath);
                }
            }
        };

        if (payload && typeof payload === 'object') {
            checkObject(payload);
        }

        return violations;
    }

    /**
     * Validateur de path - Annexe A
     * Vérifie le format standardisé n0[i].n1[j].n2[k].n3[l]
     */
    validatePathFormat(path) {
        if (!path) return [];

        const violations = [];
        const pathPattern = /^n\d+\[\d+\](?:\.n\d+\[\d+\])*$/;

        if (!pathPattern.test(path)) {
            violations.push({
                type: 'PATH_FORMAT_VIOLATION',
                path: path,
                expected: 'n0[i].n1[j].n2[k].n3[l]',
                severity: 'MAJOR'
            });
        }

        return violations;
    }

    // ==================== INTERCEPTEUR FETCH ====================

    setupInterceptors() {
        const self = this;

        window.fetch = async function (input, init = {}) {
            // Cloner la requête pour inspection
            const request = new Request(input, init);
            const url = request.url;

            // Vérifier si c'est une requête vers l'API backend
            if (self.isBackendAPI(url) && self.isActive) {
                try {
                    // Intercepter le body pour validation
                    if (init.body) {
                        let bodyContent = init.body;

                        // Si c'est un FormData, on ne peut pas l'intercepter facilement
                        // Dans ce cas, on log un warning
                        if (bodyContent instanceof FormData) {
                            console.warn('⚠️  FormData détecté - validation limitée');
                            return self.originalFetch(input, init);
                        }

                        // Si c'est une string, on parse
                        if (typeof bodyContent === 'string') {
                            try {
                                const parsed = JSON.parse(bodyContent);
                                self.validatePayload(parsed, url);
                            } catch (e) {
                                // Si ce n'est pas du JSON, on valide comme texte brut
                                self.validateTextContent(bodyContent, url);
                            }
                        }
                        // Si c'est un objet, on le valide
                        else if (typeof bodyContent === 'object') {
                            self.validatePayload(bodyContent, url);
                        }
                    }

                    // Exécuter la requête originale
                    const response = await self.originalFetch(input, init);

                    // Intercepter la réponse pour validation
                    const clonedResponse = response.clone();
                    const responseText = await clonedResponse.text();

                    try {
                        const responseJson = JSON.parse(responseText);
                        self.validateResponse(responseJson, url);
                    } catch (e) {
                        // Réponse non-JSON, validation limitée
                    }

                    return response;

                } catch (error) {
                    if (error instanceof ConstitutionalViolationError) {
                        self.handleViolation(error);
                        throw error;
                    }
                    throw error;
                }
            }

            // Pour les autres requêtes, passer directement
            return self.originalFetch(input, init);
        };
    }

    isBackendAPI(url) {
        const backendPatterns = [
            /\/api\//,
            /\/modifications/,
            /\/genome/,
            /\/snapshot/,
            /\/drilldown/,
            /\/components/,
            /\/breadcrumb/
        ];

        return backendPatterns.some(pattern => pattern.test(url));
    }

    /**
     * API Contextualisation - Phase 3
     * Récupère un fragment précis du génome pour limiter la charge cognitive
     */
    async getPrunedContext(targetId) {
        try {
            const response = await this.originalFetch(`/api/genome/pruned/${targetId}`);
            if (!response.ok) throw new Error(`Pruning error: ${response.statusText}`);
            return await response.json();
        } catch (error) {
            console.error(`❌ Semantic Bridge - Erreur de contextualisation pour ${targetId}:`, error);
            return null;
        }
    }

    validatePayload(payload, url) {
        const violations = [];

        // Convertir en string pour validation CSS/HTML
        const payloadString = JSON.stringify(payload);

        // Exécuter tous les validateurs
        violations.push(...this.validateNoCSS(payloadString));
        violations.push(...this.validateNoHTML(payloadString));
        violations.push(...this.validateSemanticAttributes(payload));

        // Valider le path si présent
        if (payload.path) {
            violations.push(...this.validatePathFormat(payload.path));
        }

        // Si violations, throw error
        if (violations.length > 0) {
            const error = new ConstitutionalViolationError(
                'Violation constitutionnelle détectée dans le payload',
                'PAYLOAD_VIOLATION',
                {
                    url,
                    payload,
                    violations,
                    timestamp: new Date().toISOString()
                }
            );
            throw error;
        }
    }

    validateTextContent(text, url) {
        const violations = [];

        violations.push(...this.validateNoCSS(text));
        violations.push(...this.validateNoHTML(text));

        if (violations.length > 0) {
            const error = new ConstitutionalViolationError(
                'Violation constitutionnelle détectée dans le contenu texte',
                'TEXT_CONTENT_VIOLATION',
                {
                    url,
                    textSample: text.substring(0, 200),
                    violations,
                    timestamp: new Date().toISOString()
                }
            );
            throw error;
        }
    }

    validateResponse(response, url) {
        // Valider que la réponse du backend ne contient pas de CSS/HTML
        const responseString = JSON.stringify(response);
        const violations = [];

        violations.push(...this.validateNoCSS(responseString));
        violations.push(...this.validateNoHTML(responseString));

        if (violations.length > 0) {
            console.error('⚠️  Backend a retourné du CSS/HTML - Violation constitutionnelle!', {
                url,
                violations,
                responseSample: responseString.substring(0, 500)
            });

            // Log mais ne pas throw (c'est une violation backend)
            this.logViolation({
                type: 'BACKEND_RESPONSE_VIOLATION',
                url,
                violations,
                severity: 'CRITICAL'
            });
        }
    }

    // ==================== GESTION DES VIOLATIONS ====================

    handleViolation(error) {
        console.error('🚨 VIOLATION CONSTITUTIONNELLE DÉTECTÉE!', error);

        // Log la violation
        this.logViolation({
            type: error.violationType,
            message: error.message,
            payload: error.payload,
            timestamp: error.timestamp,
            stack: error.stack
        });

        // Afficher une alerte à l'utilisateur
        this.showViolationAlert(error);

        // Optionnel: envoyer à un service de monitoring
        this.reportToMonitoring(error);
    }

    logViolation(violation) {
        this.violationLog.push(violation);

        // Sauvegarder dans localStorage pour persistance
        try {
            const stored = JSON.parse(localStorage.getItem('aetherflow_violations') || '[]');
            stored.push(violation);
            localStorage.setItem('aetherflow_violations', JSON.stringify(stored.slice(-100))); // Garder les 100 dernières
        } catch (e) {
            console.error('Erreur lors du stockage de la violation:', e);
        }

        // Émettre un événement personnalisé
        const event = new CustomEvent('constitutional-violation', {
            detail: violation
        });
        window.dispatchEvent(event);
    }

    showViolationAlert(error) {
        // Créer une overlay d'alerte
        const alert = document.createElement('div');
        alert.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dc2626;
            color: white;
            padding: 16px;
            border-radius: 8px;
            z-index: 99999;
            max-width: 400px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            font-family: system-ui, -apple-system, sans-serif;
        `;

        alert.innerHTML = `
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 20px; margin-right: 8px;">🚨</span>
                <strong>Violation Constitutionnelle</strong>
            </div>
            <div style="font-size: 14px; margin-bottom: 12px;">
                ${error.message}
            </div>
            <div style="font-size: 12px; opacity: 0.9; margin-bottom: 12px;">
                Type: ${error.violationType}
            </div>
            <button onclick="this.parentElement.remove()" 
                    style="background: rgba(255,255,255,0.2); 
                           border: none; 
                           color: white; 
                           padding: 6px 12px; 
                           border-radius: 4px; 
                           cursor: pointer; 
                           font-size: 12px;">
                Compris
            </button>
        `;

        document.body.appendChild(alert);

        // Auto-remove après 10 secondes
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 10000);
    }

    reportToMonitoring(error) {
        // Envoyer à un service de monitoring (à implémenter)
        // fetch('/api/monitoring/violations', {...})
    }

    // ==================== UTILITAIRES ====================

    setupGlobalHandlers() {
        // Intercepter les erreurs non attrapées
        window.addEventListener('error', (event) => {
            if (event.error instanceof ConstitutionalViolationError) {
                event.preventDefault();
                this.handleViolation(event.error);
            }
        });

        // Intercepter les promesses rejetées
        window.addEventListener('unhandledrejection', (event) => {
            if (event.reason instanceof ConstitutionalViolationError) {
                event.preventDefault();
                this.handleViolation(event.reason);
            }
        });
    }

    // ==================== API PUBLIQUE ====================

    /**
     * Valider manuellement un payload
     */
    validate(payload) {
        const violations = [];
        const payloadString = JSON.stringify(payload);

        violations.push(...this.validateNoCSS(payloadString));
        violations.push(...this.validateNoHTML(payloadString));
        violations.push(...this.validateSemanticAttributes(payload));

        return {
            isValid: violations.length === 0,
            violations,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Obtenir l'historique des violations
     */
    getViolationHistory() {
        return [...this.violationLog];
    }

    /**
     * Activer/désactiver le bridge
     */
    setActive(active) {
        this.isActive = active;
        console.log(`🔒 Semantic Bridge ${active ? 'activé' : 'désactivé'}`);
    }

    /**
     * Vérifier la conformité d'un snippet de code
     */
    checkCodeCompliance(code, role = 'backend') {
        const checks = {
            backend: {
                hasCSS: this.validateNoCSS(code).length > 0,
                hasHTML: this.validateNoHTML(code).length > 0,
                hasTailwind: /bg-|text-|border-|rounded-|p-|m-|w-|h-|flex-|grid-|gap-|justify-|items-/.test(code),
                usesSemanticAttributes: /layout_type|density|importance|semantic_role|accent_color|border_weight|visibility/.test(code)
            },
            frontend: {
                accessesGenomeState: /GenomeStateManager|ModificationLog|CorpsEntity/.test(code),
                implementsBusinessLogic: /max.*items|if.*navigation|business.*rule/.test(code),
                persistsState: /localStorage.*genome|sessionStorage.*state/.test(code),
                usesAPI: /fetch.*\/api|axios.*\/api/.test(code)
            }
        };

        return {
            role,
            checks: checks[role] || {},
            isCompliant: role === 'backend'
                ? !checks.backend.hasCSS && !checks.backend.hasHTML && !checks.backend.hasTailwind
                : !checks.frontend.implementsBusinessLogic && !checks.frontend.persistsState
        };
    }
}

window.semanticBridge = new SemanticBridge();