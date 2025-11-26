# JARVIS AI - Smart Voice Assistant

A Python-based intelligent voice assistant with both voice and manual input modes, featuring natural language understanding, system control, and smart session management.

## Features

### Core Capabilities
- **Dual Mode Operation**: Voice mode (default) and manual text input mode
- **Speech Recognition**: Google Web API with automatic fallback to manual mode after 3 failed attempts
- **Text-to-Speech**: Offline TTS with 3 voice styles (formal, casual, robotic)
- **Smart Error Recovery**: Network errors and unrecognized commands handled gracefully

### Session Intelligence
- **Short-Term Memory**: Remembers last 3 commands
- **Command Confirmation**: Asks for confirmation on sensitive actions
- **Repeat & Undo**: "Repeat that" or "Do the previous one"

### System Functions
- Tell current time and date
- Weather information (requires API key)
- System status (CPU, battery, network)
- Open safe applications
- Google search
- Wikipedia summaries (first 3 sentences)
- Alarms and reminders

### Advanced Features
- **Natural Language Understanding**: Multiple ways to ask the same thing
- **Voice Customization**: Change voice style, volume control, mute
- **Wake-Word Mode**: Continuous listening (manual toggle)
- **Session Logging**: All commands logged with timestamps

## Project Structure

```
jarvis-ai/
├── jarvis.py                 # Main controller
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── core/
│   ├── speech_engine.py     # Speech recognition & TTS
│   ├── command_processor.py # Natural language processing
│   └── session_manager.py   # Memory & confirmations
├── functions/
│   └── system_functions.py  # System operations
├── utils/
│   └── logger.py            # Command logging
└── logs/
    └── history.txt          # Command history log
```

## Installation

### Prerequisites
- Python 3.10 or higher
- Microphone for voice input
- Internet connection for speech recognition

### Setup Steps

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install PyAudio** (required for microphone access):

**On Windows:**
```bash
pip install pyaudio
```

**On macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**On Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

3. **(Optional) Configure Weather API:**
- Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
- Edit `config.py` and set `WEATHER_API_KEY = "your_api_key_here"`

## Usage

### Start Jarvis
```bash
python jarvis.py
```

### Basic Commands

**Time & Date:**
- "What time is it?"
- "Tell me the date"
- "What's today's date?"

**Weather:**
- "What's the weather?"
- "Weather in New York"

**Search & Information:**
- "Search for Python tutorials"
- "Google machine learning"
- "Wikipedia Albert Einstein"
- "Tell me about quantum physics"

**System Status:**
- "System status"
- "CPU usage"
- "Battery level"
- "Network status"

**Voice Control:**
- "Switch to casual voice"
- "Speak louder"
- "Speak softer"
- "Mute your voice"

**Mode Switching:**
- "Switch to manual mode"
- "Switch to voice mode"

**Alarms & Reminders:**
- "Set an alarm for 5 minutes"
- "Remind me to call John in 1 hour"

**Session Commands:**
- "Repeat that"
- "Do the previous one"
- "Help"
- "Exit"

### Example Session

```
Jarvis: Hello! I am Jarvis, your AI assistant. I'm currently in voice mode.
Jarvis: Say 'help' to know what I can do.

Listening...
You: What time is it?
Jarvis: It's 02:30 PM

Listening...
You: Tell me about Python programming
Jarvis: Python is a high-level, interpreted programming language...

Listening...
You: Switch to manual mode
Jarvis: Switched to manual mode

Jarvis: Type your command:
You: search for AI news
Jarvis: Searching Google for AI news
```

## Configuration

Edit `config.py` to customize:

- **Voice styles**: Rate and volume for each style
- **Recognition settings**: Timeout, retry limits
- **API keys**: Weather API key
- **Paths**: Log directory location
- **Memory size**: Number of commands to remember

## Troubleshooting

**Microphone not working:**
- Check microphone permissions
- Test with: `python -m speech_recognition`

**Speech recognition failing:**
- Check internet connection (Google API requires network)
- Jarvis will auto-switch to manual mode after 3 failures

**PyAudio installation issues:**
- Windows: Download wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
- Linux: Install portaudio19-dev first
- macOS: Install portaudio via Homebrew first

**Import errors:**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Use Python 3.10+

## Advanced Usage

### Continuous Listening Mode
```
You: Jarvis, start listening
Jarvis: Starting continuous listening mode
[Jarvis now listens continuously]
You: Jarvis, stop listening
Jarvis: Stopping continuous listening mode
```

### Command Confirmation
Sensitive actions require confirmation:
```
You: Open calculator
Jarvis: Do you want me to open calculator? Say yes or no.
You: Yes
Jarvis: Confirmed
Jarvis: Opening calculator
```

### View Command History
Check `logs/history.txt` for complete command history with timestamps.

## Safety Features

- Only safe applications can be opened
- No file system modifications allowed
- Confirmation required for sensitive actions
- All commands logged for review

## Contributing

Feel free to extend Jarvis with additional features:
- Add new command patterns in `command_processor.py`
- Add new functions in `system_functions.py`
- Update command mappings in `jarvis.py`

## License

MIT License - Feel free to use and modify as needed.

## Credits

Built with:
- `pyttsx3` - Text-to-speech
- `SpeechRecognition` - Voice recognition
- `psutil` - System information
- `wikipedia` - Wikipedia API
- `requests` - HTTP requests
