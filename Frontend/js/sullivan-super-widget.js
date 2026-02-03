/**
 * SUPER WIDGET SULLIVAN - AGENT MODE
 * Widget flottant avec z-index max au-dessus du Studio.
 * Session persistée dans localStorage.
 */

(function() {
  'use strict';

  console.log('[Sullivan] ===========================================');
  console.log('[Sullivan] SCRIPT CHARGÉ - Début initialisation');
  console.log('[Sullivan] ===========================================');

  // Éviter double init
  if (window.SullivanWidgetLoaded) {
    console.log('[Sullivan] Déjà chargé, skip');
    return;
  }
  window.SullivanWidgetLoaded = true;

  // Helpers localStorage pour session persistante
  const STORAGE_KEY = 'sullivan_session_v2';

  function getStoredSession() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const data = JSON.parse(stored);
        // Session valide 24h
        const age = Date.now() - (data.timestamp || 0);
        if (age < 24 * 60 * 60 * 1000 && data.sessionId) {
          console.log('[Sullivan] Session restaurée depuis localStorage:', data.sessionId);
          return data.sessionId;
        }
      }
    } catch (e) {
      console.warn('[Sullivan] Erreur lecture localStorage:', e);
    }
    return null;
  }

  function saveSession(sessionId) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        sessionId: sessionId,
        timestamp: Date.now()
      }));
      console.log('[Sullivan] Session sauvegardée:', sessionId);
    } catch (e) {
      console.warn('[Sullivan] Erreur écriture localStorage:', e);
    }
  }

  // Générer ou récupérer session
  let sessionId = getStoredSession();
  if (!sessionId) {
    sessionId = 'studio_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    saveSession(sessionId);
    console.log('[Sullivan] Nouvelle session créée:', sessionId);
  }

  // Configuration
  const CONFIG = {
    apiUrl: '/sullivan/agent/chat',
    sessionId: sessionId,
    userId: 'studio-user',
    step: 9,
    mode: 'agent',
  };

  console.log('[Sullivan] API URL:', CONFIG.apiUrl);
  console.log('[Sullivan] Session ID:', CONFIG.sessionId);

  // Styles CSS
  const STYLES = `
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
  background: #6366f1;
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
  background: #6366f1;
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
  border-color: #6366f1;
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
  background: #6366f1;
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
  border-color: #6366f1;
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
  background: #6366f1;
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
  background: #4f46e5;
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
  background: linear-gradient(135deg, #6366f1, #4f46e5);
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
`;

  // Template HTML
  const HTML = `
<div id="sullivan-super-widget" class="minimized">
  <div class="sullivan-header" onclick="window.SullivanWidget.toggle()">
    <div class="sullivan-avatar">🎨</div>
    <div class="sullivan-info">
      <h3>Sullivan</h3>
      <p>Agent <span class="sullivan-badge">● AGENT MODE</span></p>
    </div>
    <div class="sullivan-controls">
      <button class="sullivan-btn" onclick="event.stopPropagation(); window.SullivanWidget.fullscreen()" title="Plein écran">⛶</button>
      <button class="sullivan-btn" onclick="event.stopPropagation(); window.SullivanWidget.toggle()" title="Fermer">−</button>
    </div>
  </div>

  <div id="sullivan-messages" class="sullivan-body">
    <div class="sullivan-message bot">
      <div class="sullivan-msg-avatar">🎨</div>
      <div class="sullivan-msg-content">
        Salut ! Je suis Sullivan en mode <strong>AGENT</strong>. 🚀<br><br>
        Je peux manipuler le DOM, générer du HTMX, lire/modifier le code.<br>
        Session: <code>${CONFIG.sessionId.slice(-12)}</code>
      </div>
    </div>
  </div>

  <div id="sullivan-typing" class="sullivan-typing">
    <span></span><span></span><span></span>
  </div>

  <div class="sullivan-quick-actions">
    <button class="sullivan-quick-btn" onclick="window.SullivanWidget.quick('Analyse cette page')">🔍 Analyser</button>
    <button class="sullivan-quick-btn" onclick="window.SullivanWidget.quick('Génère HTMX')">⚡ HTMX</button>
    <button class="sullivan-quick-btn" onclick="window.SullivanWidget.quick('Modifie le style')">🎨 Styler</button>
    <button class="sullivan-quick-btn" onclick="window.SullivanWidget.quick('Debug')">🐛 Debug</button>
  </div>

  <div id="sullivan-tools" class="sullivan-tools">
    <span class="sullivan-tools-badge">⚡</span>
    <span id="sullivan-tools-text">Exécution...</span>
  </div>

  <div class="sullivan-input">
    <div class="sullivan-input-box">
      <textarea id="sullivan-input-text" class="sullivan-textarea"
        placeholder="Dis-moi ce que tu veux faire..." rows="1"></textarea>
      <button class="sullivan-send" id="sullivan-send-btn">➤</button>
    </div>
  </div>
</div>

<button id="sullivan-toggle" class="visible" onclick="window.SullivanWidget.toggle()">🎨</button>
`;

  // Classe du widget
  class SullivanWidgetClass {
    constructor() {
      console.log('[Sullivan] Initialisation...');
      this.isOpen = false;
      this.isTyping = false;
      this.isFullscreen = false;
      this.elements = {};
      
      // === PLAN MANAGEMENT STATE ===
      this.planState = {
        currentPlan: null,
        currentStepIndex: 0,
        logs: [],
        startTime: null
      };
      
      this.init();
    }

    init() {
      try {
        // Injecter les styles
        const styleEl = document.createElement('style');
        styleEl.textContent = STYLES;
        document.head.appendChild(styleEl);
        console.log('[Sullivan] Styles injectés');

        // Injecter le HTML
        const container = document.createElement('div');
        container.innerHTML = HTML;
        document.body.appendChild(container);
        console.log('[Sullivan] HTML injecté');

        // Récupérer les éléments
        this.elements = {
          widget: document.getElementById('sullivan-super-widget'),
          toggle: document.getElementById('sullivan-toggle'),
          messages: document.getElementById('sullivan-messages'),
          input: document.getElementById('sullivan-input-text'),
          sendBtn: document.getElementById('sullivan-send-btn'),
          typing: document.getElementById('sullivan-typing'),
          tools: document.getElementById('sullivan-tools'),
          toolsText: document.getElementById('sullivan-tools-text'),
        };

        console.log('[Sullivan] Éléments:', Object.keys(this.elements));

        // Bind events
        this.bindEvents();

        console.log('[Sullivan] Widget initialisé avec succès !');
      } catch (e) {
        console.error('[Sullivan] Erreur initialisation:', e);
      }
    }

    bindEvents() {
      // Bouton envoyer
      this.elements.sendBtn.addEventListener('click', () => this.send());

      // Touche Entrée
      this.elements.input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.send();
        }
      });

      // Auto-resize
      this.elements.input.addEventListener('input', () => {
        this.elements.input.style.height = 'auto';
        this.elements.input.style.height = Math.min(this.elements.input.scrollHeight, 120) + 'px';
      });
    }

    toggle() {
      this.isOpen = !this.isOpen;
      this.elements.widget.classList.toggle('minimized', !this.isOpen);
      this.elements.toggle.classList.toggle('visible', !this.isOpen);

      if (this.isOpen) {
        setTimeout(() => this.elements.input.focus(), 100);
      }
    }

    fullscreen() {
      this.isFullscreen = !this.isFullscreen;
      this.elements.widget.classList.toggle('fullscreen', this.isFullscreen);
    }

    quick(text) {
      this.elements.input.value = text;
      this.send();
    }

    async send() {
      const text = this.elements.input.value.trim();
      if (!text || this.isTyping) {
        console.log('[Sullivan] Envoi bloqué - texte vide ou déjà en train de taper');
        return;
      }

      console.log('[Sullivan] Envoi message:', text);

      // Ajouter message utilisateur
      this.addMessage('user', text);
      this.elements.input.value = '';
      this.elements.input.style.height = 'auto';

      // Show typing
      this.showTyping(true);
      this.isTyping = true;
      this.elements.sendBtn.disabled = true;

      try {
        // Construire l'URL complète
        const baseUrl = window.location.origin;
        const apiUrl = baseUrl + CONFIG.apiUrl + '?_=' + Date.now();
        console.log('[Sullivan] Envoi requête POST à:', apiUrl);

        const requestBody = {
          message: text,
          session_id: CONFIG.sessionId,
          user_id: CONFIG.userId,
          step: CONFIG.step,
          mode: CONFIG.mode,
        };
        console.log('[Sullivan] Body:', JSON.stringify(requestBody));

        const response = await fetch(apiUrl, {
          method: 'POST',
          mode: 'cors',
          credentials: 'same-origin',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(requestBody)
        });

        console.log('[Sullivan] Réponse status:', response.status, response.statusText);
        console.log('[Sullivan] Réponse headers:', [...response.headers.entries()]);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        console.log('[Sullivan] Réponse:', data);

        // Mettre à jour session si le backend en renvoie une différente
        if (data.session_id && data.session_id !== CONFIG.sessionId) {
          CONFIG.sessionId = data.session_id;
          saveSession(data.session_id);
        }

        // Afficher outils
        if (data.tool_calls?.length > 0) {
          this.showTools(data.tool_calls.map(t => t.tool).join(', '));
        }

        // Afficher réponse
        this.addMessage('bot', data.content);

        // Exécuter actions DOM
        if (data.dom_actions?.length > 0) {
          this.executeDomActions(data.dom_actions);
        }

        // Exécuter actions code (HTML généré)
        if (data.code_actions?.length > 0) {
          this.executeCodeActions(data.code_actions);
        }

        // Auto-load plan if response contains one
        if (data.actions && data.actions.plan) {
          this.loadPlan(data.actions.plan);
        }

      } catch (e) {
        console.error('[Sullivan] Erreur:', e);
        this.addMessage('bot', `❌ Erreur: ${e.message}`);
      } finally {
        this.showTyping(false);
        this.showTools(null);
        this.isTyping = false;
        this.elements.sendBtn.disabled = false;
      }
    }

    addMessage(role, content) {
      const msg = document.createElement('div');
      msg.className = `sullivan-message ${role}`;
      msg.innerHTML = `
        <div class="sullivan-msg-avatar">${role === 'user' ? '👤' : '🎨'}</div>
        <div class="sullivan-msg-content">${this.escapeHtml(content)}</div>
      `;
      this.elements.messages.appendChild(msg);
      this.scrollToBottom();
    }

    escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML.replace(/\n/g, '<br>');
    }

    showTyping(show) {
      this.elements.typing.classList.toggle('active', show);
      if (show) {
        this.elements.messages.appendChild(this.elements.typing);
        this.scrollToBottom();
      }
    }

    showTools(text) {
      if (!text) {
        this.elements.tools.classList.remove('active');
        return;
      }
      this.elements.toolsText.textContent = `Outils: ${text}`;
      this.elements.tools.classList.add('active');
    }

    scrollToBottom() {
      this.elements.messages.scrollTop = this.elements.messages.scrollHeight;
    }

    executeDomActions(actions) {
      console.log('[Sullivan] DOM actions:', actions);
      actions.forEach(action => {
        try {
          switch (action.type) {
            case 'setStyle':
              document.querySelectorAll(action.selector).forEach(el => {
                Object.assign(el.style, action.styles);
              });
              break;
            case 'addClass':
              document.querySelectorAll(action.selector).forEach(el => el.classList.add(action.className));
              break;
            case 'removeClass':
              document.querySelectorAll(action.selector).forEach(el => el.classList.remove(action.className));
              break;
            case 'scrollTo':
              document.querySelector(action.selector)?.scrollIntoView({ behavior: 'smooth' });
              break;
            case 'highlight':
              document.querySelectorAll(action.selector).forEach(el => {
                el.style.boxShadow = '0 0 0 4px rgba(99, 102, 241, 0.5)';
                setTimeout(() => el.style.boxShadow = '', 2000);
              });
              break;
            case 'insertHTML':
              // Injection HTML directe via dom_action
              if (action.selector && action.html) {
                const target = document.querySelector(action.selector);
                if (target) {
                  const position = action.position || 'beforeend';
                  target.insertAdjacentHTML(position, action.html);
                  console.log('[Sullivan] HTML injecté via dom_action:', action.selector, position);
                } else {
                  console.warn('[Sullivan] Cible non trouvée pour insertHTML:', action.selector);
                }
              }
              break;
            case 'setContent':
              const setTarget = document.querySelector(action.selector);
              if (setTarget) {
                setTarget.innerHTML = action.content || action.html || '';
              }
              break;
          }
        } catch (e) {
          console.error('[Sullivan] DOM error:', e);
        }
      });
    }

    executeCodeActions(actions) {
      console.log('[Sullivan] Code actions:', actions);
      actions.forEach(action => {
        try {
          switch (action.type) {
            case 'insert_html':
              // Afficher preview avec bouton pour injecter
              if (action.html) {
                const targetSelector = action.target || '#studio-main-zone';
                const position = action.position || 'beforeend';
                this.addHtmlPreviewWithInject(action.html, targetSelector, position);
                console.log('[Sullivan] HTML preview avec injection:', action.html.substring(0, 100) + '...');
              }
              break;
            case 'replace_html':
              const replaceTarget = document.querySelector(action.selector);
              if (replaceTarget && action.html) {
                replaceTarget.outerHTML = action.html;
              }
              break;
            case 'append_html':
              const appendTarget = document.querySelector(action.selector);
              if (appendTarget && action.html) {
                appendTarget.insertAdjacentHTML('beforeend', action.html);
              }
              break;
          }
        } catch (e) {
          console.error('[Sullivan] Code action error:', e);
        }
      });
    }

    // Injecte le HTML dans le DOM réel
    injectHtmlIntoPage(html, targetSelector, position) {
      const target = document.querySelector(targetSelector);
      if (!target) {
        // Si la cible n'existe pas, injecter avant le widget Sullivan
        const sullivanWidget = document.getElementById('sullivan-super-widget');
        if (sullivanWidget && sullivanWidget.parentElement) {
          sullivanWidget.parentElement.insertAdjacentHTML('beforebegin', html);
          console.log('[Sullivan] HTML injecté avant le widget');
          return true;
        }
        console.error('[Sullivan] Cible non trouvée:', targetSelector);
        return false;
      }

      target.insertAdjacentHTML(position, html);
      console.log('[Sullivan] HTML injecté dans', targetSelector, 'position:', position);
      return true;
    }

    addHtmlPreviewWithInject(html, targetSelector, position) {
      // Ajouter une preview du HTML avec boutons Copier ET Injecter
      const msg = document.createElement('div');
      msg.className = 'sullivan-message bot';
      const uniqueId = 'html-preview-' + Date.now();
      msg.innerHTML = `
        <div class="sullivan-msg-avatar">🎨</div>
        <div class="sullivan-msg-content" style="padding: 0; overflow: hidden;">
          <div style="padding: 8px 12px; background: #1e293b; color: #94a3b8; font-size: 11px; border-radius: 12px 12px 0 0; display: flex; justify-content: space-between; align-items: center;">
            <span>📦 Composant généré</span>
            <div style="display: flex; gap: 6px;">
              <button onclick="window.SullivanWidget.copyHtml(this)" style="background: #475569; border: none; color: white; padding: 2px 8px; border-radius: 4px; cursor: pointer; font-size: 10px;">📋 Copier</button>
              <button onclick="window.SullivanWidget.injectFromPreview('${uniqueId}', '${targetSelector}', '${position}')" style="background: #10b981; border: none; color: white; padding: 2px 8px; border-radius: 4px; cursor: pointer; font-size: 10px; font-weight: 600;">🚀 Injecter</button>
            </div>
          </div>
          <div style="padding: 16px; background: white; border: 1px solid #e2e8f0; border-top: none;">
            ${html}
          </div>
          <textarea id="${uniqueId}" class="sullivan-html-source" style="display: none;">${this.escapeHtml(html)}</textarea>
        </div>
      `;
      this.elements.messages.appendChild(msg);
      this.scrollToBottom();
    }

    injectFromPreview(previewId, targetSelector, position) {
      const textarea = document.getElementById(previewId);
      if (textarea) {
        const html = textarea.value;
        const success = this.injectHtmlIntoPage(html, targetSelector, position);
        if (success) {
          // Feedback visuel
          const btn = event.target;
          btn.textContent = '✓ Injecté !';
          btn.style.background = '#059669';
          setTimeout(() => {
            btn.textContent = '🚀 Injecter';
            btn.style.background = '#10b981';
          }, 2000);
        }
      }
    }

    addHtmlPreview(html) {
      // Version simple sans injection (legacy)
      const msg = document.createElement('div');
      msg.className = 'sullivan-message bot';
      msg.innerHTML = `
        <div class="sullivan-msg-avatar">🎨</div>
        <div class="sullivan-msg-content" style="padding: 0; overflow: hidden;">
          <div style="padding: 8px 12px; background: #1e293b; color: #94a3b8; font-size: 11px; border-radius: 12px 12px 0 0;">
            📦 Composant généré <button onclick="window.SullivanWidget.copyHtml(this)" style="float: right; background: #475569; border: none; color: white; padding: 2px 8px; border-radius: 4px; cursor: pointer; font-size: 10px;">Copier</button>
          </div>
          <div style="padding: 16px; background: white; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 12px 12px;">
            ${html}
          </div>
          <textarea class="sullivan-html-source" style="display: none;">${this.escapeHtml(html)}</textarea>
        </div>
      `;
      this.elements.messages.appendChild(msg);
      this.scrollToBottom();
    }

    copyHtml(btn) {
      const textarea = btn.closest('.sullivan-msg-content').querySelector('.sullivan-html-source');
      if (textarea) {
        navigator.clipboard.writeText(textarea.value).then(() => {
          btn.textContent = '✓ Copié!';
          setTimeout(() => btn.textContent = 'Copier', 2000);
        });
      }
    }

    // === PLAN MANAGEMENT METHODS ===

    /**
     * Charge un plan et l'affiche dans la sidebar
     * @param {Object} planJson - Plan au format {title, steps: [{id, title, status}]}
     */
    loadPlan(planJson) {
      if (!planJson || !planJson.steps) {
        console.error('[Sullivan] loadPlan: Invalid plan JSON');
        return;
      }

      this.planState.currentPlan = planJson;
      this.planState.currentStepIndex = 0;
      this.planState.startTime = Date.now();
      this.planState.logs.push({
        time: new Date().toISOString(),
        action: 'plan_loaded',
        data: { title: planJson.title, stepCount: planJson.steps.length }
      });

      this.renderPlanSteps();
      console.log('[Sullivan] Plan loaded:', planJson.title);
    }

    /**
     * Affiche les etapes du plan dans la sidebar
     * Cible: #sullivan-plan-steps
     */
    renderPlanSteps() {
      const container = document.querySelector('#sullivan-plan-steps');
      if (!container) {
        console.warn('[Sullivan] renderPlanSteps: #sullivan-plan-steps not found');
        return;
      }

      const plan = this.planState.currentPlan;
      if (!plan || !plan.steps) {
        container.innerHTML = '<p class="plan-placeholder">Aucun plan actif.</p>';
        return;
      }

      const stepsHtml = plan.steps.map((step, index) => {
        const isActive = index === this.planState.currentStepIndex;
        const isCompleted = step.status === 'completed';
        const statusClass = isCompleted ? 'completed' : (isActive ? 'active' : '');
        const checkboxChecked = isCompleted ? 'checked disabled' : '';

        return `
          <div class="plan-step ${statusClass}" data-step-index="${index}">
            <input type="checkbox" ${checkboxChecked}>
            <span>${step.title}</span>
          </div>
        `;
      }).join('');

      container.innerHTML = `
        <div class="plan-title" style="font-weight:600;margin-bottom:8px;color:#1e293b;">
          ${plan.title || 'Plan sans titre'}
        </div>
        ${stepsHtml}
      `;
    }

    /**
     * Marque l'etape courante comme terminee et passe a la suivante
     */
    completeCurrentStep() {
      const plan = this.planState.currentPlan;
      if (!plan) return;

      const currentStep = plan.steps[this.planState.currentStepIndex];
      if (currentStep) {
        currentStep.status = 'completed';
        this.planState.logs.push({
          time: new Date().toISOString(),
          action: 'step_completed',
          data: { stepIndex: this.planState.currentStepIndex, title: currentStep.title }
        });
      }

      if (this.planState.currentStepIndex < plan.steps.length - 1) {
        this.planState.currentStepIndex++;
        this.renderPlanSteps();
      } else {
        this.completePlan();
      }
    }

    /**
     * Marque le plan comme termine
     */
    completePlan() {
      const duration = Date.now() - this.planState.startTime;
      this.planState.logs.push({
        time: new Date().toISOString(),
        action: 'plan_completed',
        data: {
          durationMs: duration,
          title: this.planState.currentPlan?.title
        }
      });

      console.log('[Sullivan] Plan completed in', Math.round(duration/1000), 'seconds');
      this.renderPlanSteps();

      const container = document.querySelector('#sullivan-plan-steps');
      if (container) {
        const successMsg = document.createElement('div');
        successMsg.style.cssText = 'background:#dcfce7;color:#166534;padding:8px;border-radius:4px;margin-top:8px;font-size:12px;';
        successMsg.textContent = 'Plan termine avec succes!';
        container.appendChild(successMsg);
      }
    }

    /**
     * Retourne les logs du plan courant
     */
    getPlanLogs() {
      return this.planState.logs;
    }

    /**
     * Reset le state du plan
     */
    clearPlan() {
      this.planState = {
        currentPlan: null,
        currentStepIndex: 0,
        logs: [],
        startTime: null
      };
      this.renderPlanSteps();
    }
  }

  // Initialiser quand le DOM est prêt
  function init() {
    console.log('[Sullivan] DOM ready, création du widget...');
    window.SullivanWidget = new SullivanWidgetClass();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
