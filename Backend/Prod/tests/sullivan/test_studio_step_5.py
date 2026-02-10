"""
Tests pour le Step 5 - Carrefour Créatif (Upload PNG + 8 Propositions)
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io

from Backend.Prod.api import app
from Backend.Prod.sullivan.studio_routes import studio_session


client = TestClient(app)


class TestStep5Choice:
    """Tests pour la page de choix (Upload vs Layouts)."""
    
    def test_step_5_choice_status_code(self):
        """Test que la page de choix retourne 200."""
        response = client.get("/studio/step/5")
        assert response.status_code == 200
    
    def test_step_5_choice_content(self):
        """Test que la page contient les deux options."""
        response = client.get("/studio/step/5")
        content = response.text
        
        assert "C'est un peu générique" in content
        assert "Importez votre layout" in content
        assert "Proposez-moi des idées" in content
        assert "hx-post=\"/studio/step/5/upload\"" in content
        assert "hx-get=\"/studio/step/5/layouts\"" in content


class TestStep5Upload:
    """Tests pour l'upload de PNG."""
    
    def test_upload_valid_png(self):
        """Test l'upload d'un fichier PNG valide."""
        # Créer un fichier PNG factice (header PNG minimal)
        png_content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        
        response = client.post(
            "/studio/step/5/upload",
            files={"design_file": ("test.png", io.BytesIO(png_content), "image/png")}
        )
        
        assert response.status_code == 200
        content = response.text
        assert "Image reçue avec succès" in content
        assert "test.png" in content
        assert "Lancer l'analyse" in content
    
    def test_upload_invalid_extension(self):
        """Test que les extensions non supportées sont rejetées."""
        response = client.post(
            "/studio/step/5/upload",
            files={"design_file": ("test.txt", io.BytesIO(b"invalid"), "text/plain")}
        )
        
        assert response.status_code == 400
        assert "Type non supporté" in response.text
    
    def test_upload_jpg_accepted(self):
        """Test que JPG est accepté."""
        jpg_content = b'\xff\xd8\xff' + b'\x00' * 100
        
        response = client.post(
            "/studio/step/5/upload",
            files={"design_file": ("test.jpg", io.BytesIO(jpg_content), "image/jpeg")}
        )
        
        assert response.status_code == 200
        assert "Image reçue avec succès" in response.text


class TestStep5Layouts:
    """Tests pour les 8 propositions de styles."""
    
    def test_layouts_status_code(self):
        """Test que la page des layouts retourne 200."""
        response = client.get("/studio/step/5/layouts")
        assert response.status_code == 200
    
    def test_layouts_contains_8_styles(self):
        """Test que les 8 styles sont présents."""
        response = client.get("/studio/step/5/layouts")
        content = response.text
        
        expected_styles = [
            "Minimaliste",
            "Brutaliste",
            "Focus TDAH",
            "Glassmorphism",
            "Neumorphism",
            "Cyberpunk",
            "Organique",
            "Corporate",
        ]
        
        for style in expected_styles:
            assert style in content, f"Style '{style}' non trouvé dans la réponse"
    
    def test_layouts_selection(self):
        """Test la sélection d'un layout."""
        response = client.post(
            "/studio/step/5/layouts/select",
            data={"style_id": "minimalist"}
        )
        
        assert response.status_code == 200
        # Vérifie que la session a été mise à jour
        assert studio_session.selected_layout == "minimalist"


class TestStep5Integration:
    """Tests d'intégration du flux Step 5."""
    
    def test_flow_upload_path(self):
        """Test le flux complet: choix → upload → confirmation."""
        # 1. Page de choix
        response = client.get("/studio/step/5")
        assert response.status_code == 200
        
        # 2. Upload
        png_content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        response = client.post(
            "/studio/step/5/upload",
            files={"design_file": ("design.png", io.BytesIO(png_content), "image/png")}
        )
        assert "Image reçue avec succès" in response.text
        
        # 3. Vérifie que le fichier est bien stocké
        assert studio_session.uploaded_filename == "design.png"
        assert studio_session.uploaded_design_path is not None
    
    def test_flow_layouts_path(self):
        """Test le flux complet: choix → layouts → sélection."""
        # 1. Page de choix
        response = client.get("/studio/step/5")
        assert response.status_code == 200
        
        # 2. Voir les layouts
        response = client.get("/studio/step/5/layouts")
        assert response.status_code == 200
        assert "8 Styles de Layout" in response.text
        
        # 3. Sélectionner un style
        response = client.post(
            "/studio/step/5/layouts/select",
            data={"style_id": "glassmorphism"}
        )
        assert response.status_code == 200
        assert studio_session.selected_layout == "glassmorphism"
    
    def test_delete_upload(self):
        """Test la suppression d'un upload."""
        # D'abord uploader
        png_content = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        client.post(
            "/studio/step/5/upload",
            files={"design_file": ("delete_test.png", io.BytesIO(png_content), "image/png")}
        )
        
        # Puis supprimer
        response = client.delete("/studio/step/5/upload")
        assert response.status_code == 200
        
        # Vérifie que la session est nettoyée
        assert studio_session.uploaded_filename is None
        assert studio_session.uploaded_design_path is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
