
// ==================== SULLIVAN CUSTOM INJECTION ====================
// Ce script est injecté dynamiquement par le serveur Sullivan v7.0 (Restoration Accord)

(function () {
    console.log('💉 Injection Sullivan active - Initialisation du Widget de Diagnostic');

    // Création du widget
    const widget = document.createElement('div');
    widget.id = 'sullivan-diagnostic-widget';
    widget.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(10, 10, 10, 0.9);
        border: 1px solid #7aca6a;
        border-radius: 8px;
        padding: 15px;
        color: white;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        z-index: 10000;
        display: flex;
        flex-direction: column;
        gap: 10px;
        backdrop-filter: blur(5px);
        min-width: 200px;
        animation: slideIn 0.5s ease-out;
    `;

    widget.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #333; padding-bottom: 8px; margin-bottom: 5px;">
            <span style="font-size: 1.2rem;">🧬</span>
            <strong style="color: #7aca6a;">Sullivan Inspector</strong>
        </div>
        <div id="inspector-stats" style="font-size: 0.85rem; color: #aaa;">
            Etat: <span style="color: #7aca6a;">Connecté</span><br>
            Engine: <span id="engine-status">Recherche...</span>
        </div>
        <button id="btn-inspect-engine" style="
            background: #7aca6a;
            color: black;
            border: none;
            padding: 8px;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s;
        ">Interroger l'Engine</button>
    `;

    document.body.appendChild(widget);

    // Style pour l'animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(110%); }
            to { transform: translateX(0); }
        }
    `;
    document.head.appendChild(style);

    // Logique d'interrogation
    setTimeout(() => {
        const engineStatus = document.getElementById('engine-status');
        if (window.genomeEngine) {
            engineStatus.textContent = "Prêt (N0-Phase)";
            engineStatus.style.color = "#7aca6a";
        } else {
            engineStatus.textContent = "Non trouvé";
            engineStatus.style.color = "#ff4d4d";
        }
    }, 1000);

    document.getElementById('btn-inspect-engine').addEventListener('click', () => {
        if (window.genomeEngine) {
            const count = window.genomeEngine.getSelectedComponents().length;
            alert(`🔍 Sullivan Engine Report:\nComposants sélectionnés : ${count}\nAccord constitutionnel : OK`);
        } else {
            alert('❌ Erreur: GenomeEngine introuvable.');
        }
    });

})();
