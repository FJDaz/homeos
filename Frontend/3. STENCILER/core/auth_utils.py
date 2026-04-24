import os
import bcrypt
import jwt
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

# --- CONFIGURATION ---
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-aetherflow-key-change-me")
JWT_ALGORITHM = "HS256"
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

# --- HASHING ---

def hash_password_bcrypt(password: str) -> str:
    """Hash un mot de passe en utilisant bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie un mot de passe. 
    Supporte bcrypt (nouveau) et SHA-256 (legacy pour migration).
    """
    try:
        # Détection bcrypt (commence par $2b$)
        if hashed_password.startswith("$2b$"):
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        
        # Fallback SHA-256 (M224)
        sha_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        return sha_hash == hashed_password
    except Exception:
        return False

# --- JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Génère un JWT signé."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Décode et valide un JWT."""
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except Exception:
        return None

# --- EMAIL (RESEND) ---

def send_magic_link_email(email: str, token: str, site_url: str):
    """Envoie un email via l'API Resend."""
    if not RESEND_API_KEY:
        # Fallback console pour dev/test sans clé
        print(f"[AUTH DEBUG] Magic link for {email}: {site_url}/auth/verify?token={token}")
        return True # On simule le succès en dev
    
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": "AetherFlow <auth@resend.dev>", 
        "to": [email],
        "subject": "🔑 Votre accès au Laboratoire AetherFlow",
        "html": f"""
            <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; padding: 40px; background-color: #F7F6F2; color: #3D3D3C; line-height: 1.6;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 40px; border: 1px solid rgba(0,0,0,0.05);">
                    <div style="width: 4px; height: 32px; background-color: #A3CD54; margin-bottom: 24px;"></div>
                    <h1 style="font-size: 24px; font-weight: 900; margin: 0 0 8px 0; color: #1A1A1A; letter-spacing: -0.02em;">HoméOS</h1>
                    <p style="font-size: 10px; font-weight: bold; color: #94A3B8; margin: 0 0 40px 0; text-transform: uppercase; letter-spacing: 0.2em;">The Rational Playroom</p>
                    
                    <p style="font-size: 16px; margin-bottom: 32px;">Bonjour,</p>
                    <p style="font-size: 16px; margin-bottom: 32px;">Vous avez demandé un accès sécurisé à votre espace de travail. Cliquez sur le bouton ci-dessous pour authentifier votre session :</p>
                    
                    <a href="{site_url}/auth/verify?token={token}" 
                       style="display: inline-block; padding: 16px 32px; background-color: #1A1A1A; color: #FFFFFF; text-decoration: none; font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 0.15em;">
                       Accéder au Laboratoire →
                    </a>
                    
                    <p style="margin-top: 48px; font-size: 12px; color: #94A3B8;">
                        Ce lien est à usage unique et expirera dans 15 minutes.<br>
                        Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email en toute sécurité.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #F1F5F9; margin: 32px 0;">
                    <p style="font-size: 10px; color: #CBD5E1; text-transform: uppercase; letter-spacing: 0.1em;">AetherFlow / Unified Auth / v3.1</p>
                </div>
            </div>
        """
    }
    try:
        resp = requests.post(url, json=payload, headers=headers)
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"[AUTH] Resend failed: {e}")
        return False
