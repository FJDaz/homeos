// DEBUG VERSION - Stenciler JS

console.log('=== STENCILER DEBUG ===');

let tarmacCanvas = null;
let mockCorps = [];

// 1. Charger mocks
document.addEventListener('DOMContentLoaded', async function() {
    console.log('1. DOM chargé');
    
    try {
        const response = await fetch('/static/4_corps_preview.json');
        console.log('2. Fetch response:', response.status);
        
        const data = await response.json();
        mockCorps = data.corps;
        console.log('3. Mocks chargés:', mockCorps.length, 'corps');
        
        renderPreviews();
        initCanvas();
        initDragDrop();
        
    } catch (e) {
        console.error('ERREUR chargement:', e);
    }
});

function renderPreviews() {
    console.log('4. Rendu previews');
    const band = document.getElementById('preview-band');
    if (!band) {
        console.error('preview-band non trouvé!');
        return;
    }
    
    band.innerHTML = '';
    mockCorps.forEach(corps => {
        const div = document.createElement('div');
        div.className = `preview-card ${corps.id.replace('n0_', '')}`;
        div.draggable = true;
        div.innerHTML = `
            <span class="name">${corps.name}</span>
            <span class="count">${corps.organes_count} organes</span>
        `;
        
        div.addEventListener('dragstart', (e) => {
            console.log('DRAG START:', corps.id);
            e.dataTransfer.setData('corpsId', corps.id);
            e.dataTransfer.effectAllowed = 'copy';
            div.style.opacity = '0.5';
        });
        
        div.addEventListener('dragend', () => {
            div.style.opacity = '1';
        });
        
        band.appendChild(div);
    });
}

function initCanvas() {
    console.log('5. Init canvas');
    const canvasEl = document.getElementById('tarmac-canvas');
    const container = document.getElementById('canvas-zone');
    
    if (!canvasEl) {
        console.error('tarmac-canvas non trouvé!');
        return;
    }
    if (!container) {
        console.error('canvas-zone non trouvé!');
        return;
    }
    if (typeof fabric === 'undefined') {
        console.error('Fabric.js non chargé!');
        return;
    }
    
    console.log('Canvas el:', canvasEl);
    console.log('Container:', container);
    console.log('Container size:', container.clientWidth, 'x', container.clientHeight);
    
    tarmacCanvas = new fabric.Canvas('tarmac-canvas', {
        width: container.clientWidth,
        height: container.clientHeight,
        backgroundColor: 'transparent'
    });
    
    console.log('Canvas Fabric créé:', tarmacCanvas);
}

function initDragDrop() {
    console.log('6. Init drag & drop');
    const zone = document.getElementById('canvas-zone');
    
    if (!zone) {
        console.error('canvas-zone non trouvé pour D&D!');
        return;
    }
    
    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        zone.style.borderColor = 'var(--accent-vert)';
        console.log('DRAG OVER');
    });
    
    zone.addEventListener('dragleave', () => {
        zone.style.borderColor = '';
    });
    
    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        console.log('DROP!');
        zone.style.borderColor = '';
        
        const corpsId = e.dataTransfer.getData('corpsId');
        console.log('Corps ID:', corpsId);
        
        if (!corpsId) {
            console.error('Pas de corpsId dans dataTransfer');
            return;
        }
        
        const rect = zone.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        console.log('Position:', x, y);
        
        addToCanvas(corpsId, x, y);
    });
}

function addToCanvas(corpsId, x, y) {
    console.log('7. Ajout au canvas:', corpsId, 'à', x, y);
    
    if (!tarmacCanvas) {
        console.error('Canvas non initialisé!');
        return;
    }
    
    const corps = mockCorps.find(c => c.id === corpsId);
    if (!corps) {
        console.error('Corps non trouvé:', corpsId);
        return;
    }
    
    console.log('Corps trouvé:', corps.name);
    
    // Créer rectangle
    const rect = new fabric.Rect({
        left: x - 90,
        top: y - 60,
        width: 180,
        height: 120,
        fill: '#1a1a1a',
        stroke: corps.color,
        strokeWidth: 2,
        rx: 8
    });
    
    const text = new fabric.Text(corps.name, {
        left: x - 78,
        top: y - 48,
        fontSize: 13,
        fill: '#e5e5e5',
        fontFamily: 'Inter, sans-serif'
    });
    
    const sub = new fabric.Text(`${corps.organes_count} organes`, {
        left: x - 78,
        top: y - 28,
        fontSize: 10,
        fill: '#888888'
    });
    
    tarmacCanvas.add(rect);
    tarmacCanvas.add(text);
    tarmacCanvas.add(sub);
    tarmacCanvas.renderAll();
    
    console.log('8. Objet ajouté!');
    
    // Cacher placeholder
    const placeholder = document.getElementById('canvas-placeholder');
    if (placeholder) placeholder.style.display = 'none';
}
