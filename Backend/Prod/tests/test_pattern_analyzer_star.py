"""Tests unitaires pour PatternAnalyzer avec intégration STAR."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
from pathlib import Path
import tempfile
import shutil

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Backend.Prod.sullivan.analyzer.pattern_analyzer import PatternAnalyzer
from Backend.Prod.sullivan.library.elite_library import EliteLibrary
from Backend.Prod.sullivan.models.component import Component


@pytest.fixture
def temp_elite_library():
    """Fixture pour créer une EliteLibrary temporaire."""
    temp_dir = tempfile.mkdtemp()
    library = EliteLibrary(path=Path(temp_dir))
    yield library
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_components():
    """Fixture pour créer des composants de test."""
    return [
        Component(
            name="component_toggle_button",
            sullivan_score=85.0,
            performance_score=90,
            accessibility_score=85,
            ecology_score=80,
            popularity_score=75,
            validation_score=88,
            size_kb=10,
            created_at=datetime.now(),
            user_id="test_user",
            category="core"
        ),
        Component(
            name="component_accordion_menu",
            sullivan_score=88.0,
            performance_score=92,
            accessibility_score=87,
            ecology_score=82,
            popularity_score=78,
            validation_score=90,
            size_kb=12,
            created_at=datetime.now(),
            user_id="test_user",
            category="core"
        )
    ]


def test_analyze_patterns_with_star_insights(temp_elite_library, test_components):
    """Test que analyze_patterns() inclut des insights STAR."""
    # Ajouter composants à la bibliothèque
    for comp in test_components:
        temp_elite_library.add(comp)
    
    # Créer PatternAnalyzer
    analyzer = PatternAnalyzer(temp_elite_library)
    
    # Mock IntentTranslator au niveau du module intent_translator (lazy import dans PatternAnalyzer)
    with patch('Backend.Prod.sullivan.intent_translator.IntentTranslator') as mock_intent_translator_class:
        mock_intent_translator = Mock()
        
        # Mock pour le premier composant (toggle_button)
        mock_situation1 = Mock()
        mock_situation1.pattern_name = "Toggle Visibility"
        mock_situation1.description = "Toggle visibility pattern"
        mock_intent_translator.search_situation.return_value = [mock_situation1]
        
        mock_realisation1 = Mock()
        mock_realisation1.description = "Toggle realisation"
        mock_intent_translator.propagate_star.return_value = mock_realisation1
        
        mock_intent_translator_class.return_value = mock_intent_translator
        
        # Appeler analyze_patterns()
        results = analyzer.analyze_patterns()
        
        # Vérifier que les résultats contiennent star_insights
        assert "star_insights" in results
        star_insights = results["star_insights"]
        assert "components_with_star_patterns" in star_insights
        assert isinstance(star_insights["components_with_star_patterns"], int)
        assert star_insights["components_with_star_patterns"] >= 0


def test_analyze_patterns_without_star_insights(temp_elite_library, test_components):
    """Test que analyze_patterns() fonctionne sans STAR (fallback)."""
    # Ajouter composants à la bibliothèque
    for comp in test_components:
        temp_elite_library.add(comp)
    
    # Créer PatternAnalyzer
    analyzer = PatternAnalyzer(temp_elite_library)
    
    # Mock IntentTranslator pour simuler ImportError
    with patch('Backend.Prod.sullivan.intent_translator.IntentTranslator', side_effect=ImportError("Not available")):
        # Appeler analyze_patterns()
        results = analyzer.analyze_patterns()
        
        # Vérifier que les résultats contiennent toujours les insights normaux
        assert "summary" in results
        assert "category_insights" in results
        assert "naming_patterns" in results
        
        # Vérifier que star_insights existe mais peut être vide
        assert "star_insights" in results
        assert results["star_insights"].get("components_with_star_patterns", 0) == 0


def test_analyze_patterns_star_most_common_patterns(temp_elite_library, test_components):
    """Test que analyze_patterns() identifie les patterns STAR les plus communs."""
    # Ajouter composants à la bibliothèque
    for comp in test_components:
        temp_elite_library.add(comp)
    
    # Créer PatternAnalyzer
    analyzer = PatternAnalyzer(temp_elite_library)
    
    # Mock IntentTranslator pour retourner différents patterns
    # PatternAnalyzer utilise un lazy import 'from ..intent_translator import IntentTranslator'
    # Il faut patcher au niveau du module intent_translator pour que le lazy import fonctionne
    with patch('Backend.Prod.sullivan.intent_translator.IntentTranslator') as mock_intent_translator_class:
        mock_intent_translator = Mock()
        
        # Simuler différents patterns selon le composant
        def mock_search_situation(intent, limit=1):
            mock_situation = Mock()
            if "toggle" in intent.lower():
                mock_situation.pattern_name = "Toggle Visibility"
            elif "accordion" in intent.lower():
                mock_situation.pattern_name = "Accordion"
            else:
                mock_situation.pattern_name = "Unknown"
            mock_situation.description = f"Pattern for {intent}"
            return [mock_situation]
        
        mock_intent_translator.search_situation.side_effect = mock_search_situation
        
        mock_realisation = Mock()
        mock_realisation.description = "Realisation"
        mock_intent_translator.propagate_star.return_value = mock_realisation
        
        mock_intent_translator_class.return_value = mock_intent_translator
        
        # Appeler analyze_patterns()
        results = analyzer.analyze_patterns()
        
        # Vérifier que most_common_star_patterns est présent
        assert "star_insights" in results
        star_insights = results["star_insights"]
        assert "most_common_star_patterns" in star_insights
        assert isinstance(star_insights["most_common_star_patterns"], dict)
