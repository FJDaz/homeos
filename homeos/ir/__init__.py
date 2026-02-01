homeos/
├── ir/
│   ├── __init__.py
│   ├── pipeline.py
│   ├── models.py
│   ├── services.py
│   └── arbiter.py
└── tests/
    └── test_ir_pipeline.py

import json
from pathlib import Path
from typing import Optional, Dict

from Backend.Prod.core.genome_generator import generate_genome

class IRPipeline:
    def run(self, backend_path: Optional[Path] = None, prd_path: Optional[Path] = None, output_path: Optional[Path] = None) -> Dict:
        """
        Run the IR pipeline to generate the genome_v1 dict.

        Args:
        - backend_path (Optional[Path]): The path to the backend (default: None)
        - prd_path (Optional[Path]): The path to the PRD (default: None)
        - output_path (Optional[Path]): The path to write the genome_v1 dict (default: None)

        Returns:
        - genome_v1 (Dict): The generated genome_v1 dict
        """

        # Call Backend.Prod.core.genome_generator.generate_genome to get base genome dict
        genome = generate_genome()

        # Ensure genome has top-level keys intents (list), features (list), compartments (list); add empty lists if missing
        genome.setdefault("intents", [])
        genome.setdefault("features", [])
        genome.setdefault("compartments", [])

        # Create the genome_v1 dict
        genome_v1 = genome

        # Write to output_path if provided (default output/studio/genome_v1.json)
        if output_path is None:
            output_path = Path("output/studio/genome_v1.json")
        with open(output_path, "w") as f:
            json.dump(genome_v1, f, indent=4)

        return genome_v1