<script>
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { page } from '$app/stores';
  import { getGenome, getApiBase } from '$lib/api';
  import ValidationOverlay from '$lib/components/ValidationOverlay.svelte';

  let genome = $state(null);
  const showValidation = $derived(browser && $page.url.searchParams?.get?.('validation') === '1');
  let loading = $state(true);
  let error = $state(null);

  // Même base que getGenome() pour que genome et appels organes passent par le proxy en dev
  const API_BASE = getApiBase();

  function substitutePathParams(path) {
    const defaults = { component_id: 'example', user_id: 'default_user' };
    return path.replace(/\{([^}]+)\}/g, (_, name) => defaults[name] ?? 'default');
  }

  function defaultPostBody(path, method) {
    if (method !== 'POST' && method !== 'PUT') return undefined;
    if (path.includes('dev/analyze')) return { backend_path: '.' };
    if (path.includes('designer/analyze')) return { design_path: '.' };
    return {};
  }

  async function callEndpoint(path, method, body) {
    const resolved = substitutePathParams(path);
    const url = resolved.startsWith('http') ? resolved : `${API_BASE}${resolved.startsWith('/') ? '' : '/'}${resolved}`;
    const opts = { method: method || 'GET', headers: { 'Content-Type': 'application/json' } };
    const payload = body ?? defaultPostBody(path, method);
    if ((method === 'POST' || method === 'PUT') && payload !== undefined) {
      opts.body = JSON.stringify(payload);
    }
    const res = await fetch(url, opts);
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) return res.json();
    return res.text();
  }

  function getButtonLabel(hint, method) {
    if (hint === 'terminal' || hint === 'gauge') return 'Refresh';
    if (hint === 'status') return 'Check';
    if (hint === 'form' && method === 'POST') return 'Execute';
    if (hint === 'dashboard' || hint === 'list') return 'Load';
    if (hint === 'detail') return 'View';
    return 'Fetch';
  }

  onMount(async () => {
    try {
      genome = await getGenome();
    } catch (e) {
      error = e.message || String(e);
    } finally {
      loading = false;
    }
  });
</script>

<svelte:head>
  <title>Studio — Genome</title>
</svelte:head>

<div class="studio-genome">
  {#if showValidation}
    <ValidationOverlay visible={true} message="Mode construction — validation disponible." />
  {/if}
  <h1>Studio Genome</h1>

  {#if loading}
    <p>Chargement du genome…</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else if genome?.endpoints?.length}
    <div class="organes">
      {#each genome.endpoints as ep}
        <div class="organe" data-path={ep.path} data-method={ep.method} data-hint={ep.x_ui_hint || 'generic'}>
          <h3>{ep.summary || ep.path}</h3>
          <div class="out" id="out-{ep.path.replace(/\//g, '_')}">—</div>
          <button
            type="button"
            on:click={async () => {
              const out = document.getElementById(`out-${ep.path.replace(/\//g, '_')}`);
              if (!out) return;
              out.classList.remove('err', 'ok');
              try {
                const data = await callEndpoint(ep.path, ep.method);
                out.classList.add('ok');
                out.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
              } catch (e) {
                out.classList.add('err');
                out.textContent = 'Error: ' + (e.message || String(e));
              }
            }}
          >
            {getButtonLabel(ep.x_ui_hint || 'generic', ep.method)}
          </button>
        </div>
      {/each}
    </div>
  {:else}
    <p>Aucun endpoint dans le genome.</p>
  {/if}
</div>

<style>
  .studio-genome {
    padding: 1rem;
    max-width: 60rem;
    margin: 0 auto;
  }
  .error {
    color: var(--error, #c00);
  }
  .organes {
    display: grid;
    gap: 1rem;
  }
  .organe {
    border: 1px solid #ccc;
    border-radius: 0.5rem;
    padding: 1rem;
  }
  .organe .out {
    font-family: monospace;
    font-size: 0.875rem;
    white-space: pre-wrap;
    margin: 0.5rem 0;
    min-height: 2rem;
  }
  .organe .out.ok {
    color: var(--success, #080);
  }
  .organe .out.err {
    color: var(--error, #c00);
  }
</style>