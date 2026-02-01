#!/usr/bin/env python3
"""
Serveur HTTP simple pour servir le frontend Homeos
"""
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8000
FRONTEND_DIR = Path(__file__).parent / "Frontend"

class FrontendHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)
    
    def end_headers(self):
        # Ajouter headers CORS pour permettre les appels API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    os.chdir(FRONTEND_DIR)
    
    with socketserver.TCPServer(("", PORT), FrontendHandler) as httpd:
        url = f"http://127.0.0.1:{PORT}"
        print(f"🚀 Serveur frontend démarré sur {url}")
        print(f"📁 Répertoire: {FRONTEND_DIR.absolute()}")
        print()
        print("⚠️  Note: Ce serveur sert uniquement le frontend HTML/CSS/JS.")
        print("   Pour que l'interface fonctionne complètement, vous devez aussi démarrer l'API FastAPI:")
        print("   python -m Backend.Prod.api")
        print()
        print(f"🌐 Ouverture de {url} dans le navigateur...")
        
        # Ouvrir dans le navigateur
        webbrowser.open(url)
        
        print()
        print("Appuyez sur Ctrl+C pour arrêter le serveur")
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✓ Serveur arrêté")

if __name__ == "__main__":
    main()
