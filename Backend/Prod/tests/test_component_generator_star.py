"""Tests unitaires pour ComponentGenerator avec intégration STAR."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Backend.Prod.sullivan.generator.component_generator import ComponentGenerator
from Backend.Prod.sullivan.knowledge.knowledge_base import KnowledgeBase


@pytest.fixture
def component_generator():
    """Fixture pour créer une instance ComponentGenerator."""
    return ComponentGenerator(workflow="PROTO")


@pytest.fixture
def mock_knowledge_base():
    """Fixture pour mock KnowledgeBase."""
    kb = Mock(spec=KnowledgeBase)
    kb.search_patterns.return_value = {}
    kb.get_hci_principles.return_value = []
    return kb


def test_enrich_context_with_star_available(component_generator, mock_knowledge_base):
    """Test enrichissement contexte avec STAR disponible."""
    component_generator.knowledge_base = mock_knowledge_base
    
    # Mock IntentTranslator pour retourner des patterns STAR
    with patch('Backend.Prod.sullivan.intent_translator.IntentTranslator') as mock_intent_translator_class:
        mock_intent_translator = Mock()
        mock_situation = Mock()
        mock_situation.pattern_name = "Toggle Visibility"
        mock_situation.description = "Toggle visibility pattern"
        mock_intent_translator.search_situation.return_value = [mock_situation]
        
        mock_realisation = Mock()
        mock_realisation.description = "Realisation template"
        mock_realisation.template = "<button>Toggle</button>"
        mock_intent_translator.propagate_star.return_value = mock_realisation
        
        mock_intent_translator_class.return_value = mock_intent_translator
        
        # Appeler _enrich_context
        intent = "bouton toggle"
        context = "Contexte initial"
        enriched = component_generator._enrich_context(intent, context)
        
        # Vérifier que le contexte enrichi contient des patterns STAR
        assert "STAR Pattern" in enriched or "Patterns STAR" in enriched
        assert "Toggle Visibility" in enriched
        assert "Realisation template" in enriched


def test_enrich_context_without_star(component_generator, mock_knowledge_base):
    """Test enrichissement contexte sans STAR (fallback)."""
    component_generator.knowledge_base = mock_knowledge_base
    
    # Mock IntentTranslator pour simuler ImportError
    with patch('Backend.Prod.sullivan.intent_translator.IntentTranslator', side_effect=ImportError("Not available")):
        intent = "bouton toggle"
        context = "Contexte initial"
        enriched = component_generator._enrich_context(intent, context)
        
        # Vérifier que le contexte enrichi ne contient pas STAR mais contient le contexte initial
        assert context in enriched
        assert "STAR Pattern" not in enriched
        assert "Patterns STAR" not in enriched


def test_enrich_with_star_returns_none_on_error(component_generator):
    """Test que _enrich_with_star retourne None en cas d'erreur."""
    # Simuler une exception dans IntentTranslator
    with patch('Backend.Prod.sullivan.intent_translator.IntentTranslator', side_effect=Exception("Error")):
        result = component_generator._enrich_with_star("test intent")
        assert result is None


def test_enrich_with_star_includes_templates(component_generator, mock_knowledge_base):
    """Test que les templates STAR sont inclus dans l'enrichissement."""
    component_generator.knowledge_base = mock_knowledge_base
    
    with patch('Backend.Prod.sullivan.intent_translator.IntentTranslator') as mock_intent_translator_class:
        mock_intent_translator = Mock()
        mock_situation = Mock()
        mock_situation.pattern_name = "Test Pattern"
        mock_situation.description = "Test description"
        mock_intent_translator.search_situation.return_value = [mock_situation]
        
        mock_realisation = Mock()
        mock_realisation.description = "Test realisation"
        mock_realisation.template = "<div>Test Template</div>"
        mock_intent_translator.propagate_star.return_value = mock_realisation
        
        mock_intent_translator_class.return_value = mock_intent_translator
        
        result = component_generator._enrich_with_star("test intent")
        
        # Vérifier que les templates sont inclus
        assert result is not None
        assert "Test Template" in result or "template" in result.lower()


def test_enrich_context_includes_knowledge_base_patterns(component_generator, mock_knowledge_base):
    """Test que les patterns KnowledgeBase sont inclus."""
    mock_knowledge_base.search_patterns.return_value = {
        "pattern1": "data1",
        "pattern2": "data2"
    }
    component_generator.knowledge_base = mock_knowledge_base
    
    # Mock IntentTranslator pour retourner None (pas de STAR)
    with patch('Backend.Prod.sullivan.intent_translator.IntentTranslator', side_effect=ImportError):
        intent = "test intent"
        context = "Contexte initial"
        enriched = component_generator._enrich_context(intent, context)
        
        # Vérifier que les patterns KnowledgeBase sont présents
        assert "Patterns similaires trouvés" in enriched
        assert "pattern1" in enriched or "pattern2" in enriched
