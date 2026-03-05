import StencilerFeature from './base.feature.js';

/**
 * PersistenceFeature
 * Gère la sauvegarde locale du Genome et le versioning.
 * Écoute l'événement 'genome:updated' pour déclencher l'auto-save.
 */
class PersistenceFeature extends StencilerFeature {
    constructor(id = 'persistence-manager', options = {}) {
        super(id, options);
        this.storageKey = 'stenciler_genome_v3';
        this.saveInterval = 2000; // ms
        this.saveTimer = null;
        this.genome = null;
    }

    init(genome) {
        this.genome = genome;
        this._loadFromLocal();
        this._setupListeners();
        console.log('💾 Persistence Manager Initialized');
    }

    render() {
        // Feature silencieuse, pas d'UI à rendre
        return '';
    }

    /**
     * Tente de charger une version locale si elle existe et est plus récente.
     */
    _loadFromLocal() {
        const saved = localStorage.getItem(this.storageKey);
        if (saved) {
            try {
                const localGenome = JSON.parse(saved);
                // Simple version check: if local has more metadata or specific marker, use it
                // For now, we favor local if it exists (Authoring mode)
                console.log('💾 Local Genome found, merging changes...');
                Object.assign(this.genome, localGenome);
            } catch (e) {
                console.error('💾 Error loading local genome', e);
            }
        }
    }

    _setupListeners() {
        document.addEventListener('genome:updated', (e) => {
            console.log('💾 Genome update detected, scheduling save...');
            this._scheduleSave();
        });
    }

    _scheduleSave() {
        if (this.saveTimer) clearTimeout(this.saveTimer);
        this.saveTimer = setTimeout(() => this.save(), this.saveInterval);
    }

    save() {
        if (!this.genome) return;

        // Add meta information for versioning
        if (!this.genome.metadata) this.genome.metadata = {};
        this.genome.metadata.last_saved = new Date().toISOString();
        this.genome.metadata.save_count = (this.genome.metadata.save_count || 0) + 1;

        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.genome));
            console.log(`💾 Genome saved successfully (v${this.genome.metadata.save_count})`);

            // Dispatch event for UI feedback if needed
            document.dispatchEvent(new CustomEvent('persistence:saved', {
                detail: { timestamp: this.genome.metadata.last_saved }
            }));
        } catch (e) {
            console.error('💾 Failed to save genome to localStorage', e);
        }
    }

    clear() {
        localStorage.removeItem(this.storageKey);
        location.reload();
    }
}

export default PersistenceFeature;
