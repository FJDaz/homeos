console.log('[DEBUG] Script stenciler_v3_main.js LOADED');

import Lexicon from './Lexicon.js';
import HeaderFeature from './features/Header.feature.js';
import NavigationFeature from './features/Navigation.feature.js';
import GenomeSectionFeature from './features/GenomeSection.feature.js';
import StyleSectionFeature from './features/StyleSection.feature.js';
import PreviewBandFeature from './features/PreviewBand.feature.js';
import CanvasFeature from './features/Canvas.feature.js';
import TSLPickerFeature from './features/TSLPicker.feature.js';
import ColorPaletteFeature from './features/ColorPalette.feature.js';
import BorderSliderFeature from './features/BorderSlider.feature.js';
import APIStatusFeature from './features/APIStatus.feature.js';
import ComponentsZoneFeature from './features/ComponentsZone.feature.js';
import PersistenceFeature from './features/Persistence.feature.js';

console.log('[DEBUG] Imports completed');

const FEATURE_CONFIG = [
  { id: 'header', class: HeaderFeature, slot: Lexicon.slots.header },
  { id: 'navigation', class: NavigationFeature, slot: Lexicon.slots.navigation },
  { id: 'genome', class: GenomeSectionFeature, slot: Lexicon.slots.genome },
  { id: 'style', class: StyleSectionFeature, slot: Lexicon.slots.style },
  { id: 'canvas', class: CanvasFeature, slot: Lexicon.slots.canvas },
  { id: 'preview', class: PreviewBandFeature, slot: Lexicon.slots.preview },
  { id: 'components', class: ComponentsZoneFeature, slot: Lexicon.slots.sidebar_right },
  { id: 'status', class: APIStatusFeature, slot: Lexicon.slots.footer },
  { id: 'persistence', class: PersistenceFeature, slot: 'body' },
];

class StencilerApp {
  constructor() {
    console.log('[DEBUG] App Constructor');
    this.features = new Map();
    this.genome = null;
  }

  async init() {
    console.log('[DEBUG] App Init Start');
    await this.loadGenome();

    for (const config of FEATURE_CONFIG) {
      try {
        console.log(`[DEBUG] Initializing ${config.id} in ${config.slot}`);
        const feature = new config.class(config.id);
        feature.mount(config.slot);
        if (feature.init) await feature.init(this.genome);
        this.features.set(config.id, feature);
      } catch (e) {
        console.error(`[DEBUG] Error init ${config.id}:`, e);
      }
    }
    console.log('[DEBUG] App Init End');
  }

  async loadGenome() {
    console.log('[DEBUG] Loading Genome...');
    try {
      const resp = await fetch('/api/genome');
      const data = await resp.json();
      // Supporte le format {genome: {...}} ou le genome direct
      this.genome = data.genome || data;
      console.log('[DEBUG] Genome loaded', this.genome);
    } catch (e) {
      console.error('[DEBUG] Genome load failed', e);
      this.genome = { n0_phases: [] };
    }
  }
}

console.log('[DEBUG] Creating App Instance');
const app = new StencilerApp();
window.stencilerApp = app;
app.init();