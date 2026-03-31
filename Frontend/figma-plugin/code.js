// AetherFlow Figma Bridge
figma.showUI(__html__, { width: 320, height: 420 });

// Initial scan of top-level frames
function scanFrames() {
    const frames = figma.currentPage.children
        .filter(node => node.type === "FRAME" || node.type === "GROUP")
        .map(node => ({ id: node.id, name: node.name }));
    figma.ui.postMessage({ type: 'frames-list', frames });
}

scanFrames();

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'export-svg' || msg.type === 'export-multi-svg') {
        const targetIds = msg.ids || (figma.currentPage.selection.length > 0 ? [figma.currentPage.selection[0].id] : []);
        
        if (targetIds.length === 0) {
            figma.notify('sélectionnez au moins une frame.');
            figma.ui.postMessage({ type: 'svg-ready', error: 'No selection' });
            return;
        }

        try {
            let exportedCount = 0;
            for (const id of targetIds) {
                const node = figma.getNodeById(id);
                if (!node || (node.type !== "FRAME" && node.type !== "GROUP")) continue;

                const svgBytes = await node.exportAsync({ format: 'SVG' });
                let svgString = '';
                const chunk = 8192;
                for (let i = 0; i < svgBytes.length; i += chunk) {
                    svgString += String.fromCharCode.apply(null, svgBytes.subarray(i, i + chunk));
                }
                figma.ui.postMessage({ type: 'svg-ready', svg: svgString, name: node.name, isLast: (exportedCount === targetIds.length - 1) });
                exportedCount++;
            }
            
            figma.notify(`${exportedCount} écran(s) envoyé(s) à HoméOS.`);
        } catch (err) {
            figma.notify('export SVG échoué — voir console.');
            console.error(err);
        }
        return;
    }

    if (msg.type !== 'import-manifest') return;

    try {
        const manifest = msg.manifest;
        const source = msg.source || "Unknown";

        // Normalize: Blueprint (v1) = .components (object), Reality (v2) = .elements (array)
        let items = [];
        if (manifest.elements && Array.isArray(manifest.elements)) {
            items = manifest.elements;
        } else if (manifest.components) {
            items = Object.entries(manifest.components).map(([id, data]) => Object.assign({ id }, data));
        }

        if (items.length === 0) {
            figma.notify('Aucun élément trouvé dans le manifest.');
            figma.ui.postMessage({ type: 'import-done', count: 0 });
            return;
        }

        figma.notify(`Import de ${items.length} éléments depuis ${source}...`);

        // Load font once before the loop
        await figma.loadFontAsync({ family: "Inter", style: "Regular" });

        // Create a parent frame to group all imported elements
        const container = figma.createFrame();
        container.name = `[AetherFlow] ${source}`;
        container.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }];

        // Compute bounding box for container sizing
        let maxX = 0, maxY = 0;
        for (const d of items) {
            const right = (d.x || 0) + (d.width || d.w || 100);
            const bottom = (d.y || 0) + (d.height || d.h || 100);
            if (right > maxX) maxX = right;
            if (bottom > maxY) maxY = bottom;
        }
        container.resize(Math.max(maxX, 100), Math.max(maxY, 100));
        container.x = 0;
        container.y = 0;

        let count = 0;

        for (const data of items) {
            const x = data.x || 0;
            const y = data.y || 0;
            const w = Math.max(data.width || data.w || 100, 1);
            const h = Math.max(data.height || data.h || 100, 1);

            const frame = figma.createFrame();
            frame.name = `[${data.id}] ${data.name || ''}`;
            frame.x = x;
            frame.y = y;
            frame.resize(w, h);
            frame.clipsContent = true;

            if (data.svg) {
                // Blueprint: SVG import
                try {
                    frame.fills = [];
                    const svgNode = figma.createNodeFromSvg(data.svg);
                    svgNode.resize(w, h);
                    svgNode.x = 0;
                    svgNode.y = 0;
                    for (const child of [...svgNode.children]) {
                        frame.appendChild(child);
                    }
                    svgNode.remove();
                } catch (e) {
                    console.error('SVG error for ' + data.id, e);
                    frame.fills = [{ type: 'SOLID', color: { r: 0.9, g: 0.9, b: 0.9 } }];
                }
            } else {
                // Reality: colored frame + label
                const bgColor = (data.style && data.style.backgroundColor) || "rgba(200, 200, 200, 0.3)";
                const colorMatch = bgColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);

                if (colorMatch) {
                    const alpha = colorMatch[4] !== undefined ? parseFloat(colorMatch[4]) : 1;
                    frame.fills = [{
                        type: 'SOLID',
                        color: {
                            r: parseInt(colorMatch[1]) / 255,
                            g: parseInt(colorMatch[2]) / 255,
                            b: parseInt(colorMatch[3]) / 255
                        },
                        opacity: alpha < 0.1 ? 0.15 : alpha  // minimum opacity so frame is visible
                    }];
                } else {
                    frame.fills = [{ type: 'SOLID', color: { r: 0.95, g: 0.95, b: 0.95 } }];
                }

                frame.strokeWeight = 1;
                frame.strokes = [{ type: 'SOLID', color: { r: 0.63, g: 0.42, b: 1 }, opacity: 0.4 }];
                frame.cornerRadius = 4;

                try {
                    const text = figma.createText();
                    text.characters = (data.text || data.name || data.id).replace(/\n/g, ' ').substring(0, 80);
                    text.fontSize = Math.max(8, Math.floor(Math.min(11, h / 3)));
                    text.resize(Math.max(w - 4, 1), Math.max(h - 4, 1));
                    text.x = 2;
                    text.y = 2;
                    frame.appendChild(text);
                } catch (e) {
                    console.error('Text error for ' + data.id, e);
                }
            }

            container.appendChild(frame);
            count++;
        }

        // Select and zoom to the imported container
        figma.currentPage.selection = [container];
        figma.viewport.scrollAndZoomIntoView([container]);

        figma.ui.postMessage({ type: 'import-done', count });
        figma.notify(`${count} éléments importés depuis ${source}.`);

    } catch (err) {
        console.error('Import failed:', err);
        figma.notify('Erreur import : ' + (err.message || err));
        figma.ui.postMessage({ type: 'import-done', count: 0 });
    }
};
