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