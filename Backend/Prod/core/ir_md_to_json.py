"""
Module for converting IR inventory Markdown to JSON format with schema validation.

This module provides functionality to parse IR inventory Markdown files,
extract structured data, and convert it to JSON format validated against
a predefined schema.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import jsonschema


class MarkdownParser:
    """Parser for extracting structured data from IR inventory Markdown."""
    
    @staticmethod
    def extract_source_paths(md_content: str) -> Tuple[str, str]:
        """
        Extract genome and PRD paths from Markdown content.
        
        Args:
            md_content: The Markdown content as a string
            
        Returns:
            Tuple of (genome_path, prd_path)
        """
        genome_path = "output/studio/homeos_genome.json"
        prd_path = "docs/04-homeos/PRD_HOMEOS.md"
        
        # Look for source lines
        for line in md_content.split('\n'):
            if "Source genome :" in line:
                # Extract path from backticks or after colon
                match = re.search(r'`([^`]+)`', line)
                if match:
                    genome_path = match.group(1)
                else:
                    # Fallback: extract after colon
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        genome_path = parts[1].strip()
            elif "Source intentions :" in line:
                match = re.search(r'`([^`]+)`', line)
                if match:
                    prd_path = match.group(1)
                else:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        prd_path = parts[1].strip()
        
        return genome_path, prd_path
    
    @staticmethod
    def find_section_lines(md_content: str, section_title: str) -> Optional[List[str]]:
        """
        Find lines belonging to a specific section.
        
        Args:
            md_content: The Markdown content
            section_title: The section title to find (e.g., "### 1.2 Topologie déclarée")
            
        Returns:
            List of lines in the section, or None if not found
        """
        lines = md_content.split('\n')
        section_start = -1
        
        # Find the section header
        for i, line in enumerate(lines):
            if line.strip().startswith(section_title):
                section_start = i
                break
        
        if section_start == -1:
            return None
        
        # Find where this section ends (next section or end of file)
        section_lines = []
        for i in range(section_start + 1, len(lines)):
            current_line = lines[i].strip()
            
            # Stop at next section (### or ##) or at horizontal rule (---)
            if (current_line.startswith('###') or 
                current_line.startswith('##') or 
                current_line.startswith('---')):
                break
            
            section_lines.append(lines[i])
        
        return section_lines
    
    @staticmethod
    def parse_topology_section(lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parse topology section (1.2) to extract claims.
        
        Args:
            lines: Lines from the topology section
            
        Returns:
            List of claim dictionaries
        """
        claims = []
        
        for line in lines:
            stripped_line = line.strip()
            # Look for the topology line with pipe separators
            if '|' in stripped_line and not stripped_line.startswith('|'):
                # Remove any Markdown formatting
                clean_line = re.sub(r'\*\*|\*|`', '', stripped_line)
                # Split by pipe and clean up
                items = [item.strip() for item in clean_line.split('|')]
                
                for item in items:
                    if item and item not in ['Brainstorm', 'Back', 'Front', 'Deploy']:
                        # This is the actual topology line
                        topology_items = [i.strip() for i in item.split() if i.strip()]
                        for topology_item in topology_items:
                            claim_id = f"topology-{topology_item.lower()}"
                            claims.append({
                                "id": claim_id,
                                "text": topology_item,
                                "description": f"Topology compartment: {topology_item}",
                                "checked": True
                            })
                        break
        
        # If we didn't find the specific format, look for the known topology
        if not claims:
            for line in lines:
                if "Brainstorm" in line and "Back" in line and "Front" in line and "Deploy" in line:
                    topology_items = ["Brainstorm", "Back", "Front", "Deploy"]
                    for item in topology_items:
                        claim_id = f"topology-{item.lower()}"
                        claims.append({
                            "id": claim_id,
                            "text": item,
                            "description": f"Topology compartment: {item}",
                            "checked": True
                        })
                    break
        
        return claims
    
    @staticmethod
    def parse_endpoints_section(lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parse endpoints section (1.3) to extract claims from Markdown table.
        
        Args:
            lines: Lines from the endpoints section
            
        Returns:
            List of claim dictionaries
        """
        claims = []
        in_table = False
        headers = []
        
        for line in lines:
            stripped_line = line.strip()
            
            # Detect table start
            if stripped_line.startswith('|') and 'Méthode' in stripped_line:
                in_table = True
                # Extract headers
                headers = [h.strip() for h in stripped_line.split('|')[1:-1]]
                continue
            
            # Detect table separator line
            if in_table and stripped_line.startswith('|---'):
                continue
            
            # Process table rows
            if in_table and stripped_line.startswith('|'):
                if not headers:  # Should not happen, but safety check
                    continue
                    
                cells = [cell.strip() for cell in stripped_line.split('|')[1:-1]]
                if len(cells) >= 2:  # Need at least method and path
                    method = cells[0]
                    path = cells[1]
                    
                    # Get summary if available
                    summary = ""
                    if len(cells) >= 4:
                        summary = cells[3]
                    
                    claim_id = f"endpoint-{method.lower()}-{path.replace('/', '_').replace('{', '').replace('}', '')}"
                    claim_text = f"{method} {path}"
                    
                    claims.append({
                        "id": claim_id,
                        "text": claim_text,
                        "description": summary if summary else f"Endpoint: {method} {path}",
                        "checked": True
                    })
            
            # Detect end of table
            if in_table and not stripped_line.startswith('|') and stripped_line:
                in_table = False
        
        return claims
    
    @staticmethod
    def parse_keys_section(lines: List[str]) -> List[Dict[str, Any]]:
        """
        Parse IR keys section (1.4) to extract claims.
        
        Args:
            lines: Lines from the IR keys section
            
        Returns:
            List of claim dictionaries
        """
        claims = []
        
        # Look for the paragraph describing what should be in this section
        section_text = ' '.join([line.strip() for line in lines if line.strip()])
        
        # Extract potential keys from the text
        key_patterns = [
            (r'intents?', 'Intents', 'Intent definitions and purposes'),
            (r'features?', 'Features', 'System features and capabilities'),
            (r'compartments?', 'Compartments', 'System compartments or modules')
        ]
        
        for pattern, key_name, description in key_patterns:
            if re.search(pattern, section_text, re.IGNORECASE):
                claim_id = f"key-{key_name.lower()}"
                claims.append({
                    "id": claim_id,
                    "text": key_name,
                    "description": description,
                    "checked": True
                })
        
        # If no patterns found, add default keys
        if not claims:
            default_keys = [
                ("Intents", "System intents and purposes"),
                ("Features", "System features and capabilities"),
                ("Compartments", "System compartments or modules")
            ]
            
            for key_name, description in default_keys:
                claim_id = f"key-{key_name.lower()}"
                claims.append({
                    "id": claim_id,
                    "text": key_name,
                    "description": description,
                    "checked": True
                })
        
        return claims


class JSONBuilder:
    """Builder for creating JSON structure from parsed data."""
    
    @staticmethod
    def build_organe(organe_id: str, title: str, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build an organe dictionary.
        
        Args:
            organe_id: The organe ID (e.g., "1.2")
            title: The organe title
            claims: List of claim dictionaries
            
        Returns:
            Organe dictionary
        """
        return {
            "id": organe_id,
            "title": title,
            "claims": claims,
            "verdict": "Accept"  # Default verdict
        }
    
    @staticmethod
    def build_source(genome_path: str, prd_path: str) -> Dict[str, Any]:
        """
        Build source metadata dictionary.
        
        Args:
            genome_path: Path to genome file
            prd_path: Path to PRD file
            
        Returns:
            Source dictionary
        """
        return {
            "genome_path": genome_path,
            "prd_path": prd_path,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    @staticmethod
    def build_json_structure(
        source: Dict[str, Any],
        organes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Build the complete JSON structure.
        
        Args:
            source: Source metadata dictionary
            organes: List of organe dictionaries
            
        Returns:
            Complete JSON structure
        """
        return {
            "source": source,
            "organes": organes
        }


class SchemaValidator:
    """Validator for JSON schema compliance."""
    
    @staticmethod
    def load_schema(schema_path: Path) -> Dict[str, Any]:
        """
        Load JSON schema from file.
        
        Args:
            schema_path: Path to schema file
            
        Returns:
            Schema dictionary
            
        Raises:
            FileNotFoundError: If schema file doesn't exist
            json.JSONDecodeError: If schema is invalid JSON
        """
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def validate_json(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Validate JSON data against schema.
        
        Args:
            data: JSON data to validate
            schema: JSON schema
            
        Returns:
            True if valid
            
        Raises:
            jsonschema.ValidationError: If validation fails
            jsonschema.SchemaError: If schema is invalid
        """
        jsonschema.validate(instance=data, schema=schema)
        return True


class IRMarkdownToJSONConverter:
    """Main converter class orchestrating the conversion process."""
    
    def __init__(self):
        """Initialize converter with required components."""
        self.parser = MarkdownParser()
        self.builder = JSONBuilder()
        self.validator = SchemaValidator()
    
    def convert(
        self,
        md_path: Path,
        json_path: Path,
        schema_path: Path
    ) -> bool:
        """
        Convert IR Markdown to JSON with schema validation.
        
        Args:
            md_path: Path to input Markdown file
            json_path: Path to output JSON file
            schema_path: Path to JSON schema file
            
        Returns:
            True if conversion successful
            
        Raises:
            FileNotFoundError: If input files don't exist
            ValueError: If parsing fails
            jsonschema.ValidationError: If validation fails
        """
        # Read Markdown file
        if not md_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {md_path}")
        
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Extract source paths
        genome_path, prd_path = self.parser.extract_source_paths(md_content)
        
        # Parse sections
        organes = []
        
        # Section 1.2: Topology
        topology_lines = self.parser.find_section_lines(
            md_content, "### 1.2 Topologie déclarée"
        )
        if topology_lines:
            topology_claims = self.parser.parse_topology_section(topology_lines)
            if topology_claims:
                organes.append(self.builder.build_organe(
                    "1.2", "Topologie déclarée", topology_claims
                ))
        
        # Section 1.3: Endpoints
        endpoints_lines = self.parser.find_section_lines(
            md_content, "### 1.3 Endpoints"
        )
        if endpoints_lines:
            endpoints_claims = self.parser.parse_endpoints_section(endpoints_lines)
            if endpoints_claims:
                organes.append(self.builder.build_organe(
                    "1.3", "Endpoints", endpoints_claims
                ))
        
        # Section 1.4: IR Keys
        keys_lines = self.parser.find_section_lines(
            md_content, "### 1.4 Clés IR (intents, features, compartments)"
        )
        if not keys_lines:
            # Try alternative title
            keys_lines = self.parser.find_section_lines(
                md_content, "### 1.4 Clés IR"
            )
        
        if keys_lines:
            keys_claims = self.parser.parse_keys_section(keys_lines)
            if keys_claims:
                organes.append(self.builder.build_organe(
                    "1.4", "Clés IR", keys_claims
                ))
        
        # Build complete JSON structure
        source = self.builder.build_source(genome_path, prd_path)
        json_data = self.builder.build_json_structure(source, organes)
        
        # Load and validate schema
        schema = self.validator.load_schema(schema_path)
        self.validator.validate_json(json_data, schema)
        
        # Write JSON file
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return True


def ir_md_to_json(md_path: Path, json_path: Path, schema_path: Path) -> bool:
    """
    Convert IR inventory Markdown to JSON format with schema validation.
    
    This function reads an IR inventory Markdown file, parses specific sections,
    converts them to a structured JSON format, validates against a JSON schema,
    and writes the result to a JSON file.
    
    Args:
        md_path: Path to the input Markdown file
        json_path: Path where the output JSON file should be written
        schema_path: Path to the JSON schema file for validation
        
    Returns:
        True if the conversion and validation were successful
        
    Raises:
        FileNotFoundError: If any of the input files don't exist
        ValueError: If the Markdown cannot be parsed correctly
        jsonschema.ValidationError: If the generated JSON doesn't conform to the schema
        json.JSONDecodeError: If the schema file contains invalid JSON
        
    Example:
        >>> from pathlib import Path
        >>> success = ir_md_to_json(
        ...     Path("ir_inventaire.md"),
        ...     Path("output.json"),
        ...     Path("schema.json")
        ... )
        >>> print(success)
        True
    """
    converter = IRMarkdownToJSONConverter()
    return converter.convert(md_path, json_path, schema_path)