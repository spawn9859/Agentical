"""AI engine for visual analysis and decision making using Google Gemini."""

import json
import base64
from io import BytesIO
from typing import Optional, Dict, List, Any, Tuple
from PIL import Image
import google.generativeai as genai
try:
    from ..utils.logger import logger
    from ..utils.config import ConfigManager
except ImportError:
    from utils.logger import logger
    from utils.config import ConfigManager


class AIEngine:
    """AI engine for analyzing desktop state and planning actions."""
    
    def __init__(self, config: ConfigManager):
        """Initialize AI engine.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.model = None
        self.vision_model = None
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize Gemini models."""
        try:
            api_key = self.config.api_key
            if not api_key:
                logger.error("Gemini API key not configured")
                return
            
            # Configure API
            genai.configure(api_key=api_key)
            
            # Initialize models
            model_name = self.config.model_name
            self.model = genai.GenerativeModel(model_name)
            self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
            
            logger.info(f"AI models initialized: {model_name}")
            
        except Exception as e:
            logger.error_with_context(e, "AI model initialization")
    
    def analyze_screen(self, screenshot: Image.Image, context: str = "") -> Dict[str, Any]:
        """Analyze screenshot to understand desktop state.
        
        Args:
            screenshot: PIL Image of the desktop
            context: Additional context about the task
            
        Returns:
            Dictionary with analysis results
        """
        try:
            if not self.vision_model:
                logger.error("Vision model not initialized")
                return {"error": "Vision model not available"}
            
            # Get vision analysis prompt
            prompt = self.config.get_prompt('vision_analysis_prompt')
            if context:
                prompt += f"\n\nAdditional context: {context}"
            
            # Convert image to format suitable for Gemini
            response = self.vision_model.generate_content([prompt, screenshot])
            
            analysis = {
                "description": response.text,
                "confidence": 0.8,  # Placeholder confidence score
                "timestamp": "",
                "elements_detected": [],
                "current_state": "unknown"
            }
            
            logger.log_ai_decision("screen analysis", analysis["description"], analysis["confidence"])
            return analysis
            
        except Exception as e:
            logger.error_with_context(e, "screen analysis")
            return {"error": str(e)}
    
    def plan_task(self, goal: str, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan a sequence of actions to accomplish a goal.
        
        Args:
            goal: User's goal description
            current_state: Current desktop state from screen analysis
            
        Returns:
            List of action dictionaries
        """
        try:
            if not self.model:
                logger.error("Text model not initialized")
                return []
            
            # Get task planning prompt
            prompt_template = self.config.get_prompt('task_planning_prompt')
            if not prompt_template:
                logger.error("Task planning prompt not found")
                return []
            
            # Format prompt with goal and current state
            prompt = prompt_template.format(
                goal=goal,
                current_state=current_state.get('description', 'Unknown state')
            )
            
            # Generate plan
            response = self.model.generate_content(prompt)
            
            # Try to parse JSON response
            try:
                actions = json.loads(response.text)
                if isinstance(actions, list):
                    logger.log_ai_decision("task planning", f"Generated {len(actions)} actions", 0.9)
                    return actions
                else:
                    logger.warning("Task plan response is not a list")
                    return []
            except json.JSONDecodeError:
                logger.warning("Failed to parse task plan as JSON")
                # Fallback: create simple action list from text
                return self._parse_text_plan(response.text)
            
        except Exception as e:
            logger.error_with_context(e, "task planning")
            return []
    
    def _parse_text_plan(self, plan_text: str) -> List[Dict[str, Any]]:
        """Parse text-based plan into action list.
        
        Args:
            plan_text: Plan as text
            
        Returns:
            List of action dictionaries
        """
        actions = []
        lines = plan_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Simple parsing for common actions
            if 'click' in line.lower():
                actions.append({
                    "action": "click",
                    "x": 100,  # Placeholder coordinates
                    "y": 100,
                    "description": line
                })
            elif 'type' in line.lower():
                actions.append({
                    "action": "type",
                    "text": "example text",  # Placeholder text
                    "description": line
                })
            elif 'key' in line.lower() or 'press' in line.lower():
                actions.append({
                    "action": "key",
                    "key": "enter",  # Placeholder key
                    "description": line
                })
            else:
                actions.append({
                    "action": "wait",
                    "seconds": 1.0,
                    "description": line
                })
        
        return actions
    
    def check_action_safety(self, action: Dict[str, Any], context: str) -> Tuple[bool, str]:
        """Use AI to check if an action is safe.
        
        Args:
            action: Action dictionary to check
            context: Current context
            
        Returns:
            Tuple of (is_safe, explanation)
        """
        try:
            if not self.model:
                logger.error("Text model not initialized")
                return True, "AI safety check unavailable"
            
            # Get safety check prompt
            prompt_template = self.config.get_prompt('safety_check_prompt')
            if not prompt_template:
                return True, "Safety check prompt not found"
            
            # Format prompt
            prompt = prompt_template.format(
                action=json.dumps(action),
                context=context
            )
            
            # Get AI safety assessment
            response = self.model.generate_content(prompt)
            response_text = response.text.strip().upper()
            
            is_safe = response_text.startswith('SAFE')
            explanation = response.text
            
            logger.log_safety_check(
                str(action), 
                "SAFE" if is_safe else "UNSAFE", 
                explanation
            )
            
            return is_safe, explanation
            
        except Exception as e:
            logger.error_with_context(e, "AI safety check")
            # Default to safe if AI check fails
            return True, f"Safety check failed: {str(e)}"
    
    def improve_plan(self, actions: List[Dict[str, Any]], feedback: str) -> List[Dict[str, Any]]:
        """Improve an action plan based on feedback.
        
        Args:
            actions: Current action plan
            feedback: Feedback about what went wrong
            
        Returns:
            Improved action plan
        """
        try:
            if not self.model:
                logger.error("Text model not initialized")
                return actions
            
            prompt = f"""
            The following action plan failed:
            {json.dumps(actions, indent=2)}
            
            Feedback: {feedback}
            
            Please provide an improved action plan in the same JSON format.
            Consider the feedback and make necessary adjustments.
            """
            
            response = self.model.generate_content(prompt)
            
            try:
                improved_actions = json.loads(response.text)
                if isinstance(improved_actions, list):
                    logger.log_ai_decision("plan improvement", f"Improved plan with {len(improved_actions)} actions", 0.8)
                    return improved_actions
            except json.JSONDecodeError:
                logger.warning("Failed to parse improved plan as JSON")
            
            return actions  # Return original if improvement fails
            
        except Exception as e:
            logger.error_with_context(e, "plan improvement")
            return actions
    
    def extract_coordinates(self, description: str, screenshot: Image.Image) -> Optional[Tuple[int, int]]:
        """Extract coordinates for a described UI element.
        
        Args:
            description: Description of the UI element
            screenshot: Current screenshot
            
        Returns:
            Tuple of (x, y) coordinates if found, None otherwise
        """
        try:
            if not self.vision_model:
                logger.error("Vision model not initialized")
                return None
            
            prompt = f"""
            In this screenshot, find the UI element described as: "{description}"
            
            Provide the approximate center coordinates as JSON in this format:
            {{"x": 123, "y": 456}}
            
            If the element is not found, respond with {{"x": null, "y": null}}
            """
            
            response = self.vision_model.generate_content([prompt, screenshot])
            
            try:
                coords = json.loads(response.text)
                if coords.get('x') is not None and coords.get('y') is not None:
                    return (coords['x'], coords['y'])
            except json.JSONDecodeError:
                logger.warning("Failed to parse coordinates from AI response")
            
            return None
            
        except Exception as e:
            logger.error_with_context(e, "coordinate extraction")
            return None
    
    def is_available(self) -> bool:
        """Check if AI models are available.
        
        Returns:
            True if models are initialized and ready
        """
        return self.model is not None and self.vision_model is not None
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about loaded models.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.config.model_name,
            "api_key_configured": bool(self.config.api_key),
            "models_loaded": self.is_available(),
            "text_model": "Available" if self.model else "Not available",
            "vision_model": "Available" if self.vision_model else "Not available"
        }