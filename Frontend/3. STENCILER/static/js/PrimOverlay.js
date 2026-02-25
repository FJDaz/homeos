/**
 * PrimOverlay.js
 * Couche mémoire des modifications de primitives (Mode Illustrateur).
 * Map<nodeId, {svg: string, h: number, w: number}>
 * CODE DIRECT — FJD 2026-02-25
 */

const _store = new Map();

export const PrimOverlay = {
    set(nodeId, svg, h, w) { _store.set(nodeId, { svg, h, w }); },
    get(nodeId)             { return _store.get(nodeId); },
    clear(nodeId)           { _store.delete(nodeId); },
    clearAll()              { _store.clear(); }
};
