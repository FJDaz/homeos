/**
 * Studio Genome – Load genome from GET /studio/genome, render organes by x_ui_hint, attach API fetch.
 */
(function () {
  const CONFIG = {
    genomeUrl: '/studio/genome',
    baseUrl: window.location.origin || 'http://localhost:8000'
  };

  function getEl(id) {
    return document.getElementById(id);
  }

  function showLoading(show) {
    const el = getEl('studio-loading');
    if (el) el.style.display = show ? 'block' : 'none';
  }

  function showError(msg) {
    const el = getEl('studio-error');
    if (el) {
      el.textContent = msg || '';
      el.style.display = msg ? 'block' : 'none';
    }
  }

  function escapeHtml(s) {
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  }

  function substitutePathParams(path) {
    var defaults = { component_id: 'example', user_id: 'default_user' };
    return path.replace(/\{([^}]+)\}/g, function (_, name) {
      return defaults[name] != null ? defaults[name] : 'default';
    });
  }

  function defaultPostBody(path, method) {
    if (method !== 'POST' && method !== 'PUT') return undefined;
    if (path.indexOf('dev/analyze') !== -1) return { backend_path: '.' };
    if (path.indexOf('designer/analyze') !== -1) return { design_path: '.' };
    return {};
  }

  function renderOrgane(endpoint, baseUrl) {
    const method = (endpoint.method || 'GET').toUpperCase();
    const path = endpoint.path || '';
    const hint = endpoint.x_ui_hint || 'generic';
    const summary = endpoint.summary || path || 'Endpoint';
    const lid = path.replace(/\//g, '_').replace(/^_|_$/g, '') || 'root';
    const bid = 'btn_' + lid;
    const oid = 'out_' + lid;

    let label = 'Fetch';
    if (hint === 'terminal') label = 'Refresh';
    else if (hint === 'gauge') label = 'Refresh';
    else if (hint === 'status') label = 'Check';
    else if (hint === 'form' && method === 'POST') label = 'Execute';
    else if (hint === 'dashboard' || hint === 'list') label = 'Load';
    else if (hint === 'detail') label = 'View';

    const safeSummary = escapeHtml(summary);
    const safePath = escapeHtml(path);
    const safeMethod = escapeHtml(method);
    const isForm = hint === 'form' && method === 'POST';

    let html = '<div class="organe" data-path="' + safePath + '" data-method="' + safeMethod + '" data-hint="' + escapeHtml(hint) + '">';
    html += '<h3>' + safeSummary + '</h3>';
    if (hint === 'terminal') {
      html += '<pre id="' + oid + '" class="out">—</pre>';
    } else {
      html += '<div id="' + oid + '" class="out">—</div>';
    }
    if (isForm) {
      html += '<form id="form_' + lid + '"><button type="submit">' + escapeHtml(label) + '</button></form>';
    } else {
      html += '<button id="' + bid + '" type="button">' + escapeHtml(label) + '</button>';
    }
    html += '</div>';
    return html;
  }

  function attachOrganHandlers(container, baseUrl) {
    const base = (baseUrl || '').replace(/\/$/, '');
    function apiCall(path, method, body) {
      var resolvedPath = substitutePathParams(path);
      const url = resolvedPath.startsWith('http') ? resolvedPath : base + (resolvedPath.startsWith('/') ? resolvedPath : '/' + resolvedPath);
      const m = method || 'GET';
      const opt = { method: m, headers: { 'Content-Type': 'application/json' } };
      var payload = body != null ? body : defaultPostBody(path, m);
      if ((m === 'POST' || m === 'PUT') && payload !== undefined) opt.body = JSON.stringify(payload);
      return fetch(url, opt).then(function (r) {
        const ct = r.headers.get('content-type') || '';
        if (ct.indexOf('application/json') !== -1) return r.json();
        return r.text();
      });
    }
    function renderOut(el, data) {
      if (typeof data === 'string') { el.textContent = data; return; }
      el.textContent = JSON.stringify(data, null, 2);
    }
    container.querySelectorAll('.organe').forEach(function (o) {
      const path = o.getAttribute('data-path');
      const method = (o.getAttribute('data-method') || 'GET').toUpperCase();
      const out = o.querySelector('.out') || o.querySelector('[id^=out_]');
      if (!path || !out) return;
      const btn = o.querySelector('button[id^=btn_]') || o.querySelector('button:not([type=submit])');
      const form = o.querySelector('form');
      function run() {
        out.classList.remove('err', 'ok');
        apiCall(path, method, undefined).then(function (d) {
          out.classList.add('ok');
          renderOut(out, d);
        }).catch(function (e) {
          out.classList.add('err');
          out.textContent = 'Error: ' + (e.message || String(e));
        });
      }
      if (btn) btn.addEventListener('click', run);
      if (form) form.addEventListener('submit', function (e) { e.preventDefault(); run(); });
    });
  }

  function run() {
    console.log('[Studio] Chargement genome:', CONFIG.genomeUrl);
    showLoading(true);
    showError('');
    fetch(CONFIG.genomeUrl)
      .then(function (res) {
        if (!res.ok) throw new Error('Genome: ' + res.status + ' ' + res.statusText);
        return res.json();
      })
      .then(function (genome) {
        console.log('[Studio] Genome reçu:', Object.keys(genome || {}), 'endpoints:', (genome && genome.endpoints && genome.endpoints.length) || 0);
        showLoading(false);
        const metadata = genome.metadata || {};
        const topology = genome.topology || ['Brainstorm', 'Back', 'Front', 'Deploy'];
        const endpoints = genome.endpoints || [];
        const intent = metadata.intent || 'PaaS_Studio';

        document.title = 'Studio – ' + intent;
        const titleEl = getEl('studio-title');
        if (titleEl) titleEl.textContent = intent;

        const navEl = getEl('studio-topology');
        if (navEl) {
          navEl.innerHTML = topology.map(function (s) {
            return '<a href="#' + escapeHtml(s) + '">' + escapeHtml(s) + '</a>';
          }).join('');
        }

        const organesEl = getEl('studio-organes');
        if (organesEl) {
          organesEl.innerHTML = endpoints.map(function (ep) { return renderOrgane(ep, CONFIG.baseUrl); }).join('');
          attachOrganHandlers(organesEl, CONFIG.baseUrl);
        }
      })
      .catch(function (err) {
        console.error('[Studio] Erreur genome:', err);
        showLoading(false);
        showError('Erreur: ' + (err.message || String(err)));
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();

Frontend/
├── studio.html
├── css/
│   └── styles.css
└── js/
    ├── studio-genome.js
    └── utils/
        └── error-handler.js

Frontend/
├── studio.html
├── css/
│   └── styles.css
└── js/
    ├── studio-genome.js
    ├── utils/
    │   ├── error-handler.js
    │   ├── organ-renderer.js
    │   └── api-client.js
    └── tests/
        └── organ-renderer.test.js