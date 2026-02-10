"""
Tests unitaires pour le module Stenciler (Étape 4 : Composants Défaut)
"""

import pytest
import json
import tempfile
import os
from pathlib import Path

# Ajouter le path pour importer sullivan
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Backend.Prod.sullivan.identity import Stenciler


@pytest.fixture
def sample_genome():
    """Fixture retournant un genome de test."""
    return {
        "genome_version": "3.0-test",
        "metadata": {"confidence_global": 0.85},
        "n0_phases": [
            {
                "id": "phase_1_ir",
                "name": "Intent Refactoring",
                "description": "Test phase",
                "order": 1,
                "n1_sections": [
                    {
                        "id": "section_ir_report",
                        "name": "Rapport IR",
                        "n2_features": [
                            {
                                "id": "feature_ir_table",
                                "name": "Tableau Organes",
                                "n3_components": [
                                    {
                                        "id": "comp_ir_table",
                                        "name": "Vue Rapport IR",
                                        "endpoint": "/studio/reports/ir",
                                        "method": "GET",
                                        "visual_hint": "table",
                                        "description_ui": "Tableau des organes"
                                    },
                                    {
                                        "id": "comp_ir_detail",
                                        "name": "Détail Organe",
                                        "endpoint": "/studio/drilldown",
                                        "method": "GET",
                                        "visual_hint": "card",
                                        "description_ui": "Carte détaillant un organe"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "id": "phase_2_arbiter",
                "name": "Arbitrage",
                "description": "Test phase 2",
                "order": 2,
                "n1_sections": [
                    {
                        "id": "section_arbiter",
                        "name": "Arbitrage HCI",
                        "n2_features": [
                            {
                                "id": "feature_stencils",
                                "name": "Stencils",
                                "n3_components": [
                                    {
                                        "id": "comp_stencil_card",
                                        "name": "Carte Stencil",
                                        "endpoint": "/studio/arbitrage/forms",
                                        "method": "GET",
                                        "visual_hint": "stencil-card",
                                        "description_ui": "Carte pouvoir avec toggle"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def stenciler_with_temp_genome(sample_genome):
    """Fixture créant un Stenciler avec un fichier genome temporaire."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_genome, f)
        temp_path = f.name
    
    stenciler = Stenciler(genome_path=temp_path)
    yield stenciler
    
    # Cleanup
    os.unlink(temp_path)


class TestStencilerInitialization:
    """Tests d'initialisation du Stenciler."""
    
    def test_load_genome_success(self, stenciler_with_temp_genome):
        """Test que le genome est chargé correctement."""
        assert stenciler_with_temp_genome.genome is not None
        assert "n0_phases" in stenciler_with_temp_genome.genome
        assert len(stenciler_with_temp_genome.genome["n0_phases"]) == 2
    
    def test_load_genome_file_not_found(self):
        """Test le comportement quand le fichier n'existe pas."""
        stenciler = Stenciler(genome_path="/nonexistent/path/genome.json")
        assert stenciler.genome == {"n0_phases": []}
    
    def test_default_genome_path(self):
        """Test que le chemin par défaut est utilisé."""
        stenciler = Stenciler()
        assert "Genome_OPTIMISE_2026-02-06" in stenciler.genome_path


class TestGetCorps:
    """Tests de la méthode get_corps."""
    
    def test_get_corps_returns_list(self, stenciler_with_temp_genome):
        """Test que get_corps retourne une liste."""
        corps = stenciler_with_temp_genome.get_corps()
        assert isinstance(corps, list)
        assert len(corps) == 2
    
    def test_get_corps_structure(self, stenciler_with_temp_genome):
        """Test la structure des corps retournés."""
        corps = stenciler_with_temp_genome.get_corps()
        first_corps = corps[0]
        
        assert "id" in first_corps
        assert "name" in first_corps
        assert "description" in first_corps
        assert "order" in first_corps
        assert "n_sections" in first_corps
        
        assert first_corps["id"] == "phase_1_ir"
        assert first_corps["name"] == "Intent Refactoring"
        assert first_corps["n_sections"] == 1
    
    def test_get_corps_empty_genome(self):
        """Test get_corps avec un genome vide."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"n0_phases": []}, f)
            temp_path = f.name
        
        try:
            stenciler = Stenciler(genome_path=temp_path)
            corps = stenciler.get_corps()
            assert corps == []
        finally:
            os.unlink(temp_path)


class TestGetComponentsForCorps:
    """Tests de la méthode get_components_for_corps."""
    
    def test_get_components_existing_corps(self, stenciler_with_temp_genome):
        """Test récupération des composants d'un corps existant."""
        components = stenciler_with_temp_genome.get_components_for_corps("phase_1_ir")
        assert len(components) == 2
        
        # Vérifier la structure
        first_comp = components[0]
        assert "id" in first_comp
        assert "name" in first_comp
        assert "endpoint" in first_comp
        assert "method" in first_comp
        assert "visual_hint" in first_comp
    
    def test_get_components_nonexistent_corps(self, stenciler_with_temp_genome):
        """Test récupération avec un corps inexistant."""
        components = stenciler_with_temp_genome.get_components_for_corps("nonexistent")
        assert components == []
    
    def test_get_components_structure(self, stenciler_with_temp_genome):
        """Test la structure complète des composants."""
        components = stenciler_with_temp_genome.get_components_for_corps("phase_2_arbiter")
        assert len(components) == 1
        
        comp = components[0]
        assert comp["id"] == "comp_stencil_card"
        assert comp["name"] == "Carte Stencil"
        assert comp["endpoint"] == "/studio/arbitrage/forms"
        assert comp["method"] == "GET"
        assert comp["visual_hint"] == "stencil-card"


class TestGenerateStencilSvg:
    """Tests de la génération de SVG."""
    
    def test_generate_svg_returns_string(self, stenciler_with_temp_genome):
        """Test que la méthode retourne une chaîne SVG."""
        svg = stenciler_with_temp_genome.generate_stencil_svg("phase_1_ir")
        assert isinstance(svg, str)
        assert "<svg" in svg
        assert "</svg>" in svg
    
    def test_generate_svg_contains_rect(self, stenciler_with_temp_genome):
        """Test que le SVG contient des éléments graphiques."""
        svg = stenciler_with_temp_genome.generate_stencil_svg("phase_1_ir")
        assert "<rect" in svg
    
    def test_generate_svg_different_types(self, stenciler_with_temp_genome):
        """Test que différents types produisent des SVG différents."""
        svg_table = stenciler_with_temp_genome.generate_stencil_svg("phase_1_ir")  # table
        svg_card = stenciler_with_temp_genome.generate_stencil_svg("phase_2_arbiter")  # card
        
        # Les SVG doivent être différents
        assert svg_table != svg_card
    
    def test_generate_svg_default_for_unknown(self, stenciler_with_temp_genome):
        """Test que les phases inconnues retournent un SVG par défaut."""
        svg = stenciler_with_temp_genome.generate_stencil_svg("unknown_phase")
        assert "<svg" in svg
        assert "</svg>" in svg


class TestSelection:
    """Tests des méthodes de sélection (keep/reserve)."""
    
    def test_set_selection_keep(self, stenciler_with_temp_genome):
        """Test marquer un composant comme 'keep'."""
        stenciler_with_temp_genome.set_selection("comp_ir_table", "keep")
        assert stenciler_with_temp_genome.get_selection("comp_ir_table") == "keep"
    
    def test_set_selection_reserve(self, stenciler_with_temp_genome):
        """Test marquer un composant comme 'reserve'."""
        stenciler_with_temp_genome.set_selection("comp_ir_table", "reserve")
        assert stenciler_with_temp_genome.get_selection("comp_ir_table") == "reserve"
    
    def test_set_selection_invalid_status(self, stenciler_with_temp_genome):
        """Test qu'un statut invalide lève une erreur."""
        with pytest.raises(ValueError, match="Status doit être 'keep' ou 'reserve'"):
            stenciler_with_temp_genome.set_selection("comp_ir_table", "invalid")
    
    def test_get_selection_nonexistent(self, stenciler_with_temp_genome):
        """Test récupération d'un composant non sélectionné."""
        assert stenciler_with_temp_genome.get_selection("nonexistent") is None
    
    def test_get_all_selections(self, stenciler_with_temp_genome):
        """Test récupération de toutes les sélections."""
        stenciler_with_temp_genome.set_selection("comp1", "keep")
        stenciler_with_temp_genome.set_selection("comp2", "reserve")
        
        selections = stenciler_with_temp_genome.get_all_selections()
        assert selections == {"comp1": "keep", "comp2": "reserve"}
    
    def test_selections_isolation(self, stenciler_with_temp_genome):
        """Test que get_all_selections retourne une copie."""
        stenciler_with_temp_genome.set_selection("comp1", "keep")
        selections = stenciler_with_temp_genome.get_all_selections()
        selections["comp2"] = "reserve"  # Modification de la copie
        
        # L'original ne doit pas être modifié
        assert "comp2" not in stenciler_with_temp_genome.selections


class TestGetValidatedGenome:
    """Tests de la méthode get_validated_genome."""
    
    def test_validated_genome_keep_only(self, stenciler_with_temp_genome):
        """Test que seuls les composants 'keep' sont conservés."""
        stenciler_with_temp_genome.set_selection("comp_ir_table", "keep")
        stenciler_with_temp_genome.set_selection("comp_ir_detail", "reserve")
        stenciler_with_temp_genome.set_selection("comp_stencil_card", "reserve")
        
        validated = stenciler_with_temp_genome.get_validated_genome()
        
        # Vérifier la structure
        assert "n0_phases" in validated
        assert len(validated["n0_phases"]) == 1  # Seulement phase_1_ir
        
        # Vérifier que comp_ir_detail n'est pas là
        components = validated["n0_phases"][0]["n1_sections"][0]["n2_features"][0]["n3_components"]
        assert len(components) == 1
        assert components[0]["id"] == "comp_ir_table"
    
    def test_validated_genome_empty_selections(self, stenciler_with_temp_genome):
        """Test que tous les composants sont conservés si pas de sélections."""
        validated = stenciler_with_temp_genome.get_validated_genome()
        
        # Tous les composants doivent être là (par défaut 'keep')
        phase_1 = validated["n0_phases"][0]
        components = phase_1["n1_sections"][0]["n2_features"][0]["n3_components"]
        assert len(components) == 2
    
    def test_validated_genome_structure_preserved(self, stenciler_with_temp_genome):
        """Test que la structure du genome est préservée."""
        stenciler_with_temp_genome.set_selection("comp_ir_table", "keep")
        validated = stenciler_with_temp_genome.get_validated_genome()
        
        assert validated["genome_version"] == "3.0-test"
        assert validated["metadata"]["confidence_global"] == 0.85


class TestGetStats:
    """Tests de la méthode get_stats."""
    
    def test_stats_empty(self, stenciler_with_temp_genome):
        """Test les stats sans sélections."""
        stats = stenciler_with_temp_genome.get_stats()
        assert stats == {"total": 0, "keep": 0, "reserve": 0}
    
    def test_stats_with_selections(self, stenciler_with_temp_genome):
        """Test les stats avec des sélections."""
        stenciler_with_temp_genome.set_selection("comp1", "keep")
        stenciler_with_temp_genome.set_selection("comp2", "keep")
        stenciler_with_temp_genome.set_selection("comp3", "reserve")
        
        stats = stenciler_with_temp_genome.get_stats()
        assert stats["total"] == 3
        assert stats["keep"] == 2
        assert stats["reserve"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
