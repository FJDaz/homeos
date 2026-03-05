// AetherFlow Figma Bridge Code
figma.showUI(__html__, { width: 300, height: 400 });

figma.ui.onmessage = async (msg) => {
    if (msg.type === 'import-manifest') {
        const manifest = msg.manifest;
        const components = manifest.components;
        let count = 0;

        for (const id in components) {
            const data = components[id];

            const frame = figma.createFrame();
            frame.name = `[${id}] ${data.name || ''}`;
            frame.x = data.x;
            frame.y = data.y;
            frame.resize(data.w, data.h);

            // Clear fills to make it transparent (acting as a container for the SVG)
            frame.fills = [];
            frame.clipsContent = true;

            if (data.svg) {
                try {
                    const svgNode = figma.createNodeFromSvg(data.svg);
                    // Resize the imported SVG group to match the frame dimensions
                    // This ensures the scale calculated by AetherFlow is respected
                    svgNode.resize(data.w, data.h);
                    svgNode.x = 0;
                    svgNode.y = 0;
                    frame.appendChild(svgNode);
                } catch (e) {
                    console.error(`Failed to import SVG for ${id}`, e);
                }
            } else {
                // Fallback styling if no SVG is present
                frame.fills = [{ type: 'SOLID', color: { r: 0.9, g: 0.9, b: 0.9 } }];
                const text = figma.createText();
                await figma.loadFontAsync({ family: "Inter", style: "Regular" });
                text.characters = data.name || id;
                text.fontSize = 12;
                frame.appendChild(text);
            }

            count++;
        }

        figma.ui.postMessage({ type: 'import-done', count });
        figma.notify(`Imported ${count} visual components from AetherFlow.`);
    }
};
