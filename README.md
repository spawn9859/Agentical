# Agentical - AI Desktop Automation Application

Agentical is a Windows-compatible agentic AI application that can autonomously perform tasks on the desktop using the Google Gemini API. It provides intelligent desktop automation with computer vision, natural language processing, and safety features.

## Features

### 🖱️ Desktop Control
- **Mouse Control**: Move cursor, click, drag, scroll, and perform various mouse operations
- **Keyboard Control**: Send keystrokes, key combinations, and text input
- **Screen Capture**: Take screenshots of the entire screen or specific regions
- **Screen Recording**: Record screen activity for analysis and decision-making

### 🧠 AI Integration
- **Google Gemini API Integration**: Uses Gemini Vision and Text models for understanding and decision-making
- **Vision Analysis**: Analyzes screenshots to understand current desktop state
- **Task Planning**: Breaks down complex tasks into actionable steps
- **Autonomous Execution**: Executes tasks without human intervention

### 🏗️ Application Architecture
- **Modular Design**: Separate modules for screen capture, AI processing, and desktop control
- **Configuration System**: Settings for API keys, behavior parameters, and safety limits
- **Logging System**: Comprehensive logging for debugging and audit trails
- **Error Handling**: Robust error handling and recovery mechanisms

### 🛡️ Safety Features
- **Boundaries**: Configurable safe zones and restricted areas
- **Confirmation Prompts**: Optional user confirmation for critical actions
- **Emergency Stop**: Quick way to halt all automated actions
- **Action Limits**: Rate limiting and maximum action counts

### 🖥️ User Interface
- **Simple GUI**: Easy-to-use interface for configuration and monitoring
- **Task Queue**: Display current and pending tasks
- **Real-time Status**: Show current AI analysis and planned actions
- **Manual Override**: Ability to take manual control when needed

## Installation

### Prerequisites

- Python 3.8 or higher
- Windows 10/11, macOS, or Linux
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/spawn9859/Agentical.git
cd Agentical
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the application:
```bash
pip install -e .
```

### Quick Start

1. Run the application:
```bash
python src/main.py
```

2. Configure your Gemini API key:
   - Go to Settings → Configuration
   - Enter your API key in the "API Settings" tab
   - Click "Save"

3. Create your first task:
   - Click "New Task" or use File → New Task
   - Enter a description like "Open Notepad and type 'Hello World'"
   - Click "Create"

4. Start automation:
   - Click the "Start" button in the toolbar
   - Watch as Agentical analyzes your screen and executes the task

## Configuration

### API Settings

Configure your Google Gemini API settings in `config/settings.yaml`:

```yaml
api:
  gemini_api_key: "your-api-key-here"
  model_name: "gemini-1.5-flash"
  temperature: 0.1
  max_tokens: 1000
```

### Safety Settings

Customize safety features to prevent unintended actions:

```yaml
safety:
  max_actions_per_minute: 60
  restricted_areas:
    - x: 0
      y: 0
      width: 100
      height: 50
      description: "Taskbar area"
  emergency_stop_key: "ctrl+shift+esc"
```

### Desktop Control

Adjust automation timing and behavior:

```yaml
desktop:
  screenshot_interval: 1.0
  action_delay: 0.5
  safe_mode: true
  confirm_actions: true
```

## Usage Examples

### Basic Task Examples

1. **Open an Application**:
   - Task: "Open Calculator"
   - The AI will identify the Start menu, search for Calculator, and launch it

2. **File Operations**:
   - Task: "Create a new text file on the desktop named 'notes.txt'"
   - The AI will right-click on desktop, create new file, and rename it

3. **Web Automation**:
   - Task: "Open Chrome and navigate to google.com"
   - The AI will launch Chrome and navigate to the specified website

### Advanced Task Examples

1. **Multi-step Workflow**:
   - Task: "Open Excel, create a new spreadsheet, add headers 'Name' and 'Age' in A1 and B1"
   - The AI will break this down into multiple coordinated actions

2. **Data Entry**:
   - Task: "Fill out the form with Name: John Doe, Email: john@example.com"
   - The AI will identify form fields and enter the specified data

## Safety Guidelines

### Best Practices

1. **Start with Safe Mode**: Always enable safe mode when getting started
2. **Define Restricted Areas**: Mark sensitive screen areas as off-limits
3. **Use Rate Limiting**: Set reasonable action limits to prevent runaway automation
4. **Monitor Execution**: Watch the application during task execution
5. **Test in Safe Environment**: Try new tasks in a test environment first

### Emergency Procedures

- **Emergency Stop**: Press Ctrl+Shift+Esc or click the red "EMERGENCY STOP" button
- **Manual Override**: Take control of mouse/keyboard at any time
- **Safe Mode**: Enable to require confirmation for each action

## Troubleshooting

### Common Issues

1. **API Key Not Working**:
   - Verify your Gemini API key is correct
   - Check your internet connection
   - Ensure API quota is not exceeded

2. **Actions Not Working**:
   - Check if safe mode is blocking actions
   - Verify coordinates are not in restricted areas
   - Review action rate limits

3. **Screenshot Issues**:
   - Check screen resolution and scaling
   - Ensure application has screen capture permissions
   - Try refreshing the screenshot manually

### Debug Mode

Enable debug mode for detailed logging:

```bash
python src/main.py --debug
```

Check logs in the `logs/` directory for detailed information.

## Development

### Project Structure

```
agentical/
├── src/
│   ├── core/                 # Core automation modules
│   │   ├── ai_engine.py      # AI processing and decision making
│   │   ├── screen_capture.py # Screen capture and recording
│   │   ├── desktop_controller.py # Mouse and keyboard control
│   │   └── task_manager.py   # Task queue and execution
│   ├── ui/                   # User interface components
│   │   ├── main_window.py    # Main application window
│   │   └── config_dialog.py  # Configuration dialog
│   ├── utils/                # Utility modules
│   │   ├── logger.py         # Logging system
│   │   ├── config.py         # Configuration management
│   │   └── safety.py         # Safety monitoring
│   └── main.py               # Application entry point
├── config/                   # Configuration files
│   ├── settings.yaml         # Main settings
│   └── prompts.yaml          # AI prompts
├── requirements.txt          # Python dependencies
├── setup.py                  # Installation script
└── README.md                 # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

## API Reference

### Core Classes

- `AIEngine`: Interface to Google Gemini API for vision and text processing
- `ScreenCapture`: Screen capture and recording functionality
- `DesktopController`: Mouse and keyboard control
- `TaskManager`: Task queue and execution management
- `SafetyMonitor`: Safety features and monitoring

### Configuration

- `ConfigManager`: Configuration file management
- `Logger`: Logging and audit trail functionality

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gemini API for AI capabilities
- PyAutoGUI for desktop automation
- Tkinter for the user interface
- OpenCV for computer vision features

## Support

- Report bugs: [GitHub Issues](https://github.com/spawn9859/Agentical/issues)
- Documentation: [GitHub Wiki](https://github.com/spawn9859/Agentical/wiki)
- Discussions: [GitHub Discussions](https://github.com/spawn9859/Agentical/discussions)

---

**⚠️ Important**: This application can control your computer automatically. Always use safety features and test in a safe environment before using on important systems.