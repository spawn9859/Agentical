"""Configuration dialog for Agentical application."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any
try:
    from ..utils.config import ConfigManager
    from ..utils.logger import logger
except ImportError:
    from utils.config import ConfigManager
    from utils.logger import logger


class ConfigDialog:
    """Configuration dialog window."""
    
    def __init__(self, parent: tk.Tk, config: ConfigManager):
        """Initialize configuration dialog.
        
        Args:
            parent: Parent window
            config: Configuration manager
        """
        self.parent = parent
        self.config = config
        self.window = None
        self.variables = {}
        self.create_dialog()
    
    def create_dialog(self) -> None:
        """Create the configuration dialog."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Agentical Configuration")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        self.window.grab_set()  # Make dialog modal
        
        # Center the dialog
        self.window.transient(self.parent)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_api_tab(notebook)
        self.create_desktop_tab(notebook)
        self.create_safety_tab(notebook)
        self.create_ui_tab(notebook)
        
        # Button frame
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="Save", command=self.save_config).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Restore Defaults", command=self.restore_defaults).pack(side=tk.LEFT)
    
    def create_api_tab(self, notebook: ttk.Notebook) -> None:
        """Create API configuration tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="API Settings")
        
        # API Key
        ttk.Label(frame, text="Gemini API Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.variables['api_key'] = tk.StringVar(value=self.config.get('api.gemini_api_key', ''))
        api_key_entry = ttk.Entry(frame, textvariable=self.variables['api_key'], show="*", width=50)
        api_key_entry.grid(row=0, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Browse for API key file
        ttk.Button(frame, text="Load from file", 
                  command=self.load_api_key_from_file).grid(row=0, column=3, padx=5, pady=5)
        
        # Model Name
        ttk.Label(frame, text="Model Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.variables['model_name'] = tk.StringVar(value=self.config.get('api.model_name', 'gemini-1.5-flash'))
        model_combo = ttk.Combobox(frame, textvariable=self.variables['model_name'], 
                                  values=['gemini-1.5-flash', 'gemini-1.5-pro'])
        model_combo.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Temperature
        ttk.Label(frame, text="Temperature:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.variables['temperature'] = tk.DoubleVar(value=self.config.get('api.temperature', 0.1))
        temp_scale = ttk.Scale(frame, from_=0.0, to=1.0, variable=self.variables['temperature'], 
                              orient=tk.HORIZONTAL)
        temp_scale.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        temp_label = ttk.Label(frame, text="0.1")
        temp_label.grid(row=2, column=2, padx=5, pady=5)
        
        # Update temperature label
        def update_temp_label(*args):
            temp_label.config(text=f"{self.variables['temperature'].get():.1f}")
        self.variables['temperature'].trace('w', update_temp_label)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
    
    def create_desktop_tab(self, notebook: ttk.Notebook) -> None:
        """Create desktop control configuration tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Desktop Control")
        
        # Action Delay
        ttk.Label(frame, text="Action Delay (seconds):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.variables['action_delay'] = tk.DoubleVar(value=self.config.get('desktop.action_delay', 0.5))
        ttk.Scale(frame, from_=0.1, to=3.0, variable=self.variables['action_delay'], 
                 orient=tk.HORIZONTAL).grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Screenshot Interval
        ttk.Label(frame, text="Screenshot Interval (seconds):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.variables['screenshot_interval'] = tk.DoubleVar(value=self.config.get('desktop.screenshot_interval', 1.0))
        ttk.Scale(frame, from_=0.5, to=5.0, variable=self.variables['screenshot_interval'], 
                 orient=tk.HORIZONTAL).grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Safe Mode
        self.variables['safe_mode'] = tk.BooleanVar(value=self.config.get('desktop.safe_mode', True))
        ttk.Checkbutton(frame, text="Enable Safe Mode", 
                       variable=self.variables['safe_mode']).grid(row=2, column=0, columnspan=2, 
                                                                  sticky=tk.W, padx=5, pady=5)
        
        # Confirm Actions
        self.variables['confirm_actions'] = tk.BooleanVar(value=self.config.get('desktop.confirm_actions', True))
        ttk.Checkbutton(frame, text="Confirm Actions", 
                       variable=self.variables['confirm_actions']).grid(row=3, column=0, columnspan=2, 
                                                                        sticky=tk.W, padx=5, pady=5)
        
        frame.columnconfigure(1, weight=1)
    
    def create_safety_tab(self, notebook: ttk.Notebook) -> None:
        """Create safety configuration tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Safety")
        
        # Max Actions Per Minute
        ttk.Label(frame, text="Max Actions Per Minute:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.variables['max_actions'] = tk.IntVar(value=self.config.get('safety.max_actions_per_minute', 60))
        ttk.Spinbox(frame, from_=10, to=200, textvariable=self.variables['max_actions']).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Emergency Stop Key
        ttk.Label(frame, text="Emergency Stop Key:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.variables['emergency_key'] = tk.StringVar(value=self.config.get('safety.emergency_stop_key', 'ctrl+shift+esc'))
        ttk.Entry(frame, textvariable=self.variables['emergency_key']).grid(
            row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Restricted Areas (simplified)
        ttk.Label(frame, text="Restricted Areas:").grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)
        
        # Text area for restricted areas
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S, padx=5, pady=5)
        
        self.restricted_areas_text = tk.Text(text_frame, height=6, width=40)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.restricted_areas_text.yview)
        self.restricted_areas_text.config(yscrollcommand=scrollbar.set)
        
        self.restricted_areas_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load current restricted areas
        self.load_restricted_areas()
        
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
    
    def create_ui_tab(self, notebook: ttk.Notebook) -> None:
        """Create UI configuration tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="UI Settings")
        
        # Debug Mode
        self.variables['debug_mode'] = tk.BooleanVar(value=self.config.get('app.debug', False))
        ttk.Checkbutton(frame, text="Enable Debug Mode", 
                       variable=self.variables['debug_mode']).grid(row=0, column=0, columnspan=2, 
                                                                   sticky=tk.W, padx=5, pady=5)
        
        # Show Debug Info
        self.variables['show_debug_info'] = tk.BooleanVar(value=self.config.get('ui.show_debug_info', True))
        ttk.Checkbutton(frame, text="Show Debug Information", 
                       variable=self.variables['show_debug_info']).grid(row=1, column=0, columnspan=2, 
                                                                         sticky=tk.W, padx=5, pady=5)
        
        # Window Size
        ttk.Label(frame, text="Window Width:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.variables['window_width'] = tk.IntVar(value=self.config.get('ui.window_width', 800))
        ttk.Spinbox(frame, from_=600, to=1400, textvariable=self.variables['window_width']).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(frame, text="Window Height:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.variables['window_height'] = tk.IntVar(value=self.config.get('ui.window_height', 600))
        ttk.Spinbox(frame, from_=400, to=1000, textvariable=self.variables['window_height']).grid(
            row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        frame.columnconfigure(1, weight=1)
    
    def load_api_key_from_file(self) -> None:
        """Load API key from a text file."""
        try:
            filename = filedialog.askopenfilename(
                title="Select API Key File",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    api_key = f.read().strip()
                    self.variables['api_key'].set(api_key)
                    messagebox.showinfo("Success", "API key loaded successfully!")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load API key: {str(e)}")
    
    def load_restricted_areas(self) -> None:
        """Load restricted areas into text widget."""
        areas = self.config.get('safety.restricted_areas', [])
        text_content = ""
        
        for area in areas:
            text_content += f"x={area.get('x', 0)}, y={area.get('y', 0)}, "
            text_content += f"width={area.get('width', 0)}, height={area.get('height', 0)}"
            if area.get('description'):
                text_content += f" ({area['description']})"
            text_content += "\n"
        
        self.restricted_areas_text.delete(1.0, tk.END)
        self.restricted_areas_text.insert(1.0, text_content)
    
    def save_config(self) -> None:
        """Save configuration changes."""
        try:
            # Save API settings
            self.config.set('api.gemini_api_key', self.variables['api_key'].get())
            self.config.set('api.model_name', self.variables['model_name'].get())
            self.config.set('api.temperature', self.variables['temperature'].get())
            
            # Save desktop settings
            self.config.set('desktop.action_delay', self.variables['action_delay'].get())
            self.config.set('desktop.screenshot_interval', self.variables['screenshot_interval'].get())
            self.config.set('desktop.safe_mode', self.variables['safe_mode'].get())
            self.config.set('desktop.confirm_actions', self.variables['confirm_actions'].get())
            
            # Save safety settings
            self.config.set('safety.max_actions_per_minute', self.variables['max_actions'].get())
            self.config.set('safety.emergency_stop_key', self.variables['emergency_key'].get())
            
            # Save UI settings
            self.config.set('app.debug', self.variables['debug_mode'].get())
            self.config.set('ui.show_debug_info', self.variables['show_debug_info'].get())
            self.config.set('ui.window_width', self.variables['window_width'].get())
            self.config.set('ui.window_height', self.variables['window_height'].get())
            
            # Save to file
            self.config.save_config()
            
            messagebox.showinfo("Success", "Configuration saved successfully!")
            logger.info("Configuration updated and saved")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            logger.error_with_context(e, "save configuration")
    
    def restore_defaults(self) -> None:
        """Restore default configuration values."""
        if messagebox.askyesno("Confirm", "Are you sure you want to restore default settings?"):
            # Reset variables to defaults
            self.variables['api_key'].set('')
            self.variables['model_name'].set('gemini-1.5-flash')
            self.variables['temperature'].set(0.1)
            self.variables['action_delay'].set(0.5)
            self.variables['screenshot_interval'].set(1.0)
            self.variables['safe_mode'].set(True)
            self.variables['confirm_actions'].set(True)
            self.variables['max_actions'].set(60)
            self.variables['emergency_key'].set('ctrl+shift+esc')
            self.variables['debug_mode'].set(False)
            self.variables['show_debug_info'].set(True)
            self.variables['window_width'].set(800)
            self.variables['window_height'].set(600)
            
            messagebox.showinfo("Success", "Default settings restored!")
    
    def show(self) -> None:
        """Show the configuration dialog."""
        if self.window:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_set()