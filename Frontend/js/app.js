// Configuration API
const API_BASE_URL = 'http://127.0.0.1:8000';

// Vérifier la connectivité API au chargement
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            // Vérifier que la réponse est bien du JSON
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                try {
                    const data = await response.json();
                    console.log('✅ API Sullivan accessible:', data);
                    return true;
                } catch (parseError) {
                    // Si le parsing échoue, c'est qu'on a reçu du HTML
                    console.warn('⚠️ API retourne du HTML au lieu de JSON');
                    return false;
                }
            } else {
                console.warn('⚠️ API retourne du HTML au lieu de JSON');
                return false;
            }
        }
    } catch (error) {
        // Ne pas afficher l'erreur brute si c'est une erreur de parsing JSON
        if (error.message && error.message.includes('Unexpected token')) {
            console.warn('⚠️ API retourne du HTML au lieu de JSON');
        } else {
            console.warn('⚠️ API non accessible:', error.message || error);
        }
        return false;
    }
    return false;
}

// Éléments DOM
const chatArea = document.getElementById('chat-area');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const typingIndicator = document.getElementById('typing-indicator');

// État
let userId = 'default_user';
let messageHistory = [];
let isChatboxOpen = false;
const CHATBOX_STATE_KEY = 'chatbox_open';

// Éléments DOM pour toggle
const chatboxOverlay = document.getElementById('chatbox-overlay');
const chatboxMinimizedBar = document.getElementById('chatbox-minimized-bar');
const toggleChatBtn = document.getElementById('toggle-chat-btn');
const closeChatBtn = document.getElementById('close-chat-btn');

// Fonctions de gestion du toggle
function openChatbox() {
    if (chatboxOverlay && chatboxMinimizedBar) {
        chatboxOverlay.classList.remove('closed');
        chatboxOverlay.classList.add('open');
        chatboxMinimizedBar.classList.add('closed');
        isChatboxOpen = true;
        localStorage.setItem(CHATBOX_STATE_KEY, 'true');
        // Focus sur input après animation
        setTimeout(() => {
            if (messageInput) messageInput.focus();
        }, 300);
    }
}

function closeChatbox() {
    if (chatboxOverlay && chatboxMinimizedBar) {
        chatboxOverlay.classList.remove('open');
        chatboxOverlay.classList.add('closed');
        chatboxMinimizedBar.classList.remove('closed');
        isChatboxOpen = false;
        localStorage.setItem(CHATBOX_STATE_KEY, 'false');
    }
}

function toggleChatbox() {
    if (isChatboxOpen) {
        closeChatbox();
    } else {
        openChatbox();
    }
}

function initializeChatboxState() {
    const savedState = localStorage.getItem(CHATBOX_STATE_KEY);
    if (savedState === 'true') {
        openChatbox();
    } else {
        closeChatbox();
    }
}

// Initialisation
document.addEventListener('DOMContentLoaded', async () => {
    // Initialiser l'état de la chatbox (uniquement si overlay + barre minimisée présents, ex. index.html)
    if (chatboxOverlay && chatboxMinimizedBar) {
        initializeChatboxState();
    }
    
    // Event listeners pour toggle
    if (toggleChatBtn) {
        toggleChatBtn.addEventListener('click', toggleChatbox);
    }
    if (closeChatBtn) {
        closeChatBtn.addEventListener('click', closeChatbox);
    }
    // Fermeture via backdrop click
    if (chatboxOverlay) {
        chatboxOverlay.addEventListener('click', (e) => {
            if (e.target === chatboxOverlay) {
                closeChatbox();
            }
        });
    }
    
    // Vérifier connectivité API
    const apiAvailable = await checkAPIHealth();
    if (!apiAvailable) {
        addMessage('sullivan', `⚠️ <strong>API Sullivan non accessible</strong><br><br>Pour démarrer l'API FastAPI, exécutez dans un terminal :<br><br><code>cd /Users/francois-jeandazin/AETHERFLOW<br>source venv/bin/activate<br>python -m Backend.Prod.api</code><br><br>Ou utilisez :<br><code>uvicorn Backend.Prod.api:app --host 127.0.0.1 --port 8000</code>`, 'error');
    }
    
    // Charger historique depuis localStorage
    if (typeof loadHistory === 'function') loadHistory();
    
    // Event listeners (si présents, ex. studio.html en aside ou index.html)
    if (sendBtn) sendBtn.addEventListener('click', handleSendMessage);
    if (messageInput) messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            handleSendMessage();
        }
    });
    
    // Auto-resize textarea
    if (messageInput) {
        messageInput.addEventListener('input', () => {
            messageInput.style.height = 'auto';
            messageInput.style.height = messageInput.scrollHeight + 'px';
        });
        messageInput.focus();
    }
});

// Envoyer un message
async function handleSendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Désactiver input et bouton
    messageInput.disabled = true;
    sendBtn.disabled = true;
    
    // Afficher message utilisateur
    addMessage('user', message);
    
    // Vider input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Afficher typing indicator
    showTypingIndicator();
    
    try {
        // Détecter le type de requête
        let response;
        
        if (message.toLowerCase().includes('analyser backend') || message.toLowerCase().includes('dev mode')) {
            // Mode DEV : Analyse backend
            response = await handleDevMode(message);
        } else if (message.toLowerCase().includes('analyser design') || message.toLowerCase().includes('designer mode')) {
            // Mode DESIGNER : Analyse design
            response = await handleDesignerMode(message);
        } else {
            // Mode recherche/génération composant
            response = await handleComponentSearch(message);
        }
        
        // Cacher typing indicator
        hideTypingIndicator();
        
        // Afficher réponse Sullivan
        displaySullivanResponse(response);
        
    } catch (error) {
        hideTypingIndicator();
        let errorMsg = `❌ Erreur : ${error.message}`;
        
        // Vérifier différents types d'erreurs
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMsg = `❌ <strong>Impossible de se connecter à l'API Sullivan</strong><br><br>L'API FastAPI n'est pas démarrée ou n'est pas accessible sur ${API_BASE_URL}.<br><br>Pour démarrer l'API :<br><code>python -m Backend.Prod.api</code>`;
        } else if (error.message.includes('Unexpected token') || error.message.includes('attendu JSON')) {
            errorMsg = `❌ <strong>Erreur de communication avec l'API</strong><br><br>L'API retourne du HTML au lieu de JSON. Cela signifie probablement que le serveur HTTP simple est actif au lieu de l'API FastAPI.<br><br>Arrêtez le serveur HTTP simple et démarrez l'API FastAPI :<br><code>python -m Backend.Prod.api</code>`;
        }
        
        addMessage('sullivan', errorMsg, 'error');
        console.error('Error:', error);
    } finally {
        // Réactiver input et bouton
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

// Recherche/génération composant
async function handleComponentSearch(intent) {
    const response = await fetch(`${API_BASE_URL}/sullivan/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            intent: intent,
            user_id: userId
        })
    });
    
    // Vérifier le Content-Type AVANT de parser
    const contentType = response.headers.get('content-type') || '';
    
    if (!response.ok) {
        // Vérifier si la réponse est du JSON
        if (contentType.includes('application/json')) {
            try {
                const error = await response.json();
                throw new Error(error.detail || 'Erreur lors de la recherche');
            } catch (parseError) {
                // Si le parsing JSON échoue, c'est qu'on a reçu du HTML
                throw new Error('API retourne du HTML au lieu de JSON');
            }
        } else {
            // Réponse HTML ou autre format
            const text = await response.text();
            throw new Error(`Erreur HTTP ${response.status}: L'API retourne du HTML au lieu de JSON`);
        }
    }
    
    // Vérifier que la réponse est bien du JSON
    if (!contentType.includes('application/json')) {
        const text = await response.text();
        throw new Error('API retourne du HTML au lieu de JSON');
    }
    
    try {
        return await response.json();
    } catch (parseError) {
        // Si le parsing échoue malgré le Content-Type, c'est qu'on a reçu du HTML
        throw new Error('Erreur de parsing JSON : l\'API retourne du HTML');
    }
}

// Mode DEV : Analyse backend
async function handleDevMode(message) {
    // Extraire chemin backend depuis le message ou utiliser chemin par défaut
    const backendPathMatch = message.match(/backend[:\s]+(.+)/i);
    const backendPath = backendPathMatch ? backendPathMatch[1].trim() : 'Backend/Prod';
    
    const response = await fetch(`${API_BASE_URL}/sullivan/dev/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            backend_path: backendPath,
            output_path: null,
            analyze_only: false,
            non_interactive: true
        })
    });
    
    // Vérifier le Content-Type AVANT de parser
    const contentType = response.headers.get('content-type') || '';
    
    if (!response.ok) {
        if (contentType.includes('application/json')) {
            try {
                const error = await response.json();
                throw new Error(error.detail || 'Erreur lors de l\'analyse');
            } catch (parseError) {
                throw new Error('API retourne du HTML au lieu de JSON');
            }
        } else {
            throw new Error(`Erreur HTTP ${response.status}: L'API retourne du HTML au lieu de JSON`);
        }
    }
    
    if (!contentType.includes('application/json')) {
        throw new Error('API retourne du HTML au lieu de JSON');
    }
    
    try {
        return await response.json();
    } catch (parseError) {
        throw new Error('Erreur de parsing JSON : l\'API retourne du HTML');
    }
}

// Mode DESIGNER : Analyse design
async function handleDesignerMode(message) {
    // Extraire chemin design depuis le message
    const designPathMatch = message.match(/design[:\s]+(.+)/i);
    if (!designPathMatch) {
        throw new Error('Veuillez spécifier le chemin vers le fichier design (ex: design: path/to/design.png)');
    }
    
    const designPath = designPathMatch[1].trim();
    
    const response = await fetch(`${API_BASE_URL}/sullivan/designer/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            design_path: designPath,
            output_path: null,
            non_interactive: true
        })
    });
    
    // Vérifier le Content-Type AVANT de parser
    const contentType = response.headers.get('content-type') || '';
    
    if (!response.ok) {
        if (contentType.includes('application/json')) {
            try {
                const error = await response.json();
                throw new Error(error.detail || 'Erreur lors de l\'analyse');
            } catch (parseError) {
                throw new Error('API retourne du HTML au lieu de JSON');
            }
        } else {
            throw new Error(`Erreur HTTP ${response.status}: L'API retourne du HTML au lieu de JSON`);
        }
    }
    
    if (!contentType.includes('application/json')) {
        throw new Error('API retourne du HTML au lieu de JSON');
    }
    
    try {
        return await response.json();
    } catch (parseError) {
        throw new Error('Erreur de parsing JSON : l\'API retourne du HTML');
    }
}

// Afficher réponse Sullivan
function displaySullivanResponse(data) {
    if (data.success && data.component) {
        // Réponse avec composant
        const component = data.component;
        const foundIn = data.found_in || 'generated';
        
        let html = `<div class="component-card">
            <h4>${escapeHtml(component.name)}</h4>
            <p><strong>Source :</strong> ${foundIn === 'local_cache' ? 'Cache Local' : foundIn === 'elite_library' ? 'Elite Library' : 'Généré'}</p>
            <div class="scores-grid">
                <div class="score-item">
                    <span class="score-label">Score Sullivan</span>
                    <span class="score-value">${component.sullivan_score?.toFixed(1) || 'N/A'}</span>
                </div>
                <div class="score-item">
                    <span class="score-label">Performance</span>
                    <span class="score-value">${component.performance_score || 'N/A'}</span>
                </div>
                <div class="score-item">
                    <span class="score-label">Accessibilité</span>
                    <span class="score-value">${component.accessibility_score || 'N/A'}</span>
                </div>
                <div class="score-item">
                    <span class="score-label">Écologie</span>
                    <span class="score-value">${component.ecology_score || 'N/A'}</span>
                </div>
                <div class="score-item">
                    <span class="score-label">Validation</span>
                    <span class="score-value">${component.validation_score || 'N/A'}</span>
                </div>
            </div>
            <p style="margin-top: 10px;"><strong>Taille :</strong> ${component.size_kb || 'N/A'} KB</p>
        </div>`;
        
        addMessage('sullivan', html);
        
    } else if (data.success && data.global_function) {
        // Réponse DevMode : Analyse backend
        const gf = data.global_function;
        let html = `<div class="component-card">
            <h4>📊 Analyse Backend Complétée</h4>
            <p><strong>Type de produit :</strong> ${gf.product_type || 'N/A'}</p>
            <p><strong>Acteurs :</strong> ${gf.actors?.join(', ') || 'N/A'}</p>
            <p><strong>Flux métier :</strong> ${gf.business_flows?.join(', ') || 'N/A'}</p>
            <p><strong>Cas d'usage :</strong> ${gf.use_cases?.join(', ') || 'N/A'}</p>
        </div>`;
        
        if (data.frontend_structure) {
            html += `<p style="margin-top: 10px;">✅ Structure frontend générée avec succès !</p>`;
        }
        
        addMessage('sullivan', html);
        
    } else if (data.success && data.design_structure) {
        // Réponse DesignerMode : Analyse design
        let html = `<div class="component-card">
            <h4>🎨 Analyse Design Complétée</h4>
            <p>✅ Structure design extraite avec succès !</p>
        </div>`;
        
        if (data.frontend_structure) {
            html += `<p style="margin-top: 10px;">✅ Structure frontend générée !</p>`;
        }
        
        addMessage('sullivan', html);
        
    } else {
        // Réponse générique
        addMessage('sullivan', data.message || 'Traitement complété avec succès.');
    }
}

// Ajouter un message au chat
function addMessage(sender, content, type = 'normal') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    if (type === 'error') {
        messageContent.className += ' error-message';
    }
    
    const messageText = document.createElement('div');
    messageText.className = 'message-text';
    messageText.innerHTML = content;
    
    const messageTime = document.createElement('div');
    messageTime.className = 'message-time';
    messageTime.textContent = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    
    messageContent.appendChild(messageText);
    messageContent.appendChild(messageTime);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    
    // Supprimer welcome message si présent
    const welcomeMsg = chatArea.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    chatArea.appendChild(messageDiv);
    
    // Scroll vers le bas
    chatArea.scrollTop = chatArea.scrollHeight;
    
    // Sauvegarder dans historique
    messageHistory.push({ sender, content, timestamp: new Date() });
    saveHistory();
}

// Afficher typing indicator
function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    chatArea.scrollTop = chatArea.scrollHeight;
}

// Cacher typing indicator
function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

// Sauvegarder historique
function saveHistory() {
    try {
        localStorage.setItem('sullivan_chat_history', JSON.stringify(messageHistory));
    } catch (e) {
        console.warn('Failed to save history:', e);
    }
}

// Charger historique
function loadHistory() {
    // Désactivé : ne plus restaurer automatiquement les anciens messages
    // L'utilisateur peut toujours utiliser le localStorage pour sauvegarder manuellement si besoin
    try {
        // Ne pas charger automatiquement l'historique à chaque rechargement
        // Pour vider l'historique : localStorage.removeItem('sullivan_chat_history')
        const saved = localStorage.getItem('sullivan_chat_history');
        if (saved) {
            // Ne pas restaurer automatiquement, mais garder en mémoire pour la session
            messageHistory = JSON.parse(saved);
            // Ne pas afficher les anciens messages
        } else {
            messageHistory = [];
        }
    } catch (e) {
        console.warn('Failed to load history:', e);
        messageHistory = [];
    }
}

// Échapper HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
