"""Tests unitaires pour preview_generator."""
import pytest
from datetime import datetime
import sys
from pathlib import Path

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Backend.Prod.sullivan.preview.preview_generator import generate_preview_html, generate_preview_page
from Backend.Prod.sullivan.models.component import Component


@pytest.fixture
def sample_component():
    """Fixture pour créer un composant de test."""
    return Component(
        name="component_test_button",
        sullivan_score=85.5,
        performance_score=90,
        accessibility_score=85,
        ecology_score=80,
        popularity_score=75,
        validation_score=88,
        size_kb=15,
        created_at=datetime.now(),
        user_id="test_user",
        category="core"
    )


def test_generate_preview_html_contains_iframe(sample_component):
    """Test que generate_preview_html génère un HTML avec iframe."""
    base_url = "http://localhost:8000"
    html = generate_preview_html(sample_component, base_url)
    
    # Vérifier présence iframe
    assert "<iframe" in html
    assert "preview-frame" in html
    assert "/sullivan/preview/test_button/render" in html or "/sullivan/preview/test_button" in html


def test_generate_preview_html_contains_component_info(sample_component):
    """Test que generate_preview_html contient les informations du composant."""
    base_url = "http://localhost:8000"
    html = generate_preview_html(sample_component, base_url)
    
    # Vérifier informations composant
    assert str(sample_component.sullivan_score) in html
    assert str(sample_component.size_kb) in html
    assert str(sample_component.performance_score) in html
    assert str(sample_component.accessibility_score) in html
    assert str(sample_component.ecology_score) in html


def test_generate_preview_html_brutalist_style(sample_component):
    """Test que generate_preview_html utilise le style brutaliste."""
    base_url = "http://localhost:8000"
    html = generate_preview_html(sample_component, base_url)
    
    # Vérifier style brutaliste (bordures noires, typographie)
    assert "#000" in html or "border: 3px solid #000" in html or "border-bottom: 3px solid #000" in html
    assert "font-family" in html
    assert "font-weight: bold" in html or "font-weight:bold" in html


def test_generate_preview_page_contains_list(sample_component):
    """Test que generate_preview_page génère une liste de composants."""
    components = [sample_component]
    base_url = "http://localhost:8000"
    html = generate_preview_page(components, base_url)
    
    # Vérifier liste
    assert "<ul>" in html or "<li>" in html
    assert "test_button" in html
    assert str(len(components)) in html  # Nombre de composants


def test_generate_preview_page_contains_links(sample_component):
    """Test que generate_preview_page contient des liens vers prévisualisations."""
    components = [sample_component]
    base_url = "http://localhost:8000"
    html = generate_preview_page(components, base_url)
    
    # Vérifier liens
    assert "<a href" in html
    assert "/sullivan/preview/test_button" in html


def test_generate_preview_page_multiple_components():
    """Test generate_preview_page avec plusieurs composants."""
    components = [
        Component(
            name="component_button_1",
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
            name="component_button_2",
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
    base_url = "http://localhost:8000"
    html = generate_preview_page(components, base_url)
    
    # Vérifier que les deux composants sont présents
    assert "button_1" in html
    assert "button_2" in html
    assert "2)" in html or "Composants disponibles (2)" in html
