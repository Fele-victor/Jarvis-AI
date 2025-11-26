"""
Configuration settings for Jarvis AI Assistant
"""

import os

# Voice Settings
VOICE_STYLES = {
    'formal': {'rate': 150, 'volume': 0.9},
    'casual': {'rate': 175, 'volume': 0.9},
    'robotic': {'rate': 120, 'volume': 1.0}
}

DEFAULT_VOICE_STYLE = 'formal'

# Speech Recognition Settings
RECOGNITION_TIMEOUT = 5
RECOGNITION_PHRASE_LIMIT = 10
MAX_RECOGNITION_RETRIES = 3

# Modes
MODE_VOICE = 'voice'
MODE_MANUAL = 'manual'
DEFAULT_MODE = MODE_VOICE

# API Keys (set your own or leave as None for fallback)
WEATHER_API_KEY = None  # Get from openweathermap.org
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# Paths
LOGS_DIR = "logs"
HISTORY_FILE = os.path.join(LOGS_DIR, "history.txt")

# Session Settings
MEMORY_SIZE = 3

# Wake Word Settings
WAKE_WORD = "jarvis"
