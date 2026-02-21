/**
 * GRID.js — Système de grille 8px universel (Figma-compatible)
 *
 * Principe : toutes les dimensions de layout passent par des constantes nommées.
 * Un LLM agent choisit G.CARD plutôt que de calculer 96. Élimine les valeurs magiques.
 *
 * Usage :
 *   import { G } from './GRID.js';
 *   const w = G.CARD;              // → 96
 *   const snapped = G.snap(dragX); // → multiple de 8 le plus proche
 *   const colW = G.cols(960, 4);   // → largeur colonne 8px-snappée
 */

// Générateur interne — ne pas utiliser directement en dehors de ce fichier
const _U = (n) => n * 8;

export const G = {

  // ─── Unités de base (multiples de 8) ────────────────────────────────────────
  U1:  _U(1),   //   8px
  U2:  _U(2),   //  16px
  U3:  _U(3),   //  24px
  U4:  _U(4),   //  32px
  U5:  _U(5),   //  40px
  U6:  _U(6),   //  48px
  U7:  _U(7),   //  56px
  U8:  _U(8),   //  64px
  U10: _U(10),  //  80px
  U12: _U(12),  //  96px
  U14: _U(14),  // 112px
  U16: _U(16),  // 128px
  U20: _U(20),  // 160px
  U22: _U(22),  // 176px
  U24: _U(24),  // 192px
  U25: _U(25),  // 200px
  U28: _U(28),  // 224px
  U32: _U(32),  // 256px
  U50: _U(50),  // 400px

  // ─── Sémantique : éléments UI ────────────────────────────────────────────────
  ICON:    _U(3),   //  24px — icône standard
  LABEL:   _U(2),   //  16px — hauteur label
  INPUT:   _U(5),   //  40px — hauteur input
  BTN:     _U(5),   //  40px — hauteur bouton action
  HEADER:  _U(6),   //  48px — bande header application
  CARD_SM: _U(10),  //  80px — carte compacte (zone RIGHT)
  CARD:    _U(12),  //  96px — carte standard (zone CENTER)
  CARD_MD: _U(14),  // 112px — carte medium / cellule dense
  SIDEBAR: _U(24),  // 192px — sidebar étroite
  PANEL:   _U(32),  // 256px — panneau large
  MODAL_W: _U(50),  // 400px — largeur modale standard
  MODAL_H: _U(32),  // 256px — hauteur modale standard

  // ─── Sémantique : espacement ─────────────────────────────────────────────────
  PAD_S: _U(1),  //   8px — padding compact
  PAD:   _U(2),  //  16px — padding interne standard
  PAD_L: _U(3),  //  24px — padding large
  GAP:   _U(2),  //  16px — gap inter-éléments standard
  GAP_S: _U(1),  //   8px — gap compact

  // ─── Sémantique : layout canvas ──────────────────────────────────────────────
  //     Ces constantes sont les valeurs cibles 8px-alignées pour LayoutEngine.
  //     Valeurs actuelles ≠ (audit ci-dessous) — FJD valide avant apply.
  //
  //     Audit LayoutEngine.js (2026-02-21) :
  //       padding  = 20   → G.PAD = 16   (delta -4px)   ⚠ à valider
  //       hTop     = 60   → G.U7  = 56   (delta -4px)   ⚠ à valider
  //       wCell    = 180  → G.CELL_W = 176 (delta -4px) ⚠ à valider
  //       hCell    = 110  → G.CELL_H = 112 (delta +2px) ⚠ à valider
  //       h(RIGHT) = 100  → G.RIGHT_H = 96 (delta -4px) ⚠ à valider
  //       wBottom  = 160  → G.BTN_W = 160 ✓ (exact)
  //       hBottom  = 40   → G.BTN: 40     ✓ (exact)
  //       wRight   = 200  → G.RIGHT_W = 200 ✓ (exact)
  //       MODAL_W  = 400  → G.MODAL_W = 400 ✓ (exact)
  //       snap 8C  = 20px → G.U3 = 24 ou G.PAD = 16    ⚠ à valider
  CELL_W:   _U(22),  // 176px — cellule CENTER (cible 8px, LayoutEngine actuel : 180)
  CELL_H:   _U(14),  // 112px — cellule CENTER (cible 8px, LayoutEngine actuel : 110)
  RIGHT_W:  _U(25),  // 200px — colonne RIGHT   ✓ déjà aligné
  RIGHT_H:  _U(12),  //  96px — bloc RIGHT      (cible 8px, LayoutEngine actuel : 100)
  BTN_W:    _U(20),  // 160px — bouton BOTTOM   ✓ déjà aligné
  TOP_H:    _U(7),   //  56px — zone TOP        (cible 8px, LayoutEngine actuel : 60)

  // ─── Utilitaires ─────────────────────────────────────────────────────────────

  /**
   * Arrondit une valeur au multiple de 8 le plus proche.
   * @param {number} val
   * @returns {number}
   */
  snap(val) {
    return Math.round(val / 8) * 8;
  },

  /**
   * Calcule la largeur d'une colonne dans un conteneur total divisé en n colonnes.
   * Résultat snappé au multiple de 8 le plus proche.
   * @param {number} totalWidth
   * @param {number} n          — nombre de colonnes
   * @param {number} [gap]      — gap entre colonnes (défaut : G.GAP = 16)
   * @returns {number}
   */
  cols(totalWidth, n, gap = _U(2)) {
    const raw = (totalWidth - gap * (n - 1)) / n;
    return Math.round(raw / 8) * 8;
  },

  /**
   * Calcule la hauteur d'une rangée dans un conteneur total divisé en n rangées.
   * Résultat snappé au multiple de 8 le plus proche.
   * @param {number} totalHeight
   * @param {number} n           — nombre de rangées
   * @param {number} [gap]       — gap entre rangées (défaut : G.GAP = 16)
   * @returns {number}
   */
  rows(totalHeight, n, gap = _U(2)) {
    const raw = (totalHeight - gap * (n - 1)) / n;
    return Math.round(raw / 8) * 8;
  },

};

export default G;
