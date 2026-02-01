<script>
  import {
    AtomeButton,
    AtomeBadge,
    MoleculeUpload,
    MoleculeSearch,
    MoleculeMetricCard,
    OrganeSidebar,
    OrganeHeader,
    OrganeCanvas,
    CorpsShell,
    CorpsSection,
    CorpsGrid
  } from '$lib/components';
</script>

<svelte:head>
  <title>Composants Sullivan — Galerie</title>
</svelte:head>

<div class="gallery">
  <h1>Composants Sullivan prégénérés</h1>
  <p>Ces composants remplacent la génération LLM (~47k tokens) par des imports (~50 tokens).</p>

  <CorpsSection label="Atomes">
    <CorpsGrid columns="repeat(4, 1fr)">
      <div><AtomeButton variant="primary">Primary</AtomeButton></div>
      <div><AtomeButton variant="ghost">Ghost</AtomeButton></div>
      <div><AtomeButton variant="danger">Danger</AtomeButton></div>
      <div><AtomeBadge variant="success" label="85" /><AtomeBadge variant="warning" label="70" /></div>
    </CorpsGrid>
  </CorpsSection>

  <CorpsSection label="Molécules">
    <CorpsGrid columns="repeat(2, 1fr)">
      <div><MoleculeUpload endpoint="/sullivan/designer/upload" accept="image/*" /></div>
      <div><MoleculeSearch placeholder="Rechercher un composant..." /></div>
      <div><MoleculeMetricCard label="Tokens" value="18,734" /><MoleculeMetricCard label="Coût" value="$0.0012" /></div>
    </CorpsGrid>
  </CorpsSection>

  <CorpsSection label="Organes (layout)">
    <div class="organe-preview">
      <OrganeHeader activeStep="Backend" />
      <div class="sidebar-canvas">
        <OrganeSidebar />
        <OrganeCanvas title="Importez votre layout" />
      </div>
    </div>
  </CorpsSection>
</div>

<style>
  .gallery { padding: 2rem; max-width: 60rem; margin: 0 auto; }
  .gallery h1 { margin: 0 0 0.5rem 0; }
  .gallery p { color: #666; margin: 0 0 2rem 0; }
  .organe-preview { border: 1px solid #E5E5E5; border-radius: 4px; overflow: hidden; }
  .sidebar-canvas { display: flex; min-height: 200px; }
</style>
