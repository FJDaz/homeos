<html lang="fr"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HoméOS Sullivan</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@1.9.12"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #fff;
            overflow: hidden;
        }

        /* Tabs container - full width with evenly distributed tabs */
        .tabs-container {
            display: flex;
            height: 50px;
            background-color: #fff;
            border-bottom: 1px solid #e0e0e0;
        }

        .tab {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 14px;
            color: #666;
            border-right: 1px solid #e0e0e0;
            transition: all 0.2s;
        }

        .tab:last-child {
            border-right: none;
        }

        .tab:hover {
            background-color: #f9f9f9;
        }

        .tab.active {
            background-color: #A6CE39;
            color: #333;
            font-weight: 500;
        }

        /* Main layout */
        .main-container {
            display: flex;
            height: calc(100vh - 50px);
        }

        /* Sidebar - Sullivan Tools */
        .sidebar {
            width: 280px;
            background-color: #f8f8f8;
            border-right: 1px solid #e0e0e0;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }

        .logo {
            padding: 16px;
            border-bottom: 1px solid #e0e0e0;
            background: #fff;
        }

        .logo-title {
            font-size: 20px;
            font-weight: 700;
            color: #8cc63f;
            letter-spacing: -0.5px;
        }

        .logo-subtitle {
            font-size: 12px;
            color: #888;
            font-weight: 400;
            margin-top: 2px;
        }

        /* Sidebar Tools */
        .sidebar-tools {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 12px;
            background: #fff;
            border-bottom: 1px solid #e0e0e0;
        }

        .tool-btn {
            padding: 6px 12px;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            color: #1e293b;
            cursor: pointer;
            transition: all 0.2s;
        }

        .tool-btn:hover {
            background: #8cc63f;
            border-color: #7ab32e;
            color: #fff;
        }

        /* Sidebar Sections */
        .sidebar-section {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
        }

        .sidebar-section-title {
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0 0 8px 0;
        }

        .plan-steps-container,
        .components-container,
        .context-container {
            min-height: 60px;
            max-height: 200px;
            overflow-y: auto;
        }

        .plan-placeholder {
            font-size: 12px;
            color: #94a3b8;
            font-style: italic;
            margin: 0;
        }

        /* Plan Steps Checklist */
        .plan-step {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 6px 0;
            font-size: 12px;
            color: #334155;
            border-bottom: 1px solid #f1f5f9;
        }

        .plan-step:last-child {
            border-bottom: none;
        }

        .plan-step.completed {
            color: #94a3b8;
            text-decoration: line-through;
        }

        .plan-step input[type="checkbox"] {
            accent-color: #8cc63f;
        }

        /* Component cards in sidebar */
        .component-card {
            padding: 8px;
            background: #fff;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            margin-bottom: 6px;
            cursor: grab;
            font-size: 11px;
        }

        .component-card:hover {
            border-color: #8cc63f;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        /* Content area */
        .content-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            background-color: #fff;
            overflow: hidden;
        }

        /* ========== STYLES FIGMA TOOLS (from sidebar-right) ========== */
        .figma-property-group {
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }

        .figma-property-group:last-child {
            border-bottom: none;
        }

        .figma-property-row {
            display: flex;
            gap: 8px;
            margin-bottom: 6px;
        }

        .figma-property-field {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .figma-property-field label {
            font-size: 10px;
            color: #64748b;
            text-transform: uppercase;
            width: 14px;
        }

        .figma-property-field input[type="number"] {
            flex: 1;
            width: 40px;
            padding: 3px 6px;
            background: #fff;
            border: 1px solid #d0d0d0;
            border-radius: 3px;
            color: #333;
            font-size: 11px;
        }

        .figma-property-label {
            font-size: 10px;
            color: #64748b;
            margin-bottom: 6px;
            text-transform: uppercase;
        }

        .figma-color-picker {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 6px;
        }

        .figma-color-picker input[type="color"] {
            width: 24px;
            height: 24px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }

        .figma-color-value {
            flex: 1;
            font-size: 10px;
            color: #64748b;
            font-family: monospace;
        }

        .figma-color-picker input[type="range"] {
            flex: 1;
            height: 4px;
        }

        /* ========== GENOME DRILLDOWN TREE ========== */
        .genome-tree-container {
            font-size: 12px;
        }

        .genome-tree-item {
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 0;
            cursor: pointer;
            border-radius: 4px;
            transition: background 0.15s;
        }

        .genome-tree-item:hover {
            background: #f0f0f0;
        }

        .genome-tree-item[data-level="1"] {
            padding-left: 16px;
        }

        .genome-tree-item[data-level="2"] {
            padding-left: 32px;
        }

        .genome-tree-item[data-level="3"] {
            padding-left: 48px;
        }

        .tree-toggle {
            font-size: 10px;
            color: #888;
            width: 12px;
        }

        .tree-icon {
            font-size: 12px;
        }

        .tree-label {
            color: #334155;
        }

        .genome-tree-children {
            display: block;
        }

        /* ========== VALIDATION WORKFLOW ========== */
        .validation-workflow {
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .validation-panel {
            display: flex;
            gap: 20px;
            min-height: 300px;
        }

        .validation-col {
            flex: 1;
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
        }

        .validation-col-header {
            font-size: 14px;
            font-weight: 600;
            color: #333;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #e0e0e0;
        }

        .validation-btn {
            display: block;
            width: 100%;
            padding: 12px;
            margin-top: 16px;
            background: #8cc63f;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .validation-btn:hover {
            background: #7ab32e;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(140, 198, 63, 0.3);
        }

        .validation-anchor {
            height: 0;
            overflow: hidden;
            transition: all 0.5s ease;
        }

        .validation-anchor.active {
            height: auto;
            padding: 20px 0;
        }

        /* ========== CANVAS FIGMA ZONE ========== */
        .canvas-figma-zone {
            width: 100%;
            min-height: 500px;
            background: #f5f5f5;
            border: 1px solid #d0d0d0;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
        }

        .canvas-toolbar {
            display: flex;
            gap: 8px;
            padding: 10px;
            background: #fff;
            border-bottom: 1px solid #e0e0e0;
        }

        .canvas-tool-btn {
            padding: 6px 12px;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            font-size: 11px;
            cursor: pointer;
        }

        .canvas-tool-btn:hover {
            background: #8cc63f;
            color: white;
        }

        #figma-canvas {
            width: 100%;
            height: 450px;
            background: #fff;
            cursor: crosshair;
        }

        /* Tab content panels */
        .tab-content {
            display: none;
            flex: 1;
            overflow-y: auto;
        }

        .tab-content.active {
            display: flex;
            flex-direction: column;
        }

        /* Frontend workflow specific */
        .frontend-workflow {
            padding: 20px;
        }

        /* Upload prompt for default state */
        .upload-prompt {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            cursor: pointer;
            transition: opacity 0.2s;
            flex: 1;
        }

        .upload-prompt:hover {
            opacity: 0.7;
        }

        .upload-text {
            font-size: 32px;
            font-weight: 300;
            color: #333;
            letter-spacing: -0.5px;
        }

        .upload-icon {
            font-size: 28px;
            color: #666;
            transform: translateY(-2px);
        }

        /* HTMX loading states */
        .htmx-request { opacity: 0.5; pointer-events: none; }
        .htmx-request button { cursor: wait; }

        /* ========== DESIGN ARBITER - PANNEAUX ========== */
        /* Panel container for Arbiter design */
        .arbiter-container {
            display: flex;
            height: 100%;
            min-height: calc(100vh - 50px);
        }

        /* Panneau Gauche (Clair) - Intent Revue */
        .panel-left {
            width: 55%;
            background: #f0f0e8;
            padding: 24px 32px;
            overflow-y: auto;
            border-right: 1px solid #d0d0c8;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid #d0d0c8;
        }

        .panel-title {
            font-size: 14px;
            font-weight: 600;
            color: #5a5a52;
            letter-spacing: 0.5px;
        }

        .arbiter-badge {
            background: #7cb342;
            color: white;
            padding: 6px 14px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }

        /* Section Typologie */
        .typology-section {
            margin-bottom: 24px;
        }

        .section-title {
            font-size: 11px;
            font-weight: 700;
            color: #7cb342;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 12px;
        }

        .typology-content {
            display: flex;
            gap: 40px;
        }

        .typology-list {
            font-size: 11px;
            color: #5a5a52;
            line-height: 1.8;
        }

        .typology-list span {
            display: block;
        }

        .typology-list span::before {
            content: "▸ ";
            color: #7cb342;
        }

        /* Dropdowns */
        .dropdowns-col {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .dropdown-item {
            font-size: 10px;
            color: #888;
            padding: 2px 0;
        }

        /* User icons avec labels */
        .users-col {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .user-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 10px;
            color: #666;
        }

        .user-avatar {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #7cb342;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 8px;
            color: white;
        }

        /* Toggle & Button */
        .action-col {
            display: flex;
            flex-direction: column;
            gap: 8px;
            align-items: flex-start;
        }

        .toggle-switch {
            width: 36px;
            height: 18px;
            background: #7cb342;
            border-radius: 9px;
            position: relative;
            cursor: pointer;
        }

        .toggle-switch::after {
            content: "";
            position: absolute;
            width: 14px;
            height: 14px;
            background: white;
            border-radius: 50%;
            top: 2px;
            right: 2px;
        }

        .action-btn {
            background: #7cb342;
            color: white;
            border: none;
            padding: 6px 14px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            cursor: pointer;
        }

        .action-btn.secondary {
            background: #5a8f2e;
        }

        /* Section Pourquoi */
        .why-section {
            display: flex;
            gap: 40px;
            margin-top: 16px;
        }

        .why-col {
            font-size: 10px;
            color: #7cb342;
            font-weight: 600;
        }

        .why-text {
            font-size: 9px;
            color: #888;
            margin-top: 4px;
            line-height: 1.5;
            max-width: 120px;
        }

        /* Expandable sections */
        .expandable-section {
            margin-top: 24px;
            border-top: 1px solid #d0d0c8;
            padding-top: 16px;
        }

        .expandable-header {
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
        }

        .expand-icon {
            color: #7cb342;
            font-size: 12px;
        }

        .expandable-title {
            font-size: 11px;
            font-weight: 600;
            color: #7cb342;
        }

        .expandable-content {
            margin-top: 12px;
            padding-left: 20px;
            font-size: 10px;
            color: #666;
            line-height: 1.8;
        }

        .expandable-content span {
            display: block;
        }

        .expandable-content span::before {
            content: "◆ ";
            color: #7cb342;
            font-size: 8px;
        }

        .section-meta {
            font-size: 9px;
            color: #999;
            margin-top: 8px;
            padding-left: 20px;
        }

        /* ========== PANNEAU DROIT (SOMBRE) ========== */
        .panel-right {
            width: 45%;
            background: #252525;
            min-height: 100%;
            padding: 24px 32px;
            color: #fff;
            overflow-y: auto;
        }

        .genome-header {
            text-align: center;
            margin-bottom: 32px;
        }

        .genome-title {
            font-size: 14px;
            font-weight: 600;
            color: #fff;
            letter-spacing: 0.5px;
        }

        /* Sections Corps/Organes/Cellules */
        .genome-section {
            margin-bottom: 28px;
        }

        .genome-section-title {
            font-size: 12px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #3a3a3a;
        }

        .genome-content {
            display: flex;
            gap: 24px;
        }

        .genome-col {
            flex: 1;
        }

        .genome-col-header {
            font-size: 10px;
            color: #7cb342;
            font-weight: 600;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Dark dropdowns */
        .dark-dropdowns {
            background: #1e1e1e;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 8px;
        }

        .dark-dropdown-item {
            font-size: 10px;
            color: #888;
            padding: 4px 0;
            border-bottom: 1px solid #2a2a2a;
        }

        .dark-dropdown-item:last-child {
            border-bottom: none;
        }

        /* Dark user items */
        .dark-users {
            background: #1e1e1e;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 8px;
        }

        .dark-user-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 10px;
            color: #aaa;
            padding: 3px 0;
        }

        .dark-user-avatar {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #555;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 7px;
            color: #ccc;
        }

        /* Dark toggle */
        .dark-toggle {
            display: flex;
            flex-direction: column;
            gap: 8px;
            align-items: flex-start;
        }

        .dark-toggle-switch {
            width: 32px;
            height: 16px;
            background: #444;
            border-radius: 8px;
            position: relative;
        }

        .dark-toggle-switch.active {
            background: #7cb342;
        }

        .dark-toggle-switch::after {
            content: "";
            position: absolute;
            width: 12px;
            height: 12px;
            background: white;
            border-radius: 50%;
            top: 2px;
            left: 2px;
        }

        .dark-toggle-switch.active::after {
            left: auto;
            right: 2px;
        }

        .dark-btn {
            background: #7cb342;
            color: white;
            border: none;
            padding: 5px 12px;
            border-radius: 3px;
            font-size: 9px;
            font-weight: 600;
            cursor: pointer;
        }

        /* Notification banner */
        .notification-banner {
            background: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 10px 14px;
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 16px 0;
        }

        .notification-icon {
            color: #7cb342;
            font-size: 14px;
        }

        .notification-text {
            font-size: 9px;
            color: #888;
            line-height: 1.4;
        }

        /* Icons grid (Organes) */
        .icons-grid {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 8px;
            margin-top: 8px;
        }

        .icon-cell {
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
        }

        .icon-cell.green {
            color: #7cb342;
        }

        .icon-cell.gray {
            color: #555;
        }

        /* Cellules row */
        .cellules-row {
            display: flex;
            gap: 24px;
        }

        .cellules-row .genome-col-header {
            font-size: 9px;
        }

        /* Profile card */
        .profile-card {
            background: #1e1e1e;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }

        .profile-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #7cb342;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: white;
        }

        .profile-name {
            font-size: 10px;
            color: #fff;
            font-weight: 600;
        }

        .profile-role {
            font-size: 8px;
            color: #7cb342;
        }

        /* Table styles for reports */
        .prose table { font-size: 0.75rem; width: 100%; border-collapse: collapse; }
        .prose th, .prose td { padding: 0.25rem 0.5rem; border: 1px solid #e5e7eb; text-align: left; }
        .prose th { background: #f3f4f6; font-weight: 600; }
        .prose tr:nth-child(even) { background: #f9fafb; }

        /* Workflow cards */
        .workflow-card {
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }

        .workflow-card h3 {
            font-size: 14px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }

        .workflow-card p {
            font-size: 12px;
            color: #666;
            line-height: 1.5;
        }

        /* Coming soon placeholder */
        .coming-soon {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            flex: 1;
            color: #999;
        }

        .coming-soon-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }

        .coming-soon-text {
            font-size: 18px;
            font-weight: 300;
        }

        /* Hidden file input */
        #fileInput {
            display: none;
        }

        /* ========== INFÉRENCE DE COMPOSANTS ========== */
        .inference-results {
            padding: 20px;
            max-height: calc(100vh - 50px);
            overflow-y: auto;
        }

        .inference-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid #e0e0e0;
        }

        .inference-stats {
            display: flex;
            gap: 24px;
        }

        .stat-item {
            text-align: center;
        }

        .stat-value {
            display: block;
            font-size: 24px;
            font-weight: 700;
            color: #7cb342;
        }

        .stat-label {
            font-size: 11px;
            color: #888;
            text-transform: uppercase;
        }

        .inference-actions {
            display: flex;
            gap: 8px;
        }

        .btn-select-all, .btn-deselect-all {
            padding: 6px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            background: #fff;
            transition: all 0.2s;
        }

        .btn-select-all:hover {
            background: #7cb342;
            color: white;
            border-color: #7cb342;
        }

        .btn-deselect-all:hover {
            background: #e74c3c;
            color: white;
            border-color: #e74c3c;
        }

        .components-form {
            margin-bottom: 20px;
        }

        .components-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 12px;
        }

        .component-card {
            background: #fff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 14px;
            transition: all 0.2s;
        }

        .component-card:hover {
            border-color: #7cb342;
            box-shadow: 0 2px 8px rgba(124, 179, 66, 0.15);
        }

        .component-card.unselected {
            opacity: 0.6;
            background: #f9f9f9;
        }

        .component-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }

        .component-checkbox {
            width: 18px;
            height: 18px;
            accent-color: #7cb342;
            cursor: pointer;
        }

        .component-title {
            font-size: 13px;
            font-weight: 600;
            color: #333;
            cursor: pointer;
        }

        .component-description {
            font-size: 11px;
            color: #666;
            line-height: 1.4;
            margin-bottom: 10px;
            min-height: 30px;
        }

        .component-endpoints {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            margin-bottom: 10px;
        }

        .endpoint-badge {
            font-size: 9px;
            padding: 2px 6px;
            background: #e3f2fd;
            color: #1976d2;
            border-radius: 3px;
            font-family: monospace;
        }

        .endpoint-badge.more {
            background: #f5f5f5;
            color: #888;
        }

        .component-reason {
            display: flex;
            align-items: flex-start;
            gap: 6px;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 10px;
            color: #666;
        }

        .reason-icon {
            font-size: 12px;
            flex-shrink: 0;
        }

        .reason-text {
            line-height: 1.4;
        }

        .inference-footer {
            display: flex;
            justify-content: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-top: 20px;
        }

        .btn-validate-components {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 24px;
            background: #7cb342;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-validate-components:hover {
            background: #6a9e38;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(124, 179, 66, 0.3);
        }

        .btn-icon {
            font-size: 16px;
        }

        /* Loading state */
        .inference-loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px 20px;
            color: #888;
        }

        .inference-loading-spinner {
            width: 40px;
            height: 40px;
            border: 3px solid #e0e0e0;
            border-top-color: #7cb342;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 16px;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* ========== ARBITER COMPONENTS PANEL ========== */
        /* Composants suggérés dans ARBITER (panel-right sombre) */
        #arbiter-components-section {
            border-top: 2px solid #7cb342;
            padding-top: 16px;
        }

        #arbiter-components-panel {
            min-height: 60px;
        }

        .arbiter-component-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin-top: 12px;
        }

        .arbiter-component-item {
            background: #1e1e1e;
            border: 1px solid #3a3a3a;
            border-radius: 4px;
            padding: 10px;
            font-size: 10px;
            color: #aaa;
            cursor: pointer;
            transition: all 0.2s;
        }

        .arbiter-component-item:hover {
            border-color: #7cb342;
            background: #2a2a2a;
        }

        .arbiter-component-item.selected {
            border-color: #7cb342;
            background: #2a3a1e;
        }

        .arbiter-component-item input[type="checkbox"] {
            margin-right: 6px;
            accent-color: #7cb342;
            cursor: pointer;
        }

        .arbiter-component-name {
            font-weight: 600;
            color: #fff;
            display: block;
            margin-bottom: 4px;
            font-size: 11px;
        }

        .arbiter-component-reason {
            font-size: 9px;
            color: #888;
            line-height: 1.3;
            margin-top: 4px;
        }

        .arbiter-component-category {
            display: inline-block;
            font-size: 8px;
            color: #7cb342;
            background: #2a3a1e;
            padding: 1px 4px;
            border-radius: 2px;
            margin-top: 6px;
            text-transform: uppercase;
        }

        .arbiter-component-actions {
            display: flex;
            gap: 8px;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #3a3a3a;
        }

        .arbiter-btn {
            flex: 1;
            padding: 8px;
            border: none;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .arbiter-btn-primary {
            background: #7cb342;
            color: white;
        }

        .arbiter-btn-primary:hover {
            background: #6a9e38;
        }

        .arbiter-btn-secondary {
            background: #3a3a3a;
            color: #aaa;
        }

        .arbiter-btn-secondary:hover {
            background: #4a4a4a;
        }
    </style>
<style>*, ::before, ::after{--tw-border-spacing-x:0;--tw-border-spacing-y:0;--tw-translate-x:0;--tw-translate-y:0;--tw-rotate:0;--tw-skew-x:0;--tw-skew-y:0;--tw-scale-x:1;--tw-scale-y:1;--tw-pan-x: ;--tw-pan-y: ;--tw-pinch-zoom: ;--tw-scroll-snap-strictness:proximity;--tw-gradient-from-position: ;--tw-gradient-via-position: ;--tw-gradient-to-position: ;--tw-ordinal: ;--tw-slashed-zero: ;--tw-numeric-figure: ;--tw-numeric-spacing: ;--tw-numeric-fraction: ;--tw-ring-inset: ;--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-color:rgb(59 130 246 / 0.5);--tw-ring-offset-shadow:0 0 #0000;--tw-ring-shadow:0 0 #0000;--tw-shadow:0 0 #0000;--tw-shadow-colored:0 0 #0000;--tw-blur: ;--tw-brightness: ;--tw-contrast: ;--tw-grayscale: ;--tw-hue-rotate: ;--tw-invert: ;--tw-saturate: ;--tw-sepia: ;--tw-drop-shadow: ;--tw-backdrop-blur: ;--tw-backdrop-brightness: ;--tw-backdrop-contrast: ;--tw-backdrop-grayscale: ;--tw-backdrop-hue-rotate: ;--tw-backdrop-invert: ;--tw-backdrop-opacity: ;--tw-backdrop-saturate: ;--tw-backdrop-sepia: ;--tw-contain-size: ;--tw-contain-layout: ;--tw-contain-paint: ;--tw-contain-style: }::backdrop{--tw-border-spacing-x:0;--tw-border-spacing-y:0;--tw-translate-x:0;--tw-translate-y:0;--tw-rotate:0;--tw-skew-x:0;--tw-skew-y:0;--tw-scale-x:1;--tw-scale-y:1;--tw-pan-x: ;--tw-pan-y: ;--tw-pinch-zoom: ;--tw-scroll-snap-strictness:proximity;--tw-gradient-from-position: ;--tw-gradient-via-position: ;--tw-gradient-to-position: ;--tw-ordinal: ;--tw-slashed-zero: ;--tw-numeric-figure: ;--tw-numeric-spacing: ;--tw-numeric-fraction: ;--tw-ring-inset: ;--tw-ring-offset-width:0px;--tw-ring-offset-color:#fff;--tw-ring-color:rgb(59 130 246 / 0.5);--tw-ring-offset-shadow:0 0 #0000;--tw-ring-shadow:0 0 #0000;--tw-shadow:0 0 #0000;--tw-shadow-colored:0 0 #0000;--tw-blur: ;--tw-brightness: ;--tw-contrast: ;--tw-grayscale: ;--tw-hue-rotate: ;--tw-invert: ;--tw-saturate: ;--tw-sepia: ;--tw-drop-shadow: ;--tw-backdrop-blur: ;--tw-backdrop-brightness: ;--tw-backdrop-contrast: ;--tw-backdrop-grayscale: ;--tw-backdrop-hue-rotate: ;--tw-backdrop-invert: ;--tw-backdrop-opacity: ;--tw-backdrop-saturate: ;--tw-backdrop-sepia: ;--tw-contain-size: ;--tw-contain-layout: ;--tw-contain-paint: ;--tw-contain-style: }/* ! tailwindcss v3.4.17 | MIT License | https://tailwindcss.com */*,::after,::before{box-sizing:border-box;border-width:0;border-style:solid;border-color:#e5e7eb}::after,::before{--tw-content:''}:host,html{line-height:1.5;-webkit-text-size-adjust:100%;-moz-tab-size:4;tab-size:4;font-family:ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";font-feature-settings:normal;font-variation-settings:normal;-webkit-tap-highlight-color:transparent}body{margin:0;line-height:inherit}hr{height:0;color:inherit;border-top-width:1px}abbr:where([title]){-webkit-text-decoration:underline dotted;text-decoration:underline dotted}h1,h2,h3,h4,h5,h6{font-size:inherit;font-weight:inherit}a{color:inherit;text-decoration:inherit}b,strong{font-weight:bolder}code,kbd,pre,samp{font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;font-feature-settings:normal;font-variation-settings:normal;font-size:1em}small{font-size:80%}sub,sup{font-size:75%;line-height:0;position:relative;vertical-align:baseline}sub{bottom:-.25em}sup{top:-.5em}table{text-indent:0;border-color:inherit;border-collapse:collapse}button,input,optgroup,select,textarea{font-family:inherit;font-feature-settings:inherit;font-variation-settings:inherit;font-size:100%;font-weight:inherit;line-height:inherit;letter-spacing:inherit;color:inherit;margin:0;padding:0}button,select{text-transform:none}button,input:where([type=button]),input:where([type=reset]),input:where([type=submit]){-webkit-appearance:button;background-color:transparent;background-image:none}:-moz-focusring{outline:auto}:-moz-ui-invalid{box-shadow:none}progress{vertical-align:baseline}::-webkit-inner-spin-button,::-webkit-outer-spin-button{height:auto}[type=search]{-webkit-appearance:textfield;outline-offset:-2px}::-webkit-search-decoration{-webkit-appearance:none}::-webkit-file-upload-button{-webkit-appearance:button;font:inherit}summary{display:list-item}blockquote,dd,dl,figure,h1,h2,h3,h4,h5,h6,hr,p,pre{margin:0}fieldset{margin:0;padding:0}legend{padding:0}menu,ol,ul{list-style:none;margin:0;padding:0}dialog{padding:0}textarea{resize:vertical}input::placeholder,textarea::placeholder{opacity:1;color:#9ca3af}[role=button],button{cursor:pointer}:disabled{cursor:default}audio,canvas,embed,iframe,img,object,svg,video{display:block;vertical-align:middle}img,video{max-width:100%;height:auto}[hidden]:where(:not([hidden=until-found])){display:none}.mb-1{margin-bottom:0.25rem}.flex{display:flex}.max-h-32{max-height:8rem}.cursor-pointer{cursor:pointer}.flex-wrap{flex-wrap:wrap}.items-start{align-items:flex-start}.items-center{align-items:center}.gap-1{gap:0.25rem}.gap-2{gap:0.5rem}.gap-3{gap:0.75rem}.space-y-1 > :not([hidden]) ~ :not([hidden]){--tw-space-y-reverse:0;margin-top:calc(0.25rem * calc(1 - var(--tw-space-y-reverse)));margin-bottom:calc(0.25rem * var(--tw-space-y-reverse))}.space-y-3 > :not([hidden]) ~ :not([hidden]){--tw-space-y-reverse:0;margin-top:calc(0.75rem * calc(1 - var(--tw-space-y-reverse)));margin-bottom:calc(0.75rem * var(--tw-space-y-reverse))}.overflow-auto{overflow:auto}.rounded{border-radius:0.25rem}.bg-indigo-50{--tw-bg-opacity:1;background-color:rgb(238 242 255 / var(--tw-bg-opacity, 1))}.bg-slate-100{--tw-bg-opacity:1;background-color:rgb(241 245 249 / var(--tw-bg-opacity, 1))}.px-1\.5{padding-left:0.375rem;padding-right:0.375rem}.px-2{padding-left:0.5rem;padding-right:0.5rem}.py-0\.5{padding-top:0.125rem;padding-bottom:0.125rem}.font-mono{font-family:ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace}.text-\[10px\]{font-size:10px}.text-xs{font-size:0.75rem;line-height:1rem}.font-medium{font-weight:500}.text-indigo-600{--tw-text-opacity:1;color:rgb(79 70 229 / var(--tw-text-opacity, 1))}.text-slate-400{--tw-text-opacity:1;color:rgb(148 163 184 / var(--tw-text-opacity, 1))}.text-slate-500{--tw-text-opacity:1;color:rgb(100 116 139 / var(--tw-text-opacity, 1))}.text-slate-700{--tw-text-opacity:1;color:rgb(51 65 85 / var(--tw-text-opacity, 1))}</style><style>                      .htmx-indicator{opacity:0}                      .htmx-request .htmx-indicator{opacity:1; transition: opacity 200ms ease-in;}                      .htmx-request.htmx-indicator{opacity:1; transition: opacity 200ms ease-in;}                    </style><style>
#sullivan-super-widget {
  position: fixed !important;
  bottom: 24px;
  right: 24px;
  width: 400px;
  height: 600px;
  background: #ffffff;
  border-radius: 0;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  z-index: 99999 !important;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  border: none;
  transition: all 0.3s ease;
}

#sullivan-super-widget.minimized {
  height: 64px;
  width: 280px;
}

#sullivan-super-widget.minimized .sullivan-body,
#sullivan-super-widget.minimized .sullivan-quick-actions,
#sullivan-super-widget.minimized .sullivan-tools,
#sullivan-super-widget.minimized .sullivan-input {
  display: none !important;
}

#sullivan-super-widget.fullscreen {
  top: 24px;
  left: 24px;
  right: 24px;
  bottom: 24px;
  width: auto;
  height: auto;
  z-index: 100000 !important;
}

.sullivan-header {
  background: #8cc63f; /* Couleur identité HOMEOS */
  color: white;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  cursor: pointer;
}

#sullivan-super-widget:not(.minimized) .sullivan-header {
  cursor: default;
}

.sullivan-avatar {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.sullivan-info {
  flex: 1;
  min-width: 0;
}

.sullivan-info h3 {
  font-size: 15px;
  font-weight: 600;
  margin: 0;
}

.sullivan-info p {
  font-size: 12px;
  opacity: 0.85;
  margin: 2px 0 0 0;
}

.sullivan-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: rgba(16, 185, 129, 0.3);
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
}

.sullivan-controls {
  display: flex;
  gap: 8px;
}

.sullivan-btn {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.sullivan-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.sullivan-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #f8fafc;
}

.sullivan-message {
  display: flex;
  gap: 12px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.sullivan-message.user {
  flex-direction: row-reverse;
}

.sullivan-msg-avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.sullivan-message.bot .sullivan-msg-avatar {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
}

.sullivan-message.user .sullivan-msg-avatar {
  background: #8cc63f;
  color: white;
}

.sullivan-msg-content {
  max-width: 75%;
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-wrap: break-word;
}

.sullivan-message.bot .sullivan-msg-content {
  background: white;
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 4px;
}

.sullivan-message.user .sullivan-msg-content {
  background: #8cc63f;
  color: white;
  border-bottom-right-radius: 4px;
}

.sullivan-typing {
  display: none;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  width: fit-content;
  margin-left: 48px;
}

.sullivan-typing.active {
  display: flex;
}

.sullivan-typing span {
  width: 8px;
  height: 8px;
  background: #64748b;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.sullivan-typing span:nth-child(1) { animation-delay: 0s; }
.sullivan-typing span:nth-child(2) { animation-delay: 0.2s; }
.sullivan-typing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

.sullivan-quick-actions {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  border-top: 1px solid #e2e8f0;
  overflow-x: auto;
  flex-shrink: 0;
}

.sullivan-quick-btn {
  padding: 8px 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  color: #1e293b;
  cursor: pointer;
  white-space: nowrap;
}

.sullivan-quick-btn:hover {
  background: #f1f5f9;
  border-color: #8cc63f;
}

.sullivan-tools {
  display: none;
  padding: 8px 20px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  font-size: 12px;
  color: #64748b;
  align-items: center;
  gap: 8px;
}

.sullivan-tools.active {
  display: flex;
}

.sullivan-tools-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  background: #8cc63f;
  color: white;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.sullivan-input {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.sullivan-input-box {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: #f8fafc;
  border-radius: 12px;
  padding: 4px;
  border: 1px solid #e2e8f0;
}

.sullivan-input-box:focus-within {
  border-color: #8cc63f;
}

.sullivan-textarea {
  flex: 1;
  border: none;
  background: transparent;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  outline: none;
  min-height: 24px;
  max-height: 120px;
  font-family: inherit;
}

.sullivan-send {
  background: #8cc63f;
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin: 4px;
  font-size: 16px;
}

.sullivan-send:hover:not(:disabled) {
  background: #8cc63f;
}

.sullivan-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

#sullivan-toggle {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, #8cc63f, #8cc63f);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 28px;
  cursor: pointer;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  z-index: 99999 !important;
  display: none;
  align-items: center;
  justify-content: center;
}

#sullivan-toggle.visible {
  display: flex !important;
}

/* === PLAN STEP STATES === */
.plan-step.active {
  background: #f0fdf4;
  border-left: 3px solid #8cc63f;
  padding-left: 5px;
}

.plan-step.completed {
  color: #94a3b8;
  text-decoration: line-through;
}

.plan-step.completed input[type="checkbox"] {
  accent-color: #8cc63f;
}
</style><style>* { cursor: crosshair !important; }</style></head>
<body data-cursor-element-id="cursor-el-1" style="cursor: crosshair;">
    <!-- Tabs - 4 HomeOS Workflow Phases -->
    <div class="tabs-container" data-cursor-element-id="cursor-el-2">
        <div class="tab" data-tab="brainstorm" data-cursor-element-id="cursor-el-3">Brainstorm</div>
        <div class="tab" data-tab="backend" data-cursor-element-id="cursor-el-4">Backend</div>
        <div class="tab active" data-tab="frontend" data-cursor-element-id="cursor-el-5">Frontend</div>
        <div class="tab" data-tab="deploy" data-cursor-element-id="cursor-el-6">Deploy</div>
    </div>

    <!-- Main content -->
    <div class="main-container" data-cursor-element-id="cursor-el-7">
        <!-- Sidebar - Sullivan Tools -->
        <aside class="sidebar" data-cursor-element-id="cursor-el-8">
            <div class="logo" data-cursor-element-id="cursor-el-9">
                <div class="logo-title" data-cursor-element-id="cursor-el-10">HoméOS</div>
                <div class="logo-subtitle" data-cursor-element-id="cursor-el-11">Sullivan Tools</div>
            </div>

            <!-- Quick Actions - Boutons outils -->
            <div class="sidebar-tools" data-cursor-element-id="cursor-el-12">
                <button class="tool-btn" onclick="window.SullivanWidget &amp;&amp; window.SullivanWidget.quick('Analyse cette page')" data-cursor-element-id="cursor-el-13">Analyser</button>
                <button class="tool-btn" onclick="window.SullivanWidget &amp;&amp; window.SullivanWidget.quick('Génère HTMX')" data-cursor-element-id="cursor-el-14">HTMX</button>
                <button class="tool-btn" onclick="window.SullivanWidget &amp;&amp; window.SullivanWidget.quick('Affiche le system prompt')" data-cursor-element-id="cursor-el-15">System</button>
                <button class="tool-btn" onclick="window.SullivanWidget &amp;&amp; window.SullivanWidget.quick('Debug: affiche l état de la session')" data-cursor-element-id="cursor-el-16">DEBUG</button>
            </div>

            <!-- Outils Figma (from sidebar-right) -->
            <div class="sidebar-section" id="figma-tools-section" data-cursor-element-id="cursor-el-17">
                <h3 class="sidebar-section-title" data-cursor-element-id="cursor-el-18">🎨 Outils Figma</h3>
                
                <!-- Position & Size -->
                <div class="figma-property-group" data-cursor-element-id="cursor-el-19">
                    <div class="figma-property-row" data-cursor-element-id="cursor-el-20">
                        <div class="figma-property-field" data-cursor-element-id="cursor-el-21">
                            <label data-cursor-element-id="cursor-el-22">X</label>
                            <input type="number" id="figma-prop-x" value="0" data-cursor-element-id="cursor-el-23">
                        </div>
                        <div class="figma-property-field" data-cursor-element-id="cursor-el-24">
                            <label data-cursor-element-id="cursor-el-25">Y</label>
                            <input type="number" id="figma-prop-y" value="0" data-cursor-element-id="cursor-el-26">
                        </div>
                    </div>
                    <div class="figma-property-row" data-cursor-element-id="cursor-el-27">
                        <div class="figma-property-field" data-cursor-element-id="cursor-el-28">
                            <label data-cursor-element-id="cursor-el-29">W</label>
                            <input type="number" id="figma-prop-w" value="0" data-cursor-element-id="cursor-el-30">
                        </div>
                        <div class="figma-property-field" data-cursor-element-id="cursor-el-31">
                            <label data-cursor-element-id="cursor-el-32">H</label>
                            <input type="number" id="figma-prop-h" value="0" data-cursor-element-id="cursor-el-33">
                        </div>
                    </div>
                </div>

                <!-- Fill -->
                <div class="figma-property-group" data-cursor-element-id="cursor-el-34">
                    <div class="figma-property-label" data-cursor-element-id="cursor-el-35">Fill</div>
                    <div class="figma-color-picker" data-cursor-element-id="cursor-el-36">
                        <input type="color" id="figma-fill-color" value="#3b82f6" data-cursor-element-id="cursor-el-37">
                        <span class="figma-color-value" data-cursor-element-id="cursor-el-38">#3B82F6</span>
                        <input type="range" id="figma-fill-opacity" min="0" max="100" value="100" data-cursor-element-id="cursor-el-39">
                    </div>
                </div>

                <!-- Stroke -->
                <div class="figma-property-group" data-cursor-element-id="cursor-el-40">
                    <div class="figma-property-label" data-cursor-element-id="cursor-el-41">Stroke</div>
                    <div class="figma-color-picker" data-cursor-element-id="cursor-el-42">
                        <input type="color" id="figma-stroke-color" value="#000000" data-cursor-element-id="cursor-el-43">
                        <span class="figma-color-value" data-cursor-element-id="cursor-el-44">#000000</span>
                    </div>
                    <div class="figma-property-field" data-cursor-element-id="cursor-el-45">
                        <label data-cursor-element-id="cursor-el-46">Width</label>
                        <input type="number" id="figma-stroke-width" value="1" min="0" data-cursor-element-id="cursor-el-47">
                    </div>
                </div>

                <!-- Corner Radius -->
                <div class="figma-property-group" data-cursor-element-id="cursor-el-48">
                    <div class="figma-property-label" data-cursor-element-id="cursor-el-49">Corner Radius</div>
                    <input type="range" id="figma-corner-radius" min="0" max="50" value="0" data-cursor-element-id="cursor-el-50">
                </div>

                <!-- Opacity -->
                <div class="figma-property-group" data-cursor-element-id="cursor-el-51">
                    <div class="figma-property-label" data-cursor-element-id="cursor-el-52">Opacity</div>
                    <input type="range" id="figma-opacity" min="0" max="100" value="100" data-cursor-element-id="cursor-el-53">
                </div>
            </div>

            <!-- Drilldown Genome -->
            <div class="sidebar-section" id="genome-drilldown-section" data-cursor-element-id="cursor-el-54">
                <h3 class="sidebar-section-title" data-cursor-element-id="cursor-el-55">🧬 Genome Drilldown</h3>
                <div id="genome-tree" class="genome-tree-container" data-cursor-element-id="cursor-el-56">
                    <div class="genome-tree-level" data-level="0" data-cursor-element-id="cursor-el-57">
                        <div class="genome-tree-item expanded" data-id="genome-root" data-cursor-element-id="cursor-el-58">
                            <span class="tree-toggle" data-cursor-element-id="cursor-el-59">▼</span>
                            <span class="tree-icon" data-cursor-element-id="cursor-el-60">🧬</span>
                            <span class="tree-label" data-cursor-element-id="cursor-el-61">Genome Root</span>
                        </div>
                        <div class="genome-tree-children" data-cursor-element-id="cursor-el-62">
                            <div class="genome-tree-item" data-level="1" data-id="corps-brainstorm" data-cursor-element-id="cursor-el-63">
                                <span class="tree-toggle" data-cursor-element-id="cursor-el-64">▶</span>
                                <span class="tree-icon" data-cursor-element-id="cursor-el-65">💡</span>
                                <span class="tree-label" data-cursor-element-id="cursor-el-66">Corps: Brainstorm</span>
                            </div>
                            <div class="genome-tree-item" data-level="1" data-id="corps-back" data-cursor-element-id="cursor-el-67">
                                <span class="tree-toggle" data-cursor-element-id="cursor-el-68">▶</span>
                                <span class="tree-icon" data-cursor-element-id="cursor-el-69">⚙️</span>
                                <span class="tree-label" data-cursor-element-id="cursor-el-70">Corps: Back</span>
                            </div>
                            <div class="genome-tree-item" data-level="1" data-id="corps-front" data-cursor-element-id="cursor-el-71">
                                <span class="tree-toggle" data-cursor-element-id="cursor-el-72">▶</span>
                                <span class="tree-icon" data-cursor-element-id="cursor-el-73">🎨</span>
                                <span class="tree-label" data-cursor-element-id="cursor-el-74">Corps: Front</span>
                            </div>
                            <div class="genome-tree-item" data-level="1" data-id="corps-deploy" data-cursor-element-id="cursor-el-75">
                                <span class="tree-toggle" data-cursor-element-id="cursor-el-76">▶</span>
                                <span class="tree-icon" data-cursor-element-id="cursor-el-77">🚀</span>
                                <span class="tree-label" data-cursor-element-id="cursor-el-78">Corps: Deploy</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Plan Steps - Target pour Sullivan -->
            <div class="sidebar-section" data-cursor-element-id="cursor-el-79">
                <h3 class="sidebar-section-title" data-cursor-element-id="cursor-el-80">Plan en cours</h3>
                <div id="sullivan-plan-steps" class="plan-steps-container" data-cursor-element-id="cursor-el-81">
                    <p class="plan-placeholder" data-cursor-element-id="cursor-el-82">Aucun plan actif. Demande à Sullivan de créer un plan.</p>
                </div>
            </div>

            <!-- Context Zone - Genome summary -->
            <div class="sidebar-section" data-cursor-element-id="cursor-el-83">
                <h3 class="sidebar-section-title" data-cursor-element-id="cursor-el-84">Contexte projet</h3>
                <div id="sullivan-context" class="context-container" hx-get="/studio/genome/summary" hx-trigger="load" hx-swap="innerHTML" data-cursor-element-id="cursor-el-85"><div class="space-y-3" data-cursor-element-id="cursor-el-86">
        <div class="flex items-center gap-2 text-xs text-slate-500" data-cursor-element-id="cursor-el-87">
            <span class="px-2 py-0.5 bg-slate-100 rounded" data-cursor-element-id="cursor-el-88">v0.1.0</span>
            <span data-cursor-element-id="cursor-el-89">PaaS_Studio</span>
        </div>
        
        <div data-cursor-element-id="cursor-el-90">
            <p class="text-xs font-medium text-slate-700 mb-1" data-cursor-element-id="cursor-el-91">Topologie (4)</p>
            <div class="flex flex-wrap gap-1" data-cursor-element-id="cursor-el-92">
                <span class="text-[10px] px-1.5 py-0.5 bg-indigo-50 text-indigo-600 rounded" data-cursor-element-id="cursor-el-93">Brainstorm</span><span class="text-[10px] px-1.5 py-0.5 bg-indigo-50 text-indigo-600 rounded" data-cursor-element-id="cursor-el-94">Back</span><span class="text-[10px] px-1.5 py-0.5 bg-indigo-50 text-indigo-600 rounded" data-cursor-element-id="cursor-el-95">Front</span><span class="text-[10px] px-1.5 py-0.5 bg-indigo-50 text-indigo-600 rounded" data-cursor-element-id="cursor-el-96">Deploy</span>
            </div>
        </div>
        
        <div data-cursor-element-id="cursor-el-97">
            <p class="text-xs font-medium text-slate-700 mb-1" data-cursor-element-id="cursor-el-98">Endpoints (44)</p>
            <div class="space-y-1 max-h-32 overflow-auto" data-cursor-element-id="cursor-el-99">
                <p class="text-[10px] text-slate-500 font-mono" data-cursor-element-id="cursor-el-100">GET /studio/reports/ir</p><p class="text-[10px] text-slate-500 font-mono" data-cursor-element-id="cursor-el-101">GET /studio/reports/arbitrage</p><p class="text-[10px] text-slate-500 font-mono" data-cursor-element-id="cursor-el-102">GET /studio/arbitrage/forms</p><p class="text-[10px] text-slate-500 font-mono" data-cursor-element-id="cursor-el-103">POST /studio/validate</p><p class="text-[10px] text-slate-500 font-mono" data-cursor-element-id="cursor-el-104">GET /studio/distillation/entries</p>
                <p class="text-[10px] text-slate-400" data-cursor-element-id="cursor-el-105">+ 39 plus...</p>
            </div>
        </div>
    </div>
    </div>
            </div>
        </aside>

        <!-- Main content area - Tab panels -->
        <main class="content-area" data-cursor-element-id="cursor-el-106">
            <!-- Brainstorm Tab -->
            <div id="tab-brainstorm" class="tab-content" data-cursor-element-id="cursor-el-107">
                <div class="coming-soon" data-cursor-element-id="cursor-el-108">
                    <div class="coming-soon-icon" data-cursor-element-id="cursor-el-109">💡</div>
                    <div class="coming-soon-text" data-cursor-element-id="cursor-el-110">Brainstorm - Phase d'idéation</div>
                    <p style="color: #bbb; margin-top: 8px; font-size: 13px;" data-cursor-element-id="cursor-el-111">Définissez votre projet, vos objectifs, et votre audience</p>
                </div>
            </div>

            <!-- Backend Tab -->
            <div id="tab-backend" class="tab-content" data-cursor-element-id="cursor-el-112">
                <div class="coming-soon" data-cursor-element-id="cursor-el-113">
                    <div class="coming-soon-icon" data-cursor-element-id="cursor-el-114">⚙️</div>
                    <div class="coming-soon-text" data-cursor-element-id="cursor-el-115">Backend - Architecture &amp; API</div>
                    <p style="color: #bbb; margin-top: 8px; font-size: 13px;" data-cursor-element-id="cursor-el-116">Configurez votre architecture backend et vos endpoints</p>
                </div>
            </div>

            <!-- Frontend Tab - Design ARBITER (Intent Revue + Génome) -->
            <div id="tab-frontend" class="tab-content active" data-cursor-element-id="cursor-el-117">
                <!-- VIEW STEP 4: Composants Inférés + Validation + Canvas -->
                <div id="frontend-step4-view" class="inference-results" style="display: none;" data-cursor-element-id="cursor-el-118">
                    
                    <!-- VALIDATION PANEL 50/50 -->
                    <div class="validation-workflow" data-cursor-element-id="cursor-el-119">
                        <div class="validation-panel" data-cursor-element-id="cursor-el-120">
                            <!-- Col Gauche: IR + Visuel -->
                            <div class="validation-col" data-cursor-element-id="cursor-el-121">
                                <div class="validation-col-header" data-cursor-element-id="cursor-el-122">📋 IR + Visuel</div>
                                <div id="ir-visual-content" data-cursor-element-id="cursor-el-123">
                                    <div class="endpoint-list" data-cursor-element-id="cursor-el-124">
                                        <div class="endpoint-item" style="padding: 8px; background: #fff; border-radius: 4px; margin-bottom: 8px; border: 1px solid #e0e0e0;" data-cursor-element-id="cursor-el-125">
                                            <div style="font-size: 12px; font-weight: 600; color: #333;" data-cursor-element-id="cursor-el-126">GET /studio/genome</div>
                                            <div style="font-size: 11px; color: #666;" data-cursor-element-id="cursor-el-127">Récupère le genome enrichi</div>
                                        </div>
                                        <div class="endpoint-item" style="padding: 8px; background: #fff; border-radius: 4px; margin-bottom: 8px; border: 1px solid #e0e0e0;" data-cursor-element-id="cursor-el-128">
                                            <div style="font-size: 12px; font-weight: 600; color: #333;" data-cursor-element-id="cursor-el-129">POST /studio/analyze</div>
                                            <div style="font-size: 11px; color: #666;" data-cursor-element-id="cursor-el-130">Analyse le design</div>
                                        </div>
                                    </div>
                                    
                                    <!-- Visual Hint Preview -->
                                    <div style="margin-top: 16px; padding: 12px; background: #fff; border: 1px dashed #8cc63f; border-radius: 4px;" data-cursor-element-id="cursor-el-131">
                                        <div style="font-size: 11px; color: #8cc63f; margin-bottom: 8px;" data-cursor-element-id="cursor-el-132">🎨 Wireframe esquissé</div>
                                        <div style="height: 80px; background: #f9f9f9; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #888; font-size: 12px;" data-cursor-element-id="cursor-el-133">
                                            Preview visuel du composant
                                        </div>
                                    </div>
                                </div>
                                
                                <button class="validation-btn" onclick="validateCurrentCorps()" data-cursor-element-id="cursor-el-134">
                                    ✓ VALIDER CE CORPS ↓
                                </button>
                            </div>
                            
                            <!-- Col Droite: Genome -->
                            <div class="validation-col" data-cursor-element-id="cursor-el-135">
                                <div class="validation-col-header" data-cursor-element-id="cursor-el-136">🧬 Genome</div>
                                <div id="genome-detail-content" data-cursor-element-id="cursor-el-137">
                                    <div class="genome-node" style="padding: 10px; background: #fff; border-radius: 4px; margin-bottom: 8px; border-left: 3px solid #8cc63f;" data-cursor-element-id="cursor-el-138">
                                        <div style="font-size: 12px; font-weight: 600; color: #333;" data-cursor-element-id="cursor-el-139">N1: Corps Front</div>
                                        <div style="font-size: 11px; color: #666; margin-top: 4px;" data-cursor-element-id="cursor-el-140">3 organes • 12 atomes</div>
                                    </div>
                                    <div class="genome-node" style="padding: 10px; background: #fff; border-radius: 4px; margin-bottom: 8px; border-left: 3px solid #3b82f6;" data-cursor-element-id="cursor-el-141">
                                        <div style="font-size: 12px; font-weight: 600; color: #333;" data-cursor-element-id="cursor-el-142">N2: Organe Navigation</div>
                                        <div style="font-size: 11px; color: #666; margin-top: 4px;" data-cursor-element-id="cursor-el-143">Endpoints: /studio/step/*</div>
                                    </div>
                                </div>
                                
                                <div style="margin-top: 12px; padding: 10px; background: #e8f5e9; border-radius: 4px; font-size: 11px; color: #2e7d32;" data-cursor-element-id="cursor-el-144">
                                    <strong data-cursor-element-id="cursor-el-145">Progression:</strong> <span id="corps-progress" data-cursor-element-id="cursor-el-146">1/4 corps validés</span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Anchor FRD Step 2 -->
                        <div id="anchor-frd-step2" class="validation-anchor" data-cursor-element-id="cursor-el-147">
                            <div style="padding: 20px; background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px;" data-cursor-element-id="cursor-el-148">
                                <h4 style="margin: 0 0 12px 0; color: #0369a1; font-size: 14px;" data-cursor-element-id="cursor-el-149">🎯 Validation Corps: <span id="validated-corps-name" data-cursor-element-id="cursor-el-150">Front</span></h4>
                                <p style="margin: 0; font-size: 12px; color: #0ea5e9;" data-cursor-element-id="cursor-el-151">Corps sauvegardé. Passage au corps suivant...</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- UPLOAD SECTION -->
                    <div id="upload-section" style="padding: 0 20px 20px 20px;" data-cursor-element-id="cursor-el-152">
                        <div style="display: flex; gap: 16px; align-items: center; padding: 20px; background: #f8f9fa; border: 2px dashed #d0d0d0; border-radius: 8px; cursor: pointer;" onclick="document.getElementById('design-upload').click()" data-cursor-element-id="cursor-el-153">
                            <div style="font-size: 32px;" data-cursor-element-id="cursor-el-154">📁</div>
                            <div data-cursor-element-id="cursor-el-155">
                                <div style="font-size: 14px; font-weight: 600; color: #333;" data-cursor-element-id="cursor-el-156">UPLOAD Fil ou Design</div>
                                <div style="font-size: 12px; color: #666;" data-cursor-element-id="cursor-el-157">Glissez-déposez ou cliquez pour sélectionner</div>
                            </div>
                            <input type="file" id="design-upload" style="display: none;" accept=".png,.jpg,.jpeg,.svg" data-cursor-element-id="cursor-el-158">
                        </div>
                        
                        <button class="validation-btn" onclick="validateForNextStep()" style="margin-top: 16px;" data-cursor-element-id="cursor-el-159">
                            ✓ VALIDER POUR ÉTAPE SUIVANTE ↓
                        </button>
                    </div>
                    
                    <!-- Anchor FRD Step 2 (Canvas) -->
                    <div id="anchor-frd-canvas" class="validation-anchor" data-cursor-element-id="cursor-el-160">
                        <div style="padding: 0 20px 20px 20px;" data-cursor-element-id="cursor-el-161">
                            <div style="padding: 16px; background: #f0fdf4; border: 1px solid #86efac; border-radius: 8px; margin-bottom: 16px;" data-cursor-element-id="cursor-el-162">
                                <h4 style="margin: 0 0 8px 0; color: #166534; font-size: 14px;" data-cursor-element-id="cursor-el-163">✅ Étape validée</h4>
                                <p style="margin: 0; font-size: 12px; color: #22c55e;" data-cursor-element-id="cursor-el-164">Ouvrir le Canvas Figma pour prototypage</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- CANVAS FIGMA ZONE (100% width) -->
                    <div style="padding: 0 20px 20px 20px;" data-cursor-element-id="cursor-el-165">
                        <div class="canvas-figma-zone" data-cursor-element-id="cursor-el-166">
                            <div class="canvas-toolbar" data-cursor-element-id="cursor-el-167">
                                <button class="canvas-tool-btn active" data-tool="select" data-cursor-element-id="cursor-el-168">↖ Select</button>
                                <button class="canvas-tool-btn" data-tool="rect" data-cursor-element-id="cursor-el-169">▭ Rect</button>
                                <button class="canvas-tool-btn" data-tool="circle" data-cursor-element-id="cursor-el-170">○ Circle</button>
                                <button class="canvas-tool-btn" data-tool="text" data-cursor-element-id="cursor-el-171">T Text</button>
                                <button class="canvas-tool-btn" data-tool="line" data-cursor-element-id="cursor-el-172">/ Line</button>
                                <div style="flex: 1;" data-cursor-element-id="cursor-el-173"></div>
                                <span style="font-size: 11px; color: #666;" data-cursor-element-id="cursor-el-174">Grid: 20px | Snap: ON</span>
                            </div>
                            <canvas id="figma-canvas" data-cursor-element-id="cursor-el-175"></canvas>
                        </div>
                        
                        <!-- Validation finale UI -->
                        <div style="display: flex; gap: 12px; margin-top: 16px;" data-cursor-element-id="cursor-el-176">
                            <button class="validation-btn" style="flex: 1; background: #3b82f6;" onclick="previewRealRender()" data-cursor-element-id="cursor-el-177">
                                👁️ APERÇU RÉEL
                            </button>
                            <button class="validation-btn" style="flex: 1;" onclick="validateModeConstruction()" data-cursor-element-id="cursor-el-178">
                                ✓ VALIDER MODE CONSTRUCTION
                            </button>
                            <button class="validation-btn" style="flex: 1; background: #ef4444;" onclick="cancelAndReturn()" data-cursor-element-id="cursor-el-179">
                                ✗ ANNULER
                            </button>
                        </div>
                    </div>
                </div>

                <!-- VIEW DEFAULT: Arbiter (affiché par défaut) -->
                <div id="frontend-arbiter-view" class="arbiter-container" data-cursor-element-id="cursor-el-180">
                    <!-- PANNEAU GAUCHE - Intent Revue (Clair) -->
                    <div class="panel-left" data-cursor-element-id="cursor-el-181">
                        <div class="panel-header" data-cursor-element-id="cursor-el-182">
                            <span class="panel-title" data-cursor-element-id="cursor-el-183">Intent Revue</span>
                            <span class="arbiter-badge" data-cursor-element-id="cursor-el-184">Arbitrage Sullivan</span>
                        </div>

                        <!-- Composants Inférés par Typologie (chargé via HTMX) -->
                        <div class="expandable-section" id="typologies-section-container" data-cursor-element-id="cursor-el-185">
                            <div class="expandable-header" data-cursor-element-id="cursor-el-186">
                                <span class="expand-icon" data-cursor-element-id="cursor-el-187">↕</span>
                                <span class="expandable-title" data-cursor-element-id="cursor-el-188">§1.5 Composants suggérés</span>
                            </div>
                            <div id="typologies-section" hx-get="/studio/typologies/arbiter" hx-trigger="load" hx-swap="innerHTML" class="" data-cursor-element-id="cursor-el-189"><div class="arbiter-component-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px;" data-cursor-element-id="cursor-el-190">
        
        <div class="arbiter-component-item" data-component-id="comp_0" style="background: rgb(30, 30, 30); border: 1px solid rgb(58, 58, 58); border-radius: 8px; padding: 12px; cursor: pointer; transition: 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-191">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-192">
                <input type="checkbox" class="component-checkbox" value="comp_0" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-193">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-194">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-195">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-196">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-197">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-198">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-199">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-200">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-201">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-202"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-203">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-204"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-205"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-206">/studio/reports/ir</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_1" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-207">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-208">
                <input type="checkbox" class="component-checkbox" value="comp_1" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-209">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-210">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-211">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-212">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-213">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-214">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-215">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-216">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-217">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-218"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-219">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-220"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-221"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-222">/studio/reports/arbitrage</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_2" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-223">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-224">
                <input type="checkbox" class="component-checkbox" value="comp_2" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-225">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-226">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-227">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-228">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-229">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-230">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-231">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-232">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-233">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-234"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-235">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-236"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-237"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-238">/studio/arbitrage/forms</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_3" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-239">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-240">
                <input type="checkbox" class="component-checkbox" value="comp_3" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-241">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-242">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-243">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-244">📝</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-245">Formulaire</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-246">POST</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-247">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 10px; width: 100%;" data-cursor-element-id="cursor-el-248">
                <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-249">
                    <div style="width: 40%; height: 4px; background: #7cb342; border-radius: 1px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-250"></div>
                    <div style="width: 100%; height: 12px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 2px;" data-cursor-element-id="cursor-el-251"></div>
                </div>
                <div data-cursor-element-id="cursor-el-252">
                    <div style="width: 30%; height: 4px; background: #7cb342; border-radius: 1px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-253"></div>
                    <div style="width: 100%; height: 12px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 2px;" data-cursor-element-id="cursor-el-254"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-255">/studio/validate</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_4" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-256">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-257">
                <input type="checkbox" class="component-checkbox" value="comp_4" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-258">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-259">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-260">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-261">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-262">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-263">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-264">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-265">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-266">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-267"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-268">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-269"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-270"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-271">/studio/distillation/entries</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_5" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-272">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-273">
                <input type="checkbox" class="component-checkbox" value="comp_5" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-274">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-275">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-276">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-277">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-278">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-279">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-280">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-281">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-282">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-283"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-284">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-285"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-286"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-287">/studio/genome/summary</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_6" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-288">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-289">
                <input type="checkbox" class="component-checkbox" value="comp_6" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-290">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-291">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-292">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-293">📝</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-294">Formulaire</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-295">POST</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-296">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 10px; width: 100%;" data-cursor-element-id="cursor-el-297">
                <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-298">
                    <div style="width: 40%; height: 4px; background: #7cb342; border-radius: 1px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-299"></div>
                    <div style="width: 100%; height: 12px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 2px;" data-cursor-element-id="cursor-el-300"></div>
                </div>
                <div data-cursor-element-id="cursor-el-301">
                    <div style="width: 30%; height: 4px; background: #7cb342; border-radius: 1px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-302"></div>
                    <div style="width: 100%; height: 12px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 2px;" data-cursor-element-id="cursor-el-303"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-304">/studio/next/{current_step}</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_7" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-305">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-306">
                <input type="checkbox" class="component-checkbox" value="comp_7" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-307">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-308">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-309">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-310">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-311">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-312">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-313">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-314">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-315">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-316"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-317">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-318"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-319"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-320">/studio/step/{step}</p>
                </div>
            </label>
        </div>
        
    </div>
    <div class="arbiter-component-actions" style="display: flex; gap: 8px; margin-top: 16px; padding-top: 16px; border-top: 1px solid #3a3a3a;" data-cursor-element-id="cursor-el-321">
        <button class="arbiter-btn arbiter-btn-secondary" onclick="selectAllArbiterComponents(false)" style="flex: 1; padding: 10px; background: #3a3a3a; color: #aaa; border: none; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer;" data-cursor-element-id="cursor-el-322">Tout désélectionner</button>
        <button class="arbiter-btn arbiter-btn-primary" onclick="validateArbiterSelection()" style="flex: 1; padding: 10px; background: #7cb342; color: white; border: none; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer;" data-cursor-element-id="cursor-el-323">Valider (8)</button>
    </div>
    <script data-cursor-element-id="cursor-el-324">
        function selectAllArbiterComponents(select) {
            document.querySelectorAll('#arbiter-components-panel .component-checkbox').forEach(chk => {
                chk.checked = select;
            });
        }
        function validateArbiterSelection() {
            const selected = Array.from(document.querySelectorAll('#arbiter-components-panel .component-checkbox:checked')).map(chk => chk.value);
            console.log('Composants ARBITER sélectionnés:', selected);
            if (window.navigateToStep4) {
                window.navigateToStep4();
            }
        }
    </script>
    </div>
                            <div class="section-meta" data-cursor-element-id="cursor-el-325">→ Composants inférés depuis le genome</div>
                        </div>
                    </div>

                    <!-- PANNEAU DROIT - Génome (Sombre) -->
                    <div class="panel-right" data-cursor-element-id="cursor-el-326">
                        <div class="genome-header" style="display: flex; justify-content: space-between; align-items: center;" data-cursor-element-id="cursor-el-327">
                            <span class="genome-title" data-cursor-element-id="cursor-el-328">Génome de HoméOS Sullivan</span>
                            <button type="button" onclick="navigateToStep4()" class="arbiter-badge" style="cursor: pointer; border: none; font-family: inherit;" data-cursor-element-id="cursor-el-329">
                                Valider → Tous les composants
                            </button>
                        </div>

                        <!-- Corps -->
                        <div class="genome-section" data-cursor-element-id="cursor-el-330">
                            <div class="genome-section-title" data-cursor-element-id="cursor-el-331">Corps</div>
                            <div class="genome-content" data-cursor-element-id="cursor-el-332">
                                <div class="genome-col" data-cursor-element-id="cursor-el-333">
                                    <div class="genome-col-header" data-cursor-element-id="cursor-el-334">Brainstorm</div>
                                    <div class="dark-dropdowns" data-cursor-element-id="cursor-el-335">
                                        <div class="dark-dropdown-item" data-cursor-element-id="cursor-el-336">Intent definition</div>
                                        <div class="dark-dropdown-item" data-cursor-element-id="cursor-el-337">User stories</div>
                                        <div class="dark-dropdown-item" data-cursor-element-id="cursor-el-338">Feature mapping</div>
                                        <div class="dark-dropdown-item" data-cursor-element-id="cursor-el-339">Acceptance criteria</div>
                                    </div>
                                    <div style="margin-top: 12px; font-size: 10px; color: #7cb342; font-weight: 600;" data-cursor-element-id="cursor-el-340">Pourquoi</div>
                                    <div style="margin-top: 4px; font-size: 9px; color: #666; line-height: 1.4;" data-cursor-element-id="cursor-el-341">
                                        Phase d'idéation structurée pour capturer les besoins métier et utilisateur.
                                    </div>
                                </div>
                                <div class="genome-col" data-cursor-element-id="cursor-el-342">
                                    <div class="genome-col-header" data-cursor-element-id="cursor-el-343">Back</div>
                                    <div class="profile-card" data-cursor-element-id="cursor-el-344">
                                        <div class="profile-avatar" data-cursor-element-id="cursor-el-345">⚙️</div>
                                        <div class="profile-name" data-cursor-element-id="cursor-el-346">API Layer</div>
                                        <div class="profile-role" data-cursor-element-id="cursor-el-347">FastAPI</div>
                                    </div>
                                    <div class="dark-users" style="margin-top: 8px;" data-cursor-element-id="cursor-el-348">
                                        <div class="dark-user-item" data-cursor-element-id="cursor-el-349">
                                            <div class="dark-user-avatar" data-cursor-element-id="cursor-el-350">📡</div>
                                            <span data-cursor-element-id="cursor-el-351">/execute</span>
                                        </div>
                                        <div class="dark-user-item" data-cursor-element-id="cursor-el-352">
                                            <div class="dark-user-avatar" data-cursor-element-id="cursor-el-353">💊</div>
                                            <span data-cursor-element-id="cursor-el-354">/health</span>
                                        </div>
                                        <div class="dark-user-item" data-cursor-element-id="cursor-el-355">
                                            <div class="dark-user-avatar" data-cursor-element-id="cursor-el-356">🧬</div>
                                            <span data-cursor-element-id="cursor-el-357">/genome</span>
                                        </div>
                                    </div>
                                </div>
                                <div class="genome-col" data-cursor-element-id="cursor-el-358">
                                    <div class="genome-col-header" data-cursor-element-id="cursor-el-359">Front</div>
                                    <div class="dark-toggle" data-cursor-element-id="cursor-el-360">
                                        <div class="dark-toggle-switch active" data-cursor-element-id="cursor-el-361"></div>
                                        <button class="dark-btn" data-cursor-element-id="cursor-el-362">Actif</button>
                                    </div>
                                </div>
                                <div class="genome-col" data-cursor-element-id="cursor-el-363">
                                    <div class="genome-col-header" data-cursor-element-id="cursor-el-364">Deploy</div>
                                    <div class="dark-toggle" data-cursor-element-id="cursor-el-365">
                                        <div class="dark-toggle-switch" data-cursor-element-id="cursor-el-366"></div>
                                        <button class="dark-btn" data-cursor-element-id="cursor-el-367">Config</button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Notification -->
                        <div class="notification-banner" data-cursor-element-id="cursor-el-368">
                            <span class="notification-icon" data-cursor-element-id="cursor-el-369">📍</span>
                            <span class="notification-text" data-cursor-element-id="cursor-el-370">Système en mode Construction.<br data-cursor-element-id="cursor-el-371">Basculer vers Mode Projet pour livraison client.</span>
                        </div>

                        <!-- Organes -->
                        <div class="genome-section" data-cursor-element-id="cursor-el-372">
                            <div class="genome-section-title" data-cursor-element-id="cursor-el-373">Organes</div>
                            <div class="genome-content" data-cursor-element-id="cursor-el-374">
                                <div class="genome-col" data-cursor-element-id="cursor-el-375">
                                    <div class="genome-col-header" data-cursor-element-id="cursor-el-376">Brainstorm</div>
                                    <div class="icons-grid" data-cursor-element-id="cursor-el-377">
                                        <div class="icon-cell green" data-cursor-element-id="cursor-el-378">💡</div>
                                        <div class="icon-cell green" data-cursor-element-id="cursor-el-379">📝</div>
                                        <div class="icon-cell green" data-cursor-element-id="cursor-el-380">🎯</div>
                                        <div class="icon-cell green" data-cursor-element-id="cursor-el-381">📊</div>
                                        <div class="icon-cell green" data-cursor-element-id="cursor-el-382">🔍</div>
                                        <div class="icon-cell green" data-cursor-element-id="cursor-el-383">💬</div>
                                        <div class="icon-cell green" data-cursor-element-id="cursor-el-384">🎨</div>
                                        <div class="icon-cell green" data-cursor-element-id="cursor-el-385">✓</div>
                                        <div class="icon-cell gray" data-cursor-element-id="cursor-el-386">○</div>
                                        <div class="icon-cell gray" data-cursor-element-id="cursor-el-387">○</div>
                                        <div class="icon-cell gray" data-cursor-element-id="cursor-el-388">○</div>
                                        <div class="icon-cell gray" data-cursor-element-id="cursor-el-389">○</div>
                                    </div>
                                </div>
                                <div class="genome-col" data-cursor-element-id="cursor-el-390">
                                    <div class="genome-col-header" data-cursor-element-id="cursor-el-391">Back/Front</div>
                                </div>
                            </div>
                        </div>

                        <!-- Cellules -->
                        <div class="genome-section" data-cursor-element-id="cursor-el-392">
                            <div class="genome-section-title" data-cursor-element-id="cursor-el-393">Cellules</div>
                            <div class="cellules-row" data-cursor-element-id="cursor-el-394">
                                <div class="genome-col" data-cursor-element-id="cursor-el-395">
                                    <div class="genome-col-header" data-cursor-element-id="cursor-el-396">Brainstorm</div>
                                    <div class="dark-dropdowns" data-cursor-element-id="cursor-el-397">
                                        <div class="dark-dropdown-item" data-cursor-element-id="cursor-el-398">Intent cards</div>
                                        <div class="dark-dropdown-item" data-cursor-element-id="cursor-el-399">User personas</div>
                                    </div>
                                </div>
                                <div class="genome-col" data-cursor-element-id="cursor-el-400">
                                    <div class="genome-col-header" data-cursor-element-id="cursor-el-401">Back/Front</div>
                                    <div class="dark-dropdowns" data-cursor-element-id="cursor-el-402">
                                        <div class="dark-dropdown-item" data-cursor-element-id="cursor-el-403">API schemas</div>
                                        <div class="dark-dropdown-item" data-cursor-element-id="cursor-el-404">Components</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Composants Inférés (chargé dynamiquement via HTMX) -->
                        <div class="genome-section" id="arbiter-components-section" style="display: block;" data-cursor-element-id="cursor-el-405">
                            <div class="genome-section-title" data-cursor-element-id="cursor-el-406">
                                Composants suggérés
                                <span style="float: right; font-size: 9px; color: #7cb342; text-transform: none;" data-cursor-element-id="cursor-el-407">
                                    <span id="arbiter-comp-count" data-cursor-element-id="cursor-el-408">0</span> trouvés
                                </span>
                            </div>
                            <div id="arbiter-components-panel" hx-get="/studio/typologies/arbiter" hx-trigger="load" hx-swap="innerHTML" class="" data-cursor-element-id="cursor-el-409"><div class="arbiter-component-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px;" data-cursor-element-id="cursor-el-410">
        
        <div class="arbiter-component-item" data-component-id="comp_0" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-411">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-412">
                <input type="checkbox" class="component-checkbox" value="comp_0" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-413">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-414">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-415">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-416">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-417">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-418">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-419">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-420">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-421">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-422"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-423">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-424"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-425"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-426">/studio/reports/ir</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_1" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-427">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-428">
                <input type="checkbox" class="component-checkbox" value="comp_1" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-429">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-430">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-431">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-432">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-433">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-434">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-435">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-436">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-437">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-438"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-439">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-440"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-441"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-442">/studio/reports/arbitrage</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_2" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-443">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-444">
                <input type="checkbox" class="component-checkbox" value="comp_2" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-445">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-446">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-447">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-448">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-449">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-450">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-451">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-452">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-453">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-454"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-455">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-456"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-457"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-458">/studio/arbitrage/forms</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_3" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-459">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-460">
                <input type="checkbox" class="component-checkbox" value="comp_3" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-461">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-462">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-463">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-464">📝</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-465">Formulaire</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-466">POST</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-467">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 10px; width: 100%;" data-cursor-element-id="cursor-el-468">
                <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-469">
                    <div style="width: 40%; height: 4px; background: #7cb342; border-radius: 1px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-470"></div>
                    <div style="width: 100%; height: 12px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 2px;" data-cursor-element-id="cursor-el-471"></div>
                </div>
                <div data-cursor-element-id="cursor-el-472">
                    <div style="width: 30%; height: 4px; background: #7cb342; border-radius: 1px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-473"></div>
                    <div style="width: 100%; height: 12px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 2px;" data-cursor-element-id="cursor-el-474"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-475">/studio/validate</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_4" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-476">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-477">
                <input type="checkbox" class="component-checkbox" value="comp_4" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-478">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-479">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-480">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-481">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-482">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-483">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-484">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-485">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-486">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-487"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-488">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-489"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-490"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-491">/studio/distillation/entries</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_5" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-492">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-493">
                <input type="checkbox" class="component-checkbox" value="comp_5" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-494">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-495">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-496">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-497">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-498">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-499">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-500">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-501">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-502">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-503"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-504">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-505"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-506"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-507">/studio/genome/summary</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_6" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-508">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-509">
                <input type="checkbox" class="component-checkbox" value="comp_6" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-510">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-511">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-512">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-513">📝</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-514">Formulaire</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-515">POST</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-516">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 10px; width: 100%;" data-cursor-element-id="cursor-el-517">
                <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-518">
                    <div style="width: 40%; height: 4px; background: #7cb342; border-radius: 1px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-519"></div>
                    <div style="width: 100%; height: 12px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 2px;" data-cursor-element-id="cursor-el-520"></div>
                </div>
                <div data-cursor-element-id="cursor-el-521">
                    <div style="width: 30%; height: 4px; background: #7cb342; border-radius: 1px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-522"></div>
                    <div style="width: 100%; height: 12px; background: #2a2a2a; border: 1px solid #3a3a3a; border-radius: 2px;" data-cursor-element-id="cursor-el-523"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-524">/studio/next/{current_step}</p>
                </div>
            </label>
        </div>
        
        <div class="arbiter-component-item" data-component-id="comp_7" style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s;" onmouseover="this.style.borderColor='#7cb342'" onmouseout="this.style.borderColor='#3a3a3a'" data-cursor-element-id="cursor-el-525">
            <label class="flex items-start gap-3 cursor-pointer" style="display: flex; align-items: flex-start; gap: 12px;" data-cursor-element-id="cursor-el-526">
                <input type="checkbox" class="component-checkbox" value="comp_7" checked="" style="margin-top: 4px; accent-color: #7cb342;" data-cursor-element-id="cursor-el-527">
                <div style="flex: 1; min-width: 0;" data-cursor-element-id="cursor-el-528">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;" data-cursor-element-id="cursor-el-529">
                        <span style="font-size: 16px;" data-cursor-element-id="cursor-el-530">📦</span>
                        <span style="font-size: 11px; color: #7cb342; font-weight: 600; text-transform: uppercase;" data-cursor-element-id="cursor-el-531">Composant</span>
                        <code style="font-size: 9px; color: #666; background: #252525; padding: 2px 6px; border-radius: 3px; margin-left: auto;" data-cursor-element-id="cursor-el-532">GET</code>
                    </div>
                    <div style="margin-bottom: 6px;" data-cursor-element-id="cursor-el-533">
                        <div style="background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 4px; padding: 12px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;" data-cursor-element-id="cursor-el-534">
                <div style="width: 24px; height: 24px; background: #333; border-radius: 4px; display: flex; align-items: center; justify-content: center;" data-cursor-element-id="cursor-el-535">
                    <div style="width: 12px; height: 12px; background: #7cb342; border-radius: 2px;" data-cursor-element-id="cursor-el-536"></div>
                </div>
                <div style="flex: 1;" data-cursor-element-id="cursor-el-537">
                    <div style="width: 70%; height: 5px; background: #555; border-radius: 2px; margin-bottom: 3px;" data-cursor-element-id="cursor-el-538"></div>
                    <div style="width: 50%; height: 3px; background: #444; border-radius: 1px;" data-cursor-element-id="cursor-el-539"></div>
                </div>
            </div>
                    </div>
                    <p style="font-size: 10px; color: #888; margin: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" data-cursor-element-id="cursor-el-540">/studio/step/{step}</p>
                </div>
            </label>
        </div>
        
    </div>
    <div class="arbiter-component-actions" style="display: flex; gap: 8px; margin-top: 16px; padding-top: 16px; border-top: 1px solid #3a3a3a;" data-cursor-element-id="cursor-el-541">
        <button class="arbiter-btn arbiter-btn-secondary" onclick="selectAllArbiterComponents(false)" style="flex: 1; padding: 10px; background: #3a3a3a; color: #aaa; border: none; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer;" data-cursor-element-id="cursor-el-542">Tout désélectionner</button>
        <button class="arbiter-btn arbiter-btn-primary" onclick="validateArbiterSelection()" style="flex: 1; padding: 10px; background: #7cb342; color: white; border: none; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer;" data-cursor-element-id="cursor-el-543">Valider (8)</button>
    </div>
    <script data-cursor-element-id="cursor-el-544">
        function selectAllArbiterComponents(select) {
            document.querySelectorAll('#arbiter-components-panel .component-checkbox').forEach(chk => {
                chk.checked = select;
            });
        }
        function validateArbiterSelection() {
            const selected = Array.from(document.querySelectorAll('#arbiter-components-panel .component-checkbox:checked')).map(chk => chk.value);
            console.log('Composants ARBITER sélectionnés:', selected);
            if (window.navigateToStep4) {
                window.navigateToStep4();
            }
        }
    </script>
    </div>
                        </div>
                    </div>
                </div><!-- /frontend-arbiter-view -->
            </div><!-- /tab-frontend -->

            <!-- Deploy Tab -->
            <div id="tab-deploy" class="tab-content" data-cursor-element-id="cursor-el-545">
                <div class="coming-soon" data-cursor-element-id="cursor-el-546">
                    <div class="coming-soon-icon" data-cursor-element-id="cursor-el-547">🚀</div>
                    <div class="coming-soon-text" data-cursor-element-id="cursor-el-548">Deploy - Publication</div>
                    <p style="color: #bbb; margin-top: 8px; font-size: 13px;" data-cursor-element-id="cursor-el-549">Déployez votre application en production</p>
                </div>
            </div>
        </main>
    </div>

    <script data-cursor-element-id="cursor-el-550">
        // Récupérer le step depuis l'URL (paramètre ?step=N)
        const urlParams = new URLSearchParams(window.location.search);
        const currentStep = parseInt(urlParams.get('step')) || 1;

        // Mapping step → tab à activer
        // step 1-3 → Brainstorm (index 0)
        // step 4-9 → Frontend (index 2)
        function getTabIndexFromStep(step) {
            if (step >= 1 && step <= 3) return 0;  // Brainstorm
            if (step >= 4 && step <= 9) return 2;  // Frontend
            return 0;  // Default: Brainstorm
        }

        // Navigation client-side vers step 4 (préserve le contexte chatbox)
        function navigateToStep4() {
            // Changer l'URL sans recharger la page
            history.pushState({step: 4}, '', '/studio?step=4');
            // Activer le tab Frontend (index 2)
            const tabs = document.querySelectorAll('.tab');
            if (tabs[2]) {
                tabs[2].click();
            }
            // Afficher la section des composants dans ARBITER
            showArbiterComponentsSection();
            console.log('Navigation client-side → Step 4 (ARBITER avec composants)');
        }

        // Afficher la section des composants dans le panneau ARBITER
        function showArbiterComponentsSection() {
            const section = document.getElementById('arbiter-components-section');
            if (section) {
                section.style.display = 'block';
                // Déclencher le chargement HTMX si pas encore chargé
                const panel = document.getElementById('arbiter-components-panel');
                if (panel && !panel.querySelector('.arbiter-component-grid')) {
                    htmx.trigger(panel, 'load');
                }
            }
        }

        // Masquer la section des composants (retour étape 3 par exemple)
        function hideArbiterComponentsSection() {
            const section = document.getElementById('arbiter-components-section');
            if (section) {
                section.style.display = 'none';
            }
        }

        // Sélectionner/désélectionner tous les composants
        function selectAllComponents(select) {
            const checkboxes = document.querySelectorAll('.component-checkbox');
            checkboxes.forEach(chk => {
                chk.checked = select;
                const card = chk.closest('.component-card');
                if (card) {
                    card.classList.toggle('unselected', !select);
                }
            });
            updateValidateButton();
        }

        // Mettre à jour le compteur du bouton valider
        function updateValidateButton() {
            const checkboxes = document.querySelectorAll('.component-checkbox:checked');
            const btn = document.querySelector('.btn-validate-components');
            if (btn) {
                const count = checkboxes.length;
                btn.innerHTML = `<span class="btn-icon">🚀</span> Valider la sélection (${count} composant${count > 1 ? 's' : ''})`;
            }
        }

        // Valider la sélection de composants
        function validateComponentSelection() {
            const selected = [];
            document.querySelectorAll('.component-checkbox:checked').forEach(chk => {
                selected.push(chk.value);
            });
            console.log('Composants sélectionnés:', selected);
            // TODO: Envoyer au backend pour génération
            alert(`${selected.length} composants validés! Prochaine étape: génération du code.`);
        }

        // Gestion des checkboxes individuels
        document.addEventListener('change', function(e) {
            if (e.target.classList.contains('component-checkbox')) {
                const card = e.target.closest('.component-card');
                if (card) {
                    card.classList.toggle('unselected', !e.target.checked);
                }
                updateValidateButton();
            }
        });

        // Activer le bon tab et vue au chargement selon le step
        document.addEventListener('DOMContentLoaded', function() {
            const tabIndex = getTabIndexFromStep(currentStep);
            const tabs = document.querySelectorAll('.tab');
            if (tabs[tabIndex]) {
                tabs[tabIndex].click();
            }
            
            // ARBITER UI DYNAMIQUE: Afficher composants si step=4
            if (currentStep === 4) {
                showArbiterComponentsSection();
            } else {
                hideArbiterComponentsSection();
            }
            
            console.log('HomeOS Studio - Step:', currentStep, '→ Tab index:', tabIndex);
        });

        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', function() {
                // Update tab active state
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                this.classList.add('active');

                // Update content visibility
                const tabName = this.dataset.tab;
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById('tab-' + tabName).classList.add('active');
            });
        });

        // HTMX event logging
        document.body.addEventListener('htmx:afterRequest', function(evt) {
            console.log('HTMX afterRequest:', evt.detail.pathInfo.requestPath, evt.detail.successful ? 'OK' : 'FAIL');
        });

        document.body.addEventListener('htmx:responseError', function(evt) {
            console.error('HTMX error:', evt.detail);
        });

        // Sullivan chat - auto-scroll on new messages
        const chatContainer = document.getElementById('sullivan-chat');
        if (chatContainer) {
            const chatObserver = new MutationObserver(() => {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            });
            chatObserver.observe(chatContainer, { childList: true, subtree: true });
        }

        // ========== VALIDATION WORKFLOW FUNCTIONS ==========
        
        let validatedCorps = [];
        let currentCorpsIndex = 0;
        const allCorps = ['Brainstorm', 'Back', 'Front', 'Deploy'];
        
        // Valider le corps actuel
        function validateCurrentCorps() {
            const currentCorps = allCorps[currentCorpsIndex];
            validatedCorps.push(currentCorps);
            
            // Mettre à jour la progression
            document.getElementById('corps-progress').textContent = 
                `${validatedCorps.length}/${allCorps.length} corps validés`;
            document.getElementById('validated-corps-name').textContent = currentCorps;
            
            // Afficher l'anchor step 2
            const anchor = document.getElementById('anchor-frd-step2');
            anchor.classList.add('active');
            anchor.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            console.log(`✓ Corps validé: ${currentCorps}`);
            
            // Passer au corps suivant si disponible
            currentCorpsIndex++;
            if (currentCorpsIndex < allCorps.length) {
                setTimeout(() => {
                    alert(`Corps "${currentCorps}" validé!\nPassage au corps suivant: ${allCorps[currentCorpsIndex]}`);
                }, 500);
            } else {
                // Tous les corps validés
                setTimeout(() => {
                    alert('🎉 Tous les corps ont été validés!\nVous pouvez maintenant valider l\'UI.');
                    showFinalValidation();
                }, 500);
            }
        }
        
        // Valider pour passer à l'étape suivante
        function validateForNextStep() {
            const anchor = document.getElementById('anchor-frd-canvas');
            anchor.classList.add('active');
            anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            // Initialiser le canvas
            setTimeout(initFigmaCanvas, 600);
        }
        
        // Afficher la validation finale
        function showFinalValidation() {
            document.getElementById('ui-validation-panel').style.display = 'block';
        }
        
        // Aperçu réel du rendu
        function previewRealRender() {
            alert('👁️ Génération de l\'aperçu réel...\n(Cette fonctionnalité nécessite le backend)');
        }
        
        // Valider le mode construction
        function validateModeConstruction() {
            if (confirm('✓ Valider et remplacer l\'UI existant par cette version?')) {
                alert('✅ Mode Construction validé!\nL\'UI va être mise à jour.');
                // Redirection ou mise à jour de l'interface
                window.location.href = '/studio?step=5';
            }
        }
        
        // Annuler et retourner au step précédent
        function cancelAndReturn() {
            if (confirm('✗ Annuler les modifications et retourner au step précédent?')) {
                window.location.href = '/studio?step=3';
            }
        }
        
        // ========== CANVAS FIGMA FUNCTIONS ==========
        
        let canvas, ctx;
        let currentTool = 'select';
        let isDrawing = false;
        let startX, startY;
        
        function initFigmaCanvas() {
            canvas = document.getElementById('figma-canvas');
            if (!canvas) return;
            
            ctx = canvas.getContext('2d');
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            
            // Dessiner la grille
            drawGrid();
            
            // Event listeners
            canvas.addEventListener('mousedown', handleCanvasMouseDown);
            canvas.addEventListener('mousemove', handleCanvasMouseMove);
            canvas.addEventListener('mouseup', handleCanvasMouseUp);
            
            console.log('🎨 Canvas Figma initialisé');
        }
        
        function drawGrid() {
            const gridSize = 20;
            ctx.strokeStyle = '#f0f0f0';
            ctx.lineWidth = 1;
            
            for (let x = 0; x < canvas.width; x += gridSize) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }
            
            for (let y = 0; y < canvas.height; y += gridSize) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }
        }
        
        function handleCanvasMouseDown(e) {
            if (currentTool === 'select') return;
            
            isDrawing = true;
            const rect = canvas.getBoundingClientRect();
            startX = e.clientX - rect.left;
            startY = e.clientY - rect.top;
        }
        
        function handleCanvasMouseMove(e) {
            if (!isDrawing) return;
            
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Redessiner la grille
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawGrid();
            
            // Dessiner la forme en preview
            ctx.strokeStyle = '#8cc63f';
            ctx.lineWidth = 2;
            
            if (currentTool === 'rect') {
                ctx.strokeRect(startX, startY, x - startX, y - startY);
            } else if (currentTool === 'circle') {
                const radius = Math.sqrt(Math.pow(x - startX, 2) + Math.pow(y - startY, 2));
                ctx.beginPath();
                ctx.arc(startX, startY, radius, 0, Math.PI * 2);
                ctx.stroke();
            }
        }
        
        function handleCanvasMouseUp(e) {
            if (!isDrawing) return;
            isDrawing = false;
        }
        
        // Gestion des outils du canvas
        document.querySelectorAll('.canvas-tool-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.canvas-tool-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentTool = this.dataset.tool;
            });
        });
        
        // Gestion du tree drilldown
        document.querySelectorAll('.genome-tree-item').forEach(item => {
            item.addEventListener('click', function() {
                const toggle = this.querySelector('.tree-toggle');
                const children = this.nextElementSibling;
                
                if (children && children.classList.contains('genome-tree-children')) {
                    const isExpanded = toggle.textContent === '▼';
                    toggle.textContent = isExpanded ? '▶' : '▼';
                    children.style.display = isExpanded ? 'none' : 'block';
                }
            });
        });
    </script>

    <!-- Sullivan Agent Widget -->
    <script src="/js/sullivan-super-widget.js" data-cursor-element-id="cursor-el-551"></script>

<div data-cursor-element-id="cursor-el-552">
<div id="sullivan-super-widget" class="minimized" data-cursor-element-id="cursor-el-553">
  <div class="sullivan-header" onclick="window.SullivanWidget.toggle()" data-cursor-element-id="cursor-el-554">
    <div class="sullivan-avatar" data-cursor-element-id="cursor-el-555">🎨</div>
    <div class="sullivan-info" data-cursor-element-id="cursor-el-556">
      <h3 data-cursor-element-id="cursor-el-557">Sullivan</h3>
      <p data-cursor-element-id="cursor-el-558">Agent <span class="sullivan-badge" data-cursor-element-id="cursor-el-559">● AGENT MODE</span></p>
    </div>
    <div class="sullivan-controls" data-cursor-element-id="cursor-el-560">
      <button class="sullivan-btn" onclick="event.stopPropagation(); window.SullivanWidget.fullscreen()" title="Plein écran" data-cursor-element-id="cursor-el-561">⛶</button>
      <button class="sullivan-btn" onclick="event.stopPropagation(); window.SullivanWidget.toggle()" title="Fermer" data-cursor-element-id="cursor-el-562">−</button>
    </div>
  </div>

  <div id="sullivan-messages" class="sullivan-body" data-cursor-element-id="cursor-el-563">
    <div class="sullivan-message bot" data-cursor-element-id="cursor-el-564">
      <div class="sullivan-msg-avatar" data-cursor-element-id="cursor-el-565">🎨</div>
      <div class="sullivan-msg-content" data-cursor-element-id="cursor-el-566">
        Salut ! Je suis Sullivan en mode <strong data-cursor-element-id="cursor-el-567">AGENT</strong>. 🚀<br data-cursor-element-id="cursor-el-568"><br data-cursor-element-id="cursor-el-569">
        Je peux manipuler le DOM, générer du HTMX, lire/modifier le code.<br data-cursor-element-id="cursor-el-570">
        Session: <code data-cursor-element-id="cursor-el-571">70_ijvuh0u04</code>
      </div>
    </div>
  </div>

  <div id="sullivan-typing" class="sullivan-typing" data-cursor-element-id="cursor-el-572">
    <span data-cursor-element-id="cursor-el-573"></span><span data-cursor-element-id="cursor-el-574"></span><span data-cursor-element-id="cursor-el-575"></span>
  </div>

  <div class="sullivan-quick-actions" data-cursor-element-id="cursor-el-576">
    <button class="sullivan-quick-btn" onclick="window.SullivanWidget.quick('Analyse cette page')" data-cursor-element-id="cursor-el-577">🔍 Analyser</button>
    <button class="sullivan-quick-btn" onclick="window.SullivanWidget.quick('Génère HTMX')" data-cursor-element-id="cursor-el-578">⚡ HTMX</button>
    <button class="sullivan-quick-btn" onclick="window.SullivanWidget.quick('Modifie le style')" data-cursor-element-id="cursor-el-579">🎨 Styler</button>
    <button class="sullivan-quick-btn" onclick="window.SullivanWidget.quick('Debug')" data-cursor-element-id="cursor-el-580">🐛 Debug</button>
  </div>

  <div id="sullivan-tools" class="sullivan-tools" data-cursor-element-id="cursor-el-581">
    <span class="sullivan-tools-badge" data-cursor-element-id="cursor-el-582">⚡</span>
    <span id="sullivan-tools-text" data-cursor-element-id="cursor-el-583">Exécution...</span>
  </div>

  <div class="sullivan-input" data-cursor-element-id="cursor-el-584">
    <div class="sullivan-input-box" data-cursor-element-id="cursor-el-585">
      <textarea id="sullivan-input-text" class="sullivan-textarea" placeholder="Dis-moi ce que tu veux faire..." rows="1" data-cursor-element-id="cursor-el-586"></textarea>
      <button class="sullivan-send" id="sullivan-send-btn" data-cursor-element-id="cursor-el-587">➤</button>
    </div>
  </div>
</div></div><div data-cursor-element-id="cursor-el-588" style="position: fixed; border: 2px solid rgb(58, 150, 221); pointer-events: none; z-index: 2147483647; display: block; top: 0px; left: 0px; width: 718px; height: 410px;"></div><div data-cursor-element-id="cursor-el-589" style="position: fixed; background: rgb(58, 150, 221); color: white; padding: 2px 6px; font-size: 11px; font-family: system-ui, -apple-system, sans-serif; font-weight: 500; border-radius: 2px; pointer-events: none; z-index: 2147483647; white-space: nowrap; display: block; top: 0px; left: 0px;">body</div></body></html>