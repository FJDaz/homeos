/**
 * WsState — M250
 * État global unique du workspace.
 * Remplace wsBackend.activeProject, session éparse, active_project.json incohérent.
 *
 * Usage : window.wsState.projectId, window.wsState.session.role, etc.
 * Traces console : [WsState] ...
 */
(function() {
    'use strict';

    var t0 = performance.now();
    console.log('[WsState] init...');

    var session = {};
    try {
        session = JSON.parse(localStorage.getItem('homeos_session') || '{}');
    } catch(e) {
        console.error('[WsState] session parse error:', e);
    }

    // Résolution du projectId depuis la session
    var projectId = session.active_project_id || session.project_id || null;
    console.log('[WsState] projectId =', projectId || '(none)');

    // Rôle utilisateur
    var role = session.role || 'unknown';
    console.log('[WsState] session.role =', role);

    // État mutable
    var state = {
        projectId: projectId,
        session: session,
        role: role,
        activeMode: 'select',
        currentFile: session.currentFile || null
    };

    // Méthodes simples (pas de classes)
    window.wsState = {
        get: function(key) { return state[key]; },
        set: function(key, val) { state[key] = val; },
        setProjectId: function(id) {
            state.projectId = id;
            console.log('[WsState] setProjectId →', id);
        },
        setMode: function(mode) {
            state.activeMode = mode;
            console.log('[WsState] setMode →', mode);
        },
        // Raccourcis
        get projectId() { return state.projectId; },
        get session() { return state.session; },
        get role() { return state.role; },
        get activeMode() { return state.activeMode; }
    };

    console.log('[WsState] ✅ OK (' + Math.round(performance.now() - t0) + 'ms)');
})();
