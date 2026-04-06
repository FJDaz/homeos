/**
 * api.config.js — Mission 169
 * Configuration centralisée des endpoints API.
 * Résout le problème de localhost hardcodé pour le déploiement HF Spaces.
 */
(function() {
    'use strict';

    // Détection automatique de l'origine
    var API_BASE = window.location.origin;

    // Export global
    window.API_CONFIG = {
        BASE: API_BASE,
        ENDPOINTS: {
            // Sullivan
            SULLIVAN_CHAT: API_BASE + '/api/sullivan/chat',
            SULLIVAN_PULSE: API_BASE + '/api/sullivan/pulse',
            SULLIVAN_FONTS: API_BASE + '/api/sullivan/fonts',
            SULLIVAN_FONT_UPLOAD: API_BASE + '/api/sullivan/font-upload',
            SULLIVAN_GENERATE_WEBFONT: API_BASE + '/api/sullivan/generate-webfont',

            // Genome
            GENOME: API_BASE + '/api/genome',
            DRILLDOWN_ENTER: API_BASE + '/api/drilldown/enter',
            DRILLDOWN_EXIT: API_BASE + '/api/drilldown/exit',

            // Retro Genome
            RETRO_IMPORTS: API_BASE + '/api/retro-genome/imports',
            RETRO_NOTIFICATIONS: API_BASE + '/api/retro-genome/notifications',
            RETRO_NOTIFICATIONS_CLEAR: API_BASE + '/api/retro-genome/notifications/clear',
            RETRO_IMPORTS_CLEAR: API_BASE + '/api/retro-genome/imports/clear',

            // Projects
            PROJECTS: API_BASE + '/api/projects',
            PROJECTS_ACTIVE: API_BASE + '/api/projects/active',
            PROJECTS_CREATE: API_BASE + '/api/projects/create',
            PROJECTS_ACTIVATE: API_BASE + '/api/projects/activate',

            // FRD
            FRD_FILES: API_BASE + '/api/frd/files',
            FRD_FILE: API_BASE + '/api/frd/file',
            FRD_CHAT: API_BASE + '/api/frd/chat',
            FRD_WIRE: API_BASE + '/api/frd/wire',
            FRD_WIRE_AUDIT: API_BASE + '/api/frd/wire-audit',
            FRD_WIRE_SOURCE: API_BASE + '/api/frd/wire-source',

            // Import
            IMPORT_UPLOAD: API_BASE + '/api/import/upload',

            // Manifest
            MANIFEST_CHECK: API_BASE + '/api/manifest/check',
            MANIFEST_GET: API_BASE + '/api/manifest/get',
            MANIFEST_CREATE: API_BASE + '/api/manifest/create',

            // Workspace
            WORKSPACE_TOKENS: API_BASE + '/api/workspace/tokens',
            WORKSPACE_TEMPLATES: API_BASE + '/api/workspace/templates',

            // BKD
            BKD_PROJECTS: API_BASE + '/api/bkd/projects',
            BKD_FILES: API_BASE + '/api/bkd/files',
            BKD_FILE: API_BASE + '/api/bkd/file',
            BKD_CHAT: API_BASE + '/api/bkd/chat',

            // Layout
            INFER_LAYOUT: API_BASE + '/api/infer_layout',
            LAYOUT: API_BASE + '/api/layout',
            ORGAN_MOVE: API_BASE + '/api/organ-move',
            COMP_MOVE: API_BASE + '/api/comp-move',
            ACCEPT: API_BASE + '/api/accept',

            // Preview
            PREVIEW_RUN: API_BASE + '/api/preview/run',
            PREVIEW_SHOW: API_BASE + '/api/preview/show',

            // Kimi
            KIMI_START: API_BASE + '/api/frd/kimi/start',
            KIMI_RESULT: API_BASE + '/api/frd/kimi/result/',

            // Cadrage
            CADRAGE_INIT: API_BASE + '/api/cadrage/init-context',

            // Stitch / Design
            DESIGN_IMPORT: API_BASE + '/api/project/import-design-md',
            DESIGN_TOKENS: API_BASE + '/api/project/design-tokens',
        }
    };

    // Helper utilitaire
    window.api = function(endpoint) {
        return API_CONFIG.ENDPOINTS[endpoint] || (API_CONFIG.BASE + endpoint);
    };

})();
