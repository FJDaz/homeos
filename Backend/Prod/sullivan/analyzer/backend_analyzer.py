"""BackendAnalyzer - Analyse backend existant et infère fonction globale métier."""
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import ast
import re
from loguru import logger

from ...models.agent_router import AgentRouter
from ...models.plan_reader import Step


class GlobalFunction:
    """Représente la fonction globale métier d'un projet backend."""
    
    def __init__(
        self,
        product_type: str,
        actors: List[str],
        business_flows: List[str],
        use_cases: List[str]
    ):
        """
        Initialise la fonction globale métier.

        Args:
            product_type: Type de produit (e-commerce, SaaS, dashboard, etc.)
            actors: Liste des acteurs (admin, client, vendeur, etc.)
            business_flows: Liste des flux métier principaux
            use_cases: Liste des cas d'usage
        """
        self.product_type = product_type
        self.actors = actors
        self.business_flows = business_flows
        self.use_cases = use_cases
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire."""
        return {
            "product_type": self.product_type,
            "actors": self.actors,
            "business_flows": self.business_flows,
            "use_cases": self.use_cases
        }


class BackendAnalyzer:
    """
    Analyseur de structure de projet backend.
    
    Analyse un backend existant (généré par Homeos) pour comprendre sa fonction globale :
    - Type de produit (e-commerce, SaaS, dashboard, etc.)
    - Acteurs (admin, client, vendeur, etc.)
    - Flux métier principaux
    - Cas d'usage
    
    Détecte automatiquement les intents depuis :
    - Routes API (FastAPI/Flask)
    - Modèles de données (Pydantic/SQLAlchemy)
    - Schémas de base de données
    - Métadonnées Homeos (plans JSON, metrics, logs)
    - Annotations optionnelles @sullivan_intent()
    """
    
    def __init__(self, backend_path: Path):
        """
        Initialise l'analyseur.

        Args:
            backend_path: Chemin vers le projet backend à analyser
        """
        self.backend_path = Path(backend_path)
        self.api_routes: List[Dict[str, Any]] = []
        self.models: List[Dict[str, Any]] = []
        self.intents: List[Dict[str, Any]] = []
        self.homeos_metadata: Dict[str, Any] = {}
        self.agent_router: Optional[AgentRouter] = None
        
        logger.info(f"BackendAnalyzer initialized for path: {self.backend_path}")
    
    def analyze_project_structure(self) -> GlobalFunction:
        """
        Analyse la structure complète du projet backend.

        Returns:
            GlobalFunction: La fonction globale métier du projet
        """
        logger.info("Starting project structure analysis")
        
        # Analyser les routes API
        self.analyze_api_routes()
        
        # Analyser les modèles de données
        self.analyze_models()
        
        # Détecter les intents
        self.detect_intents()
        
        # Analyser les métadonnées Homeos
        self.analyze_homeos_metadata()
        
        # Inférer la fonction globale
        global_function = self.infer_global_function()
        
        logger.info(f"Analysis complete. Product type: {global_function.product_type}")
        return global_function
    
    def analyze_api_routes(self) -> None:
        """
        Analyse les routes API du projet (FastAPI/Flask).

        Extrait les endpoints, méthodes HTTP, paramètres.
        """
        logger.info("Analyzing API routes")
        
        # Chercher les fichiers FastAPI
        api_files = list(self.backend_path.rglob("**/api.py"))
        api_files.extend(list(self.backend_path.rglob("**/routes.py")))
        api_files.extend(list(self.backend_path.rglob("**/endpoints.py")))
        
        for api_file in api_files:
            try:
                content = api_file.read_text(encoding="utf-8")
                
                # Parser les routes FastAPI (@app.get, @app.post, etc.)
                route_patterns = [
                    (r'@app\.(get|post|put|delete|patch)\s*\(["\']([^"\']+)["\']', r'\1', r'\2'),
                    (r'@router\.(get|post|put|delete|patch)\s*\(["\']([^"\']+)["\']', r'\1', r'\2'),
                ]
                
                for pattern, method_group, path_group in route_patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        method = match.group(1).upper()
                        path = match.group(2)
                        self.api_routes.append({
                            "method": method,
                            "path": path,
                            "file": str(api_file.relative_to(self.backend_path))
                        })
            except Exception as e:
                logger.warning(f"Error analyzing {api_file}: {e}")
        
        logger.info(f"Found {len(self.api_routes)} API routes")
    
    def analyze_models(self) -> None:
        """
        Analyse les modèles de données (Pydantic/SQLAlchemy).

        Extrait les champs, types, relations.
        """
        logger.info("Analyzing data models")
        
        # Chercher les fichiers de modèles
        model_files = list(self.backend_path.rglob("**/models/*.py"))
        model_files.extend(list(self.backend_path.rglob("**/model.py")))
        
        for model_file in model_files:
            try:
                content = model_file.read_text(encoding="utf-8")
                tree = ast.parse(content)
                
                # Parser les classes Pydantic (BaseModel) et SQLAlchemy
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Vérifier si c'est un modèle Pydantic ou SQLAlchemy
                        bases = [base.id if isinstance(base, ast.Name) else "" for base in node.bases]
                        if "BaseModel" in bases or "db.Model" in bases or "DeclarativeBase" in bases:
                            fields = []
                            for item in node.body:
                                if isinstance(item, ast.AnnAssign) and item.target:
                                    field_name = item.target.id if isinstance(item.target, ast.Name) else ""
                                    if field_name:
                                        fields.append(field_name)
                            
                            self.models.append({
                                "name": node.name,
                                "fields": fields,
                                "file": str(model_file.relative_to(self.backend_path))
                            })
            except Exception as e:
                logger.warning(f"Error analyzing {model_file}: {e}")
        
        logger.info(f"Found {len(self.models)} data models")
    
    def detect_intents(self) -> None:
        """
        Détecte les intents automatiquement depuis le code et les logs.
        
        Supporte aussi les annotations optionnelles @sullivan_intent().
        """
        logger.info("Detecting intents")
        
        # Détecter depuis les routes API
        for route in self.api_routes:
            path = route["path"]
            method = route["method"]
            
            # Inférer intent depuis le chemin et la méthode
            intent = {
                "type": "api_endpoint",
                "method": method,
                "path": path,
                "description": f"{method} {path}"
            }
            self.intents.append(intent)
        
        # Détecter depuis les modèles
        for model in self.models:
            intent = {
                "type": "data_model",
                "model": model["name"],
                "fields": model["fields"],
                "description": f"Model {model['name']} with fields: {', '.join(model['fields'])}"
            }
            self.intents.append(intent)
        
        # Chercher les annotations @sullivan_intent()
        for py_file in self.backend_path.rglob("**/*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                if "@sullivan_intent" in content:
                    # Parser les annotations (simplifié)
                    matches = re.finditer(r'@sullivan_intent\(["\']([^"\']+)["\']\)', content)
                    for match in matches:
                        intent_desc = match.group(1)
                        self.intents.append({
                            "type": "explicit",
                            "description": intent_desc,
                            "file": str(py_file.relative_to(self.backend_path))
                        })
            except Exception:
                pass
        
        logger.info(f"Detected {len(self.intents)} intents")
    
    def analyze_homeos_metadata(self) -> None:
        """
        Analyse les métadonnées Homeos (plans JSON, metrics, logs, sullivan_intents.json).
        """
        logger.info("Analyzing Homeos metadata")
        
        # Chercher les plans JSON
        plan_files = list(self.backend_path.rglob("**/*.plan.json"))
        plan_files.extend(list(self.backend_path.rglob("**/plan.json")))
        
        for plan_file in plan_files:
            try:
                with open(plan_file, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)
                    self.homeos_metadata.setdefault("plans", []).append({
                        "file": str(plan_file.relative_to(self.backend_path)),
                        "data": plan_data
                    })
            except Exception as e:
                logger.warning(f"Error reading plan {plan_file}: {e}")
        
        # Chercher sullivan_intents.json
        intents_file = self.backend_path / "sullivan_intents.json"
        if intents_file.exists():
            try:
                with open(intents_file, 'r', encoding='utf-8') as f:
                    intents_data = json.load(f)
                    self.homeos_metadata["sullivan_intents"] = intents_data
            except Exception as e:
                logger.warning(f"Error reading sullivan_intents.json: {e}")
        
        logger.info(f"Found {len(self.homeos_metadata.get('plans', []))} Homeos plans")
    
    def infer_global_function(self) -> GlobalFunction:
        """
        Infère la fonction globale métier à partir de l'analyse.

        Returns:
            GlobalFunction: La fonction globale identifiée
        """
        logger.info("Inferring global function")
        
        # Initialiser AgentRouter pour utiliser LLM si nécessaire
        if not self.agent_router:
            self.agent_router = AgentRouter(execution_mode="BUILD")
        
        # Inférer le type de produit
        product_type = self.infer_product_type()
        
        # Inférer les acteurs
        actors = self.infer_actors()
        
        # Inférer les flux métier
        business_flows = self.infer_business_flows()
        
        # Inférer les cas d'usage
        use_cases = self.infer_use_cases()
        
        return GlobalFunction(
            product_type=product_type,
            actors=actors,
            business_flows=business_flows,
            use_cases=use_cases
        )
    
    def infer_product_type(self) -> str:
        """
        Infère le type de produit depuis les routes et modèles.

        Returns:
            Type de produit identifié
        """
        # Analyser les routes pour identifier le type
        route_paths = [r["path"] for r in self.api_routes]
        route_paths_str = " ".join(route_paths)
        
        # Heuristiques simples
        if any(keyword in route_paths_str.lower() for keyword in ["product", "cart", "order", "checkout"]):
            return "e-commerce"
        elif any(keyword in route_paths_str.lower() for keyword in ["user", "subscription", "plan", "billing"]):
            return "SaaS"
        elif any(keyword in route_paths_str.lower() for keyword in ["dashboard", "analytics", "metrics", "report"]):
            return "dashboard"
        elif any(keyword in route_paths_str.lower() for keyword in ["chat", "message", "conversation"]):
            return "chatbot"
        else:
            return "web-application"
    
    def infer_actors(self) -> List[str]:
        """
        Infère les acteurs depuis les routes et modèles.

        Returns:
            Liste des acteurs identifiés
        """
        actors = set()
        
        route_paths = [r["path"] for r in self.api_routes]
        route_paths_str = " ".join(route_paths)
        
        # Détecter les acteurs depuis les chemins
        if "admin" in route_paths_str.lower():
            actors.add("admin")
        if "user" in route_paths_str.lower() or "client" in route_paths_str.lower():
            actors.add("user")
        if "vendor" in route_paths_str.lower() or "seller" in route_paths_str.lower():
            actors.add("vendor")
        
        # Si aucun acteur détecté, ajouter "user" par défaut
        if not actors:
            actors.add("user")
        
        return sorted(list(actors))
    
    def infer_business_flows(self) -> List[str]:
        """
        Infère les flux métier principaux.

        Returns:
            Liste des flux métier identifiés
        """
        flows = []
        
        route_paths = [r["path"] for r in self.api_routes]
        route_paths_str = " ".join(route_paths)
        methods = [r["method"] for r in self.api_routes]
        
        # Détecter CRUD
        if any(m in methods for m in ["GET", "POST", "PUT", "DELETE"]):
            flows.append("CRUD")
        
        # Détecter authentification
        if any(keyword in route_paths_str.lower() for keyword in ["login", "auth", "register", "logout"]):
            flows.append("Authentication")
        
        # Détecter paiement
        if any(keyword in route_paths_str.lower() for keyword in ["payment", "checkout", "billing"]):
            flows.append("Payment")
        
        # Détecter recherche
        if any(keyword in route_paths_str.lower() for keyword in ["search", "query", "filter"]):
            flows.append("Search")
        
        return flows if flows else ["General"]
    
    def infer_use_cases(self) -> List[str]:
        """
        Infère les cas d'usage principaux.

        Returns:
            Liste des cas d'usage identifiés
        """
        use_cases = []
        
        route_paths = [r["path"] for r in self.api_routes]
        route_paths_str = " ".join(route_paths)
        
        # Inférer depuis les routes
        if "product" in route_paths_str.lower() and "order" in route_paths_str.lower():
            use_cases.append("Purchase product")
        
        if "user" in route_paths_str.lower() and "register" in route_paths_str.lower():
            use_cases.append("User registration")
        
        if "dashboard" in route_paths_str.lower():
            use_cases.append("View dashboard")
        
        if "chat" in route_paths_str.lower() or "message" in route_paths_str.lower():
            use_cases.append("Chat conversation")
        
        return use_cases if use_cases else ["General usage"]


# Exemple d'utilisation
if __name__ == "__main__":
    analyzer = BackendAnalyzer(Path("/path/to/backend"))
    global_function = analyzer.analyze_project_structure()
    print(f"Product type: {global_function.product_type}")
    print(f"Actors: {global_function.actors}")
    print(f"Business flows: {global_function.business_flows}")
    print(f"Use cases: {global_function.use_cases}")

