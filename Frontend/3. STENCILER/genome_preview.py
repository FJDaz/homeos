#!/usr/bin/env python3
"""
genome_preview.py
Rend le genome AetherFlow en vrais composants Flowbite HTML.
Route: GET /preview          → première phase (Brainstorm)
Route: GET /preview/<phase_id> → phase ciblée
Mission 18A — 2026-03-02
"""


def _comp_html(comp):
    """N3 visual_hint → snippet Flowbite HTML."""
    vh   = comp.get('visual_hint', 'button')
    name = comp.get('name', comp.get('id', 'Component'))
    gid  = comp.get('id', '')
    w    = f'data-genome-id="{gid}" data-hint="{vh}"'

    if vh in ('button', 'apply-changes'):
        return f'<button type="button" {w} class="genome-comp text-white bg-blue-600 hover:bg-blue-700 font-medium rounded-lg text-sm px-4 py-2">{name}</button>'

    elif vh == 'launch-button':
        return f'<button type="button" {w} class="genome-comp w-full text-white bg-gradient-to-r from-blue-500 to-blue-700 hover:from-blue-600 font-semibold rounded-xl text-base px-6 py-3">{name}</button>'

    elif vh == 'stepper':
        return f'''<div {w} class="genome-comp">
  <ol class="flex items-center w-full text-xs text-gray-500">
    <li class="flex items-center text-blue-600 after:content-[\\'\\'] after:w-full after:h-0.5 after:bg-blue-200 after:mx-2">
      <span class="flex items-center justify-center w-6 h-6 bg-blue-100 rounded-full shrink-0 mr-1">1</span>{name}
    </li>
    <li class="flex items-center after:content-[\\'\\'] after:w-full after:h-0.5 after:bg-gray-200 after:mx-2">
      <span class="flex items-center justify-center w-6 h-6 bg-gray-100 rounded-full shrink-0 mr-1">2</span>Étape 2
    </li>
    <li class="flex items-center">
      <span class="flex items-center justify-center w-6 h-6 bg-gray-100 rounded-full shrink-0 mr-1">3</span>Étape 3
    </li>
  </ol>
</div>'''

    elif vh == 'breadcrumb':
        return f'''<nav {w} aria-label="Breadcrumb" class="genome-comp">
  <ol class="inline-flex items-center space-x-1 text-sm">
    <li><a href="#" class="text-gray-500 hover:text-blue-600">Accueil</a></li>
    <li><span class="mx-1 text-gray-400">/</span><span class="text-gray-700 font-medium">{name}</span></li>
  </ol>
</nav>'''

    elif vh in ('chat/bubble', 'chat'):
        return f'''<div {w} class="genome-comp flex items-start gap-2">
  <div class="flex flex-col max-w-xs leading-1.5 p-3 bg-gray-100 rounded-e-xl rounded-es-xl">
    <p class="text-sm text-gray-900">{name}</p>
  </div>
</div>'''

    elif vh == 'chat-input':
        return f'''<div {w} class="genome-comp flex items-center gap-2 p-2 bg-gray-50 border border-gray-300 rounded-lg">
  <input type="text" class="flex-1 text-sm bg-white border border-gray-200 rounded-lg p-2 focus:ring-blue-500" placeholder="{name}...">
  <button class="p-2 text-blue-600 hover:bg-blue-100 rounded-full">
    <svg class="w-4 h-4 rotate-90" fill="currentColor" viewBox="0 0 18 20"><path d="m17.914 18.594-8-18a1 1 0 0 0-1.828 0l-8 18a1 1 0 0 0 1.157 1.376L8 18.281V9a1 1 0 0 1 2 0v9.281l6.758 1.689a1 1 0 0 0 1.156-1.376Z"/></svg>
  </button>
</div>'''

    elif vh == 'choice-card':
        return f'''<div {w} class="genome-comp p-3 bg-white border-2 border-blue-400 rounded-lg cursor-pointer hover:bg-blue-50">
  <h5 class="text-sm font-semibold text-gray-900">{name}</h5>
  <p class="text-xs text-gray-500 mt-0.5">Sélectionner</p>
</div>'''

    elif vh in ('dashboard', 'status'):
        return f'''<div {w} class="genome-comp p-3 bg-white border border-gray-200 rounded-lg shadow-sm">
  <p class="text-2xl font-bold text-gray-700">—</p>
  <p class="text-xs text-gray-500 mt-1">{name}</p>
  <span class="inline-flex items-center mt-2 bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded-full">
    <span class="w-1.5 h-1.5 bg-green-500 rounded-full mr-1"></span>Actif
  </span>
</div>'''

    elif vh == 'accordion':
        uid = gid.replace('_', '-')
        return f'''<div {w} class="genome-comp" id="acc-{uid}" data-accordion="collapse">
  <h2 id="h-{uid}">
    <button type="button" class="flex items-center justify-between w-full p-3 font-medium text-sm text-gray-500 border border-gray-200 rounded-lg hover:bg-gray-50"
      data-accordion-target="#b-{uid}" aria-expanded="false" aria-controls="b-{uid}">
      <span>{name}</span>
      <svg class="w-3 h-3 rotate-180 shrink-0" fill="none" viewBox="0 0 10 6"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5 5 1 1 5"/></svg>
    </button>
  </h2>
  <div id="b-{uid}" class="hidden" aria-labelledby="h-{uid}">
    <div class="p-3 border border-t-0 border-gray-200 rounded-b-lg text-xs text-gray-500">Contenu : {name}</div>
  </div>
</div>'''

    elif vh == 'upload':
        return f'''<div {w} class="genome-comp flex items-center justify-center w-full">
  <label class="flex flex-col items-center justify-center w-full h-28 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
    <svg class="w-7 h-7 mb-2 text-gray-400" fill="none" viewBox="0 0 20 16"><path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/></svg>
    <p class="text-xs text-gray-500">{name}</p>
    <input type="file" class="hidden">
  </label>
</div>'''

    elif vh == 'color-palette':
        return f'''<div {w} class="genome-comp">
  <p class="text-xs text-gray-400 mb-2">{name}</p>
  <div class="flex gap-2">
    <div class="w-7 h-7 rounded-full bg-blue-400 border border-white shadow" title="#60a5fa"></div>
    <div class="w-7 h-7 rounded-full bg-rose-400 border border-white shadow" title="#fb7185"></div>
    <div class="w-7 h-7 rounded-full bg-amber-400 border border-white shadow" title="#fbbf24"></div>
    <div class="w-7 h-7 rounded-full bg-emerald-400 border border-white shadow" title="#34d399"></div>
    <div class="w-7 h-7 rounded-full bg-purple-400 border border-white shadow" title="#a78bfa"></div>
  </div>
</div>'''

    elif vh in ('grid', 'layout'):
        return f'''<div {w} class="genome-comp">
  <div class="grid grid-cols-3 gap-1.5">
    <div class="h-10 bg-gray-100 border border-gray-200 rounded flex items-center justify-center text-xs text-gray-400">A</div>
    <div class="h-10 bg-blue-50 border border-blue-200 rounded flex items-center justify-center text-xs text-blue-500 font-medium">B</div>
    <div class="h-10 bg-gray-100 border border-gray-200 rounded flex items-center justify-center text-xs text-gray-400">C</div>
  </div>
  <p class="text-xs text-gray-400 mt-1">{name}</p>
</div>'''

    elif vh == 'table':
        return f'''<div {w} class="genome-comp overflow-x-auto rounded-lg border border-gray-200">
  <table class="w-full text-xs text-left text-gray-500">
    <thead class="text-xs text-gray-700 uppercase bg-gray-50">
      <tr><th class="px-3 py-2">ID</th><th class="px-3 py-2">{name}</th><th class="px-3 py-2">Status</th></tr>
    </thead>
    <tbody>
      <tr class="bg-white border-b"><td class="px-3 py-2">001</td><td class="px-3 py-2">Item A</td><td class="px-3 py-2"><span class="bg-green-100 text-green-800 px-1.5 py-0.5 rounded">OK</span></td></tr>
      <tr class="bg-gray-50"><td class="px-3 py-2">002</td><td class="px-3 py-2">Item B</td><td class="px-3 py-2"><span class="bg-yellow-100 text-yellow-800 px-1.5 py-0.5 rounded">En cours</span></td></tr>
    </tbody>
  </table>
</div>'''

    elif vh in ('stencil-card', 'detail-card', 'card'):
        return f'''<div {w} class="genome-comp p-3 bg-white border border-gray-200 rounded-lg shadow-sm">
  <h5 class="text-sm font-semibold text-gray-900 mb-1">{name}</h5>
  <p class="text-xs text-gray-500">Détails et recommandations</p>
  <a href="#" class="text-xs text-blue-600 hover:underline mt-2 inline-block">Voir →</a>
</div>'''

    elif vh == 'preview':
        return f'''<div {w} class="genome-comp p-2 bg-gray-50 border border-gray-200 rounded-lg">
  <div class="h-20 bg-gray-200 rounded flex items-center justify-center text-gray-400">
    <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
  </div>
  <p class="text-xs text-gray-500 mt-1">{name}</p>
</div>'''

    elif vh in ('modal', 'confirm'):
        return f'<button {w} type="button" class="genome-comp text-blue-700 bg-white border border-blue-300 hover:bg-blue-50 font-medium rounded-lg text-sm px-4 py-2">{name}</button>'

    elif vh == 'download':
        return f'''<a href="#" {w} class="genome-comp inline-flex items-center gap-2 text-white bg-green-600 hover:bg-green-700 font-medium rounded-lg text-sm px-4 py-2">
  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
  {name}
</a>'''

    elif vh == 'zoom-controls':
        return f'''<div {w} class="genome-comp inline-flex rounded-md shadow-sm" role="group">
  <button type="button" class="px-3 py-1.5 text-sm text-gray-900 bg-white border border-gray-200 rounded-s-lg hover:bg-gray-100">−</button>
  <button type="button" class="px-3 py-1.5 text-sm text-gray-900 bg-white border-t border-b border-gray-200 hover:bg-gray-100">{name}</button>
  <button type="button" class="px-3 py-1.5 text-sm text-gray-900 bg-white border border-gray-200 rounded-e-lg hover:bg-gray-100">+</button>
</div>'''

    elif vh == 'form':
        return f'''<form {w} class="genome-comp space-y-2">
  <div>
    <label class="block text-xs font-medium text-gray-700 mb-1">{name}</label>
    <input type="text" class="bg-gray-50 border border-gray-300 text-sm rounded-lg block w-full p-2 focus:ring-blue-500">
  </div>
  <button type="submit" class="w-full text-white bg-blue-600 hover:bg-blue-700 font-medium rounded-lg text-sm px-4 py-2">Valider</button>
</form>'''

    else:
        return f'<span {w} class="genome-comp inline-flex items-center bg-gray-100 text-gray-700 text-sm px-3 py-1.5 rounded-full">{name} <span class="text-xs text-gray-400 ml-1.5">({vh})</span></span>'


def _render_organ_card(organ):
    name    = organ.get('name', organ.get('id', ''))
    gid     = organ.get('id', '')
    n2_list = organ.get('n2_features', [])

    body = ''
    for feat in n2_list:
        feat_name = feat.get('name', '')
        if feat_name:
            body += f'<p class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2 mt-3 first:mt-0">{feat_name}</p>'
        for comp in feat.get('n3_components', []):
            body += f'<div class="mb-2">{_comp_html(comp)}</div>'

    return f'''
<div class="bg-white border border-gray-200 rounded-xl shadow-sm p-5" data-genome-id="{gid}">
  <h3 class="flex items-center gap-2 text-sm font-semibold text-gray-800 mb-4">
    <span class="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></span>
    {name}
  </h3>
  {body}
</div>'''


def render_genome_preview(genome, phase_id=None):
    phases = genome.get('n0_phases', [])

    # Phase active
    active_phase = None
    if phase_id:
        for p in phases:
            if p['id'] == phase_id:
                active_phase = p
                break
    if active_phase is None and phases:
        active_phase = phases[0]

    # Tabs
    tabs_html = ''
    for p in phases:
        is_active = (p is active_phase)
        cls = ('inline-block px-4 py-3 text-sm font-medium border-b-2 border-blue-600 text-blue-600'
               if is_active else
               'inline-block px-4 py-3 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent')
        tabs_html += f'<a href="/preview/{p["id"]}" class="{cls}">{p.get("name", p["id"])}</a>'

    # Organs grid
    organs_html = ''
    if active_phase:
        for organ in active_phase.get('n1_sections', []):
            organs_html += _render_organ_card(organ)

    phase_title = active_phase.get('name', 'Genome') if active_phase else 'Genome'

    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Preview — {phase_title}</title>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.3.0/flowbite.min.css" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
    .genome-comp {{ transition: outline 0.1s; cursor: default; display: block; }}
    .genome-comp:hover {{ outline: 2px solid #3b82f6; outline-offset: 3px; border-radius: 4px; }}
    .genome-selected {{ outline: 3px solid #f59e0b !important; outline-offset: 3px; border-radius: 4px; }}
  </style>
</head>
<body class="bg-stone-50">

  <header class="bg-white border-b border-gray-200 sticky top-0 z-30">
    <div class="max-w-7xl mx-auto px-6 flex items-center justify-between h-12">
      <span class="text-sm font-semibold text-gray-700">AetherFlow <span class="text-gray-400 font-normal">Preview</span></span>
      <nav class="flex">{tabs_html}</nav>
      <a href="/stenciler" class="text-xs text-gray-400 hover:text-gray-600">Stenciler →</a>
    </div>
  </header>

  <div class="max-w-7xl mx-auto px-6 pt-6 pb-2">
    <h1 class="text-lg font-semibold text-gray-800">{phase_title}</h1>
    <p class="text-xs text-gray-400 mt-0.5">Organes N1 — composants Flowbite depuis visual_hint N3</p>
  </div>

  <main class="max-w-7xl mx-auto px-6 py-4">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {organs_html}
    </div>
  </main>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.3.0/flowbite.min.js"></script>
  <script>
    document.querySelectorAll('[data-genome-id]').forEach(el => {{
      el.addEventListener('click', function(e) {{
        if (['INPUT','BUTTON','A','LABEL'].includes(e.target.tagName)) return;
        document.querySelectorAll('.genome-selected').forEach(x => x.classList.remove('genome-selected'));
        this.classList.add('genome-selected');
        console.log('genome:', this.dataset.genomeId);
      }});
    }});
  </script>
</body>
</html>'''
