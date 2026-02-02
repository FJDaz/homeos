<script>
  import { sullivanDesignerUpload } from '$lib/api';

  let fileInput;
  let uploading = false;
  let result = null;
  let error = null;

  const ALLOWED = ['.png', '.jpg', '.jpeg', '.svg'];

  function triggerUpload() {
    fileInput?.click();
  }

  async function onFileChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    const ext = '.' + (file.name.split('.').pop() || '').toLowerCase();
    if (!ALLOWED.includes(ext)) {
      error = `Format non supporté. Utilisez : ${ALLOWED.join(', ')}`;
      result = null;
      e.target.value = '';
      return;
    }
    error = null;
    result = null;
    uploading = true;
    try {
      result = await sullivanDesignerUpload(file);
    } catch (e) {
      error = e.message || 'Erreur lors de l’analyse.';
    } finally {
      uploading = false;
      e.target.value = '';
    }
  }
</script>

<div class="main-content">
  <div class="upload-zone">
    <input
      type="file"
      bind:this={fileInput}
      accept=".png,.jpg,.jpeg,.svg,image/png,image/jpeg,image/svg+xml"
      on:change={onFileChange}
      class="hidden-input"
      aria-hidden="true"
    />
    <button
      type="button"
      class="upload-btn"
      disabled={uploading}
      on:click={triggerUpload}
    >
      {#if uploading}
        Analyse en cours…
      {:else}
        Uploadez votre template
      {/if}
    </button>
    <p class="upload-hint">PNG, JPG ou SVG. Sullivan (Gemini) analysera le design.</p>
  </div>

  {#if error}
    <div class="result result-error">{error}</div>
  {/if}

  {#if result}
    <div class="result result-ok">
      <p class="result-message">{result.message}</p>
      {#if result.design_structure}
        <details>
          <summary>Structure design</summary>
          <pre>{JSON.stringify(result.design_structure, null, 2)}</pre>
        </details>
      {/if}
      {#if result.matched_patterns && result.matched_patterns.length}
        <details>
          <summary>Patterns matchés</summary>
          <pre>{JSON.stringify(result.matched_patterns, null, 2)}</pre>
        </details>
      {/if}
      {#if result.frontend_structure}
        <details>
          <summary>Structure frontend</summary>
          <pre>{JSON.stringify(result.frontend_structure, null, 2)}</pre>
        </details>
      {/if}
    </div>
  {/if}
</div>

<style>
  .main-content {
    flex: 1;
    padding: 2rem;
    overflow: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
  }
  .upload-zone {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }
  .hidden-input {
    position: absolute;
    width: 0;
    height: 0;
    opacity: 0;
    pointer-events: none;
  }
  .upload-btn {
    min-width: 280px;
    padding: 1.25rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    color: #0d0d0d;
    background: #22c55e;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }
  .upload-btn:hover:not(:disabled) {
    background: #16a34a;
  }
  .upload-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  .upload-hint {
    margin: 0;
    font-size: 0.9rem;
    color: #888;
  }
  .result {
    width: 100%;
    max-width: 720px;
    padding: 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
  }
  .result-error {
    background: #3f1f1f;
    color: #fca5a5;
    border: 1px solid #7f1d1d;
  }
  .result-ok {
    background: #1a2a1a;
    color: #bbf7d0;
    border: 1px solid #166534;
  }
  .result-message {
    margin: 0 0 0.75rem 0;
    font-weight: 600;
  }
  .result details {
    margin-top: 0.5rem;
  }
  .result summary {
    cursor: pointer;
    color: #22c55e;
  }
  .result pre {
    margin: 0.5rem 0 0 0;
    padding: 0.75rem;
    background: #0d0d0d;
    border-radius: 4px;
    overflow: auto;
    font-size: 0.8rem;
    max-height: 320px;
  }
</style>
