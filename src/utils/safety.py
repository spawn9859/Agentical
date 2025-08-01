"""Safety features and monitoring for desktop automation."""

import time
import threading
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
try:
    from ..utils.logger import logger
    from ..utils.config import ConfigManager
except ImportError:
    from utils.logger import logger
    from utils.config import ConfigManager


@dataclass
class RestrictedArea:
    """Represents a restricted screen area."""
    x: int
    y: int
    width: int
    height: int
    description: str = ""
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is within restricted area."""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)


class SafetyMonitor:
    """Monitors and enforces safety constraints for desktop automation."""
    
    def __init__(self, config: ConfigManager):
        """Initialize safety monitor.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.action_history: List[Dict[str, Any]] = []
        self.restricted_areas: List[RestrictedArea] = []
        self._emergency_stop = False
        self._lock = threading.Lock()
        
        self.load_restricted_areas()
        self.setup_emergency_stop()
    
    def load_restricted_areas(self) -> None:
        """Load restricted areas from configuration."""
        areas_config = self.config.get('safety.restricted_areas', [])
        self.restricted_areas = []
        
        for area_config in areas_config:
            area = RestrictedArea(
                x=area_config.get('x', 0),
                y=area_config.get('y', 0),
                width=area_config.get('width', 0),
                height=area_config.get('height', 0),
                description=area_config.get('description', '')
            )
            self.restricted_areas.append(area)
            logger.debug(f"Loaded restricted area: {area.description} at ({area.x}, {area.y})")
    
    def setup_emergency_stop(self) -> None:
        """Set up emergency stop mechanism."""
        # This would normally set up a global hotkey listener
        # For now, we'll implement a simple flag system
        self._emergency_stop = False
        logger.info("Emergency stop mechanism initialized")
    
    def is_emergency_stop_activated(self) -> bool:
        """Check if emergency stop is activated."""
        return self._emergency_stop
    
    def activate_emergency_stop(self) -> None:
        """Activate emergency stop."""
        with self._lock:
            self._emergency_stop = True
            logger.critical("EMERGENCY STOP ACTIVATED")
    
    def deactivate_emergency_stop(self) -> None:
        """Deactivate emergency stop."""
        with self._lock:
            self._emergency_stop = False
            logger.info("Emergency stop deactivated")
    
    def check_action_safety(self, action_type: str, **kwargs) -> Tuple[bool, str]:
        """Check if an action is safe to perform.
        
        Args:
            action_type: Type of action (click, type, key, etc.)
            **kwargs: Action parameters
            
        Returns:
            Tuple of (is_safe, reason)
        """
        if self._emergency_stop:
            return False, "Emergency stop is activated"
        
        # Check rate limiting
        if not self._check_rate_limit():
            return False, "Rate limit exceeded"
        
        # Check coordinates for click actions
        if action_type == "click":
            x, y = kwargs.get('x', 0), kwargs.get('y', 0)
            if not self._check_coordinates_safe(x, y):
                return False, f"Coordinates ({x}, {y}) are in restricted area"
        
        # Check for dangerous key combinations
        if action_type == "key":
            key = kwargs.get('key', '')
            if not self._check_key_safe(key):
                return False, f"Key combination '{key}' is potentially dangerous"
        
        # Check for dangerous text input
        if action_type == "type":
            text = kwargs.get('text', '')
            if not self._check_text_safe(text):
                return False, f"Text input contains potentially dangerous content"
        
        return True, "Action is safe"
    
    def _check_rate_limit(self) -> bool:
        """Check if action rate limit is exceeded."""
        max_actions = self.config.get('safety.max_actions_per_minute', 60)
        current_time = time.time()
        
        # Remove actions older than 1 minute
        self.action_history = [
            action for action in self.action_history 
            if current_time - action['timestamp'] < 60
        ]
        
        return len(self.action_history) < max_actions
    
    def _check_coordinates_safe(self, x: int, y: int) -> bool:
        """Check if coordinates are in a safe area."""
        for area in self.restricted_areas:
            if area.contains_point(x, y):
                logger.warning(f"Coordinates ({x}, {y}) blocked by restriction: {area.description}")
                return False
        return True
    
    def _check_key_safe(self, key: str) -> bool:
        """Check if key combination is safe."""
        dangerous_keys = [
            'alt+f4', 'ctrl+alt+del', 'win+l', 'alt+tab',
            'ctrl+shift+esc', 'win+r'
        ]
        
        key_lower = key.lower().strip()
        for dangerous in dangerous_keys:
            if dangerous in key_lower:
                logger.warning(f"Dangerous key combination blocked: {key}")
                return False
        
        return True
    
    def _check_text_safe(self, text: str) -> bool:
        """Check if text input is safe."""
        # Check for potentially dangerous commands or paths
        dangerous_patterns = [
            'rm -rf', 'del /f', 'format c:', 'shutdown', 'reboot',
            'cmd.exe', 'powershell.exe', '../../', '../..'
        ]
        
        text_lower = text.lower()
        for pattern in dangerous_patterns:
            if pattern in text_lower:
                logger.warning(f"Dangerous text pattern blocked: {pattern}")
                return False
        
        return True
    
    def record_action(self, action_type: str, **kwargs) -> None:
        """Record an action in the history.
        
        Args:
            action_type: Type of action performed
            **kwargs: Action parameters
        """
        action_record = {
            'type': action_type,
            'timestamp': time.time(),
            'parameters': kwargs
        }
        
        with self._lock:
            self.action_history.append(action_record)
        
        logger.log_action(action_type, kwargs)
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get current safety status.
        
        Returns:
            Dictionary with safety status information
        """
        current_time = time.time()
        recent_actions = [
            action for action in self.action_history 
            if current_time - action['timestamp'] < 60
        ]
        
        return {
            'emergency_stop': self._emergency_stop,
            'actions_last_minute': len(recent_actions),
            'max_actions_per_minute': self.config.get('safety.max_actions_per_minute', 60),
            'restricted_areas_count': len(self.restricted_areas),
            'safe_mode_enabled': self.config.safe_mode
        }