"""
Module for applying distillation entries to the HomeOS genome.
Handles reading distillation entries, normalizing verdicts, and updating the genome.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, TypedDict


# ==================== MODELS ====================

class DistillationEntry(TypedDict):
    """Model representing a distillation entry."""
    section_id: str
    section_title: str
    items: List[str]
    verdict: str


class DistillationData(TypedDict):
    """Model representing the distillation data to be added to genome."""
    updated_at: str
    entries: List[DistillationEntry]


class GenomeData(TypedDict, total=False):
    """Model representing the HomeOS genome structure."""
    metadata: Dict[str, Any]
    topology: List[str]
    endpoints: List[Dict[str, Any]]
    schema_definitions: Dict[str, Any]
    distillation: Optional[DistillationData]


# ==================== SERVICES ====================

class FileService:
    """Service for file operations."""
    
    @staticmethod
    def read_json(file_path: Path) -> Any:
        """
        Read JSON data from a file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    @staticmethod
    def write_json(file_path: Path, data: Any, indent: int = 2) -> None:
        """
        Write data to a JSON file.
        
        Args:
            file_path: Path to write the JSON file
            data: Data to write
            indent: JSON indentation level
        """
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=indent, ensure_ascii=False)


class DistillationService:
    """Service for distillation-related operations."""
    
    @staticmethod
    def normalize_verdicts(entries: List[DistillationEntry]) -> List[DistillationEntry]:
        """
        Normalize verdict values in distillation entries.
        
        Args:
            entries: List of distillation entries
            
        Returns:
            List of entries with normalized verdicts
        """
        normalized_entries = []
        for entry in entries:
            normalized_entry = entry.copy()
            if normalized_entry['verdict'] == 'Garder':
                normalized_entry['verdict'] = 'Accept'
            normalized_entries.append(normalized_entry)
        return normalized_entries
    
    @staticmethod
    def create_distillation_data(entries: List[DistillationEntry]) -> DistillationData:
        """
        Create distillation data structure with current timestamp.
        
        Args:
            entries: Normalized distillation entries
            
        Returns:
            Distillation data structure
        """
        return {
            'updated_at': datetime.utcnow().isoformat() + 'Z',
            'entries': entries
        }


class GenomeService:
    """Service for genome-related operations."""
    
    @staticmethod
    def update_genome_with_distillation(
        genome: GenomeData,
        distillation_data: DistillationData
    ) -> GenomeData:
        """
        Update genome with distillation data.
        
        Args:
            genome: Original genome data
            distillation_data: Distillation data to add
            
        Returns:
            Updated genome data
        """
        updated_genome = genome.copy()
        updated_genome['distillation'] = distillation_data
        return updated_genome


# ==================== CONTROLLER ====================

class DistillationController:
    """Controller for applying distillation to genome."""
    
    def __init__(
        self,
        file_service: Optional[FileService] = None,
        distillation_service: Optional[DistillationService] = None,
        genome_service: Optional[GenomeService] = None
    ):
        """
        Initialize the controller with services.
        
        Args:
            file_service: Service for file operations
            distillation_service: Service for distillation operations
            genome_service: Service for genome operations
        """
        self.file_service = file_service or FileService()
        self.distillation_service = distillation_service or DistillationService()
        self.genome_service = genome_service or GenomeService()
    
    def apply_distillation_to_genome(
        self,
        entries_path: Path,
        genome_path: Path
    ) -> bool:
        """
        Apply distillation entries to the genome.
        
        Args:
            entries_path: Path to distillation entries JSON file
            genome_path: Path to genome JSON file
            
        Returns:
            True if operation successful, False otherwise
        """
        try:
            # Read distillation entries
            entries = self.file_service.read_json(entries_path)
            
            # Normalize verdicts
            normalized_entries = self.distillation_service.normalize_verdicts(entries)
            
            # Read genome
            genome = self.file_service.read_json(genome_path)
            
            # Create distillation data
            distillation_data = self.distillation_service.create_distillation_data(
                normalized_entries
            )
            
            # Update genome with distillation
            updated_genome = self.genome_service.update_genome_with_distillation(
                genome,
                distillation_data
            )
            
            # Write updated genome
            self.file_service.write_json(genome_path, updated_genome)
            
            return True
            
        except FileNotFoundError as e:
            print(f"Error: File not found - {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format - {e}")
            return False
        except Exception as e:
            print(f"An error occurred: {e}")
            return False


# ==================== PUBLIC API ====================

def apply_distillation_to_genome(entries_path: Path, genome_path: Path) -> bool:
    """
    Public function to apply distillation to genome.
    
    Args:
        entries_path: Path to distillation entries JSON file
        genome_path: Path to genome JSON file
        
    Returns:
        True if operation successful, False otherwise
    """
    controller = DistillationController()
    return controller.apply_distillation_to_genome(entries_path, genome_path)


# ==================== MAIN GUARD ====================

if __name__ == "__main__":
    # Example usage
    entries_path = Path('output/studio/distillation_entries.json')
    genome_path = Path('output/studio/homeos_genome.json')
    
    success = apply_distillation_to_genome(entries_path, genome_path)
    print(f"Operation successful: {success}")