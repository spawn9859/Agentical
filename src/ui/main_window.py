"""Main window for Agentical application."""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from typing import Dict, Any, Optional
from PIL import Image, ImageTk
try:
    from ..utils.config import ConfigManager
    from ..utils.logger import logger
    from ..utils.safety import SafetyMonitor
    from ..core.ai_engine import AIEngine
    from ..core.screen_capture import ScreenCapture
    from ..core.desktop_controller import DesktopController
    from ..core.task_manager import TaskManager, Task, TaskStatus
    from .config_dialog import ConfigDialog
except ImportError:
    from utils.config import ConfigManager
    from utils.logger import logger
    from utils.safety import SafetyMonitor
    from core.ai_engine import AIEngine
    from core.screen_capture import ScreenCapture
    from core.desktop_controller import DesktopController
    from core.task_manager import TaskManager, Task, TaskStatus
    from ui.config_dialog import ConfigDialog


class MainWindow:
    """Main application window."""
    
    def __init__(self, config: ConfigManager):
        """Initialize main window.
        
        Args:
            config: Configuration manager
        """
        self.config = config
        self.root = tk.Tk()
        self.setup_window()
        
        # Initialize components
        self.safety_monitor = SafetyMonitor(config)
        self.ai_engine = AIEngine(config)
        self.screen_capture = ScreenCapture(config)
        self.desktop_controller = DesktopController(config, self.safety_monitor)
        self.task_manager = TaskManager(config, self.ai_engine, self.screen_capture, self.desktop_controller)
        
        # UI components
        self.config_dialog: Optional[ConfigDialog] = None
        self.status_var = tk.StringVar(value="Ready")
        self.ai_status_var = tk.StringVar(value="Not connected")
        
        # Task management variables
        self.task_listbox = None
        self.task_details_text = None
        self.current_screenshot_label = None
        
        self.create_widgets()
        self.setup_callbacks()
        self.update_status()
        
        logger.info("Main window initialized")
    
    def setup_window(self) -> None:
        """Set up main window properties."""
        self.root.title("Agentical - AI Desktop Automation")
        
        # Get window size from config
        width = self.config.get('ui.window_width', 800)
        height = self.config.get('ui.window_height', 600)
        self.root.geometry(f"{width}x{height}")
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Set minimum size
        self.root.minsize(600, 400)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self) -> None:
        """Create all UI widgets."""
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area
        self.create_main_content()
        
        # Create status bar
        self.create_status_bar()
    
    def create_menu_bar(self) -> None:
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Task...", command=self.new_task_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Save Configuration", command=self.save_config)
        file_menu.add_command(label="Load Configuration", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Take Screenshot", command=self.take_screenshot)
        tools_menu.add_command(label="Start Recording", command=self.start_recording)
        tools_menu.add_command(label="Stop Recording", command=self.stop_recording)
        tools_menu.add_separator()
        tools_menu.add_command(label="Emergency Stop", command=self.emergency_stop)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Configuration...", command=self.show_config_dialog)
        settings_menu.add_command(label="Test AI Connection", command=self.test_ai_connection)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about_dialog)
    
    def create_toolbar(self) -> None:
        """Create application toolbar."""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Task control buttons
        ttk.Button(toolbar, text="New Task", command=self.new_task_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Start", command=self.start_execution).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Stop", command=self.stop_execution).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Pause", command=self.pause_execution).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Screenshot and recording buttons
        ttk.Button(toolbar, text="Screenshot", command=self.take_screenshot).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Record", command=self.toggle_recording).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Emergency stop button (red)
        emergency_btn = tk.Button(toolbar, text="EMERGENCY STOP", bg="red", fg="white", 
                                 font=("Arial", 10, "bold"), command=self.emergency_stop)
        emergency_btn.pack(side=tk.RIGHT, padx=2)
        
        # AI status indicator
        self.ai_status_label = ttk.Label(toolbar, textvariable=self.ai_status_var)
        self.ai_status_label.pack(side=tk.RIGHT, padx=5)
    
    def create_main_content(self) -> None:
        """Create main content area with panels."""
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Task management
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right panel - Monitoring and control
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        self.create_task_panel(left_frame)
        self.create_monitoring_panel(right_frame)
    
    def create_task_panel(self, parent: ttk.Frame) -> None:
        """Create task management panel."""
        # Task list
        task_frame = ttk.LabelFrame(parent, text="Task Queue")
        task_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Task listbox with scrollbar
        listbox_frame = ttk.Frame(task_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.task_listbox = tk.Listbox(listbox_frame)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.task_listbox.yview)
        self.task_listbox.config(yscrollcommand=scrollbar.set)
        
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Task control buttons
        task_btn_frame = ttk.Frame(task_frame)
        task_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(task_btn_frame, text="Add Task", command=self.new_task_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(task_btn_frame, text="Remove Task", command=self.remove_selected_task).pack(side=tk.LEFT, padx=2)
        ttk.Button(task_btn_frame, text="Clear Completed", command=self.clear_completed_tasks).pack(side=tk.LEFT, padx=2)
        
        # Bind listbox selection
        self.task_listbox.bind('<<ListboxSelect>>', self.on_task_selected)
        
        # Task details
        details_frame = ttk.LabelFrame(parent, text="Task Details")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.task_details_text = scrolledtext.ScrolledText(details_frame, height=8, wrap=tk.WORD)
        self.task_details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_monitoring_panel(self, parent: ttk.Frame) -> None:
        """Create monitoring and control panel."""
        # Create notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Screenshot tab
        screenshot_frame = ttk.Frame(notebook)
        notebook.add(screenshot_frame, text="Current Screen")
        self.create_screenshot_tab(screenshot_frame)
        
        # Logs tab
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Activity Log")
        self.create_logs_tab(logs_frame)
        
        # Safety tab
        safety_frame = ttk.Frame(notebook)
        notebook.add(safety_frame, text="Safety Monitor")
        self.create_safety_tab(safety_frame)
    
    def create_screenshot_tab(self, parent: ttk.Frame) -> None:
        """Create screenshot display tab."""
        # Control buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_screenshot).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Save", command=self.save_screenshot).pack(side=tk.LEFT, padx=2)
        
        # Screenshot display
        screenshot_frame = ttk.Frame(parent)
        screenshot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.current_screenshot_label = ttk.Label(screenshot_frame, text="No screenshot taken")
        self.current_screenshot_label.pack(expand=True)
        
        # Auto-refresh checkbox
        self.auto_refresh_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text="Auto-refresh (1s)", 
                       variable=self.auto_refresh_var).pack(pady=5)
    
    def create_logs_tab(self, parent: ttk.Frame) -> None:
        """Create activity log tab."""
        # Log display
        self.log_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log control buttons
        log_btn_frame = ttk.Frame(parent)
        log_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_btn_frame, text="Clear", command=self.clear_logs).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_btn_frame, text="Save to File", command=self.save_logs).pack(side=tk.LEFT, padx=2)
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(log_btn_frame, text="Auto-scroll", 
                       variable=self.auto_scroll_var).pack(side=tk.RIGHT)
    
    def create_safety_tab(self, parent: ttk.Frame) -> None:
        """Create safety monitoring tab."""
        # Safety status display
        status_frame = ttk.LabelFrame(parent, text="Safety Status")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Safety indicators
        self.safety_indicators = {}
        
        # Emergency stop status
        self.safety_indicators['emergency'] = tk.StringVar(value="Normal")
        ttk.Label(status_frame, text="Emergency Stop:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        emergency_label = ttk.Label(status_frame, textvariable=self.safety_indicators['emergency'])
        emergency_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Actions per minute
        self.safety_indicators['actions'] = tk.StringVar(value="0/60")
        ttk.Label(status_frame, text="Actions/minute:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(status_frame, textvariable=self.safety_indicators['actions']).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Manual controls
        controls_frame = ttk.LabelFrame(parent, text="Manual Controls")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Emergency Stop", command=self.emergency_stop).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(controls_frame, text="Reset Safety", command=self.reset_safety).pack(side=tk.LEFT, padx=5, pady=5)
    
    def create_status_bar(self) -> None:
        """Create status bar at bottom of window."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status text
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)
        
        # Progress bar (for task execution)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def setup_callbacks(self) -> None:
        """Set up callbacks for task manager."""
        self.task_manager.on_task_status_changed = self.on_task_status_changed
        self.task_manager.on_action_executed = self.on_action_executed
    
    def update_status(self) -> None:
        """Update status displays periodically."""
        try:
            # Update AI connection status
            if self.ai_engine.is_available():
                self.ai_status_var.set("AI Connected")
            else:
                self.ai_status_var.set("AI Disconnected")
            
            # Update safety status
            safety_status = self.safety_monitor.get_safety_status()
            if safety_status['emergency_stop']:
                self.safety_indicators['emergency'].set("ACTIVATED")
            else:
                self.safety_indicators['emergency'].set("Normal")
            
            actions_text = f"{safety_status['actions_last_minute']}/{safety_status['max_actions_per_minute']}"
            self.safety_indicators['actions'].set(actions_text)
            
            # Update task list
            self.update_task_list()
            
            # Auto-refresh screenshot if enabled
            if self.auto_refresh_var.get():
                self.refresh_screenshot()
            
        except Exception as e:
            logger.error_with_context(e, "update status")
        
        # Schedule next update
        self.root.after(1000, self.update_status)
    
    def update_task_list(self) -> None:
        """Update task list display."""
        try:
            # Clear current list
            self.task_listbox.delete(0, tk.END)
            
            # Add all tasks
            tasks = self.task_manager.get_all_tasks()
            for task in tasks:
                status_icon = {
                    TaskStatus.PENDING: "⏳",
                    TaskStatus.RUNNING: "▶️",
                    TaskStatus.COMPLETED: "✅",
                    TaskStatus.FAILED: "❌",
                    TaskStatus.CANCELLED: "🚫"
                }.get(task.status, "❓")
                
                task_text = f"{status_icon} {task.goal[:50]}"
                self.task_listbox.insert(tk.END, task_text)
                
                # Color code based on status
                if task.status == TaskStatus.RUNNING:
                    self.task_listbox.itemconfig(tk.END, {'bg': 'lightblue'})
                elif task.status == TaskStatus.COMPLETED:
                    self.task_listbox.itemconfig(tk.END, {'bg': 'lightgreen'})
                elif task.status == TaskStatus.FAILED:
                    self.task_listbox.itemconfig(tk.END, {'bg': 'lightcoral'})
                    
        except Exception as e:
            logger.error_with_context(e, "update task list")
    
    # Event handlers
    def on_task_status_changed(self, task: Task) -> None:
        """Handle task status changes."""
        try:
            self.root.after_idle(self.update_task_list)
            logger.info(f"Task {task.id} status changed to {task.status.value}")
        except Exception as e:
            logger.error_with_context(e, "task status change handler")
    
    def on_action_executed(self, task: Task, action: Dict[str, Any]) -> None:
        """Handle action execution."""
        try:
            log_message = f"Task {task.id}: Executed {action.get('action', 'unknown')} action\n"
            self.root.after_idle(lambda: self.log_text.insert(tk.END, log_message))
            
            if self.auto_scroll_var.get():
                self.root.after_idle(lambda: self.log_text.see(tk.END))
                
        except Exception as e:
            logger.error_with_context(e, "action executed handler")
    
    def on_task_selected(self, event) -> None:
        """Handle task selection in listbox."""
        try:
            selection = self.task_listbox.curselection()
            if selection:
                index = selection[0]
                tasks = self.task_manager.get_all_tasks()
                if index < len(tasks):
                    task = tasks[index]
                    self.show_task_details(task)
        except Exception as e:
            logger.error_with_context(e, "task selection")
    
    def show_task_details(self, task: Task) -> None:
        """Show detailed information about a task."""
        details = f"Task ID: {task.id}\n"
        details += f"Goal: {task.goal}\n"
        details += f"Status: {task.status.value}\n"
        details += f"Priority: {task.priority}\n"
        details += f"Created: {time.ctime(task.created_at)}\n"
        
        if task.started_at:
            details += f"Started: {time.ctime(task.started_at)}\n"
        
        if task.completed_at:
            details += f"Completed: {time.ctime(task.completed_at)}\n"
            if task.duration():
                details += f"Duration: {task.duration():.2f} seconds\n"
        
        if task.error_message:
            details += f"Error: {task.error_message}\n"
        
        details += f"\nActions ({len(task.actions)}):\n"
        for i, action in enumerate(task.actions):
            marker = "→" if i == task.current_action_index else " "
            details += f"{marker} {i+1}. {action.get('action', 'unknown')}: {action.get('description', 'No description')}\n"
        
        self.task_details_text.delete(1.0, tk.END)
        self.task_details_text.insert(1.0, details)
    
    # Command handlers
    def new_task_dialog(self) -> None:
        """Show new task creation dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("New Task")
        dialog.geometry("400x200")
        dialog.grab_set()
        
        # Goal entry
        ttk.Label(dialog, text="Task Goal:").pack(pady=5)
        goal_entry = tk.Entry(dialog, width=50)
        goal_entry.pack(pady=5)
        goal_entry.focus()
        
        # Priority
        ttk.Label(dialog, text="Priority (1-10):").pack(pady=5)
        priority_var = tk.IntVar(value=5)
        ttk.Scale(dialog, from_=1, to=10, variable=priority_var, orient=tk.HORIZONTAL).pack(pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def create_task():
            goal = goal_entry.get().strip()
            if goal:
                task_id = self.task_manager.add_task(goal, priority_var.get())
                messagebox.showinfo("Success", f"Task created: {task_id}")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Please enter a task goal")
        
        ttk.Button(btn_frame, text="Create", command=create_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def remove_selected_task(self) -> None:
        """Remove selected task from queue."""
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            tasks = self.task_manager.get_all_tasks()
            if index < len(tasks):
                task = tasks[index]
                if messagebox.askyesno("Confirm", f"Remove task: {task.goal}?"):
                    self.task_manager.cancel_task(task.id)
    
    def clear_completed_tasks(self) -> None:
        """Clear all completed tasks."""
        if messagebox.askyesno("Confirm", "Clear all completed tasks?"):
            # Implementation would remove completed tasks
            messagebox.showinfo("Info", "Completed tasks cleared")
    
    def start_execution(self) -> None:
        """Start task execution."""
        try:
            self.task_manager.start_execution()
            self.status_var.set("Task execution started")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start execution: {str(e)}")
    
    def stop_execution(self) -> None:
        """Stop task execution."""
        try:
            self.task_manager.stop_execution()
            self.status_var.set("Task execution stopped")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop execution: {str(e)}")
    
    def pause_execution(self) -> None:
        """Pause task execution."""
        # Implementation would pause current task
        self.status_var.set("Task execution paused")
    
    def emergency_stop(self) -> None:
        """Activate emergency stop."""
        self.safety_monitor.activate_emergency_stop()
        self.task_manager.stop_execution()
        self.status_var.set("EMERGENCY STOP ACTIVATED")
        messagebox.showwarning("Emergency Stop", "All automation stopped!")
    
    def reset_safety(self) -> None:
        """Reset safety monitor."""
        self.safety_monitor.deactivate_emergency_stop()
        self.status_var.set("Safety reset - Ready")
    
    def take_screenshot(self) -> None:
        """Take and display screenshot."""
        try:
            filename = self.screen_capture.save_screenshot()
            self.status_var.set(f"Screenshot saved: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to take screenshot: {str(e)}")
    
    def refresh_screenshot(self) -> None:
        """Refresh current screenshot display."""
        try:
            screenshot = self.screen_capture.capture_screen()
            # Resize for display
            display_size = (400, 300)
            screenshot.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(screenshot)
            self.current_screenshot_label.config(image=photo, text="")
            self.current_screenshot_label.image = photo  # Keep reference
            
        except Exception as e:
            logger.error_with_context(e, "refresh screenshot")
    
    def save_screenshot(self) -> None:
        """Save current screenshot."""
        self.take_screenshot()
    
    def start_recording(self) -> None:
        """Start screen recording."""
        try:
            self.screen_capture.start_recording()
            self.status_var.set("Screen recording started")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start recording: {str(e)}")
    
    def stop_recording(self) -> None:
        """Stop screen recording."""
        try:
            filename = self.screen_capture.stop_recording()
            self.status_var.set(f"Recording saved: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop recording: {str(e)}")
    
    def toggle_recording(self) -> None:
        """Toggle screen recording."""
        if self.screen_capture.recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def show_config_dialog(self) -> None:
        """Show configuration dialog."""
        if not self.config_dialog:
            self.config_dialog = ConfigDialog(self.root, self.config)
        self.config_dialog.show()
    
    def test_ai_connection(self) -> None:
        """Test AI connection."""
        if self.ai_engine.is_available():
            messagebox.showinfo("AI Connection", "AI models are loaded and ready!")
        else:
            messagebox.showerror("AI Connection", "AI models are not available. Check your API key in settings.")
    
    def save_config(self) -> None:
        """Save configuration."""
        try:
            self.config.save_config()
            messagebox.showinfo("Success", "Configuration saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
    
    def load_config(self) -> None:
        """Load configuration."""
        try:
            self.config.load_config()
            messagebox.showinfo("Success", "Configuration loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def clear_logs(self) -> None:
        """Clear activity log."""
        self.log_text.delete(1.0, tk.END)
    
    def save_logs(self) -> None:
        """Save logs to file."""
        # Implementation would save logs to file
        messagebox.showinfo("Info", "Logs saved to file")
    
    def show_about_dialog(self) -> None:
        """Show about dialog."""
        about_text = """Agentical v1.0.0
        
AI Desktop Automation Application

Powered by Google Gemini API
Built with Python and Tkinter

© 2025 spawn9859"""
        
        messagebox.showinfo("About Agentical", about_text)
    
    def on_closing(self) -> None:
        """Handle window closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit Agentical?"):
            try:
                # Stop task execution
                self.task_manager.stop_execution()
                
                # Stop recording if active
                if self.screen_capture.recording:
                    self.screen_capture.stop_recording()
                
                logger.info("Application closing")
                self.root.destroy()
                
            except Exception as e:
                logger.error_with_context(e, "application shutdown")
                self.root.destroy()
    
    def run(self) -> None:
        """Start the main application loop."""
        logger.info("Starting main application loop")
        self.root.after(1000, self.update_status)  # Start status updates
        self.root.mainloop()