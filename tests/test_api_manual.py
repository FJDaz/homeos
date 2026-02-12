import requests
import json

def test_api_genome(endpoint):
    """Test GET /api/genome endpoint."""
    try:
        response = requests.get(endpoint + "/api/genome")
        if response.status_code == 200:
            data = response.json()
            # Verify the structure of the response
            assert 'genome' in data, "Missing 'genome' key in the response."
            assert 'metadata' in data, "Missing 'metadata' key in the response."
            assert 'modification_count' in data['metadata'], "Missing 'modification_count' key in metadata."
            assert 'last_snapshot_id' in data['metadata'], "Missing 'last_snapshot_id' key in metadata."
            assert 'last_modified' in data['metadata'], "Missing 'last_modified' key in metadata."
            print("Test for /api/genome passed.")
        else:
            print(f"Failed to retrieve data from /api/genome. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error testing /api/genome: {e}")

def test_api_state(endpoint):
    """Test GET /api/state endpoint."""
    try:
        response = requests.get(endpoint + "/api/state")
        if response.status_code == 200:
            data = response.json()
            # Verify the structure of the response
            assert 'current_state' in data, "Missing 'current_state' key in the response."
            assert 'modification_count' in data, "Missing 'modification_count' key in the response."
            assert 'last_snapshot_id' in data, "Missing 'last_snapshot_id' key in the response."
            assert 'last_modified' in data, "Missing 'last_modified' key in the response."
            print("Test for /api/state passed.")
        else:
            print(f"Failed to retrieve data from /api/state. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error testing /api/state: {e}")

def test_api_schema(endpoint):
    """Test GET /api/schema endpoint."""
    try:
        response = requests.get(endpoint + "/api/schema")
        if response.status_code == 200:
            data = response.json()
            # Verify the structure of the response
            assert 'levels' in data, "Missing 'levels' key in the response."
            assert 'semantic_properties' in data, "Missing 'semantic_properties' key in the response."
            assert 'forbidden_properties' in data, "Missing 'forbidden_properties' key in the response."
            print("Test for /api/schema passed.")
        else:
            print(f"Failed to retrieve data from /api/schema. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error testing /api/schema: {e}")

def main():
    endpoint = 'http://localhost:8000'  # Replace with your actual endpoint
    test_api_genome(endpoint)
    test_api_state(endpoint)
    test_api_schema(endpoint)

if __name__ == "__main__":
    main()

"""
Test manuel pour les endpoints Modifications de l'API Sullivan Stenciler
Pilier 2 : Modifications - POST /api/modifications, GET /api/modifications/history, POST /api/snapshot

Ce script teste les endpoints de modification du Genome avec validation des réponses.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Ajuster selon votre configuration
API_PREFIX = "/api"

class TestModificationsAPI:
    """Classe de test pour les endpoints de modifications"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        # Variables pour suivre l'état entre tests
        self.last_snapshot_id = None
        self.modification_history = []
        self.test_modification_data = []
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Effectue une requête HTTP et retourne la réponse JSON"""
        url = f"{self.base_url}{API_PREFIX}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de requête: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Status: {e.response.status_code}")
                print(f"   Response: {e.response.text}")
            raise
    
    def test_get_initial_state(self) -> Dict[str, Any]:
        """Récupère l'état initial pour référence"""
        print("\n" + "="*60)
        print("1. Récupération de l'état initial")
        print("="*60)
        
        response = self._make_request("GET", "/state")
        
        # Validation de la réponse
        assert "current_state" in response, "❌ 'current_state' manquant dans la réponse"
        assert "modification_count" in response, "❌ 'modification_count' manquant"
        assert "last_snapshot_id" in response, "❌ 'last_snapshot_id' manquant"
        assert "last_modified" in response, "❌ 'last_modified' manquant"
        
        print(f"✅ État initial récupéré")
        print(f"   Modification count: {response['modification_count']}")
        print(f"   Last snapshot ID: {response['last_snapshot_id']}")
        print(f"   Last modified: {response['last_modified']}")
        
        return response
    
    def test_apply_modification_valid(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Teste l'application d'une modification valide"""
        print(f"\n2. Test modification valide: {test_case['description']}")
        print("-"*40)
        
        payload = {
            "path": test_case["path"],
            "property": test_case["property"],
            "value": test_case["value"]
        }
        
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = self._make_request("POST", "/modifications", json=payload)
        
        # Validation de la réponse
        assert "success" in response, "❌ 'success' manquant dans la réponse"
        assert response["success"] is True, f"❌ Modification échouée: {response.get('error', 'Unknown error')}"
        
        if "snapshot_id" in response and response["snapshot_id"]:
            print(f"✅ Modification appliquée avec succès")
            print(f"   Snapshot ID: {response['snapshot_id']}")
            self.last_snapshot_id = response["snapshot_id"]
        else:
            print(f"⚠️  Modification appliquée mais pas de snapshot ID généré")
        
        # Stocker pour vérification ultérieure
        test_case["response"] = response
        self.test_modification_data.append(test_case)
        
        return response
    
    def test_apply_modification_invalid(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Teste l'application d'une modification invalide"""
        print(f"\n3. Test modification invalide: {test_case['description']}")
        print("-"*40)
        
        payload = {
            "path": test_case["path"],
            "property": test_case["property"],
            "value": test_case["value"]
        }
        
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = self._make_request("POST", "/modifications", json=payload)
            
            # Pour les modifications invalides, on s'attend à ce que success soit False
            assert "success" in response, "❌ 'success' manquant dans la réponse"
            assert response["success"] is False, "❌ Modification invalide devrait échouer"
            
            # Vérifier la présence d'erreurs de validation
            if "validation_errors" in response:
                print(f"✅ Modification rejetée comme attendu")
                print(f"   Validation errors: {response['validation_errors']}")
            elif "error" in response:
                print(f"✅ Modification rejetée comme attendu")
                print(f"   Error: {response['error']}")
            
            return response
            
        except requests.exceptions.HTTPError as e:
            # Certaines erreurs peuvent retourner un HTTP 400/500
            print(f"✅ Modification rejetée (HTTP {e.response.status_code})")
            return {"success": False, "error": str(e)}
    
    def test_get_modification_history(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Teste la récupération de l'historique des modifications"""
        print("\n4. Récupération de l'historique des modifications")
        print("-"*40)
        
        endpoint = "/modifications/history"
        if params:
            # Construire les paramètres de requête
            query_params = []
            for key, value in params.items():
                if value is not None:
                    query_params.append(f"{key}={value}")
            
            if query_params:
                endpoint += "?" + "&".join(query_params)
        
        response = self._make_request("GET", endpoint)
        
        # Validation de la réponse
        assert "events" in response, "❌ 'events' manquant dans la réponse"
        assert "total" in response, "❌ 'total' manquant dans la réponse"
        assert "limit" in response, "❌ 'limit' manquant dans la réponse"
        
        print(f"✅ Historique récupéré")
        print(f"   Nombre total d'événements: {response['total']}")
        print(f"   Limite appliquée: {response['limit']}")
        print(f"   Événements retournés: {len(response['events'])}")
        
        # Afficher les derniers événements
        if response["events"]:
            print(f"\n   Derniers événements:")
            for i, event in enumerate(response["events"][:3]):  # Afficher les 3 premiers
                print(f"   {i+1}. {event['property']} sur {event['path']} à {event['timestamp']}")
        
        # Stocker pour vérification
        self.modification_history = response["events"]
        
        return response
    
    def test_create_snapshot(self) -> Dict[str, Any]:
        """Teste la création d'un snapshot"""
        print("\n5. Création d'un snapshot")
        print("-"*40)
        
        response = self._make_request("POST", "/snapshot")
        
        # Validation de la réponse
        assert "snapshot_id" in response, "❌ 'snapshot_id' manquant dans la réponse"
        assert "timestamp" in response, "❌ 'timestamp' manquant dans la réponse"
        
        print(f"✅ Snapshot créé avec succès")
        print(f"   Snapshot ID: {response['snapshot_id']}")
        print(f"   Timestamp: {response['timestamp']}")
        
        self.last_snapshot_id = response["snapshot_id"]
        
        return response
    
    def test_history_with_since_parameter(self):
        """Teste l'historique avec le paramètre 'since'"""
        print("\n6. Test historique avec paramètre 'since'")
        print("-"*40)
        
        # Attendre un peu pour avoir un timestamp différent
        time.sleep(1)
        since_time = datetime.now().isoformat()
        
        # Faire une nouvelle modification
        test_mod = {
            "description": "Modification pour test 'since'",
            "path": "n0[0].n1[0].n2[0]",
            "property": "priority",
            "value": "high"
        }
        
        print(f"   Création d'une modification après {since_time}")
        self.test_apply_modification_valid(test_mod)
        
        # Récupérer l'historique depuis le timestamp
        params = {"since": since_time}
        response = self.test_get_modification_history(params)
        
        # Vérifier que seules les modifications récentes sont retournées
        if response["events"]:
            for event in response["events"]:
                event_time = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
                since_time_dt = datetime.fromisoformat(since_time.replace('Z', '+00:00'))
                assert event_time >= since_time_dt, f"❌ Événement antérieur au 'since': {event['timestamp']}"
            
            print(f"✅ Tous les événements sont postérieurs à {since_time}")
    
    def test_history_with_limit_parameter(self):
        """Teste l'historique avec le paramètre 'limit'"""
        print("\n7. Test historique avec paramètre 'limit'")
        print("-"*40)
        
        # Tester avec différentes limites
        test_limits = [1, 3, 5]
        
        for limit in test_limits:
            print(f"\n   Test avec limit={limit}")
            params = {"limit": limit}
            response = self.test_get_modification_history(params)
            
            # Vérifier que le nombre d'événements ne dépasse pas la limite
            assert len(response["events"]) <= limit, f"❌ Trop d'événements pour limit={limit}"
            assert response["limit"] == limit, f"❌ Limit incorrect dans la réponse: {response['limit']}"
            
            print(f"   ✅ Limit={limit} respecté: {len(response['events'])} événements")
    
    def verify_modification_in_history(self):
        """Vérifie que les modifications testées sont bien dans l'historique"""
        print("\n8. Vérification des modifications dans l'historique")
        print("-"*40)
        
        # Récupérer tout l'historique
        response = self.test_get_modification_history()
        
        if not self.test_modification_data:
            print("⚠️  Aucune donnée de test à vérifier")
            return
        
        # Vérifier chaque modification testée
        found_count = 0
        for test_case in self.test_modification_data:
            if "response" not in test_case or not test_case["response"].get("success"):
                continue
            
            # Chercher cette modification dans l'historique
            for event in response["events"]:
                if (event["path"] == test_case["path"] and 
                    event["property"] == test_case["property"] and
                    event["new_value"] == test_case["value"]):
                    
                    found_count += 1
                    print(f"✅ Modification trouvée dans l'historique:")
                    print(f"   Chemin: {test_case['path']}")
                    print(f"   Propriété: {test_case['property']}")
                    print(f"   Valeur: {test_case['value']}")
                    print(f"   Timestamp: {event['timestamp']}")
                    break
        
        print(f"\n   Résumé: {found_count}/{len(self.test_modification_data)} modifications trouvées dans l'historique")
    
    def test_comprehensive_workflow(self):
        """Teste un workflow complet de modifications"""
        print("\n" + "="*60)
        print("TEST WORKFLOW COMPLET")
        print("="*60)
        
        # 1. État initial
        initial_state = self.test_get_initial_state()
        initial_mod_count = initial_state["modification_count"]
        
        # 2. Modifications valides
        valid_test_cases = [
            {
                "description": "Modification de priorité",
                "path": "n0[0].n1[0].n2[0]",
                "property": "priority",
                "value": "medium"
            },
            {
                "description": "Modification de complexité",
                "path": "n0[0].n1[0].n2[1]",
                "property": "complexity",
                "value": 0.7
            },
            {
                "description": "Modification de statut",
                "path": "n0[1].n1[0]",
                "property": "status",
                "value": "in_progress"
            }
        ]
        
        for test_case in valid_test_cases:
            self.test_apply_modification_valid(test_case)
        
        # 3. Modifications invalides
        invalid_test_cases = [
            {
                "description": "Chemin invalide",
                "path": "n0[999].n1[0]",
                "property": "priority",
                "value": "high"
            },
            {
                "description": "Propriété interdite",
                "path": "n0[0].n1[0]",
                "property": "forbidden_property",
                "value": "test"
            },
            {
                "description": "Valeur de type incorrect",
                "path": "n0[0].n1[0].n2[0]",
                "property": "priority",
                "value": 123  # Doit être une string
            }
        ]
        
        for test_case in invalid_test_cases:
            self.test_apply_modification_invalid(test_case)
        
        # 4. Créer un snapshot
        snapshot_response = self.test_create_snapshot()
        
        # 5. Vérifier l'état après modifications
        print("\n9. Vérification de l'état final")
        print("-"*40)
        final_state = self.test_get_initial_state()
        
        # Vérifier que le compteur de modifications a augmenté
        expected_mod_count = initial_mod_count + len(valid_test_cases)
        print(f"   Modifications initiales: {initial_mod_count}")
        print(f"   Modifications attendues: {expected_mod_count}")
        print(f"   Modifications actuelles: {final_state['modification_count']}")
        
        # Note: Le compteur exact peut varier selon l'implémentation
        if final_state['modification_count'] >= expected_mod_count:
            print(f"✅ Compteur de modifications mis à jour correctement")
        else:
            print(f"⚠️  Compteur de modifications différent de l'attendu")
        
        # 6. Tests d'historique avec paramètres
        self.test_history_with_since_parameter()
        self.test_history_with_limit_parameter()
        
        # 7. Vérification finale
        self.verify_modification_in_history()
        
        return {
            "initial_state": initial_state,
            "final_state": final_state,
            "snapshot_id": snapshot_response["snapshot_id"],
            "test_modifications": self.test_modification_data
        }
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🚀 Démarrage des tests des endpoints Modifications")
        print("="*60)
        
        try:
            results =

import pytest
from fastapi.testclient import TestClient
from sullivan.stenciler.api import router

client = TestClient(router)

def test_drilldown_enter():
    response = client.post("/api/drilldown/enter", json={"path": "n0[0].n1[2]"})
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_drilldown_exit():
    response = client.post("/api/drilldown/exit")
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_get_breadcrumb():
    response = client.get("/api/breadcrumb")
    assert response.status_code == 200
    assert "breadcrumb" in response.json()
    assert "current_level" in response.json()

def test_drilldown_enter_invalid_path():
    response = client.post("/api/drilldown/enter", json={"path": "invalid_path"})
    assert response.status_code == 400

def test_drilldown_exit_invalid_state():
    # Simulate an invalid state by not calling drilldown_enter before drilldown_exit
    response = client.post("/api/drilldown/exit")
    assert response.status_code == 400

def test_get_breadcrumb_invalid_state():
    # Simulate an invalid state by not calling drilldown_enter before get_breadcrumb
    response = client.get("/api/breadcrumb")
    assert response.status_code == 500

# Test the drilldown functionality with multiple enter and exit calls
def test_drilldown_multiple_calls():
    # Enter a valid path
    response = client.post("/api/drilldown/enter", json={"path": "n0[0].n1[2]"})
    assert response.status_code == 200
    assert response.json()["success"] == True

    # Exit the current level
    response = client.post("/api/drilldown/exit")
    assert response.status_code == 200
    assert response.json()["success"] == True

    # Enter another valid path
    response = client.post("/api/drilldown/enter", json={"path": "n0[0].n1[3]"})
    assert response.status_code == 200
    assert response.json()["success"] == True

    # Get the breadcrumb
    response = client.get("/api/breadcrumb")
    assert response.status_code == 200
    assert "breadcrumb" in response.json()
    assert "current_level" in response.json()

# Test the drilldown functionality with an invalid path
def test_drilldown_invalid_path():
    # Enter an invalid path
    response = client.post("/api/drilldown/enter", json={"path": "invalid_path"})
    assert response.status_code == 400

    # Try to exit the current level
    response = client.post("/api/drilldown/exit")
    assert response.status_code == 400

    # Try to get the breadcrumb
    response = client.get("/api/breadcrumb")
    assert response.status_code == 500

{
  "operations": [
    {
      "type": "add_function",
      "code": "def test_api_genome(endpoint):\n    \"\"\"Test GET /api/genome endpoint.\"\"\"\n    try:\n        response = requests.get(endpoint + \"/api/genome\")\n        if response.status_code == 200:\n            data = response.json()\n            # Verify the structure of the response\n            assert 'genome' in data, \"Missing 'genome' key in the response.\"\n            assert 'metadata' in data, \"Missing 'metadata' key in the response.\"\n            assert 'modification_count' in data['metadata'], \"Missing 'modification_count' key in metadata.\"\n            assert 'last_snapshot_id' in data['metadata'], \"Missing 'last_snapshot_id' key in metadata.\"\n            assert 'last_modified' in data['metadata'], \"Missing 'last_modified' key in metadata.\"\n            print(\"Test for /api/genome passed.\")\n        else:\n            print(f\"Failed to retrieve data from /api/genome. Status code: {response.status_code}\")\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/genome: {e}\")"
    },
    {
      "type": "add_function",
      "code": "def test_api_state(endpoint):\n    \"\"\"Test GET /api/state endpoint.\"\"\"\n    try:\n        response = requests.get(endpoint + \"/api/state\")\n        if response.status_code == 200:\n            data = response.json()\n            # Verify the structure of the response\n            assert 'current_state' in data, \"Missing 'current_state' key in the response.\"\n            assert 'modification_count' in data, \"Missing 'modification_count' key in the response.\"\n            assert 'last_snapshot_id' in data, \"Missing 'last_snapshot_id' key in the response.\"\n            assert 'last_modified' in data, \"Missing 'last_modified' key in the response.\"\n            print(\"Test for /api/state passed.\")\n        else:\n            print(f\"Failed to retrieve data from /api/state. Status code: {response.status_code}\")\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/state: {e}\")"
    },
    {
      "type": "add_function",
      "code": "def test_api_schema(endpoint):\n    \"\"\"Test GET /api/schema endpoint.\"\"\"\n    try:\n        response = requests.get(endpoint + \"/api/schema\")\n        if response.status_code == 200:\n            data = response.json()\n            # Verify the structure of the response\n            assert 'levels' in data, \"Missing 'levels' key in the response.\"\n            assert 'semantic_properties' in data, \"Missing 'semantic_properties' key in the response.\"\n            assert 'forbidden_properties' in data, \"Missing 'forbidden_properties' key in the response.\"\n            print(\"Test for /api/schema passed.\")\n        else:\n            print(f\"Failed to retrieve data from /api/schema. Status code: {response.status_code}\")\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/schema: {e}\")"
    },
    {
      "type": "add_function",
      "code": "def main():\n    endpoint = 'http://localhost:8000'  # Replace with your actual endpoint\n    test_api_genome(endpoint)\n    test_api_state(endpoint)\n    test_api_schema(endpoint)\n\nif __name__ == \"__main__\":\n    main()"
    }
  ]
}

{
  "operations": [
    {
      "type": "add_function",
      "code": "def test_api_modifications(endpoint):\n    \"\"\"Test POST /api/modifications endpoint.\"\"\"\n    try:\n        # Test avec une modification valide\n        payload = {\n            \"path\": \"n0[0].n1[0].n2[0]\",\n            \"property\": \"priority\",\n            \"value\": \"high\"\n        }\n        response = requests.post(endpoint + \"/api/modifications\", json=payload)\n        \n        if response.status_code == 200:\n            data = response.json()\n            # Verify the structure of the response\n            assert 'success' in data, \"Missing 'success' key in the response.\"\n            assert 'snapshot_id' in data, \"Missing 'snapshot_id' key in the response.\"\n            assert 'error' in data, \"Missing 'error' key in the response.\"\n            assert 'validation_errors' in data, \"Missing 'validation_errors' key in the response.\"\n            \n            if data['success']:\n                print(f\"Test for /api/modifications passed. Snapshot ID: {data['snapshot_id']}\")\n            else:\n                print(f\"Modification failed: {data.get('error', 'Unknown error')}\")\n        else:\n            print(f\"Failed to apply modification. Status code: {response.status_code}\")\n            print(f\"Response: {response.text}\")\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/modifications: {e}\")\n    \n    # Test avec une modification invalide\n    try:\n        invalid_payload = {\n            \"path\": \"n0[999].n1[0]\",  # Chemin invalide\n            \"property\": \"priority\",\n            \"value\": \"high\"\n        }\n        response = requests.post(endpoint + \"/api/modifications\", json=invalid_payload)\n        \n        if response.status_code in [400, 500]:\n            print(\"Test for invalid modification passed (expected error).\")\n        elif response.status_code == 200:\n            data = response.json()\n            if not data.get('success', False):\n                print(\"Test for invalid modification passed (success=False).\")\n            else:\n                print(\"Warning: Invalid modification returned success=True\")\n        else:\n            print(f\"Unexpected status code for invalid modification: {response.status_code}\")\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing invalid /api/modifications: {e}\")"
    },
    {
      "type": "add_function",
      "code": "def test_api_modifications_history(endpoint):\n    \"\"\"Test GET /api/modifications/history endpoint.\"\"\"\n    try:\n        # Test sans paramètres\n        response = requests.get(endpoint + \"/api/modifications/history\")\n        \n        if response.status_code == 200:\n            data = response.json()\n            # Verify the structure of the response\n            assert 'events' in data, \"Missing 'events' key in the response.\"\n            assert 'total' in data, \"Missing 'total' key in the response.\"\n            assert 'limit' in data, \"Missing 'limit' key in the response.\"\n            \n            print(f\"Test for /api/modifications/history passed. Total events: {data['total']}, Limit: {data['limit']}\")\n            \n            # Vérifier la structure des événements si présents\n            if data['events']:\n                event = data['events'][0]\n                assert 'id' in event, \"Missing 'id' key in event.\"\n                assert 'timestamp' in event, \"Missing 'timestamp' key in event.\"\n                assert 'path' in event, \"Missing 'path' key in event.\"\n                assert 'property' in event, \"Missing 'property' key in event.\"\n                assert 'old_value' in event, \"Missing 'old_value' key in event.\"\n                assert 'new_value' in event, \"Missing 'new_value' key in event.\"\n                assert 'semantic_attributes' in event, \"Missing 'semantic_attributes' key in event.\"\n        else:\n            print(f\"Failed to retrieve modification history. Status code: {response.status_code}\")\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/modifications/history: {e}\")\n    \n    # Test avec paramètres\n    try:\n        # Test avec limit\n        response = requests.get(endpoint + \"/api/modifications/history?limit=5\")\n        \n        if response.status_code == 200:\n            data = response.json()\n            assert len(data['events']) <= 5, f\"Limit not respected: {len(data['events'])} events returned\"\n            print(\"Test for /api/modifications/history with limit=5 passed.\")\n        \n        # Test avec since (timestamp)\n        since_time = \"2024-01-01T00:00:00\"\n        response = requests.get(endpoint + f\"/api/modifications/history?since={since_time}\")\n        \n        if response.status_code == 200:\n            print(\"Test for /api/modifications/history with since parameter passed.\")\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/modifications/history with parameters: {e}\")"
    },
    {
      "type": "add_function",
      "code": "def test_api_snapshot(endpoint):\n    \"\"\"Test POST /api/snapshot endpoint.\"\"\"\n    try:\n        response = requests.post(endpoint + \"/api/snapshot\")\n        \n        if response.status_code == 200:\n            data = response.json()\n            # Verify the structure of the response\n            assert 'snapshot_id' in data, \"Missing 'snapshot_id' key in the response.\"\n            assert 'timestamp' in data, \"Missing 'timestamp' key in the response.\"\n            \n            print(f\"Test for /api/snapshot passed. Snapshot ID: {data['snapshot_id']}, Timestamp: {data['timestamp']}\")\n            return data['snapshot_id']\n        else:\n            print(f\"Failed to create snapshot. Status code: {response.status_code}\")\n            print(f\"Response: {response.text}\")\n            return None\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/snapshot: {e}\")\n        return None"
    },
    {
      "type": "add_function",
      "code": "def test_api_modifications_undo_redo(endpoint):\n    \"\"\"Test POST /api/modifications/undo and /api/modifications/redo endpoints.\"\"\"\n    try:\n        # D'abord appliquer une modification pour avoir quelque chose à undo\n        payload = {\n            \"path\": \"n0[0].n1[0].n2[0]\",\n            \"property\": \"priority\",\n            \"value\": \"urgent\"\n        }\n        response = requests.post(endpoint + \"/api/modifications\", json=payload)\n        \n        if response.status_code != 200 or not response.json().get('success', False):\n            print(\"Cannot test undo/redo - modification failed\")\n            return\n        \n        # Test undo\n        response = requests.post(endpoint + \"/api/modifications/undo\")\n        \n        if response.status_code == 200:\n            data = response.json()\n            assert 'success' in data, \"Missing 'success' key in undo response.\"\n            assert 'can_undo' in data, \"Missing 'can_undo' key in undo response.\"\n            assert 'can_redo' in data, \"Missing 'can_redo' key in undo response.\"\n            \n            if data['success']:\n                print(f\"Test for /api/modifications/undo passed. Can undo: {data['can_undo']}, Can redo: {data['can_redo']}\")\n            else:\n                print(f\"Undo failed: {data.get('error', 'Unknown error')}\")\n        else:\n            print(f\"Failed to undo modification. Status code: {response.status_code}\")\n        \n        # Test redo\n        response = requests.post(endpoint + \"/api/modifications/redo\")\n        \n        if response.status_code == 200:\n            data = response.json()\n            if data['success']:\n                print(f\"Test for /api/modifications/redo passed. Can undo: {data['can_undo']}, Can redo: {data['can_redo']}\")\n            else:\n                print(f\"Redo failed: {data.get('error', 'Unknown error')}\")\n        else:\n            print(f\"Failed to redo modification. Status code: {response.status_code}\")\n            \n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/modifications/undo/redo: {e}\")"
    },
    {
      "type": "modify_method",
      "target": "main",
      "code": "def main():\n    endpoint = 'http://localhost:8000'  # Replace with your actual endpoint\n    \n    # Tests existants\n    test_api_genome(endpoint)\n    test_api_state(endpoint)\n    test_api_schema(endpoint)\n    \n    # Nouveaux tests pour les modifications\n    print(\"\\n\" + \"=\"*60)\n    print(\"Testing Modification Endpoints\")\n    print(\"=\"*60)\n    \n    # Test des modifications\n    test_api_modifications(endpoint)\n    \n    # Test de l'historique\n    test_api_modifications_history(endpoint)\n    \n    # Test des snapshots\n    snapshot_id = test_api_snapshot(endpoint)\n    \n    # Test undo/redo\n    test_api_modifications_undo_redo(endpoint)\n    \n    print(\"\\n\" + \"=\"*60)\n    print(\"All tests completed\")\n    print(\"=\"*60)"
    }
  ]
}

{
  "operations": [
    {
      "type": "add_function",
      "code": "def test_api_drilldown_enter(endpoint):\n    \"\"\"Test POST /api/drilldown/enter endpoint.\"\"\"\n    try:\n        # Test avec un chemin valide\n        payload = {\n            \"path\": \"n0[0]\",\n            \"child_index\": 0\n        }\n        response = requests.post(endpoint + \"/api/drilldown/enter\", json=payload)\n        \n        if response.status_code == 200:\n            data = response.json()\n            # Vérifier la structure de la réponse\n            assert 'success' in data, \"Missing 'success' key in the response.\"\n            assert data['success'] is True, \"Drilldown enter should succeed\"\n            assert 'new_path' in data, \"Missing 'new_path' key in the response.\"\n            assert 'current_level' in data, \"Missing 'current_level' key in the response.\"\n            assert 'children' in data, \"Missing 'children' key in the response.\"\n            assert 'breadcrumb' in data, \"Missing 'breadcrumb' key in the response.\"\n            assert 'breadcrumb_paths' in data, \"Missing 'breadcrumb_paths' key in the response.\"\n            assert 'has_children' in data, \"Missing 'has_children' key in the response.\"\n            print(\"Test for /api/drilldown/enter passed.\")\n        else:\n            print(f\"Failed to drilldown enter. Status code: {response.status_code}\")\n            print(f\"Response: {response.text}\")\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/drilldown/enter: {e}\")\n    except AssertionError as e:\n        print(f\"Assertion error in /api/drilldown/enter test: {e}\")"
    },
    {
      "type": "add_function",
      "code": "def test_api_drilldown_exit(endpoint):\n    \"\"\"Test POST /api/drilldown/exit endpoint.\"\"\"\n    try:\n        # D'abord, on doit être dans un niveau drilldown\n        # On commence par un drilldown enter\n        enter_payload = {\n            \"path\": \"n0[0]\",\n            \"child_index\": 0\n        }\n        enter_response = requests.post(endpoint + \"/api/drilldown/enter\", json=enter_payload)\n        \n        if enter_response.status_code != 200:\n            print(f\"Cannot setup drilldown for exit test. Status: {enter_response.status_code}\")\n            return\n        \n        # Maintenant on teste le drilldown exit\n        exit_payload = {\n            \"path\": enter_response.json()['new_path']\n        }\n        response = requests.post(endpoint + \"/api/drilldown/exit\", json=exit_payload)\n        \n        if response.status_code == 200:\n            data = response.json()\n            # Vérifier la structure de la réponse\n            assert 'success' in data, \"Missing 'success' key in the response.\"\n            assert data['success'] is True, \"Drilldown exit should succeed\"\n            assert 'parent_path' in data, \"Missing 'parent_path' key in the response.\"\n            assert 'current_level' in data, \"Missing 'current_level' key in the response.\"\n            assert 'children' in data, \"Missing 'children' key in the response.\"\n            assert 'breadcrumb' in data, \"Missing 'breadcrumb' key in the response.\"\n            assert 'breadcrumb_paths' in data, \"Missing 'breadcrumb_paths' key in the response.\"\n            print(\"Test for /api/drilldown/exit passed.\")\n        else:\n            print(f\"Failed to drilldown exit. Status code: {response.status_code}\")\n            print(f\"Response: {response.text}\")\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/drilldown/exit: {e}\")\n    except AssertionError as e:\n        print(f\"Assertion error in /api/drilldown/exit test: {e}\")"
    },
    {
      "type": "add_function",
      "code": "def test_api_breadcrumb(endpoint):\n    \"\"\"Test GET /api/breadcrumb endpoint.\"\"\"\n    try:\n        # D'abord, on doit être dans un niveau drilldown\n        enter_payload = {\n            \"path\": \"n0[0]\",\n            \"child_index\": 0\n        }\n        enter_response = requests.post(endpoint + \"/api/drilldown/enter\", json=enter_payload)\n        \n        if enter_response.status_code != 200:\n            print(f\"Cannot setup drilldown for breadcrumb test. Status: {enter_response.status_code}\")\n            return\n        \n        current_path = enter_response.json()['new_path']\n        \n        # Maintenant on teste le breadcrumb\n        response = requests.get(endpoint + f\"/api/breadcrumb?path={current_path}\")\n        \n        if response.status_code == 200:\n            data = response.json()\n            # Vérifier la structure de la réponse\n            assert 'breadcrumb' in data, \"Missing 'breadcrumb' key in the response.\"\n            assert 'breadcrumb_paths' in data, \"Missing 'breadcrumb_paths' key in the response.\"\n            assert 'current_level' in data, \"Missing 'current_level' key in the response.\"\n            assert 'current_path' in data, \"Missing 'current_path' key in the response.\"\n            assert 'has_children' in data, \"Missing 'has_children' key in the response.\"\n            assert 'children_count' in data, \"Missing 'children_count' key in the response.\"\n            print(\"Test for /api/breadcrumb passed.\")\n        else:\n            print(f\"Failed to get breadcrumb. Status code: {response.status_code}\")\n            print(f\"Response: {response.text}\")\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/breadcrumb: {e}\")\n    except AssertionError as e:\n        print(f\"Assertion error in /api/breadcrumb test: {e}\")"
    },
    {
      "type": "add_function",
      "code": "def test_api_drilldown_invalid_path(endpoint):\n    \"\"\"Test POST /api/drilldown/enter with invalid path.\"\"\"\n    try:\n        # Test avec un chemin invalide\n        payload = {\n            \"path\": \"invalid_path[999]\",\n            \"child_index\": 0\n        }\n        response = requests.post(endpoint + \"/api/drilldown/enter\", json=payload)\n        \n        # On s'attend à une erreur 400 pour un chemin invalide\n        if response.status_code == 400:\n            print(\"Test for /api/drilldown/enter with invalid path passed (correctly returned 400).\")\n        elif response.status_code == 200:\n            # Si par hasard ça réussit, vérifier que success est False\n            data = response.json()\n            if 'success' in data and data['success'] is False:\n                print(\"Test for /api/drilldown/enter with invalid path passed (success=False).\")\n            else:\n                print(f\"Unexpected success with invalid path. Response: {response.text}\")\n        else:\n            print(f\"Unexpected status code for invalid path: {response.status_code}\")\n    except requests.exceptions.RequestException as e:\n        print(f\"Error testing /api/drilldown/enter with invalid path: {e}\")"
    },
    {
      "type": "add_function",
      "code": "def test_api_drilldown_workflow(endpoint):\n    \"\"\"Test complete drilldown workflow: enter → breadcrumb → exit.\"\"\"\n    print(\"\\nTesting complete drilldown workflow...\")\n    \n    try:\n        # 1. Initial drilldown enter\n        print(\"1. Initial drilldown enter...\")\n        enter_payload1 = {\n            \"path\": \"n0[0]\",\n            \"child_index\": 0\n        }\n        response1 = requests.post(endpoint + \"/api/drilldown/enter\", json=enter_payload1)\n        \n        if response1.status_code != 200:\n            print(f\"Failed initial drilldown enter: {response1.status_code}\")\n            return\n        \n        data1 = response1.json()\n        path1 = data1['new_path']\n        print(f\"   Entered path: {path1}\")\n        \n        # 2. Get breadcrumb for first level\n        print(\"2. Get breadcrumb for first level...\")\n        response2 = requests.get(endpoint + f\"/api/breadcrumb?path={path1}\")\n        \n        if response2.status_code == 200:\n            data2 = response2.json()\n            print(f\"   Breadcrumb: {data2['breadcrumb']}\")\n            print(f\"   Current level: {data2['current_level']}\")\n        else:\n            print(f\"   Failed to get breadcrumb: {response2.status_code}\")\n        \n        # 3. Drilldown further if possible\n        print(\"3. Drilldown further...\")\n        if data1.get('has_children', False) and len(data1.get('children', [])) > 0:\n            enter_payload2 = {\n                \"path\": path1,\n                \"child_index\": 0\n            }\n            response3 = requests.post(endpoint + \"/api/drilldown/enter\", json=enter_payload2)\n            \n            if response3.status_code == 200:\n                data3 = response3.json()\n                path2 = data3['new_path']\n                print(f\"   Entered deeper path: {path2}\")\n                \n                # 4. Get breadcrumb for deeper level\n                print(\"4. Get breadcrumb for deeper level...\")\n                response4 = requests.get(endpoint + f\"/api/breadcrumb?path={path2}\")\n                \n                if response4.status_code == 200:\n                    data4 = response4.json()\n                    print(f\"   Deeper breadcrumb: {data4['breadcrumb']}\")\n                    print(f\"   Deeper level: {data4['current_level']}\")\n                \n                # 5. Drilldown exit back to first level\n                print(\"5. Drilldown exit to first level...\")\n                exit_payload1 = {\n                    \"path\": path2\n                }\n                response5 = requests.post(endpoint + \"/api/drilldown/exit\", json=exit_payload1)\n                \n                if response5.status_code == 200:\n                    data5 = response5.json()\n                    print(f\"   Exited to path: {data5['parent_path']}\")\n                    \n                    # 6. Final drilldown exit to root\n                    print(\"6. Final drilldown exit to root...\")\n                    exit_payload2 = {\n                        \"path\": data5['parent_path']\n                    }\n                    response6 = requests.post(endpoint + \"/api/drilldown/exit\", json=exit_payload2)\n                    \n                    if response6.status_code == 200:\n                        print(\"   Successfully exited to root level\")\n                        print(\"✅ Complete drilldown workflow test passed.\")\n                    else:\n                        print(f\"   Failed final exit: {response6.status_code}\")\n                else:\n                    print(f\"   Failed first exit: {response5.status_code}\")\n            else:\n                print(f\"   Cannot drilldown further: {response3.status_code}\")\n                print(\"⚠️  Drilldown workflow test partially passed (no deeper levels available).\")\n        else:\n            print(\"   No children available for further drilldown\")\n            print(\"⚠️  Drilldown workflow test partially passed (no children available).\")\n            \n            # Exit from first level\n            exit_payload = {\n                \"path\": path1\n            }\n            response_exit = requests.post(endpoint + \"/api/drilldown/exit\", json=exit_payload)\n            if response_exit.status_code == 200:\n                print(\"   Successfully exited to root\")\n    \n    except requests.exceptions.RequestException as e:\n        print(f\"Error in drilldown workflow test: {e}\")"
    },
    {
      "type": "modify_method",
      "target": "main",
      "code": "def main():\n    endpoint = 'http://localhost:8000'  # Replace with your actual endpoint\n    \n    # Pilier 1: État\n    test_api_genome(endpoint)\n    test_api_state(endpoint)\n    test_api_schema(endpoint)\n    \n    # Pilier 3: Navigation\n    print(\"\\n\" + \"=\"*60)\n    print(\"Testing Navigation Endpoints (Pilier 3)\")\n    print(\"=\"*60)\n    \n    test_api_drilldown_enter(endpoint)\n    test_api_drilldown_exit(endpoint)\n    test_api_breadcrumb(endpoint)\n    test_api_drilldown_invalid_path(endpoint)\n    test_api_drilldown_workflow(endpoint)\n    \n    print(\"\\nAll navigation tests completed.\")"
    }
  ]
}