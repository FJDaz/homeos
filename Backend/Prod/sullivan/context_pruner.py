import json
import os
from typing import Dict, Any, Optional, List

def prune_genome(genome: Dict[str, Any], target_id: str) -> Optional[Dict[str, Any]]:
    """
    Extrait un sous-ensemble du génome à partir d'un ID de composant (N0, N1, N2 ou N3).
    Retourne None si l'ID n'est pas trouvé.
    """
    
    # Recherche dans les phases N0
    for phase in genome.get("n0_phases", []):
        if phase.get("id") == target_id:
            return phase
        
        # Recherche dans les sections N1
        for section in phase.get("n1_sections", []):
            if section.get("id") == target_id:
                return section
            
            # Recherche dans les features N2
            for feature in section.get("n2_features", []):
                if feature.get("id") == target_id:
                    return feature
                
                # Recherche dans les composants N3
                for component in feature.get("n3_components", []):
                    if component.get("id") == target_id:
                        return component
                        
    return None

def get_pruned_genome_v2(genome_path: str, target_id: str) -> Optional[Dict[str, Any]]:
    """Charge le génome et le découpe."""
    if not os.path.exists(genome_path):
        return None
        
    try:
        with open(genome_path, 'r', encoding='utf-8') as f:
            genome = json.load(f)
        return prune_genome(genome, target_id)
    except Exception:
        return None

if __name__ == "__main__":
    # Test simple
    test_genome = {
        "n0_phases": [
            {
                "id": "n0_test",
                "n1_sections": [
                    {
                        "id": "n1_test",
                        "n2_features": [{"id": "n2_test"}]
                    }
                ]
            }
        ]
    }
    print(f"Test N1: {prune_genome(test_genome, 'n1_test')}")
    print(f"Test N2: {prune_genome(test_genome, 'n2_test')}")
