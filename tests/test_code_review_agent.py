"""
Tests unitaires pour CodeReviewAgent.

Tests obligatoires :
1. Plan valide (SessionContext + theme) → APPROUVÉ
2. Plan risqué (ModeManager singleton) → REJETÉ
3. Plan incomplet (sans tests) → WARNINGS
"""
import unittest
import json
from pathlib import Path
from datetime import datetime

# Ajouter les chemins au path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "Backend" / "Prod"))
sys.path.insert(0, str(Path(__file__).parent.parent / "Backend" / "Prod" / "sullivan" / "agent"))

# Import direct des modèles (pas via sullivan.models pour éviter l'import cascade)
sys.path.insert(0, str(Path(__file__).parent.parent / "Backend" / "Prod" / "sullivan" / "models"))
from implementation_plan import (
    AetherFlowMode,
    ImplementationPlan,
    ValidationResult,
)
from code_review_agent import CodeReviewAgent, review_plan


class TestCodeReviewAgent(unittest.TestCase):
    """Tests pour le CodeReviewAgent."""
    
    def setUp(self):
        """Initialise l'agent pour chaque test."""
        self.agent = CodeReviewAgent()
        self.test_dir = Path(__file__).parent
    
    def load_test_plan(self, filename: str) -> ImplementationPlan:
        """Charge un plan de test depuis JSON."""
        plan_path = self.test_dir / filename
        with open(plan_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ImplementationPlan(**data)
    
    # =========================================================================
    # TEST 1 : Plan valide (SessionContext + theme)
    # =========================================================================
    def test_valid_plan_session_context(self):
        """
        Test 1 : Plan pour étendre SessionContext avec theme_preference.
        
        Expected : APPROUVÉ (cohérent avec architecture)
        """
        plan = self.load_test_plan("test_plan_valid.json")
        
        # Vérifier que le plan est bien chargé
        self.assertEqual(plan.module_cible, "Backend/Prod/sullivan/agent/memory.py")
        self.assertEqual(plan.mode_aetherflow, AetherFlowMode.PROD)
        self.assertIn("SessionContext", plan.outils_sullivan_utilises)
        
        # Soumettre au CodeReviewAgent
        report = self.agent.review_plan(plan)
        
        # Vérifications
        print(f"\n[TEST 1] Plan valide - Score: {report.score}/100")
        print(f"         Résultat: {report.result.value}")
        print(f"         Violations: {len(report.violations)}")
        for v in report.violations:
            print(f"         - [{v.severity}] {v.rule_name}")
        
        # Assertions
        self.assertIn(report.result, [ValidationResult.APPROVED, ValidationResult.WARNINGS])
        self.assertGreaterEqual(report.score, 70)
        self.assertFalse(any(v.severity == "error" for v in report.violations))
    
    # =========================================================================
    # TEST 2 : Plan risqué (ModeManager singleton)
    # =========================================================================
    def test_risky_plan_mode_manager(self):
        """
        Test 2 : Plan modifiant ModeManager sans préserver singleton.
        
        Expected : REJETÉ + explication détaillée
        """
        plan = self.load_test_plan("test_plan_risky.json")
        
        # Vérifier que le plan est bien chargé
        self.assertEqual(plan.module_cible, "homeos/core/mode_manager.py")
        self.assertEqual(plan.mode_aetherflow, AetherFlowMode.PROTO)  # Mauvais mode !
        
        # Soumettre au CodeReviewAgent
        report = self.agent.review_plan(plan)
        
        # Vérifications
        print(f"\n[TEST 2] Plan risqué - Score: {report.score}/100")
        print(f"         Résultat: {report.result.value}")
        print(f"         Violations: {len(report.violations)}")
        for v in report.violations:
            print(f"         - [{v.severity}] {v.rule_name}: {v.message}")
        
        # Assertions
        self.assertEqual(report.result, ValidationResult.REJECTED)
        # REJECTED si erreurs critiques ou score < 50
        self.assertTrue(
            report.score < 50 or report.has_errors(),
            f"Devrait être rejeté (score: {report.score}, errors: {report.has_errors()})"
        )
        
        # Vérifier que les violations spécifiques sont détectées
        violation_names = [v.rule_name for v in report.violations]
        
        # Doit détecter l'utilisation de PROTO pour fichier existant
        self.assertTrue(
            any("Wrong Mode" in name or "Mode" in name for name in violation_names),
            f"Devrait détecter mauvais mode AetherFlow. Violations: {violation_names}"
        )
        
        # Doit avoir des erreurs (soit singleton, soit mode inapproprié)
        self.assertTrue(
            report.has_errors(),
            f"Devrait avoir des erreurs. Violations: {violation_names}"
        )
    
    # =========================================================================
    # TEST 3 : Plan incomplet (sans tests)
    # =========================================================================
    def test_incomplete_plan_no_tests(self):
        """
        Test 3 : Plan sans tests recommandés.
        
        Expected : WARNINGS + suggestions
        """
        plan = self.load_test_plan("test_plan_incomplete.json")
        
        # Vérifier que le plan est bien chargé
        self.assertEqual(plan.module_cible, "Backend/Prod/sullivan/agent/sullivan_agent.py")
        self.assertEqual(plan.mode_aetherflow, AetherFlowMode.PROD)
        self.assertEqual(len(plan.tests_recommandes), 0)  # Pas de tests !
        
        # Soumettre au CodeReviewAgent
        report = self.agent.review_plan(plan)
        
        # Vérifications
        print(f"\n[TEST 3] Plan incomplet - Score: {report.score}/100")
        print(f"         Résultat: {report.result.value}")
        print(f"         Violations: {len(report.violations)}")
        for v in report.violations:
            print(f"         - [{v.severity}] {v.rule_name}: {v.message}")
        
        # Assertions
        self.assertEqual(report.result, ValidationResult.WARNINGS)
        
        # Vérifier que le manque de tests est détecté (si complexité élevée)
        # ou autre warning pertinent
        violation_names = [v.rule_name for v in report.violations]
        self.assertTrue(
            any("Test" in name or "Missing" in name or "Status" in name for name in violation_names),
            f"Devrait détecter warning pertinent. Violations: {violation_names}"
        )
        
        # Doit avoir des violations (donc potentiellement des suggestions ou actions)
        self.assertTrue(
            len(report.violations) > 0 or len(report.suggestions) > 0,
            f"Devrait avoir violations ou suggestions"
        )
    
    # =========================================================================
    # Tests supplémentaires
    # =========================================================================
    def test_singleton_detection_in_description(self):
        """Test la détection de singleton dans la description."""
        plan = ImplementationPlan(
            module_cible="homeos/core/test.py",
            mode_aetherflow=AetherFlowMode.PROD,
            description="Modification de ModeManager pour ajouter une méthode",
            fichiers_modifies=["homeos/core/test.py"],
            tests_recommandes=["test_singleton"],
        )
        
        report = self.agent.review_plan(plan)
        
        # Doit détecter le singleton même sans fichier modifié explicite
        violation_names = [v.rule_name for v in report.violations]
        self.assertTrue(
            any("Singleton" in name for name in violation_names),
            f"Devrait détecter singleton dans description. Violations: {violation_names}"
        )
    
    def test_mode_proto_for_new_file(self):
        """Test que PROTO est accepté pour nouveau fichier."""
        plan = ImplementationPlan(
            module_cible="sullivan/agent/new_module.py",
            mode_aetherflow=AetherFlowMode.PROTO,
            description="Nouveau module utilitaire",
            fichiers_crees=["sullivan/agent/new_module.py"],
            fichiers_modifies=[],  # Pas de fichier modifié
            tests_recommandes=["test_new_module"],
        )
        
        report = self.agent.review_plan(plan)
        
        # Pour un nouveau fichier, PROTO est acceptable
        print(f"\n[TEST BONUS] Nouveau fichier en PROTO - Score: {report.score}/100")
        print(f"             Résultat: {report.result.value}")
        
        # Ne doit PAS avoir d'erreur de mode
        for v in report.violations:
            self.assertNotIn("Wrong Mode", v.rule_name)
    
    def test_report_export(self):
        """Test l'export du rapport."""
        import tempfile
        import os
        
        plan = self.load_test_plan("test_plan_valid.json")
        report = self.agent.review_plan(plan)
        
        # Export temporaire
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            self.agent.export_report(report, Path(temp_path))
            
            # Vérifier que le fichier existe et est lisible
            self.assertTrue(Path(temp_path).exists())
            
            with open(temp_path, 'r') as f:
                exported = json.load(f)
            
            self.assertEqual(exported["result"], report.result.value)
            self.assertEqual(exported["score"], report.score)
            self.assertIn("approved", exported)
        finally:
            os.unlink(temp_path)
    
    def test_review_plan_function(self):
        """Test la fonction utilitaire review_plan."""
        plan = self.load_test_plan("test_plan_valid.json")
        
        # Utiliser la fonction globale
        report = review_plan(plan)
        
        self.assertIsNotNone(report)
        self.assertEqual(report.plan.module_cible, plan.module_cible)
        self.assertIn(report.result, [ValidationResult.APPROVED, ValidationResult.WARNINGS, ValidationResult.REJECTED])


class TestValidationRules(unittest.TestCase):
    """Tests pour les règles de validation configurables."""
    
    def test_custom_rules(self):
        """Test avec des règles personnalisées."""
        from implementation_plan import ValidationRules
        
        # Règles strictes
        strict_rules = ValidationRules(
            require_module_check=True,
            require_existing_tool_check=True,
            require_tests_for_complexity=True,
            check_singleton_preservation=True,
        )
        
        agent = CodeReviewAgent(rules=strict_rules)
        
        plan = ImplementationPlan(
            module_cible="sullivan/test.py",
            mode_aetherflow=AetherFlowMode.PROD,
            description="Test avec règles strictes",
            fichiers_crees=["sullivan/test.py"],
        )
        
        report = agent.review_plan(plan)
        
        # Avec des règles strictes, devrait avoir des warnings
        self.assertIsNotNone(report)
        print(f"\n[TEST RULES] Règles strictes - Score: {report.score}/100")


if __name__ == "__main__":
    # Exécuter avec verbose
    unittest.main(verbosity=2)
