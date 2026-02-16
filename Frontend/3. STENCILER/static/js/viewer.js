/**
 * VIEWER JS - Version 3.0
 * Rôle : Manipulation DOM, événements, interactions utilisateur
 * Conformité : Article 5 - Système de Rendu
 */

// Mapping des tabs vers les corps
const tabMapping = {
    'all': 'all',
    'brs': 'brainstorm',
    'bkd': 'backend',
    'frd': 'frontend',
    'dpl': 'deploy'
};

function switchTab(element, tab) {
    if (typeof tab !== 'string' || !tabMapping[tab]) {
        console.warn('⚠️ Paramètre tab invalide - Ignoré');
        return;
    }

    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    element.classList.add('active');

    const corpsFilter = tabMapping[tab];
    const cards = document.querySelectorAll('.comp-card');

    cards.forEach(card => {
        if (corpsFilter === 'all' || card.dataset.corps === corpsFilter) {
            card.classList.remove('hidden');
        } else {
            card.classList.add('hidden');
        }
    });

    updateValidateButton();
}

function toggleSection(header) {
    const arrow = header.querySelector('.wingding-arrow');
    const content = header.nextElementSibling;

    if (arrow) arrow.classList.toggle('collapsed');
    if (content) content.classList.toggle('collapsed');
}

function toggleAll(source) {
    const visibleCards = document.querySelectorAll('.comp-card:not(.hidden)');
    visibleCards.forEach(card => {
        const checkbox = card.querySelector('.comp-checkbox');
        if (checkbox) checkbox.checked = source.checked;
    });
    updateValidateButton();
}

function updateValidateButton() {
    const count = document.querySelectorAll('.comp-checkbox:checked').length;
    const btn = document.getElementById('validate-btn');
    if (btn) {
        btn.innerHTML = 'Valider (' + count + ')';
        btn.disabled = count === 0;
    }
}

function toggleCheckbox(id) {
    const cb = document.getElementById(id);
    if (cb) {
        cb.checked = !cb.checked;
        updateValidateButton();
    }
}

function scrollToStyleChoice() {
    const styleSection = document.getElementById('section-style-choice');
    if (styleSection) {
        styleSection.style.display = 'block';
        setTimeout(() => {
            styleSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }, 100);
    }
}

function handleFileUpload(file) {
    console.log('Fichier uploadé:', file.name);
    alert(`Maquette "${file.name}" uploadée !\nAnalyse Gemini Vision à implémenter côté backend...`);
}

function initializeStats() {
    const statBoxes = document.querySelectorAll('.stat-box');
    statBoxes.forEach(box => {
        box.addEventListener('click', () => {
            box.style.transform = 'scale(0.98)';
            setTimeout(() => {
                box.style.transform = '';
            }, 150);
        });
    });
}

// Initialisation globale
document.addEventListener('DOMContentLoaded', () => {
    // Initialiser les composants
    initializeStats();

    // Gestion upload de fichier
    const uploadZone = document.getElementById('upload-zone');
    const fileInput = document.getElementById('file-input');

    if (uploadZone && fileInput) {
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.style.borderColor = '#7aca6a';
            uploadZone.style.background = '#f0fdf4';
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.style.borderColor = '#cbd5e1';
            uploadZone.style.background = 'transparent';
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }

    // Gestion sélection de style
    document.querySelectorAll('.style-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.style-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');

            const selectedStyle = card.dataset.style;
            localStorage.setItem('aetherflow_selected_style', selectedStyle);
            localStorage.setItem('aetherflow_timestamp', Date.now().toString());

            window.location.href = '/stenciler';
        });
    });
});