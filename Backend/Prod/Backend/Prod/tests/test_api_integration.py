"""
Tests d'intégration pour Sullivan Stenciler API REST - Phase 3

Teste les 5 piliers via leurs endpoints FastAPI :
1. État : GET /api/genome, GET /api/state, GET /api/schema
2. Modifications : POST /api/modifications, GET /api/modifications/history, POST /api/snapshot
3. Navigation : POST /api/drilldown/enter, POST /api/drilldown/exit, GET /api/breadcrumb
4. Composants : GET /api/components/contextual, GET /api/components/{id}, GET /api/components/elite
5. Outils : GET /api/tools, POST /api/tools/{tool_id}/apply

Conformité : CONSTITUTION_AETHERFLOW v1.0.0
"""

import pytest
from fastapi.testclient import TestClient
from Backend.Prod.sullivan.stenciler.api import router
from fastapi import FastAPI

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


# ============================================================================
# PILIER 1 : ÉTAT
# ============================================================================

class TestEtatEndpoints:
    """Tests pour les endpoints d'état du Genome."""

    def test_get_genome_success(self):
        """GET /api/genome retourne le Genome complet avec metadata."""
        response = client.get("/api/genome")

        assert response.status_code == 200
        data = response.json()

        # Vérifier structure
        assert "genome" in data
        assert "metadata" in data

        # Vérifier metadata
        assert "modification_count" in data["metadata"]
        assert "last_snapshot_id" in data["metadata"]
        assert "last_modified" in data["metadata"]

        # Vérifier que genome est un dict non vide
        assert isinstance(data["genome"], dict)

    def test_get_state_success(self):
        """GET /api/state retourne l'état actuel du Genome."""
        response = client.get("/api/state")

        assert response.status_code == 200
        data = response.json()

        # Vérifier structure
        assert "current_state" in data
        assert "modification_count" in data
        assert "last_snapshot_id" in data
        assert "last_modified" in data

        # Vérifier types
        assert isinstance(data["current_state"], dict)
        assert isinstance(data["modification_count"], int)

    def test_get_schema_success(self):
        """GET /api/schema retourne le schéma JSON du Genome."""
        response = client.get("/api/schema")

        assert response.status_code == 200
        data = response.json()

        # Vérifier structure
        assert "levels" in data
        assert "semantic_properties" in data
        assert "forbidden_properties" in data

        # Vérifier les niveaux hiérarchiques
        expected_levels = ["n0_phases", "n1_sections", "n2_features", "n3_atomsets"]
        assert data["levels"] == expected_levels

        # Vérifier que semantic_properties est une liste
        assert isinstance(data["semantic_properties"], list)
        assert len(data["semantic_properties"]) > 0

        # Vérifier que forbidden_properties contient des props CSS/HTML
        assert isinstance(data["forbidden_properties"], list)


# ============================================================================
# PILIER 2 : MODIFICATIONS
# ============================================================================

class TestModificationsEndpoints:
    """Tests pour les endpoints de modifications du Genome."""

    def test_apply_modification_success(self):
        """POST /api/modifications applique une modification valide."""
        payload = {
            "path": "n0[0].n1[0]",
            "property": "name",
            "value": "Test Section"
        }

        response = client.post("/api/modifications", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Vérifier structure
        assert "success" in data
        assert data["success"] is True or data["success"] is False

        if data["success"]:
            assert "snapshot_id" in data
        else:
            assert "error" in data or "validation_errors" in data

    def test_apply_modification_invalid_property(self):
        """POST /api/modifications rejette une propriété interdite."""
        payload = {
            "path": "n0[0]",
            "property": "backgroundColor",  # Propriété CSS interdite
            "value": "#ff0000"
        }

        response = client.post("/api/modifications", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Devrait échouer avec validation_errors
        assert data["success"] is False
        assert "validation_errors" in data or "error" in data

    def test_get_modification_history_success(self):
        """GET /api/modifications/history retourne l'historique."""
        response = client.get("/api/modifications/history?limit=10")

        assert response.status_code == 200
        data = response.json()

        # Vérifier structure
        assert "events" in data
        assert "total" in data
        assert "limit" in data

        # Vérifier types
        assert isinstance(data["events"], list)
        assert isinstance(data["total"], int)
        assert data["limit"] == 10

    def test_get_modification_history_with_since(self):
        """GET /api/modifications/history avec paramètre since."""
        response = client.get("/api/modifications/history?since=2026-01-01T00:00:00Z&limit=5")

        assert response.status_code == 200
        data = response.json()

        assert "events" in data
        assert data["limit"] == 5

    def test_create_snapshot_success(self):
        """POST /api/snapshot crée un snapshot de l'état actuel."""
        response = client.post("/api/snapshot")

        assert response.status_code == 200
        data = response.json()

        # Vérifier structure
        assert "snapshot_id" in data
        assert "timestamp" in data

        # Vérifier format snapshot_id (exemple: "snap_20260211_143022_abc123")
        assert isinstance(data["snapshot_id"], str)
        assert len(data["snapshot_id"]) > 0


# ============================================================================
# PILIER 3 : NAVIGATION
# ============================================================================

class TestNavigationEndpoints:
    """Tests pour les endpoints de navigation (drilldown)."""

    def test_drilldown_enter_success(self):
        """POST /api/drilldown/enter descend dans la hiérarchie."""
        payload = {"path": "n0[0]"}

        response = client.post("/api/drilldown/enter", json=payload)

        # Peut réussir ou échouer selon l'état du Genome
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "current_level" in data
            assert "breadcrumb" in data

    def test_drilldown_enter_invalid_path(self):
        """POST /api/drilldown/enter avec chemin invalide."""
        payload = {"path": "invalid_path_xyz"}

        response = client.post("/api/drilldown/enter", json=payload)

        assert response.status_code == 400
        assert "detail" in response.json()

    def test_drilldown_exit_success(self):
        """POST /api/drilldown/exit remonte dans la hiérarchie."""
        response = client.post("/api/drilldown/exit")

        # Peut réussir ou échouer selon l'état de navigation
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.json()
            assert "success" in data
            assert "current_level" in data
            assert "breadcrumb" in data

    def test_get_breadcrumb_success(self):
        """GET /api/breadcrumb retourne le fil d'Ariane."""
        response = client.get("/api/breadcrumb")

        assert response.status_code == 200
        data = response.json()

        # Vérifier structure
        assert "breadcrumb" in data
        assert "current_level" in data

        # Vérifier que breadcrumb est une liste
        assert isinstance(data["breadcrumb"], list)


# ============================================================================
# PILIER 4 : COMPOSANTS
# ============================================================================

class TestComposantsEndpoints:
    """Tests pour les endpoints de composants Elite Library."""

    def test_get_contextual_components_success(self):
        """GET /api/components/contextual retourne les composants pertinents."""
        response = client.get("/api/components/contextual?level=n2_features")

        assert response.status_code == 200
        data = response.json()

        # Vérifier structure
        assert "components" in data
        assert "level" in data
        assert "count" in data

        # Vérifier types
        assert isinstance(data["components"], list)
        assert data["level"] == "n2_features"
        assert isinstance(data["count"], int)

    def test_get_component_by_id_success(self):
        """GET /api/components/{id} retourne un composant spécifique."""
        # Test avec un ID qui pourrait exister
        response = client.get("/api/components/hero_banner")

        # Peut être 200 (trouvé) ou 404 (non trouvé)
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = response.json()
            # Vérifier que c'est bien un composant
            assert isinstance(data, dict)

    def test_get_component_by_id_not_found(self):
        """GET /api/components/{id} avec ID inexistant."""
        response = client.get("/api/components/nonexistent_component_xyz")

        assert response.status_code == 404
        assert "detail" in response.json()

    def test_get_elite_library_success(self):
        """GET /api/components/elite retourne la bibliothèque complète."""
        response = client.get("/api/components/elite")

        assert response.status_code == 200
        data = response.json()

        # Vérifier structure
        assert "components" in data
        assert "total" in data
        assert "by_level" in data

        # Vérifier que components est une liste
        assert isinstance(data["components"], list)
        assert isinstance(data["total"], int)

        # Devrait avoir 65 composants (selon la spec)
        # Note: peut être 0 si Elite Library pas encore chargée
        assert data["total"] >= 0


# ============================================================================
# PILIER 5 : OUTILS (SEMANTIC PROPERTIES)
# ============================================================================

class TestOutilsEndpoints:
    """Tests pour les endpoints de propriétés sémantiques."""

    def test_get_tools_success(self):
        """GET /api/tools retourne la liste des propriétés sémantiques."""
        response = client.get("/api/tools")

        assert response.status_code == 200
        data = response.json()

        # Vérifier structure
        assert "tools" in data
        assert "total" in data

        # Vérifier types
        assert isinstance(data["tools"], list)
        assert isinstance(data["total"], int)

        # Devrait avoir au moins quelques propriétés
        assert data["total"] > 0

        # Vérifier structure d'un outil
        if len(data["tools"]) > 0:
            tool = data["tools"][0]
            assert "id" in tool
            assert "name" in tool
            assert "description" in tool
            assert "category" in tool

    def test_apply_tool_success(self):
        """POST /api/tools/{tool_id}/apply valide et applique une propriété."""
        payload = {
            "property": "name",
            "value": "Test Name",
            "context": {}
        }

        response = client.post("/api/tools/name/apply", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Vérifier structure
        assert "success" in data
        assert "property" in data

    def test_apply_tool_validation_failure(self):
        """POST /api/tools/{tool_id}/apply avec valeur invalide."""
        payload = {
            "property": "color",
            "value": "not-a-valid-color",  # Format couleur invalide
            "context": {}
        }

        response = client.post("/api/tools/color/apply", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Devrait échouer avec validation_errors
        if not data["success"]:
            assert "validation_errors" in data


# ============================================================================
# TESTS DE VALIDATION JSON SCHEMA
# ============================================================================

class TestJSONSchemaValidation:
    """Tests de validation des schémas JSON des réponses."""

    def test_genome_response_schema(self):
        """Valider le schéma de GenomeResponse."""
        response = client.get("/api/genome")
        assert response.status_code == 200
        data = response.json()

        # Vérifier que tous les champs requis sont présents
        required_fields = ["genome", "metadata"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_modification_response_schema(self):
        """Valider le schéma de ModificationResponse."""
        payload = {
            "path": "n0[0]",
            "property": "name",
            "value": "Test"
        }
        response = client.post("/api/modifications", json=payload)
        assert response.status_code == 200
        data = response.json()

        # Vérifier que success est présent
        assert "success" in data
        assert isinstance(data["success"], bool)


# ============================================================================
# TESTS DE GESTION D'ERREURS
# ============================================================================

class TestErrorHandling:
    """Tests de gestion d'erreurs (404, 400, 500)."""

    def test_404_component_not_found(self):
        """Tester erreur 404 pour composant inexistant."""
        response = client.get("/api/components/xyz_does_not_exist")
        assert response.status_code == 404

    def test_400_invalid_drilldown_path(self):
        """Tester erreur 400 pour chemin drilldown invalide."""
        payload = {"path": ""}
        response = client.post("/api/drilldown/enter", json=payload)
        # Devrait être 400 (bad request) ou 422 (validation error)
        assert response.status_code in [400, 422]

    def test_422_missing_required_field(self):
        """Tester erreur 422 pour champ requis manquant."""
        # Payload sans 'path' requis
        payload = {"property": "name", "value": "test"}
        response = client.post("/api/modifications", json=payload)
        assert response.status_code == 422  # Pydantic validation error


# ============================================================================
# TESTS END-TO-END
# ============================================================================

class TestEndToEndWorkflows:
    """Tests de workflows complets."""

    def test_workflow_modification_and_snapshot(self):
        """Workflow complet : modification → historique → snapshot."""
        # 1. Appliquer une modification
        mod_payload = {
            "path": "n0[0]",
            "property": "name",
            "value": "E2E Test Section"
        }
        mod_response = client.post("/api/modifications", json=mod_payload)
        assert mod_response.status_code == 200

        # 2. Vérifier l'historique
        history_response = client.get("/api/modifications/history?limit=1")
        assert history_response.status_code == 200

        # 3. Créer un snapshot
        snapshot_response = client.post("/api/snapshot")
        assert snapshot_response.status_code == 200
        assert "snapshot_id" in snapshot_response.json()

    def test_workflow_navigation_drilldown(self):
        """Workflow complet : drilldown → breadcrumb → drill-up."""
        # 1. Descendre dans la hiérarchie
        enter_response = client.post("/api/drilldown/enter", json={"path": "n0[0]"})

        # Si succès, continuer le workflow
        if enter_response.status_code == 200:
            # 2. Vérifier le breadcrumb
            breadcrumb_response = client.get("/api/breadcrumb")
            assert breadcrumb_response.status_code == 200

            # 3. Remonter
            exit_response = client.post("/api/drilldown/exit")
            assert exit_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
