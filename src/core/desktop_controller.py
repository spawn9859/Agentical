"""Desktop control for mouse and keyboard operations."""

import time
import pyautogui
from typing import Optional, Tuple, List
try:
    from ..utils.logger import logger
    from ..utils.config import ConfigManager
    from ..utils.safety import SafetyMonitor
except ImportError:
    from utils.logger import logger
    from utils.config import ConfigManager
    from utils.safety import SafetyMonitor


class DesktopController:
    """Handles mouse and keyboard control operations."""
    
    def __init__(self, config: ConfigManager, safety_monitor: SafetyMonitor):
        """Initialize desktop controller.
        
        Args:
            config: Configuration manager instance
            safety_monitor: Safety monitor instance
        """
        self.config = config
        self.safety_monitor = safety_monitor
        
        # Configure PyAutoGUI
        pyautogui.PAUSE = config.get('desktop.action_delay', 0.5)
        pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort
        
        logger.info("Desktop controller initialized")
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> bool:
        """Click at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button ('left', 'right', 'middle')
            clicks: Number of clicks
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Safety check
            is_safe, reason = self.safety_monitor.check_action_safety(
                'click', x=x, y=y, button=button, clicks=clicks
            )
            if not is_safe:
                logger.warning(f"Click action blocked: {reason}")
                return False
            
            # Perform click
            pyautogui.click(x, y, clicks=clicks, button=button)
            
            # Record action
            self.safety_monitor.record_action(
                'click', x=x, y=y, button=button, clicks=clicks
            )
            
            logger.debug(f"Clicked at ({x}, {y}) with {button} button, {clicks} times")
            return True
            
        except Exception as e:
            logger.error_with_context(e, f"click at ({x}, {y})")
            return False
    
    def double_click(self, x: int, y: int) -> bool:
        """Double-click at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if successful, False otherwise
        """
        return self.click(x, y, clicks=2)
    
    def right_click(self, x: int, y: int) -> bool:
        """Right-click at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if successful, False otherwise
        """
        return self.click(x, y, button='right')
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
        """Drag from start to end coordinates.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Duration of drag in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Safety checks for both start and end positions
            is_safe, reason = self.safety_monitor.check_action_safety(
                'click', x=start_x, y=start_y
            )
            if not is_safe:
                logger.warning(f"Drag start position blocked: {reason}")
                return False
            
            is_safe, reason = self.safety_monitor.check_action_safety(
                'click', x=end_x, y=end_y
            )
            if not is_safe:
                logger.warning(f"Drag end position blocked: {reason}")
                return False
            
            # Perform drag
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
            
            # Record action
            self.safety_monitor.record_action(
                'drag', start_x=start_x, start_y=start_y, 
                end_x=end_x, end_y=end_y, duration=duration
            )
            
            logger.debug(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
            
        except Exception as e:
            logger.error_with_context(e, f"drag from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return False
    
    def scroll(self, x: int, y: int, clicks: int, direction: str = 'vertical') -> bool:
        """Scroll at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            clicks: Number of scroll clicks (positive=up/right, negative=down/left)
            direction: 'vertical' or 'horizontal'
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Safety check
            is_safe, reason = self.safety_monitor.check_action_safety(
                'scroll', x=x, y=y, clicks=clicks, direction=direction
            )
            if not is_safe:
                logger.warning(f"Scroll action blocked: {reason}")
                return False
            
            # Move to position first
            pyautogui.moveTo(x, y)
            
            # Perform scroll
            if direction == 'vertical':
                pyautogui.scroll(clicks)
            else:
                pyautogui.hscroll(clicks)
            
            # Record action
            self.safety_monitor.record_action(
                'scroll', x=x, y=y, clicks=clicks, direction=direction
            )
            
            logger.debug(f"Scrolled {clicks} clicks {direction} at ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error_with_context(e, f"scroll at ({x}, {y})")
            return False
    
    def type_text(self, text: str, interval: float = 0.0) -> bool:
        """Type text with optional interval between characters.
        
        Args:
            text: Text to type
            interval: Interval between characters in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Safety check
            is_safe, reason = self.safety_monitor.check_action_safety(
                'type', text=text
            )
            if not is_safe:
                logger.warning(f"Type action blocked: {reason}")
                return False
            
            # Type text
            pyautogui.typewrite(text, interval=interval)
            
            # Record action
            self.safety_monitor.record_action('type', text=text, interval=interval)
            
            logger.debug(f"Typed text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            return True
            
        except Exception as e:
            logger.error_with_context(e, f"type text '{text[:50]}'")
            return False
    
    def press_key(self, key: str, presses: int = 1) -> bool:
        """Press a key or key combination.
        
        Args:
            key: Key name or combination (e.g., 'enter', 'ctrl+c', 'alt+tab')
            presses: Number of times to press
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Safety check
            is_safe, reason = self.safety_monitor.check_action_safety(
                'key', key=key
            )
            if not is_safe:
                logger.warning(f"Key action blocked: {reason}")
                return False
            
            # Handle key combinations
            if '+' in key:
                keys = key.split('+')
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key, presses=presses)
            
            # Record action
            self.safety_monitor.record_action('key', key=key, presses=presses)
            
            logger.debug(f"Pressed key: '{key}' {presses} times")
            return True
            
        except Exception as e:
            logger.error_with_context(e, f"press key '{key}'")
            return False
    
    def move_mouse(self, x: int, y: int, duration: float = 0.0) -> bool:
        """Move mouse to specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration of movement in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Safety check
            is_safe, reason = self.safety_monitor.check_action_safety(
                'move', x=x, y=y
            )
            if not is_safe:
                logger.warning(f"Mouse move blocked: {reason}")
                return False
            
            # Move mouse
            pyautogui.moveTo(x, y, duration=duration)
            
            # Record action
            self.safety_monitor.record_action('move', x=x, y=y, duration=duration)
            
            logger.debug(f"Moved mouse to ({x}, {y})")
            return True
            
        except Exception as e:
            logger.error_with_context(e, f"move mouse to ({x}, {y})")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return pyautogui.position()
    
    def wait(self, seconds: float) -> bool:
        """Wait for specified duration.
        
        Args:
            seconds: Duration to wait in seconds
            
        Returns:
            True if successful, False if interrupted
        """
        try:
            if self.safety_monitor.is_emergency_stop_activated():
                logger.warning("Wait interrupted by emergency stop")
                return False
            
            time.sleep(seconds)
            
            # Record action
            self.safety_monitor.record_action('wait', seconds=seconds)
            
            logger.debug(f"Waited {seconds} seconds")
            return True
            
        except Exception as e:
            logger.error_with_context(e, f"wait {seconds} seconds")
            return False
    
    def capture_and_click_image(self, image_path: str, threshold: float = 0.8) -> bool:
        """Find and click on an image on the screen.
        
        Args:
            image_path: Path to image template
            threshold: Matching threshold
            
        Returns:
            True if found and clicked, False otherwise
        """
        try:
            # This would require integration with screen capture
            # For now, return False as placeholder
            logger.warning("Image-based clicking not yet implemented")
            return False
            
        except Exception as e:
            logger.error_with_context(e, f"capture and click image '{image_path}'")
            return False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size.
        
        Returns:
            Tuple of (width, height)
        """
        return pyautogui.size()