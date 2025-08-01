"""Task management system for queuing and executing automation tasks."""

import time
import threading
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
try:
    from ..utils.logger import logger
    from ..utils.config import ConfigManager
    from ..core.ai_engine import AIEngine
    from ..core.screen_capture import ScreenCapture
    from ..core.desktop_controller import DesktopController
except ImportError:
    from utils.logger import logger
    from utils.config import ConfigManager
    from core.ai_engine import AIEngine
    from core.screen_capture import ScreenCapture
    from core.desktop_controller import DesktopController


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents an automation task."""
    id: str
    goal: str
    priority: int = 1
    status: TaskStatus = TaskStatus.PENDING
    actions: List[Dict[str, Any]] = field(default_factory=list)
    current_action_index: int = 0
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def duration(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


class TaskManager:
    """Manages task queue and execution."""
    
    def __init__(self, config: ConfigManager, ai_engine: AIEngine, 
                 screen_capture: ScreenCapture, desktop_controller: DesktopController):
        """Initialize task manager.
        
        Args:
            config: Configuration manager
            ai_engine: AI engine for planning and analysis
            screen_capture: Screen capture module
            desktop_controller: Desktop controller module
        """
        self.config = config
        self.ai_engine = ai_engine
        self.screen_capture = screen_capture
        self.desktop_controller = desktop_controller
        
        self.tasks: List[Task] = []
        self.current_task: Optional[Task] = None
        self.is_running = False
        self.execution_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._task_counter = 0
        
        # Callbacks for UI updates
        self.on_task_status_changed: Optional[Callable[[Task], None]] = None
        self.on_action_executed: Optional[Callable[[Task, Dict[str, Any]], None]] = None
        
        logger.info("Task manager initialized")
    
    def add_task(self, goal: str, priority: int = 1) -> str:
        """Add a new task to the queue.
        
        Args:
            goal: Description of what to accomplish
            priority: Task priority (higher = more urgent)
            
        Returns:
            Task ID
        """
        with self._lock:
            self._task_counter += 1
            task_id = f"task_{self._task_counter}_{int(time.time())}"
            
            task = Task(
                id=task_id,
                goal=goal,
                priority=priority
            )
            
            # Insert task based on priority
            inserted = False
            for i, existing_task in enumerate(self.tasks):
                if existing_task.priority < priority:
                    self.tasks.insert(i, task)
                    inserted = True
                    break
            
            if not inserted:
                self.tasks.append(task)
            
            logger.info(f"Added task {task_id}: {goal}")
            self._notify_task_status_changed(task)
            
            return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task if found, None otherwise
        """
        with self._lock:
            for task in self.tasks:
                if task.id == task_id:
                    return task
            return None
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks.
        
        Returns:
            List of all tasks
        """
        with self._lock:
            return self.tasks.copy()
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if cancelled, False if not found or already completed
        """
        with self._lock:
            task = self.get_task(task_id)
            if task and task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task.status = TaskStatus.CANCELLED
                task.completed_at = time.time()
                logger.info(f"Cancelled task {task_id}")
                self._notify_task_status_changed(task)
                return True
            return False
    
    def start_execution(self) -> None:
        """Start task execution in background thread."""
        if self.is_running:
            logger.warning("Task execution already running")
            return
        
        self.is_running = True
        self.execution_thread = threading.Thread(
            target=self._execution_worker,
            daemon=True
        )
        self.execution_thread.start()
        logger.info("Task execution started")
    
    def stop_execution(self) -> None:
        """Stop task execution."""
        self.is_running = False
        if self.execution_thread:
            self.execution_thread.join(timeout=5.0)
        logger.info("Task execution stopped")
    
    def _execution_worker(self) -> None:
        """Main execution loop."""
        while self.is_running:
            try:
                # Get next task
                next_task = self._get_next_task()
                if not next_task:
                    time.sleep(1.0)
                    continue
                
                self.current_task = next_task
                self._execute_task(next_task)
                
            except Exception as e:
                logger.error_with_context(e, "task execution worker")
                time.sleep(5.0)  # Wait before retrying
    
    def _get_next_task(self) -> Optional[Task]:
        """Get the next pending task.
        
        Returns:
            Next task to execute or None if queue is empty
        """
        with self._lock:
            for task in self.tasks:
                if task.status == TaskStatus.PENDING:
                    return task
            return None
    
    def _execute_task(self, task: Task) -> None:
        """Execute a single task.
        
        Args:
            task: Task to execute
        """
        try:
            logger.info(f"Starting execution of task {task.id}: {task.goal}")
            
            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            self._notify_task_status_changed(task)
            
            # Plan the task if no actions exist
            if not task.actions:
                success = self._plan_task(task)
                if not success:
                    self._fail_task(task, "Failed to plan task")
                    return
            
            # Execute actions
            success = self._execute_actions(task)
            
            if success:
                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
                logger.info(f"Completed task {task.id} in {task.duration():.2f} seconds")
            else:
                self._handle_task_failure(task)
            
            self._notify_task_status_changed(task)
            
        except Exception as e:
            logger.error_with_context(e, f"execute task {task.id}")
            self._fail_task(task, str(e))
        finally:
            self.current_task = None
    
    def _plan_task(self, task: Task) -> bool:
        """Plan actions for a task.
        
        Args:
            task: Task to plan
            
        Returns:
            True if planning succeeded
        """
        try:
            # Capture current screen state
            screenshot = self.screen_capture.capture_screen()
            current_state = self.ai_engine.analyze_screen(screenshot, task.goal)
            
            if "error" in current_state:
                logger.error(f"Screen analysis failed: {current_state['error']}")
                return False
            
            # Plan actions
            actions = self.ai_engine.plan_task(task.goal, current_state)
            if not actions:
                logger.error(f"Failed to generate action plan for task {task.id}")
                return False
            
            task.actions = actions
            logger.info(f"Planned {len(actions)} actions for task {task.id}")
            return True
            
        except Exception as e:
            logger.error_with_context(e, f"plan task {task.id}")
            return False
    
    def _execute_actions(self, task: Task) -> bool:
        """Execute all actions in a task.
        
        Args:
            task: Task with actions to execute
            
        Returns:
            True if all actions succeeded
        """
        for i, action in enumerate(task.actions):
            if not self.is_running or task.status == TaskStatus.CANCELLED:
                return False
            
            task.current_action_index = i
            success = self._execute_action(action)
            
            self._notify_action_executed(task, action)
            
            if not success:
                logger.error(f"Action {i} failed in task {task.id}: {action}")
                return False
            
            # Wait between actions
            action_delay = self.config.get('desktop.action_delay', 0.5)
            time.sleep(action_delay)
        
        return True
    
    def _execute_action(self, action: Dict[str, Any]) -> bool:
        """Execute a single action.
        
        Args:
            action: Action dictionary
            
        Returns:
            True if action succeeded
        """
        action_type = action.get('action', '').lower()
        
        try:
            if action_type == 'click':
                return self.desktop_controller.click(
                    action.get('x', 0),
                    action.get('y', 0),
                    action.get('button', 'left'),
                    action.get('clicks', 1)
                )
            
            elif action_type == 'type':
                return self.desktop_controller.type_text(
                    action.get('text', ''),
                    action.get('interval', 0.0)
                )
            
            elif action_type == 'key':
                return self.desktop_controller.press_key(
                    action.get('key', ''),
                    action.get('presses', 1)
                )
            
            elif action_type == 'scroll':
                return self.desktop_controller.scroll(
                    action.get('x', 0),
                    action.get('y', 0),
                    action.get('clicks', 1),
                    action.get('direction', 'vertical')
                )
            
            elif action_type == 'wait':
                return self.desktop_controller.wait(
                    action.get('seconds', 1.0)
                )
            
            elif action_type == 'move':
                return self.desktop_controller.move_mouse(
                    action.get('x', 0),
                    action.get('y', 0),
                    action.get('duration', 0.0)
                )
            
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            logger.error_with_context(e, f"execute action {action_type}")
            return False
    
    def _handle_task_failure(self, task: Task) -> None:
        """Handle task failure with retry logic.
        
        Args:
            task: Failed task
        """
        task.retry_count += 1
        
        if task.retry_count <= task.max_retries:
            logger.info(f"Retrying task {task.id} (attempt {task.retry_count}/{task.max_retries})")
            task.status = TaskStatus.PENDING
            task.current_action_index = 0
            # Clear actions to force re-planning
            task.actions = []
        else:
            self._fail_task(task, f"Task failed after {task.max_retries} retries")
    
    def _fail_task(self, task: Task, error_message: str) -> None:
        """Mark task as failed.
        
        Args:
            task: Task to fail
            error_message: Error description
        """
        task.status = TaskStatus.FAILED
        task.error_message = error_message
        task.completed_at = time.time()
        logger.error(f"Task {task.id} failed: {error_message}")
    
    def _notify_task_status_changed(self, task: Task) -> None:
        """Notify callback about task status change."""
        if self.on_task_status_changed:
            try:
                self.on_task_status_changed(task)
            except Exception as e:
                logger.error_with_context(e, "task status change callback")
    
    def _notify_action_executed(self, task: Task, action: Dict[str, Any]) -> None:
        """Notify callback about action execution."""
        if self.on_action_executed:
            try:
                self.on_action_executed(task, action)
            except Exception as e:
                logger.error_with_context(e, "action executed callback")
    
    def get_status(self) -> Dict[str, Any]:
        """Get task manager status.
        
        Returns:
            Status dictionary
        """
        with self._lock:
            pending_tasks = sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)
            running_tasks = sum(1 for t in self.tasks if t.status == TaskStatus.RUNNING)
            completed_tasks = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
            failed_tasks = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
            
            return {
                "is_running": self.is_running,
                "current_task": self.current_task.id if self.current_task else None,
                "total_tasks": len(self.tasks),
                "pending_tasks": pending_tasks,
                "running_tasks": running_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks
            }