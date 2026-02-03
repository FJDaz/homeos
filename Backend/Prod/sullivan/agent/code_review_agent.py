"""
CodeReviewAgent - Agent de revue de code pour validation des plans d'implémentation.

Valide les plans selon les règles HomeOS/Sullivan avant exécution.
Analyse en < 1 seconde, pas d'appels API externes.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

try:
    # Import relatif (quand utilisé comme package)
    from ..models.implementation_plan import (
        AetherFlowMode,
        ImplementationPlan,
        ReviewReport,
        RuleViolation,
        ValidationResult,
        ValidationRules,
        RULE_TEMPLATES,
    )
except ImportError:
    # Import absolu (quand utilisé directement)
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "models"))
    from implementation_plan import (
        AetherFlowMode,
        ImplementationPlan,
        ReviewReport,
        RuleViolation,
        ValidationResult,
        ValidationRules,
        RULE_TEMPLATES,
    )


class CodeReviewAgent:
    """
    Agent de revue de code pour le binôme Kimi/Claude-Code.
    
    Responsabilités :
    - Analyser les plans d'implémentation de Kimi
    - Vérifier la cohérence avec HomeOS/Sullivan
    - Identifier les conflits potentiels
    - Proposer des alternatives plus sûres
    - Générer un rapport de validation
    
    Example:
        >>> agent = CodeReviewAgent()
        >>> plan = ImplementationPlan(
        ...     module_cible="sullivan/agent",
        ...     mode_aetherflow=AetherFlowMode.PROD,
        ...     description="Ajout de fonctionnalité"
        ... )
        >>> report = agent.review_plan(plan)
        >>> print(report.result)  # APPROVED, WARNINGS, ou REJECTED
    """
    
    def __init__(self, rules: Optional[ValidationRules] = None):
        """
        Initialise le CodeReviewAgent.
        
        Args:
            rules: Configuration des règles de validation (défaut: ValidationRules())
        """
        self.rules = rules or ValidationRules()
        self.violations: List[RuleViolation] = []
        self.suggestions: List[str] = []
        
        logger.info("CodeReviewAgent initialized")
    
    def review_plan(self, plan: ImplementationPlan) -> ReviewReport:
        """
        Revue complète d'un plan d'implémentation.
        
        Args:
            plan: Plan à valider
            
        Returns:
            ReviewReport avec résultat, violations et suggestions
        """
        self.violations = []
        self.suggestions = []
        
        logger.info(f"Starting review for plan: {plan.module_cible}")
        
        # Exécuter toutes les validations
        self._validate_architecture_rules(plan)
        self._validate_mode_selection(plan)
        self._validate_risks(plan)
        self._validate_sullivan_specific(plan)
        
        # Calculer le score et le résultat
        score = self._calculate_score(plan)
        result = self._determine_result(score)
        
        report = ReviewReport(
            plan=plan,
            result=result,
            violations=self.violations,
            suggestions=self.suggestions,
            score=score,
            reviewed_at=datetime.now().isoformat(),
        )
        
        logger.info(f"Review completed: {result.value} (score: {score})")
        return report
    
    def _validate_architecture_rules(self, plan: ImplementationPlan) -> None:
        """Règle 1 : Cohérence Architecture."""
        # Vérifier consultation STATUS_REPORT
        if not plan.known_attention_points:
            self._add_violation(
                RULE_TEMPLATES["missing_status_report_check"],
                fichier_concerne=None,
            )
        
        # Vérifier utilisation outils existants
        if self.rules.require_existing_tool_check:
            self._check_existing_tools(plan)
        
        # Vérifier cohérence module
        if self.rules.require_module_check:
            self._check_module_exists(plan)
    
    def _validate_mode_selection(self, plan: ImplementationPlan) -> None:
        """Règle 2 : Utilisation des Modes."""
        if not self.rules.validate_mode_selection:
            return
        
        # Vérifier mode approprié selon les fichiers modifiés
        has_existing_files = len(plan.fichiers_modifies) > 0
        
        if has_existing_files and plan.mode_aetherflow == AetherFlowMode.PROTO:
            self._add_violation(
                {
                    "rule_name": "Wrong Mode for File Modification",
                    "severity": "error",
                    "message": "PROTO mode (-q) should not be used for modifying existing files",
                    "suggestion": "Use PROD (-f) or SURGICAL mode for file modifications",
                },
                fichier_concerne=plan.fichiers_modifies[0] if plan.fichiers_modifies else None,
            )
        
        # Vérifier utilisation outils Sullivan
        if self.rules.require_prod_for_existing_files:
            self._check_sullivan_tools_usage(plan)
    
    def _validate_risks(self, plan: ImplementationPlan) -> None:
        """Règle 3 : Gestion des Risques."""
        # Trop de risques identifiés
        if len(plan.risques_identifies) > self.rules.max_risks_allowed:
            self._add_violation(
                {
                    "rule_name": "Too Many Risks",
                    "severity": "warning",
                    "message": f"Plan identifies {len(plan.risques_identifies)} risks (max: {self.rules.max_risks_allowed})",
                    "suggestion": "Consider breaking down the implementation into smaller steps",
                },
                fichier_concerne=None,
            )
        
        # Tests manquants pour complexité
        if self.rules.require_tests_for_complexity:
            complexity_indicators = [
                len(plan.fichiers_modifies) > 3,
                len(plan.fichiers_crees) > 2,
                len(plan.etapes) > 5,
            ]
            is_complex = any(complexity_indicators)
            
            if is_complex and not plan.tests_recommandes:
                self._add_violation(
                    RULE_TEMPLATES["missing_tests"],
                    fichier_concerne=None,
                )
    
    def _validate_sullivan_specific(self, plan: ImplementationPlan) -> None:
        """Règles spécifiques HomeOS/Sullivan."""
        # Vérifier préservation singleton
        if self.rules.check_singleton_preservation:
            self._check_singleton_preservation(plan)
        
        # Vérifier compliance z-index
        if self.rules.check_z_index_compliance:
            self._check_z_index_compliance(plan)
        
        # Vérifier préservation mémoire Sullivan
        if self.rules.check_memory_preservation:
            self._check_memory_preservation(plan)
    
    def _check_existing_tools(self, plan: ImplementationPlan) -> None:
        """Vérifie si des outils Sullivan existants pourraient être utilisés."""
        # Patterns d'outils existants
        existing_tools = {
            "image": ["upload/image_preprocessor.py", "preprocess_for_gemini"],
            "frontend": ["modes/frontend_mode.py", "FrontendMode"],
            "design": ["modes/designer_mode.py", "DesignerMode"],
            "chat": ["agent/memory.py", "ConversationMemory"],
            "audit": ["auditor/sullivan_auditor.py", "audit_visual_output"],
        }
        
        description_lower = plan.description.lower()
        
        for tool_name, tool_refs in existing_tools.items():
            if tool_name in description_lower and tool_name not in str(plan.outils_sullivan_utilises).lower():
                # Vérifier si l'outil n'est pas déjà listé
                already_listed = any(
                    ref in str(plan.outils_sullivan_utilises) 
                    for ref in tool_refs
                )
                
                if not already_listed:
                    self._add_violation(
                        {
                            "rule_name": "Existing Tool Not Used",
                            "severity": "warning",
                            "message": f"Task involves '{tool_name}' but no existing Sullivan tool is used",
                            "suggestion": f"Consider using: {', '.join(tool_refs)}",
                        },
                        fichier_concerne=None,
                    )
    
    def _check_module_exists(self, plan: ImplementationPlan) -> None:
        """Vérifie que le module cible existe."""
        module_path = Path("Backend/Prod") / plan.module_cible.replace(".", "/")
        
        if not module_path.exists() and not module_path.with_suffix(".py").exists():
            # Module n'existe pas encore - warning si mode PROD
            if plan.mode_aetherflow == AetherFlowMode.PROD and not plan.fichiers_crees:
                self._add_violation(
                    {
                        "rule_name": "Module Does Not Exist",
                        "severity": "warning",
                        "message": f"Target module '{plan.module_cible}' does not exist",
                        "suggestion": "Use PROTO mode for new modules or specify files to create",
                    },
                    fichier_concerne=None,
                )
    
    def _check_sullivan_tools_usage(self, plan: ImplementationPlan) -> None:
        """Vérifie l'utilisation appropriée des outils Sullivan."""
        # Si modification fichier Python sans outils Sullivan → warning
        python_files = [f for f in plan.fichiers_modifies if f.endswith(".py")]
        
        if python_files and not plan.outils_sullivan_utilises:
            if "sullivan" in plan.module_cible.lower():
                self._add_violation(
                    {
                        "rule_name": "Missing Sullivan Tools",
                        "severity": "info",
                        "message": "Modifying Sullivan files without using Sullivan tools",
                        "suggestion": "Consider using appropriate Sullivan utilities",
                    },
                    fichier_concerne=python_files[0],
                )
    
    def _check_singleton_preservation(self, plan: ImplementationPlan) -> None:
        """Vérifie la préservation des patterns singleton."""
        singleton_patterns = [
            "ModeManager", "mode_manager",
            "PreferencesManager", "preferences_manager",
            "ConversationMemory", "_instance",
        ]
        
        description_and_files = f"{plan.description} {' '.join(plan.fichiers_modifies)}"
        
        for pattern in singleton_patterns:
            if pattern in description_and_files:
                # Vérifier si le plan mentionne explicitement la préservation
                preservation_keywords = ["singleton", "preserve", "conserver", "respecter"]
                has_preservation = any(
                    kw in plan.description.lower() 
                    for kw in preservation_keywords
                )
                
                if not has_preservation:
                    self._add_violation(
                        RULE_TEMPLATES["singleton_violation"],
                        fichier_concerne=plan.fichiers_modifies[0] if plan.fichiers_modifies else None,
                    )
                    break  # Une seule violation suffit
    
    def _check_z_index_compliance(self, plan: ImplementationPlan) -> None:
        """Vérifie la compliance z-index pour les modes HomeOS."""
        if plan.z_index_layers:
            # Si z-index spécifiés mais pas cohérent avec mode
            if "frontend" in plan.module_cible.lower() or "ui" in plan.module_cible.lower():
                valid_order = ["background", "content", "overlay", "modal", "notification", "system"]
                
                for i, layer in enumerate(plan.z_index_layers):
                    if layer not in valid_order:
                        self._add_violation(
                            RULE_TEMPLATES["z_index_violation"],
                            fichier_concerne=None,
                        )
                        break
    
    def _check_memory_preservation(self, plan: ImplementationPlan) -> None:
        """Vérifie la préservation de la mémoire Sullivan."""
        memory_keywords = ["SessionContext", "ConversationMemory", "session", "mémoire"]
        description_lower = plan.description.lower()
        
        for keyword in memory_keywords:
            if keyword.lower() in description_lower:
                # Vérifier si on mentionne SessionContext plutôt que nouveau système
                if "sessioncontext" in description_lower or "conversationmemory" in description_lower:
                    return  # OK, on utilise l'existant
                
                # Si on parle de mémoire mais pas de SessionContext → warning
                if keyword == "mémoire" or keyword == "session":
                    self._add_violation(
                        {
                            "rule_name": "Memory Pattern Violation",
                            "severity": "error",
                            "message": "Plan involves memory/session without using SessionContext",
                            "suggestion": "Use sullivan/agent/memory.py SessionContext instead of creating new system",
                        },
                        fichier_concerne=None,
                    )
                    break
    
    def _add_violation(self, template: Dict[str, str], fichier_concerne: Optional[str]) -> None:
        """Ajoute une violation à la liste."""
        violation = RuleViolation(
            rule_name=template["rule_name"],
            severity=template["severity"],
            message=template["message"],
            suggestion=template.get("suggestion"),
            fichier_concerne=fichier_concerne,
        )
        self.violations.append(violation)
    
    def _calculate_score(self, plan: ImplementationPlan) -> int:
        """Calcule le score de validation (0-100)."""
        score = 100
        
        # Pénalités par sévérité
        for violation in self.violations:
            if violation.severity == "error":
                score -= 25
            elif violation.severity == "warning":
                score -= 10
            elif violation.severity == "info":
                score -= 5
        
        # Bonus pour bonnes pratiques
        if plan.tests_recommandes:
            score += 5
        if plan.known_attention_points:
            score += 5
        if plan.z_index_layers:
            score += 5
        
        return max(0, min(100, score))
    
    def _determine_result(self, score: int) -> ValidationResult:
        """Détermine le résultat final selon le score."""
        has_errors = any(v.severity == "error" for v in self.violations)
        
        if has_errors or score < 50:
            return ValidationResult.REJECTED
        elif score < 80 or self.violations:
            return ValidationResult.WARNINGS
        else:
            return ValidationResult.APPROVED
    
    def export_report(self, report: ReviewReport, output_path: Path) -> None:
        """Exporte le rapport vers un fichier JSON."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"Report exported to {output_path}")


# Singleton instance pour usage global
code_review_agent = CodeReviewAgent()


def review_plan(plan: ImplementationPlan) -> ReviewReport:
    """
    Fonction utilitaire pour revue rapide.
    
    Args:
        plan: Plan à valider
        
    Returns:
        ReviewReport
    """
    return code_review_agent.review_plan(plan)


__all__ = [
    "CodeReviewAgent",
    "review_plan",
    "code_review_agent",
]
