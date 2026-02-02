<script>
  import { browser } from '$app/environment';
  import { page } from '$app/stores';
  import Chat from '$lib/components/Chat.svelte';
  import ValidationOverlay from '$lib/components/ValidationOverlay.svelte';
  import CorpsShell from '$lib/components/corps/CorpsShell.svelte';
  import OrganeHeader from '$lib/components/organes/OrganeHeader.svelte';

  const showValidationOverlay = $derived(
    $page.url.pathname.startsWith('/studio') ||
    (browser && $page.url.searchParams?.get?.('validation') === '1')
  );
  const isStudio = $derived($page.url.pathname.startsWith('/studio'));
</script>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: "Helvetica Roman", Helvetica, Arial, sans-serif;
    background: #FFFFFF;
    color: #000;
    min-height: 100vh;
  }

  .homeos {
    position: relative;
    min-height: 100vh;
  }

  /* Z-1: layout user (background, construction_config.z_index_layers.background) */
  .layout-user {
    position: absolute;
    inset: 0;
    z-index: 1;
    display: grid;
    grid-template-rows: auto 1fr;
    grid-template-columns: 1fr 320px;
    grid-template-areas:
      "header header"
      "main aside";
    background: #FFFFFF;
  }

  .layout-user .header-shell {
    grid-area: header;
    background: #F5F5F5;
    height: 48px;
    border-bottom: 1px solid #E5E5E5;
  }

  .layout-user .aside-shell {
    grid-area: aside;
    background: #F5F5F5;
    border-left: 1px solid #E5E5E5;
  }

  .layout-user .main-shell {
    grid-area: main;
    background: #FFFFFF;
    display: flex;
    flex-direction: column;
  }

  .layout-user .main-shell header {
    flex-shrink: 0;
  }

  .layout-user .main-shell header nav {
    display: flex;
    gap: 1rem;
    padding: 0.5rem 1rem;
    border-bottom: 1px solid #222;
  }

  .layout-user .main-shell .content-shell {
    flex: 1;
  }

  /* Z-1000: interface Sullivan (Studio + Chatbot à droite, construction_config.z_index_layers.studio_admin) */
  .layout-sullivan {
    position: relative;
    z-index: 1000;
    display: grid;
    grid-template-rows: auto 1fr;
    grid-template-columns: 1fr 320px;
    grid-template-areas:
      "header header"
      "main aside";
    min-height: 100vh;
    pointer-events: none;
  }

  .layout-sullivan > * {
    pointer-events: auto;
  }

  .header {
    grid-area: header;
    background: #F5F5F5;
    color: #166534;
    border-bottom: 1px solid #E5E5E5;
    padding: 0.5rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 48px;
  }

  .header .left {
    display: flex;
    flex-direction: column;
    gap: 0;
    font-size: 0.9rem;
    font-weight: 600;
  }

  .header .left .brand {
    line-height: 1.2;
  }

  .header .center {
    font-size: 1rem;
    font-weight: 600;
    color: #166534;
  }

  .aside {
    grid-area: aside;
    background: #F5F5F5;
    border-left: 1px solid #E5E5E5;
    width: 320px;
    padding: 1rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .chat-block {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
  }

  .chat-avatar {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
  }

  .chat-block.user .chat-avatar {
    background: #E5E5E5;
    color: #333;
  }

  .chat-block.sullivan .chat-avatar {
    background: #22c55e;
    color: #fff;
  }

  .chat-bubble {
    background: #FFF;
    color: #000;
    border: 1px solid #E5E5E5;
    padding: 0.6rem 0.9rem;
    border-radius: 6px;
    font-size: 0.9rem;
    line-height: 1.4;
    max-width: 260px;
  }

  .main {
    grid-area: main;
    display: flex;
    flex-direction: column;
    background: transparent;
    min-height: 0;
  }

  .main :global(.main-content) {
    flex: 1;
    padding: 1rem;
    overflow: auto;
  }

  /* Layout Organes (Studio) */
  .layout-organes {
    position: relative;
    z-index: 1000;
    pointer-events: none;
  }
  .layout-organes > * {
    pointer-events: auto;
  }
  .layout-organes .aside {
    background: #F5F5F5;
    width: 100%;
    padding: 1rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
</style>

<div class="homeos">
  <!-- Z-1: structure user (vanilla layout, chatbot à droite) -->
  <div class="layout-user" aria-hidden="true">
    <div class="header-shell"></div>
    <div class="main-shell">
      <header>
        <nav></nav>
      </header>
      <div class="content-shell"></div>
    </div>
    <div class="aside-shell"></div>
  </div>

  <!-- Z-10: interface Sullivan (chatbot à droite) -->
  {#if isStudio}
    <CorpsShell sidebarWidth="320px" class="layout-sullivan layout-organes">
      <svelte:fragment slot="header">
        <OrganeHeader activeStep="Backend" />
      </svelte:fragment>
      <svelte:fragment slot="sidebar">
        <aside class="aside">
          <Chat />
        </aside>
      </svelte:fragment>
      <slot />
    </CorpsShell>
  {:else}
    <div class="layout-sullivan">
      <header class="header">
        <div class="left">
          <span class="brand">OS</span>
          <span class="brand">Sullivan</span>
        </div>
        <div class="center">Backend</div>
      </header>

      <main class="main">
        <slot />
      </main>

      <aside class="aside">
        <Chat />
      </aside>
    </div>
  {/if}

  <ValidationOverlay visible={showValidationOverlay} />
</div>
