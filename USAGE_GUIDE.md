# Agentical Usage Guide

This guide provides step-by-step instructions for setting up and using the Agentical AI Desktop Automation Application.

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/spawn9859/Agentical.git
cd Agentical

# Install Python dependencies
pip install -r requirements.txt

# Install the application
pip install -e .
```

### 2. Configuration

#### Get a Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key for the next step

#### Configure the Application
1. Open `config/settings.yaml`
2. Add your API key:
```yaml
api:
  gemini_api_key: "your-api-key-here"
```

### 3. First Run

```bash
# Run the application
python src/main.py

# Or run with debug mode
python src/main.py --debug
```

## Using the Application

### Creating Your First Task

1. **Start the Application**: Run `python src/main.py`
2. **Open Configuration**: Go to Settings → Configuration and verify your API key
3. **Create a Task**: 
   - Click "New Task" or use File → New Task
   - Enter a simple goal like "Open Calculator"
   - Set priority (1-10)
   - Click "Create"
4. **Start Automation**: Click the "Start" button in the toolbar
5. **Monitor Progress**: Watch the task execution in real-time

### Example Tasks

#### Simple Tasks
- "Open Notepad"
- "Take a screenshot"
- "Open Calculator and calculate 2+2"

#### Medium Complexity
- "Open Chrome and navigate to google.com"
- "Create a new text file on desktop called 'notes.txt'"
- "Open File Explorer and navigate to Documents folder"

#### Advanced Tasks
- "Open Excel, create a new spreadsheet, and add headers"
- "Search for 'weather' in Start menu and open the Weather app"
- "Open Command Prompt and run 'dir' command"

### Safety Features

#### Emergency Stop
- **Red Button**: Click the red "EMERGENCY STOP" button
- **Keyboard**: Press Ctrl+Shift+Esc (configurable)
- **Manual Override**: Take control of mouse/keyboard anytime

#### Safe Mode
- **Enable in Settings**: Go to Settings → Configuration → Desktop Control
- **Action Confirmation**: Each action requires confirmation
- **Restricted Areas**: Define screen areas that are off-limits

#### Rate Limiting
- **Default**: Maximum 60 actions per minute
- **Configurable**: Adjust in Safety settings
- **Automatic**: System pauses when limit reached

### Configuration Options

#### API Settings
```yaml
api:
  gemini_api_key: "your-key"
  model_name: "gemini-1.5-flash"  # or gemini-1.5-pro
  temperature: 0.1                # 0.0 = deterministic, 1.0 = creative
  max_tokens: 1000
```

#### Desktop Control
```yaml
desktop:
  screenshot_interval: 1.0        # Seconds between screenshots
  action_delay: 0.5              # Delay between actions
  safe_mode: true                # Enable safe mode
  confirm_actions: true          # Confirm each action
```

#### Safety Settings
```yaml
safety:
  max_actions_per_minute: 60
  restricted_areas:
    - x: 0                      # Taskbar area
      y: 0
      width: 100
      height: 50
      description: "Taskbar"
  emergency_stop_key: "ctrl+shift+esc"
```

## User Interface Guide

### Main Window Layout

1. **Toolbar**: Quick access to common functions
   - New Task, Start, Stop, Pause
   - Screenshot, Record
   - Emergency Stop

2. **Task Panel** (Left):
   - Task queue with status indicators
   - Task details and action list
   - Task management buttons

3. **Monitoring Panel** (Right):
   - **Current Screen**: Live screenshot display
   - **Activity Log**: Real-time action logging
   - **Safety Monitor**: Safety status and controls

4. **Status Bar** (Bottom):
   - Current status and progress
   - Progress bar for task execution

### Status Indicators

- ⏳ **Pending**: Task waiting to execute
- ▶️ **Running**: Task currently executing  
- ✅ **Completed**: Task finished successfully
- ❌ **Failed**: Task failed or error occurred
- 🚫 **Cancelled**: Task was cancelled

### Menu Options

#### File Menu
- **New Task**: Create a new automation task
- **Save/Load Configuration**: Manage settings
- **Exit**: Close application

#### Tools Menu
- **Take Screenshot**: Capture current screen
- **Start/Stop Recording**: Record screen activity
- **Emergency Stop**: Immediately halt all automation

#### Settings Menu
- **Configuration**: Open settings dialog
- **Test AI Connection**: Verify API connectivity

## Troubleshooting

### Common Issues

#### "AI Disconnected" Status
- **Check API Key**: Verify your Gemini API key is correct
- **Internet Connection**: Ensure you have internet access
- **API Quota**: Check if you've exceeded API limits

#### Actions Not Working
- **Safe Mode**: Check if safe mode is blocking actions
- **Restricted Areas**: Verify coordinates aren't in restricted zones
- **Rate Limiting**: Wait if you've hit the action limit

#### Screenshot Issues
- **Permissions**: Ensure app has screen capture permissions
- **Display Settings**: Check screen scaling settings
- **Refresh**: Try manually refreshing the screenshot

#### Task Failures
- **Screen Changes**: Desktop state may have changed
- **Timing Issues**: Increase action delays in settings
- **Coordinates**: UI elements may have moved

### Debug Mode

Enable debug mode for detailed logging:

```bash
python src/main.py --debug
```

Check logs in `logs/agentical.log` for detailed information.

### Getting Help

1. **Check Logs**: Review `logs/agentical.log` for error details
2. **GitHub Issues**: Report bugs on the repository
3. **Documentation**: See README.md for detailed information

## Best Practices

### Task Design
- **Start Simple**: Begin with basic tasks before complex ones
- **Be Specific**: Clear, specific goals work better than vague ones
- **Test in Safe Environment**: Try new tasks on test systems first

### Safety
- **Use Safe Mode**: Enable for important systems
- **Define Restricted Areas**: Mark sensitive screen areas
- **Monitor Execution**: Watch the first few runs of new tasks
- **Have Emergency Stop Ready**: Know how to quickly stop automation

### Performance
- **Reasonable Delays**: Don't set action delays too low
- **Monitor Resources**: Watch CPU and memory usage
- **Close Unnecessary Apps**: Reduce screen complexity for better AI analysis

## Advanced Usage

### Custom Prompts
Edit `config/prompts.yaml` to customize AI behavior:

```yaml
task_planning_prompt: |
  Custom instructions for task planning...
```

### API Configuration
For advanced users, adjust API parameters:

```yaml
api:
  temperature: 0.2      # Higher = more creative
  max_tokens: 2000      # Longer responses
```

### Logging Configuration
Customize logging in `config/settings.yaml`:

```yaml
logging:
  level: "DEBUG"        # DEBUG, INFO, WARNING, ERROR
  max_size_mb: 50       # Log file size limit
  backup_count: 10      # Number of backup files
```

This guide should help you get started with Agentical. For more detailed information, see the README.md file and source code documentation.