from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

CWD = Path(__file__).parent.parent.resolve()
STATIC_DIR_PATH = CWD / "static"

router = APIRouter()


@router.get("/stenciler")
async def get_stenciler_redirect():
    """Mission 168: Redirect ancien /stenciler -> /workspace (architecture hexagonale M156)."""
    return RedirectResponse(url="/workspace", status_code=301)


@router.get("/stenciler_v3")
async def get_stenciler_v3_redirect():
    """Mission 168: Redirect ancien /stenciler_v3 -> /workspace."""
    return RedirectResponse(url="/workspace", status_code=301)


@router.get("/bkd")
async def get_bkd_editor():
    path = STATIC_DIR_PATH / "templates/bkd_editor.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="bkd_editor.html not yet generated")
    return FileResponse(path)


@router.get("/frd-editor")
async def get_frd_editor():
    path = STATIC_DIR_PATH / "templates/frd_editor.html"
    return FileResponse(path)


@router.get("/bkd-frd")
async def get_bkd_frd():
    path = STATIC_DIR_PATH / "templates/bkd_frd.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@router.get("/brainstorm")
async def get_brainstorm():
    path = STATIC_DIR_PATH / "templates/brainstorm_war_room_tw.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@router.get("/brainstorm-alt")
async def get_brainstorm_alt():
    path = STATIC_DIR_PATH / "templates/brainstorm_alt.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@router.get("/intent-viewer")
async def get_intent_viewer():
    path = STATIC_DIR_PATH / "templates/intent_viewer.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@router.get("/")
async def get_root():
    return RedirectResponse(url="/workspace")


@router.get("/landing")
async def get_landing():
    return RedirectResponse(url="/login", status_code=301)


@router.get("/login")
async def get_login():
    """Mission 190: Page d'entrée auth — nom uniquement, pas de mot de passe."""
    path = STATIC_DIR_PATH / "templates/login.html"
    if not path.exists():
        # Fallback inline si le fichier n'existe pas encore
        return HTMLResponse(content="""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>HomeOS — Login</title>
<style>body{font-family:system-ui,sans-serif;background:#f7f6f2;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.card{background:#fff;padding:2rem;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.08);max-width:360px;width:100%}
h1{font-size:1.25rem;margin:0 0 .5rem;color:#3d3d3c;text-transform:lowercase}
p{font-size:.875rem;color:#6a6a69;margin:0 0 1rem;text-transform:lowercase}
input{width:100%;padding:.5rem;border:1px solid #d5d4d0;border-radius:4px;font-size:.875rem;box-sizing:border-box}
button{width:100%;padding:.5rem;margin-top:.75rem;background:#8cc63f;color:#fff;border:none;border-radius:4px;font-size:.875rem;cursor:pointer;font-weight:600}
button:hover{opacity:.9}
.error{color:#d56363;font-size:.75rem;margin-top:.5rem;display:none}</style></head>
<body><div class="card"><h1>homéos</h1><p>entre ton nom pour continuer</p>
<form id="login-form"><input type="text" id="name-input" placeholder="ton nom" required autocomplete="off">
<div class="error" id="error-msg">erreur de connexion</div>
<button type="submit">entrer</button></form></div>
<script>document.getElementById('login-form').onsubmit=async e=>{e.preventDefault();
const n=document.getElementById('name-input').value.trim();if(!n)return;
try{const r=await fetch('/api/auth/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n})});
const d=await r.json();if(d.token){localStorage.setItem('homeos_user',JSON.stringify(d));window.location.href='/workspace'}}
catch(e){document.getElementById('error-msg').style.display='block'}};</script></body></html>""", status_code=200)
    return FileResponse(path)


@router.get("/student-login")
async def get_student_login():
    """Mission 214: Page login étudiant — sans mot de passe."""
    path = STATIC_DIR_PATH / "templates/student_login.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(path)


@router.get("/teacher")
async def get_teacher_dashboard():
    """Mission 216: Dashboard prof -- vue classe temps reel."""
    path = STATIC_DIR_PATH / "templates/teacher_dashboard.html"
    if not path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(path)


@router.get("/cadrage")
async def get_cadrage(mode: str = "prof", class_id: str = ""):
    """Mission 219/221: Cadrage mode Studio -- sujet x referentiel DNMADE."""
    if mode == "standard":
        path = STATIC_DIR_PATH / "templates/cadrage_alt.html"
    else:
        # Par défaut, on sert le nouveau Cadrage Prof "Studio Edition"
        path = STATIC_DIR_PATH / "templates/cadrage_prof.html"
    
    if not path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(path)
