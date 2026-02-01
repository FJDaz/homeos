"""
Mode Manager Module for Homeos System.

This module provides functionality for managing operational modes (construction vs project)
including mode detection, configuration loading, and mode switching.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import yaml


class HomeosMode(Enum):
    """Enumeration of available Homeos operational modes."""
    
    CONSTRUCTION = "construction"
    PROJECT = "project"


class ModeConfiguration:
    """Loads and provides access to mode-specific configuration."""
    
    def __init__(self, mode: HomeosMode):
        """
        Initialize configuration for a specific mode.
        
        Args:
            mode: The operational mode to load configuration for
        """
        self.mode = mode
        self.config_path = self._get_config_path()
        self.z_index_layers: Optional[List[str]] = None
        self.allowed_frontend_stack: Optional[List[str]] = None
        self.workflow_steps: Optional[List[str]] = None
        self._load_config()
    
    def _get_config_path(self) -> Path:
        """
        Get the path to the configuration file for the current mode.
        
        Returns:
            Path object pointing to the configuration file
            
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
        """
        # Resolve path relative to the homeos package
        package_root = Path(__file__).resolve().parent.parent
        config_path = package_root / 'config' / f'{self.mode.value}_config.yaml'
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )
        
        return config_path
    
    def _load_config(self) -> None:
        """
        Load configuration from YAML file.
        
        Raises:
            yaml.YAMLError: If the YAML file is malformed
        """
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.z_index_layers = config.get('z_index_layers')
        self.allowed_frontend_stack = config.get('frontend_stack')
        self.workflow_steps = config.get('workflow')
    
    @property
    def frontend_stack(self) -> Optional[List[str]]:
        """
        Get the allowed frontend stack (alias for allowed_frontend_stack).
        
        Returns:
            List of allowed frontend technologies or None if not configured
        """
        return self.allowed_frontend_stack
    
    @property
    def workflow(self) -> Optional[List[str]]:
        """
        Get the workflow steps (alias for workflow_steps).
        
        Returns:
            List of workflow steps or None if not configured
        """
        return self.workflow_steps
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: The configuration key to retrieve
            default: Default value if key is not found
            
        Returns:
            The configuration value or default
        """
        config = self._load_full_config()
        return config.get(key, default)
    
    def _load_full_config(self) -> Dict[str, Any]:
        """Load and return the full configuration dictionary."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f) or {}


class ModeManager:
    """
    Singleton manager for Homeos operational modes.
    
    Manages mode detection, switching, and provides access to mode-specific adapters.
    """
    
    _instance: Optional['ModeManager'] = None
    _mode_file = '.homeos_mode'
    _construction_dir = 'homeos_construction'
    
    def __new__(cls) -> 'ModeManager':
        """
        Create or return the singleton instance.
        
        Returns:
            The singleton ModeManager instance
        """
        if cls._instance is None:
            cls._instance = super(ModeManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize the mode manager instance."""
        self.current_mode: Optional[HomeosMode] = None
        self.current_config: Optional[ModeConfiguration] = None
        self._detect_current_mode()
        self._load_current_config()
    
    def _detect_current_mode(self) -> None:
        """
        Detect the current operational mode.
        
        Detection order:
        1. Check .homeos_mode file
        2. Check for homeos_construction directory
        3. Default to PROJECT mode
        """
        if self._mode_file_exists():
            self.current_mode = self._read_mode_from_file()
        elif self._construction_dir_exists():
            self.current_mode = HomeosMode.CONSTRUCTION
        else:
            self.current_mode = HomeosMode.PROJECT
    
    def _mode_file_exists(self) -> bool:
        """Check if the mode file exists."""
        return os.path.exists(self._mode_file)
    
    def _construction_dir_exists(self) -> bool:
        """Check if the construction directory exists."""
        return os.path.exists(self._construction_dir)
    
    def _read_mode_from_file(self) -> HomeosMode:
        """
        Read the mode from the .homeos_mode file.
        
        Returns:
            The mode read from the file
            
        Raises:
            ValueError: If the file contains an invalid mode value
        """
        with open(self._mode_file, 'r') as f:
            # Read first line, strip whitespace
            mode_line = f.readline().strip()
            
            # Handle potential comments or empty lines
            if '#' in mode_line:
                mode_line = mode_line.split('#')[0].strip()
            
            if not mode_line:
                raise ValueError(f"Empty mode in {self._mode_file}")
            
            try:
                return HomeosMode(mode_line)
            except ValueError as e:
                raise ValueError(
                    f"Invalid mode '{mode_line}' in {self._mode_file}. "
                    f"Valid modes: {[m.value for m in HomeosMode]}"
                ) from e
    
    def _load_current_config(self) -> None:
        """Load configuration for the current mode."""
        if self.current_mode:
            self.current_config = ModeConfiguration(self.current_mode)
    
    def switch_mode(self, new_mode: HomeosMode) -> None:
        """
        Switch to a new operational mode.
        
        Args:
            new_mode: The mode to switch to
            
        Raises:
            ValueError: If mode switch validation fails
        """
        if self.current_mode == new_mode:
            return  # Already in the requested mode
        
        self._validate_mode_switch(new_mode)
        self._save_current_state()
        
        # Update mode and configuration
        self.current_mode = new_mode
        self._load_current_config()
        
        self._reconfigure_components()
        self._write_current_mode()
    
    def _validate_mode_switch(self, new_mode: HomeosMode) -> None:
        """
        Validate that a mode switch is allowed.
        
        Args:
            new_mode: The mode to switch to
            
        Raises:
            ValueError: If the mode switch is not allowed
        """
        # Basic validation - can be extended with business logic
        if not isinstance(new_mode, HomeosMode):
            raise ValueError(f"Invalid mode type: {type(new_mode)}")
        
        # Add any business-specific validation rules here
        # Example: Prevent switching from PROJECT to CONSTRUCTION if certain conditions exist
        if (self.current_mode == HomeosMode.PROJECT and 
            new_mode == HomeosMode.CONSTRUCTION):
            # Check if construction is allowed
            pass
    
    def _save_current_state(self) -> None:
        """
        Save the current system state before mode switch.
        
        This method should be extended to save application state,
        database connections, file handles, etc.
        """
        # Placeholder for state saving logic
        # In a real implementation, this would save:
        # - Open file handles
        # - Database connections
        # - Cache state
        # - User sessions
        pass
    
    def _reconfigure_components(self) -> None:
        """
        Reconfigure system components for the new mode.
        
        This method should be extended to reconfigure:
        - Database connections
        - API endpoints
        - Service configurations
        - UI components
        """
        # Placeholder for component reconfiguration logic
        # In a real implementation, this would:
        # - Update service configurations
        # - Switch database connections
        # - Reload UI components
        # - Update API routes
        pass
    
    def _write_current_mode(self) -> None:
        """Write the current mode to the .homeos_mode file."""
        with open(self._mode_file, 'w') as f:
            f.write(f"{self.current_mode.value}\n")
            f.write(f"# Mode switched at: {datetime.now().isoformat()}\n")
            f.write(f"switched_at: {datetime.now().isoformat()}\n")
    
    def get_aetherflow(self) -> str:
        """
        Get the Aetherflow adapter for the current mode.
        
        Returns:
            The adapter identifier string
            
        Note:
            In a real implementation, this would import and return
            actual adapter instances
        """
        if self.current_mode == HomeosMode.CONSTRUCTION:
            return 'construction_adapter'
        else:
            return 'project_adapter'
    
    def get_sullivan(self) -> str:
        """
        Get the Sullivan adapter for the current mode.
        
        Returns:
            The adapter identifier string
            
        Note:
            In a real implementation, this would import and return
            actual adapter instances
        """
        if self.current_mode == HomeosMode.CONSTRUCTION:
            return 'construction_adapter'
        else:
            return 'project_adapter'
    
    def get_configuration(self) -> ModeConfiguration:
        """
        Get the current mode configuration.
        
        Returns:
            The current ModeConfiguration instance
            
        Raises:
            RuntimeError: If mode is not initialized
        """
        if self.current_config is None:
            raise RuntimeError("Mode configuration not initialized")
        return self.current_config
    
    def get_mode_info(self) -> Dict[str, Any]:
        """
        Get information about the current mode.
        
        Returns:
            Dictionary with mode information
        """
        return {
            'mode': self.current_mode.value if self.current_mode else None,
            'config_path': str(self.current_config.config_path) if self.current_config else None,
            'z_index_layers': self.current_config.z_index_layers if self.current_config else None,
            'frontend_stack': self.current_config.frontend_stack if self.current_config else None,
            'workflow': self.current_config.workflow if self.current_config else None,
        }


# Singleton instance
mode_manager = ModeManager()