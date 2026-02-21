
  🎯 Fichier Principal

   Fichier                                 Lignes   Rôle
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Frontend/3. STENCILER/server_9998_v2.   ~2306    Serveur HTTP unique — Gère /, /stencil
   py                                               er, /api/genome

  ─────────────────────────────────────────────────────────────────────────────────────────
  🔧 Fonctions clés dans server_9998_v2.py

   Fonction                    Ligne   Description
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   load_genome()               ~8      Charge genome_inferred_kimi_innocent_v2.json
   generate_html(genome)       516     Génère la page / (Genome Viewer + style picker)
   generate_stenciler_html()   1948    Génère la page /stenciler (canvas + sidebar)
   generate_wireframe_*()      ~100+   Wireframes SVG pour chaque niveau (Corps/Organes/Ce
                                       llules/Atomes)
   Handler.do_GET()            1872    Routeur HTTP — /, /stenciler, /api/genome, /static/
                                       *
   Handler.serve_static()      1936    Sert les fichiers CSS/JS

  ─────────────────────────────────────────────────────────────────────────────────────────
  📡 Routes HTTP exposées

   Route          Méthode   Handler                     Retour
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   / ou /studio   GET       generate_html(genome)       HTML page Genome
   /stenciler     GET       generate_stenciler_html()   HTML page Stenciler
   /api/genome    GET       json.dumps(genome)          JSON genome
   /static/*      GET       serve_static()              CSS, JS, JSON
   /fonts/*       GET       serve_font()                Wingdings3.woff2

  ─────────────────────────────────────────────────────────────────────────────────────────
  🔌 Point d'entrée

  if __name__ == '__main__':
      server = HTTPServer(('0.0.0.0', 9998), Handler)
      # → http://localhost:9998/

  ─────────────────────────────────────────────────────────────────────────────────────────
  ⚙️ Commande de lancement

  cd "/Users/francois-jeandazin/AETHERFLOW/Frontend/3. STENCILER" && python3 server_9998_v2
  .py

  PID typique : 58524
  Port : 9998
