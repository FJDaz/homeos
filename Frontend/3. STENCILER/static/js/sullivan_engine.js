// static/js/sullivan_engine.js
// Sullivan Engine - Modular Component System with Hooks
// Version 1.0.0 - AETHERFLOW Architecture

/**
 * CONSTITUTION AETHERFLOW - Article 7: Système Sullivan
 * Le Système Sullivan fournit :
 * - Un système de hooks (add_filter/do_action) pour l'extensibilité
 * - Une classe de base Component pour la modularité
 * - Un système d'événements découplé
 * - Une architecture plugin-friendly
 */

// ==================== CORE TYPES AND INTERFACES ====================

/**
 * @typedef {Object} HookCallback
 * @property {Function} callback - The callback function
 * @property {number} priority - Execution priority (lower = earlier)
 * @property {string} namespace - Optional namespace for grouping
 */

/**
 * @typedef {Object} ComponentConfig
 * @property {Function} init - Initialization function
 * @property {Object} [methods] - Component methods
 * @property {Object} [hooks] - Hook registrations
 * @property {Object} [events] - Event handlers
 */

/**
 * @typedef {Object} EventData
 * @property {string} type - Event type
 * @property {*} data - Event payload
 * @property {string} source - Event source component
 * @property {number} timestamp - Event timestamp
 */

// ==================== ERROR CLASSES ====================

class SullivanError extends Error {
    /**
     * Base error class for Sullivan Engine
     * @param {string} message - Error message
     * @param {string} code - Error code
     */
    constructor(message, code = 'SULLIVAN_ERROR') {
        super(message);
        this.name = 'SullivanError';
        this.code = code;
        this.timestamp = new Date().toISOString();
    }
}

class HookError extends SullivanError {
    /**
     * Error for hook-related issues
     * @param {string} message - Error message
     * @param {string} hookName - Hook name
     */
    constructor(message, hookName) {
        super(message, 'HOOK_ERROR');
        this.hookName = hookName;
    }
}

class ComponentError extends SullivanError {
    /**
     * Error for component-related issues
     * @param {string} message - Error message
     * @param {string} componentName - Component name
     */
    constructor(message, componentName) {
        super(message, 'COMPONENT_ERROR');
        this.componentName = componentName;
    }
}

// ==================== HOOK MANAGER ====================

class HookManager {
    /**
     * Manages hooks (filters and actions) with priority system
     */
    constructor() {
        /** @type {Object.<string, HookCallback[]>} */
        this.filters = {};
        /** @type {Object.<string, HookCallback[]>} */
        this.actions = {};
        /** @type {Object.<string, any>} */
        this.hookCache = {};
        this.cacheEnabled = true;
        this.debug = false;
    }

    /**
     * Add a filter callback
     * @param {string} hookName - Filter name
     * @param {Function} callback - Callback function
     * @param {number} [priority=10] - Execution priority
     * @param {string} [namespace='default'] - Namespace for grouping
     * @returns {HookManager} - Chainable
     */
    addFilter(hookName, callback, priority = 10, namespace = 'default') {
        this._validateHookParams(hookName, callback, priority, namespace);
        
        if (!this.filters[hookName]) {
            this.filters[hookName] = [];
        }
        
        this.filters[hookName].push({
            callback,
            priority,
            namespace
        });
        
        // Sort by priority (ascending)
        this.filters[hookName].sort((a, b) => a.priority - b.priority);
        
        // Clear cache for this hook
        delete this.hookCache[hookName];
        
        if (this.debug) {
            console.log(`🔧 Filter added: ${hookName} (priority: ${priority}, namespace: ${namespace})`);
        }
        
        return this;
    }

    /**
     * Apply filters to a value
     * @param {string} hookName - Filter name
     * @param {*} value - Initial value
     * @param {...*} args - Additional arguments for callbacks
     * @returns {*} - Filtered value
     */
    applyFilters(hookName, value, ...args) {
        // Check cache first
        const cacheKey = this._getCacheKey(hookName, value, args);
        if (this.cacheEnabled && this.hookCache[cacheKey] !== undefined) {
            return this.hookCache[cacheKey];
        }
        
        let filteredValue = value;
        
        if (this.filters[hookName]) {
            for (const hook of this.filters[hookName]) {
                try {
                    const newValue = hook.callback(filteredValue, ...args);
                    if (newValue !== undefined) {
                        filteredValue = newValue;
                    }
                } catch (error) {
                    console.error(`❌ Filter error in ${hookName}:`, error);
                    throw new HookError(`Filter execution failed: ${error.message}`, hookName);
                }
            }
        }
        
        // Cache the result
        if (this.cacheEnabled) {
            this.hookCache[cacheKey] = filteredValue;
        }
        
        return filteredValue;
    }

    /**
     * Add an action callback
     * @param {string} hookName - Action name
     * @param {Function} callback - Callback function
     * @param {number} [priority=10] - Execution priority
     * @param {string} [namespace='default'] - Namespace for grouping
     * @returns {HookManager} - Chainable
     */
    addAction(hookName, callback, priority = 10, namespace = 'default') {
        this._validateHookParams(hookName, callback, priority, namespace);
        
        if (!this.actions[hookName]) {
            this.actions[hookName] = [];
        }
        
        this.actions[hookName].push({
            callback,
            priority,
            namespace
        });
        
        // Sort by priority (ascending)
        this.actions[hookName].sort((a, b) => a.priority - b.priority);
        
        if (this.debug) {
            console.log(`🔧 Action added: ${hookName} (priority: ${priority}, namespace: ${namespace})`);
        }
        
        return this;
    }

    /**
     * Execute action callbacks
     * @param {string} hookName - Action name
     * @param {...*} args - Arguments for callbacks
     */
    doAction(hookName, ...args) {
        if (this.actions[hookName]) {
            for (const hook of this.actions[hookName]) {
                try {
                    hook.callback(...args);
                } catch (error) {
                    console.error(`❌ Action error in ${hookName}:`, error);
                    throw new HookError(`Action execution failed: ${error.message}`, hookName);
                }
            }
        }
        
        if (this.debug) {
            console.log(`🔧 Action executed: ${hookName}`);
        }
    }

    /**
     * Remove a hook callback
     * @param {string} hookName - Hook name
     * @param {Function} [callback] - Specific callback to remove (optional)
     * @param {string} [namespace] - Specific namespace to remove (optional)
     * @returns {boolean} - True if removed, false otherwise
     */
    removeHook(hookName, callback = null, namespace = null) {
        let removed = false;
        
        // Remove from filters
        if (this.filters[hookName]) {
            this.filters[hookName] = this.filters[hookName].filter(hook => {
                const shouldRemove = (!callback || hook.callback === callback) &&
                                   (!namespace || hook.namespace === namespace);
                if (shouldRemove) {
                    removed = true;
                    if (this.debug) {
                        console.log(`🔧 Filter removed: ${hookName}`);
                    }
                }
                return !shouldRemove;
            });
            
            if (this.filters[hookName].length === 0) {
                delete this.filters[hookName];
            }
        }
        
        // Remove from actions
        if (this.actions[hookName]) {
            this.actions[hookName] = this.actions[hookName].filter(hook => {
                const shouldRemove = (!callback || hook.callback === callback) &&
                                   (!namespace || hook.namespace === namespace);
                if (shouldRemove) {
                    removed = true;
                    if (this.debug) {
                        console.log(`🔧 Action removed: ${hookName}`);
                    }
                }
                return !shouldRemove;
            });
            
            if (this.actions[hookName].length === 0) {
                delete this.actions[hookName];
            }
        }
        
        // Clear cache
        delete this.hookCache[hookName];
        
        return removed;
    }

    /**
     * Check if a hook has callbacks
     * @param {string} hookName - Hook name
     * @returns {boolean} - True if hook exists
     */
    hasHook(hookName) {
        return !!(this.filters[hookName] || this.actions[hookName]);
    }

    /**
     * Get hook callbacks
     * @param {string} hookName - Hook name
     * @returns {Object} - Object with filters and actions arrays
     */
    getHook(hookName) {
        return {
            filters: this.filters[hookName] || [],
            actions: this.actions[hookName] || []
        };
    }

    /**
     * Clear all hooks
     * @param {string} [namespace] - Optional namespace to clear
     */
    clearHooks(namespace = null) {
        const clearArray = (arr) => {
            if (!namespace) return [];
            return arr.filter(hook => hook.namespace !== namespace);
        };
        
        for (const hookName in this.filters) {
            this.filters[hookName] = clearArray(this.filters[hookName]);
            if (this.filters[hookName].length === 0) {
                delete this.filters[hookName];
            }
        }
        
        for (const hookName in this.actions) {
            this.actions[hookName] = clearArray(this.actions[hookName]);
            if (this.actions[hookName].length === 0) {
                delete this.actions[hookName];
            }
        }
        
        this.hookCache = {};
        
        if (this.debug) {
            console.log(`🔧 Hooks cleared${namespace ? ` for namespace: ${namespace}` : ''}`);
        }
    }

    /**
     * Enable/disable debug mode
     * @param {boolean} enabled - Debug mode state
     */
    setDebug(enabled) {
        this.debug = enabled;
    }

    /**
     * Enable/disable hook caching
     * @param {boolean} enabled - Cache state
     */
    setCache(enabled) {
        this.cacheEnabled = enabled;
        if (!enabled) {
            this.hookCache = {};
        }
    }

    // ==================== PRIVATE METHODS ====================

    /**
     * Validate hook parameters
     * @private
     */
    _validateHookParams(hookName, callback, priority, namespace) {
        if (typeof hookName !== 'string' || !hookName.trim()) {
            throw new HookError('Hook name must be a non-empty string', hookName);
        }
        
        if (typeof callback !== 'function') {
            throw new HookError('Callback must be a function', hookName);
        }
        
        if (typeof priority !== 'number' || priority < 0) {
            throw new HookError('Priority must be a non-negative number', hookName);
        }
        
        if (typeof namespace !== 'string') {
            throw new HookError('Namespace must be a string', hookName);
        }
    }

    /**
     * Generate cache key for hook results
     * @private
     */
    _getCacheKey(hookName, value, args) {
        try {
            return `${hookName}_${JSON.stringify(value)}_${JSON.stringify(args)}`;
        } catch (e) {
            // Fallback for non-serializable values
            return `${hookName}_${typeof value}_${args.length}`;
        }
    }
}

// ==================== EVENT MANAGER ====================

class EventManager {
    /**
     * Manages component events with pub/sub pattern
     */
    constructor() {
        /** @type {Object.<string, Function[]>} */
        this.listeners = {};
        /** @type {EventData[]} */
        this.eventHistory = [];
        this.maxHistory = 100;
        this.debug = false;
    }

    /**
     * Subscribe to an event
     * @param {string} eventType - Event type
     * @param {Function} callback - Event handler
     * @param {string} [componentName] - Optional component name for debugging
     * @returns {Function} - Unsubscribe function
     */
    on(eventType, callback, componentName = null) {
        if (typeof eventType !== 'string' || !eventType.trim()) {
            throw new SullivanError('Event type must be a non-empty string', 'EVENT_ERROR');
        }
        
        if (typeof callback !== 'function') {
            throw new SullivanError('Callback must be a function', 'EVENT_ERROR');
        }
        
        if (!this.listeners[eventType]) {
            this.listeners[eventType] = [];
        }
        
        const listener = { callback, componentName };
        this.listeners[eventType].push(listener);
        
        if (this.debug) {
            console.log(`🎯 Event listener added: ${eventType}${componentName ? ` (${componentName})` : ''}`);
        }
        
        // Return unsubscribe function
        return () => this.off(eventType, callback);
    }

    /**
     * Unsubscribe from an event
     * @param {string} eventType - Event type
     * @param {Function} [callback] - Specific callback to remove (optional)
     * @returns {boolean} - True if removed, false otherwise
     */
    off(eventType, callback = null) {
        if (!this.listeners[eventType]) {
            return false;
        }
        
        if (!callback) {
            // Remove all listeners for this event
            const count = this.listeners[eventType].length;
            delete this.listeners[eventType];
            
            if (this.debug) {
                console.log(`🎯 All listeners removed for event: ${eventType} (${count} listeners)`);
            }
            
            return count > 0;
        }
        
        // Remove specific callback
        const initialLength = this.listeners[eventType].length;
        this.listeners[eventType] = this.listeners[eventType].filter(
            listener => listener.callback !== callback
        );
        
        const removed = initialLength !== this.listeners[eventType].length;
        
        if (removed && this.debug) {
            console.log(`🎯 Listener removed for event: ${eventType}`);
        }
        
        if (this.listeners[eventType].length === 0) {
            delete this.listeners[eventType];
        }
        
        return removed;
    }

    /**
     * Emit an event
     * @param {string} eventType - Event type
     * @param {*} data - Event data
     * @param {string} [source] - Event source component
     * @returns {EventData} - The emitted event
     */
    emit(eventType, data = null, source = null) {
        const event = {
            type: eventType,
            data,
            source,
            timestamp: Date.now()
        };
        
        // Add to history
        this.eventHistory.push(event);
        if (this.eventHistory.length > this.maxHistory) {
            this.eventHistory.shift();
        }
        
        // Notify listeners
        if (this.listeners[eventType]) {
            // Clone array to avoid modification during iteration
            const listeners = [...this.listeners[eventType]];
            
            for (const listener of listeners) {
                try {
                    listener.callback(event);
                } catch (error) {
                    console.error(`❌ Event handler error for ${eventType}:`, error);
                    // Don't throw, continue with other listeners
                }
            }
        }
        
        if (this.debug) {
            console.log(`🎯 Event emitted: ${eventType}`, {
                source,
                data: typeof data === 'object' ? JSON.stringify(data).substring(0, 100) : data
            });
        }
        
        return event;
    }

    /**
     * Get event history
     * @param {string} [eventType] - Optional filter by event type
     * @param {number} [limit] - Optional limit results
     * @returns {EventData[]} - Event history
     */
    getHistory(eventType = null, limit = null) {
        let history = this.eventHistory;
        
        if (eventType) {
            history = history.filter(event => event.type === eventType);
        }
        
        if (limit && limit > 0) {
            history = history.slice(-limit);
        }
        
        return history;
    }

    /**
     * Clear event history
     */
    clearHistory() {
        this.eventHistory = [];
    }

    /**
     * Enable/disable debug mode
     * @param {boolean} enabled - Debug mode state
     */
    setDebug(enabled) {
        this.debug = enabled;
    }
}

// ==================== COMPONENT BASE CLASS ====================

class Component {
    /**
     * Base class for Sullivan components
     * @param {string} name - Component name
     * @param {ComponentConfig} config - Component configuration
     */
    constructor(name, config = {}) {
        if (!name || typeof name !== 'string') {
            throw new ComponentError('Component name must be a non-empty string', name);
        }
        
        this.name = name;
        this.config = config;
        this.initialized = false;
        this.hooks = new HookManager();
        this.events = new EventManager();
        
        // Auto-register hooks from config
        if (config.hooks) {
            this._registerConfigHooks();
        }
        
        // Auto-register events from config
        if (config.events) {
            this._registerConfigEvents();
        }
        
        if (Sullivan.debug) {
            console