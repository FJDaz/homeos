import os

target_dir = "/Users/francois-jeandazin/TRACES/extension"
os.makedirs(target_dir, exist_ok=True)

manifest = """{
  "manifest_version": 3,
  "name": "Trace Catcher",
  "version": "1.0.0",
  "description": "Capture IA conversations and search them instantly.",
  "permissions": [
    "storage",
    "activeTab",
    "scripting"
  ],
  "host_permissions": [
    "*://chatgpt.com/*",
    "*://chat.openai.com/*",
    "*://chat.deepseek.com/*",
    "*://claude.ai/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js", "ui.js"],
      "css": ["overlay.css"]
    }
  ],
  "web_accessible_resources": [
    {
      "resources": ["inject.js"],
      "matches": ["<all_urls>"]
    }
  ],
  "action": {
    "default_title": "Trace Catcher"
  }
}"""

content_js = """
// Inject script to main world to intercept fetch
const script = document.createElement('script');
script.src = chrome.runtime.getURL('inject.js');
script.onload = function() {
    this.remove();
};
(document.head || document.documentElement).appendChild(script);

// Listen for messages from injected script
window.addEventListener('message', function(event) {
    if (event.source !== window) return;
    if (event.data.type && (event.data.type === 'TRACE_INTERCEPT')) {
        console.log("Trace intercepted data:", event.data.payload);
        saveToTraceDB(event.data.payload);
    }
});

// IndexedDB logic
function saveToTraceDB(data) {
    const request = indexedDB.open("TraceDB", 1);
    request.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains("conversations")) {
            db.createObjectStore("conversations", { autoIncrement: true });
        }
    };
    request.onsuccess = (e) => {
        const db = e.target.result;
        const tx = db.transaction("conversations", "readwrite");
        tx.objectStore("conversations").add({
            timestamp: Date.now(),
            url: window.location.href,
            data: data
        });
    };
}
"""

inject_js = """
(function() {
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        const response = await originalFetch.apply(this, args);
        // Clone the response to read it without consuming it
        const clone = response.clone();
        
        try {
            const contentType = clone.headers.get('content-type');
            if (contentType && (contentType.includes('application/json') || contentType.includes('text/event-stream'))) {
                const text = await clone.text();
                // Send basic info to content script
                window.postMessage({
                    type: 'TRACE_INTERCEPT',
                    payload: {
                        url: args[0] ? args[0].toString() : '',
                        text: text.substring(0, 1000) // Truncated for POC
                    }
                }, '*');
            }
        } catch (e) {
            console.error("Trace interception error", e);
        }
        
        return response;
    };
})();
"""

ui_js = """
// Alt + S to open overlay
document.addEventListener('keydown', (e) => {
    if (e.altKey && e.code === 'KeyS') {
        toggleTraceOverlay();
    }
});

let overlay = null;

function toggleTraceOverlay() {
    if (overlay) {
        overlay.remove();
        overlay = null;
        return;
    }

    overlay = document.createElement('div');
    overlay.id = 'trace-overlay';
    overlay.innerHTML = `
        <div id="trace-container">
            <h2>Trace Search</h2>
            <input type="text" id="trace-search" placeholder="Search your thoughts..." />
            <div id="trace-results"></div>
        </div>
    `;
    document.body.appendChild(overlay);

    const searchInput = document.getElementById('trace-search');
    searchInput.focus();
    searchInput.addEventListener('input', (e) => {
        performSearch(e.target.value);
    });
}

function performSearch(query) {
    const resultsDiv = document.getElementById('trace-results');
    if (!query) {
        resultsDiv.innerHTML = '';
        return;
    }
    
    const request = indexedDB.open("TraceDB", 1);
    request.onsuccess = (e) => {
        const db = e.target.result;
        // Protect against empty DB
        if (!db.objectStoreNames.contains("conversations")) return;
        
        const tx = db.transaction("conversations", "readonly");
        const store = tx.objectStore("conversations");
        const getAll = store.getAll();
        
        getAll.onsuccess = () => {
            const data = getAll.result;
            // Simple string search
            const matches = data.filter(item => 
                JSON.stringify(item.data).toLowerCase().includes(query.toLowerCase())
            );
            
            resultsDiv.innerHTML = matches.map(m => `
                <div class="trace-result-item">
                    <p>${new Date(m.timestamp).toLocaleString()} - ${m.url}</p>
                    <pre>${JSON.stringify(m.data).substring(0, 150)}...</pre>
                </div>
            `).join('');
        };
    };
}
"""

overlay_css = """
#trace-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.8);
    z-index: 2147483647;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding-top: 10vh;
    font-family: sans-serif;
}

#trace-container {
    background: #1e1e1e;
    color: white;
    width: 600px;
    max-width: 90%;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

#trace-container h2 {
    margin-top: 0;
    font-size: 1.2rem;
    color: #a8b2d1;
}

#trace-search {
    width: 100%;
    padding: 12px;
    border: 1px solid #333;
    background: #2d2d2d;
    color: white;
    border-radius: 6px;
    font-size: 1rem;
    margin-bottom: 20px;
    box-sizing: border-box;
}

#trace-results {
    max-height: 60vh;
    overflow-y: auto;
}

.trace-result-item {
    padding: 10px;
    border-bottom: 1px solid #333;
}

.trace-result-item p {
    margin: 0 0 5px 0;
    font-size: 0.8rem;
    color: #888;
}

.trace-result-item pre {
    margin: 0;
    font-size: 0.9rem;
    white-space: pre-wrap;
    word-break: break-all;
}
"""

background_js = """
// Background service worker for TRACE
chrome.runtime.onInstalled.addListener(() => {
    console.log("TRACE Catcher Installed.");
});
"""

files = {
    "manifest.json": manifest,
    "content.js": content_js,
    "inject.js": inject_js,
    "ui.js": ui_js,
    "overlay.css": overlay_css,
    "background.js": background_js
}

for filename, content in files.items():
    with open(os.path.join(target_dir, filename), "w") as f:
        f.write(content.strip() + "
")

print(f"✅ Extension POC created in {target_dir}")
