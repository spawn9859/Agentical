"""
Example usage script for Agentical - demonstrates basic functionality
without requiring external dependencies for testing.
"""

import sys
import os
sys.path.insert(0, '/home/runner/work/Agentical/Agentical/src')

def demo_configuration():
    """Demonstrate configuration management."""
    print("=== Configuration Demo ===")
    
    from utils.config import ConfigManager
    
    # Initialize config
    config = ConfigManager('/home/runner/work/Agentical/Agentical/config')
    
    print(f"App Name: {config.get('app.name')}")
    print(f"App Version: {config.get('app.version')}")
    print(f"Debug Mode: {config.get('app.debug')}")
    print(f"Safe Mode: {config.safe_mode}")
    print(f"Model Name: {config.model_name}")
    
    # Demonstrate setting values
    config.set('app.debug', True)
    print(f"Debug Mode (after setting): {config.get('app.debug')}")
    
    return config

def demo_logging():
    """Demonstrate logging system."""
    print("\n=== Logging Demo ===")
    
    from utils.logger import logger
    
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.debug("This is a debug message")
    
    # Demonstrate specialized logging
    logger.log_action("click", {"x": 100, "y": 200})
    logger.log_ai_decision("test context", "test decision", 0.85)
    logger.log_safety_check("test action", "SAFE", "No issues found")

def demo_safety_monitor():
    """Demonstrate safety monitoring."""
    print("\n=== Safety Monitor Demo ===")
    
    from utils.safety import SafetyMonitor
    from utils.config import ConfigManager
    
    config = ConfigManager('/home/runner/work/Agentical/Agentical/config')
    safety = SafetyMonitor(config)
    
    # Test action safety checks
    safe, reason = safety.check_action_safety("click", x=500, y=300)
    print(f"Click safety check: {safe} - {reason}")
    
    safe, reason = safety.check_action_safety("key", key="alt+f4")
    print(f"Key safety check: {safe} - {reason}")
    
    safe, reason = safety.check_action_safety("type", text="Hello World")
    print(f"Type safety check: {safe} - {reason}")
    
    # Demonstrate safety status
    status = safety.get_safety_status()
    print(f"Safety Status: {status}")

def demo_task_structure():
    """Demonstrate task structure without external dependencies."""
    print("\n=== Task Structure Demo ===")
    
    from core.task_manager import Task, TaskStatus
    import time
    
    # Create a sample task
    task = Task(
        id="demo_task_001",
        goal="Open calculator and perform 2+2",
        priority=5
    )
    
    print(f"Task ID: {task.id}")
    print(f"Goal: {task.goal}")
    print(f"Status: {task.status}")
    print(f"Priority: {task.priority}")
    print(f"Created: {time.ctime(task.created_at)}")
    
    # Simulate some actions
    task.actions = [
        {"action": "key", "key": "win", "description": "Open start menu"},
        {"action": "type", "text": "calculator", "description": "Type calculator"},
        {"action": "key", "key": "enter", "description": "Press enter"},
        {"action": "click", "x": 100, "y": 200, "description": "Click button 2"},
        {"action": "click", "x": 150, "y": 250, "description": "Click plus button"},
        {"action": "click", "x": 100, "y": 200, "description": "Click button 2"},
        {"action": "click", "x": 200, "y": 300, "description": "Click equals button"}
    ]
    
    print(f"\nPlanned Actions ({len(task.actions)}):")
    for i, action in enumerate(task.actions):
        print(f"  {i+1}. {action['action']}: {action['description']}")

def demo_prompts():
    """Demonstrate AI prompt system."""
    print("\n=== AI Prompts Demo ===")
    
    from utils.config import ConfigManager
    
    config = ConfigManager('/home/runner/work/Agentical/Agentical/config')
    
    print("Available prompts:")
    system_prompt = config.get_prompt('system_prompt')
    if system_prompt:
        print("- System Prompt (first 100 chars):")
        print(f"  {system_prompt[:100]}...")
    
    vision_prompt = config.get_prompt('vision_analysis_prompt')
    if vision_prompt:
        print("- Vision Analysis Prompt (first 100 chars):")
        print(f"  {vision_prompt[:100]}...")
    
    task_prompt = config.get_prompt('task_planning_prompt')
    if task_prompt:
        print("- Task Planning Prompt (first 100 chars):")
        print(f"  {task_prompt[:100]}...")

def main():
    """Run all demonstrations."""
    print("Agentical Application Demo")
    print("=" * 50)
    print("This demo shows the application functionality")
    print("without requiring external API keys or GUI dependencies.\n")
    
    try:
        # Run demos
        config = demo_configuration()
        demo_logging()
        demo_safety_monitor()
        demo_task_structure()
        demo_prompts()
        
        print("\n" + "=" * 50)
        print("✓ Demo completed successfully!")
        print("\nTo run the full application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set your Gemini API key in config/settings.yaml")
        print("3. Run: python src/main.py")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)