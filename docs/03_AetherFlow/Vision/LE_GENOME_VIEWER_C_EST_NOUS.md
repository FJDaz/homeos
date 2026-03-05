# 🧬 GENOME VIEWER - FICHIER OFFICIEL

**⚠️ ATTENTION CLAUDE & AUTRES IA : NE PAS TOUCHER CE FICHIER ⚠️**

## Le bon fichier

```
server_9998_v2.py  ← C'EST CELUI-LÀ (racine du projet)
```

**PAS** `server_9999_v2.py` dans les sous-dossiers  
**PAS** `server_9998.py`  
**PAS** un nouveau fichier qu'un IA veut créer  
**C'EST** `server_9998_v2.py` à la racine, point final.

## Pourquoi celui-là ?

- ✅ Wireframes par niveau (Corps/Organes/Cellules/Atomes)
- ✅ Wingdings3 intégré
- ✅ Emojis partout (💡 ⚙️ 🚀)
- ✅ Dégradés CSS artisanaux (pas de Tailwind)
- ✅ Port 9998 (9999 c'est pour les tests foireux)
- ✅ Pointe vers : `docs/02-sullivan/Genome_Enrichi/Genome_OPTIMISE_2026-02-06/genome_inferred_kimi_innocent_v2.json`

## Commandes rapides

```bash
# Tuer tout ce qui bouge
pkill -f "server_9998\|http.server 9998\|Prod.api"

# Relancer API
cd Backend && python -m Prod.api &

# Relancer Genome Viewer
cd /Users/francois-jeandazin/AETHERFLOW && python server_9998_v2.py &
```

## Signes que c'est le bon

Dans le HTML généré tu dois voir :
- `<title>HoméOS - Genome Viewer (Port 9998)</title>`
- `@font-face { font-family: 'Wingdings3'...`
- `style="background:linear-gradient(...` (PAS `class="bg-gray-...`)
- Des emojis dans les wireframes

Si tu vois du Tailwind (`class="max-w-4xl mx-auto"`), c'est le MAUVAIS serveur.

---
*Document créé pour ne plus jamais galérer*
