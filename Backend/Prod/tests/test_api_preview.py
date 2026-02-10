"""Tests d'intégration pour endpoints API /sullivan/preview."""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil
from datetime import datetime
import sys

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Backend.Prod.api import app
from Backend.Prod.sullivan.registry import ComponentRegistry
from Backend.Prod.sullivan.models.component import Component


@pytest.fixture
def client():
    """Fixture pour créer un TestClient FastAPI."""
    return TestClient(app)


@pytest.fixture
def temp_cache_dir():
    """Fixture pour créer un répertoire de cache temporaire."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_component():
    """Fixture pour créer un composant de test."""
    return Component(
        name="component_test_preview",
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


@pytest.fixture
def registry_with_component(test_component, temp_cache_dir):
    """Fixture pour créer un ComponentRegistry avec un composant de test."""
    registry = ComponentRegistry()
    
    # Sauvegarder composant dans LocalCache
    registry.local_cache.save(test_component, "test_user")
    
    # Créer fichiers HTML/CSS/JS pour le composant
    component_dir = registry.local_cache.cache_dir / "test_user" / "component_test_preview"
    component_dir.mkdir(parents=True, exist_ok=True)
    
    (component_dir / "component.html").write_text("<button>Test Button</button>", encoding='utf-8')
    (component_dir / "component.css").write_text(".btn { color: red; }", encoding='utf-8')
    (component_dir / "component.js").write_text("console.log('test');", encoding='utf-8')
    
    return registry


def test_preview_component_exists(client, registry_with_component, test_component):
    """Test GET /sullivan/preview/{component_id} avec composant existant."""
    # Note: Le composant doit être accessible via le ComponentRegistry
    # Pour ce test, on suppose que le composant est déjà dans le cache
    
    response = client.get(
        "/sullivan/preview/component_test_preview",
        params={"user_id": "test_user"}
    )
    
    # Vérifier réponse
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    
    # Vérifier contenu HTML
    html_content = response.text
    assert "<iframe" in html_content
    assert "test_preview" in html_content or "Test Button" in html_content


def test_preview_component_not_found(client):
    """Test GET /sullivan/preview/{component_id} avec composant inexistant."""
    response = client.get(
        "/sullivan/preview/nonexistent_component",
        params={"user_id": "test_user"}
    )
    
    # Vérifier 404
    assert response.status_code == 404


def test_preview_list(client, registry_with_component):
    """Test GET /sullivan/preview pour liste de composants."""
    response = client.get(
        "/sullivan/preview",
        params={"user_id": "test_user"}
    )
    
    # Vérifier réponse
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    
    # Vérifier contenu HTML
    html_content = response.text
    assert "<html" in html_content
    assert "Composants disponibles" in html_content or "composants" in html_content.lower()


def test_render_component(client, registry_with_component, test_component):
    """Test GET /sullivan/preview/{component_id}/render pour rendu HTML/CSS/JS."""
    response = client.get(
        "/sullivan/preview/component_test_preview/render",
        params={"user_id": "test_user"}
    )
    
    # Vérifier réponse
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    
    # Vérifier contenu HTML complet
    html_content = response.text
    assert "<html" in html_content
    assert "<button>Test Button</button>" in html_content
    assert ".btn { color: red; }" in html_content or "color: red" in html_content
    assert "console.log('test');" in html_content or "console.log" in html_content


def test_render_component_not_found(client):
    """Test GET /sullivan/preview/{component_id}/render avec composant inexistant."""
    response = client.get(
        "/sullivan/preview/nonexistent_component/render",
        params={"user_id": "test_user"}
    )
    
    # Vérifier 404
    assert response.status_code == 404

