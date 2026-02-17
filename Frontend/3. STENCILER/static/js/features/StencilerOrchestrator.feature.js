import StencilerFeature from './base.feature.js';

// StencilerOrchestrator.feature.js
class StencilerOrchestratorFeature extends StencilerFeature {
    constructor() {
        super('stenciler-orchestrator');
        this.features = [];
    }

    init() {
        console.log('StencilerOrchestrator initialisé');
        this.setupEventBus();
    }

    setupEventBus() {
        // Event bus pour la communication entre features
        window.stencilerEvents = {
            listeners: {},
            on(event, callback) {
                if (!this.listeners[event]) this.listeners[event] = [];
                this.listeners[event].push(callback);
            },
            emit(event, data) {
                if (this.listeners[event]) {
                    this.listeners[event].forEach(cb => cb(data));
                }
            }
        };
    }

    registerFeature(feature) {
        this.features.push(feature);
    }
}

export default StencilerOrchestratorFeature;
