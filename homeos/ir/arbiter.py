from typing import Dict, List, Tuple

class SullivanArbiter:
    """Validator for genome dictionaries."""

    REQUIRED_KEYS = {'metadata', 'topology', 'endpoints'}
    OPTIONAL_KEYS = {'intents', 'features', 'compartments'}

    def validate(self, genome: Dict) -> Dict[str, bool | List[str]]:
        """
        Validate a genome dictionary.

        Args:
            genome: Dictionary to validate

        Returns:
            Dictionary with:
            - 'valid': Boolean indicating if genome is valid
            - 'errors': List of error messages if invalid
        """
        errors = []

        # Check required keys
        for key in self.REQUIRED_KEYS:
            if key not in genome:
                errors.append(f"Missing required key: {key}")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

class SullivanArbiter:
    def validate(self, genome: dict) -> dict:
        """
        Validates a genome dictionary.

        Args:
        genome (dict): The genome dictionary to validate.

        Returns:
        dict: A dictionary with 'valid' and 'errors' keys. 'valid' is a boolean indicating whether the genome is valid, and 'errors' is a list of error messages.
        """

        # Define the required top-level keys
        required_keys = ['metadata', 'topology', 'endpoints']
        optional_keys = ['intents', 'features', 'compartments']

        # Initialize the validation result
        result = {'valid': True, 'errors': []}

        # Check for missing required keys
        for key in required_keys:
            if key not in genome:
                result['valid'] = False
                result['errors'].append(f"Missing required key: {key}")

        # If the genome is invalid, return the result
        if not result['valid']:
            return result

        # If the genome is valid, return the result
        return result


# Example usage:
if __name__ == "__main__":
    arbiter = SullivanArbiter()

    # Test with a valid genome
    valid_genome = {
        'metadata': {},
        'topology': {},
        'endpoints': {},
        'intents': {},
        'features': {},
        'compartments': {}
    }
    print(arbiter.validate(valid_genome))

    # Test with an invalid genome
    invalid_genome = {
        'metadata': {},
        'topology': {}
    }
    print(arbiter.validate(invalid_genome))