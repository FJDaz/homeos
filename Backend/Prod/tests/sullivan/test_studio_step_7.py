"""
Tests pour le Step 7 - Dialogue Sullivan
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from Backend.Prod.api import app
from Backend.Prod.sullivan.studio_routes import studio_session


client = TestClient(app)


class TestStep7Dialogue:
    """Tests pour l'interface de dialogue."""
    
    def setup_method(self):
        """Reset dialogue state before each test."""
        if hasattr(studio_session, 'dialogue_state'):
            delattr(studio_session, 'dialogue_state')
        # Set up mock visual report
        studio_session.visual_intent_report = {
            "layout": {
                "type": "dashboard",
                "zones": [
                    {
                        "id": "zone_header",
                        "hypothesis": {"label": "Header", "confidence": 0.85}
                    },
                    {
                        "id": "zone_main", 
                        "hypothesis": {"label": "Contenu principal", "confidence": 0.92}
                    }
                ]
            },
            "style": {
                "colors": {"primary": "#6366f1"}
            }
        }
    
    def test_dialogue_page_loads(self):
        """Test que la page de dialogue charge correctement."""
        response = client.get("/studio/step/7/dialogue")
        
        assert response.status_code == 200
        content = response.text
        
        # Vérifier les éléments clés
        assert "Un dernier mot" in content
        assert "Sullivan" in content
        assert "Commençons" in content or "Prêt" in content
    
    def test_dialogue_shows_context(self):
        """Test que le contexte de l'analyse est affiché."""
        response = client.get("/studio/step/7/dialogue")
        content = response.text
        
        # Stats de l'analyse
        assert "Zones détectées" in content
        assert "2" in content  # Nombre de zones
        assert "dashboard" in content.lower() or "Style principal" in content
    
    def test_dialogue_progress_bar(self):
        """Test que la barre de progression est présente."""
        response = client.get("/studio/step/7/dialogue")
        content = response.text
        
        assert "Progression" in content
        assert "0/" in content or "progress" in content.lower()
    
    def test_answer_question(self):
        """Test la réponse à une question."""
        # D'abord charger le dialogue
        client.get("/studio/step/7/dialogue")
        
        # Répondre à une question
        response = client.post(
            "/studio/step/7/answer",
            data={"question_id": "welcome", "answer": "oui"}
        )
        
        assert response.status_code == 200
        
        # Vérifier que la réponse est enregistrée
        assert hasattr(studio_session, 'dialogue_state')
        assert studio_session.dialogue_state['answers'].get('welcome') == 'oui'
    
    def test_free_message(self):
        """Test l'envoi d'un message libre."""
        # Charger le dialogue
        client.get("/studio/step/7/dialogue")
        
        # Envoyer un message
        response = client.post(
            "/studio/step/7/message",
            data={"message": "Je veux changer les couleurs"}
        )
        
        assert response.status_code == 200
        content = response.text
        
        # Vérifier que le message utilisateur apparaît
        assert "Je veux changer les couleurs" in content
    
    def test_skip_dialogue(self):
        """Test le skip du dialogue."""
        response = client.post("/studio/step/7/skip")
        
        assert response.status_code == 200
        # Devrait rediriger vers step 8
        assert "Validation" in response.text or "validation" in response.text.lower()
    
    def test_dialogue_navigation_back(self):
        """Test le bouton retour vers l'analyse."""
        response = client.get("/studio/step/7/dialogue")
        content = response.text
        
        assert "Retour à l'analyse" in content or "Retour" in content
        assert 'hx-get="/studio/step/6/analysis"' in content
    
    def test_complete_dialogue_flow(self):
        """Test le flux complet du dialogue."""
        # 1. Charger le dialogue
        response = client.get("/studio/step/7/dialogue")
        assert response.status_code == 200
        
        # 2. Répondre à l'accueil
        response = client.post(
            "/studio/step/7/answer",
            data={"question_id": "welcome", "answer": "oui"}
        )
        assert response.status_code == 200
        
        # 3. Répondre aux questions de zones
        response = client.post(
            "/studio/step/7/answer",
            data={"question_id": "zone_zone_header", "answer": "oui"}
        )
        assert response.status_code == 200
        
        # 4. Vérifier que les messages s'accumulent
        assert len(studio_session.dialogue_state['messages']) >= 4  # Sullivan + user + Sullivan + user


class TestStep7Template:
    """Tests pour le rendu du template."""
    
    def setup_method(self):
        """Setup."""
        if hasattr(studio_session, 'dialogue_state'):
            delattr(studio_session, 'dialogue_state')
    
    def test_chat_bubbles_structure(self):
        """Test que les bulles de chat sont correctement structurées."""
        studio_session.visual_intent_report = {
            "layout": {"type": "single", "zones": []},
            "style": {"colors": {}}
        }
        
        response = client.get("/studio/step/7/dialogue")
        content = response.text
        
        # Vérifier structure des messages
        assert "chat-messages" in content
        assert "bg-slate-100" in content  # Bulles Sullivan
        assert "bg-indigo-600" in content  # Bulles utilisateur
    
    def test_question_options_rendered(self):
        """Test que les options de réponse sont rendues."""
        studio_session.visual_intent_report = {
            "layout": {"type": "single", "zones": []},
            "style": {"colors": {}}
        }
        
        response = client.get("/studio/step/7/dialogue")
        content = response.text
        
        # Vérifier présence de boutons d'options
        assert "hx-post=\"/studio/step/7/answer\"" in content
        assert "question_id" in content
    
    def test_progress_indicators(self):
        """Test que les indicateurs de progression sont présents."""
        response = client.get("/studio/step/7/dialogue")
        content = response.text
        
        # Barre de progression
        assert "progress" in content.lower() or "w-full bg-indigo-200" in content
    
    def test_design_thumbnail(self):
        """Test que la miniature du design est affichée."""
        studio_session.uploaded_filename = "test_design.png"
        
        response = client.get("/studio/step/7/dialogue")
        content = response.text
        
        assert "Votre design" in content
        assert "/uploads/test_design.png" in content


class TestStep7EdgeCases:
    """Tests des cas limites."""
    
    def test_dialogue_without_visual_report(self):
        """Test le dialogue sans rapport visuel."""
        studio_session.visual_intent_report = None
        if hasattr(studio_session, 'dialogue_state'):
            delattr(studio_session, 'dialogue_state')
        
        response = client.get("/studio/step/7/dialogue")
        
        # Devrait quand même fonctionner avec des valeurs par défaut
        assert response.status_code == 200
    
    def test_empty_message(self):
        """Test l'envoi d'un message vide."""
        client.get("/studio/step/7/dialogue")
        
        response = client.post(
            "/studio/step/7/message",
            data={"message": ""}
        )
        
        # Devrait ignorer le message vide
        assert response.status_code == 200
    
    def test_multiple_answers_same_question(self):
        """Test réponses multiples à la même question."""
        client.get("/studio/step/7/dialogue")
        
        # Première réponse
        client.post(
            "/studio/step/7/answer",
            data={"question_id": "test_q", "answer": "oui"}
        )
        
        # Deuxième réponse (même question)
        response = client.post(
            "/studio/step/7/answer",
            data={"question_id": "test_q", "answer": "non"}
        )
        
        # La dernière réponse devrait être enregistrée
        assert studio_session.dialogue_state['answers']['test_q'] == 'non'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
