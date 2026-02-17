// Lexicon.js — Source de vérité partagée (LEXICON_DESIGN.json v1.0.4)
const Lexicon = {
  slots: {
    header: '#slot-header',
    sidebar_left: '#slot-sidebar-left',
    sidebar_right: '#slot-sidebar-right',
    main: '#slot-main',
    canvas: '#slot-canvas-zone',
    preview: '#slot-preview-band',
    footer: '#slot-footer',
    navigation: '#slot-navigation',
    genome: '#slot-genome',
    style: '#slot-style'
  },
  classes: {
    containers: {
      app: 'body',
      workspace: 'stenciler-workspace',
      header: 'stenciler-header',
      navigation: 'tabs'
    },
    components: {
      card: 'component-card',
      tab: 'tab',
      active_tab: 'active',
      style_card: 'style-card',
      wireframe_base: 'wireframe-',
      button_back: 'btn-back',
      header_actions: 'header-actions',
      theme_toggle: 'theme-toggle'
    },
    typography: {
      brand: 'sidebar-brand',
      tagline: 'sidebar-tagline',
      muted: 'text-muted'
    }
  },
  data: {
    corps: 'data-corps',
    level: 'data-level',
    theme: 'data-theme',
    style: 'data-style'
  },
  tokens: {
    accent_rose: '--accent-rose',
    accent_bleu: '--accent-bleu',
    accent_vert: '--accent-vert',
    accent_orange: '--accent-orange'
  }
};

export default Lexicon;
window.Lexicon = Lexicon;
