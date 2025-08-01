"""Configuration management for Agentical application."""

import os
import yaml
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages application configuration from YAML files."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir
        self._settings = {}
        self._prompts = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from YAML files."""
        # Load main settings
        settings_path = os.path.join(self.config_dir, "settings.yaml")
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                self._settings = yaml.safe_load(f)
        
        # Load prompts
        prompts_path = os.path.join(self.config_dir, "prompts.yaml")
        if os.path.exists(prompts_path):
            with open(prompts_path, 'r') as f:
                self._prompts = yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'api.gemini_api_key')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_prompt(self, prompt_name: str) -> Optional[str]:
        """Get AI prompt by name.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            Prompt text or None if not found
        """
        return self._prompts.get(prompt_name)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation.
        
        Args:
            key: Configuration key (e.g., 'api.gemini_api_key')
            value: Value to set
        """
        keys = key.split('.')
        config = self._settings
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        settings_path = os.path.join(self.config_dir, "settings.yaml")
        os.makedirs(self.config_dir, exist_ok=True)
        
        with open(settings_path, 'w') as f:
            yaml.dump(self._settings, f, default_flow_style=False)
    
    @property
    def api_key(self) -> str:
        """Get Gemini API key."""
        return self.get('api.gemini_api_key', '')
    
    @property
    def model_name(self) -> str:
        """Get Gemini model name."""
        return self.get('api.model_name', 'gemini-1.5-flash')
    
    @property
    def safe_mode(self) -> bool:
        """Check if safe mode is enabled."""
        return self.get('desktop.safe_mode', True)
    
    @property
    def debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get('app.debug', False)