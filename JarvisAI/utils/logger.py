"""
Logging utility for Jarvis AI
"""

import os
from datetime import datetime
from config import LOGS_DIR, HISTORY_FILE


class Logger:
    """Handles logging of commands and interactions"""

    def __init__(self):
        """Initialize logger and create logs directory if needed"""
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)

    def log_command(self, command, mode='voice'):
        """
        Log a command with timestamp

        Args:
            command (str): The command executed
            mode (str): The mode used (voice/manual)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{mode.upper()}] {command}\n"

        try:
            with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Logging error: {e}")

    def get_recent_logs(self, count=10):
        """
        Retrieve recent log entries

        Args:
            count (int): Number of recent entries to retrieve

        Returns:
            list: List of recent log entries
        """
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    return lines[-count:]
            return []
        except Exception as e:
            print(f"Error reading logs: {e}")
            return []
