import CanvasFeature from './Canvas.feature.js';
import { AtomPrototypes } from '../AtomPrototypes.js';

/**
 * SandboxFeature
 * Extends CanvasFeature to inject experimental behaviors.
 */
class SandboxFeature extends CanvasFeature {
    constructor(id, options) {
        super(id, options);
        console.log('🧪 Sandbox Mode Active');
    }

    _renderNode(data, pos, color, level = 0) {
        const g = super._renderNode(data, pos, color, level);
        g.classList.add('sandbox-mode');
        return g;
    }
}

export default SandboxFeature;
