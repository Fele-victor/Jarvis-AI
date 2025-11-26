"""
Session manager for handling memory, confirmations, and alarms/reminders
"""

import threading
import time
from datetime import datetime, timedelta
from collections import deque
from config import MEMORY_SIZE


class SessionManager:
    """Manages session state, memory, and confirmations"""

    def __init__(self):
        """Initialize session manager"""
        self.command_history = deque(maxlen=MEMORY_SIZE)
        self.pending_confirmation = None
        self.alarms = []
        self.reminders = []
        self.alarm_threads = []

    def add_to_history(self, command):
        """
        Add command to history

        Args:
            command (dict): Command dictionary with action and params
        """
        self.command_history.append({
            'command': command,
            'timestamp': datetime.now()
        })

    def get_last_command(self):
        """
        Get the last command from history

        Returns:
            dict: Last command or None
        """
        if self.command_history:
            return self.command_history[-1]['command']
        return None

    def get_previous_command(self, offset=1):
        """
        Get a previous command from history

        Args:
            offset (int): How many commands back (1 = last, 2 = second to last)

        Returns:
            dict: Command or None
        """
        if len(self.command_history) >= offset:
            return self.command_history[-offset]['command']
        return None

    def set_pending_confirmation(self, action, params, message):
        """
        Set a pending confirmation for sensitive actions

        Args:
            action (str): Action to confirm
            params (dict): Parameters for the action
            message (str): Confirmation message
        """
        self.pending_confirmation = {
            'action': action,
            'params': params,
            'message': message
        }

    def get_pending_confirmation(self):
        """
        Get pending confirmation

        Returns:
            dict: Pending confirmation or None
        """
        return self.pending_confirmation

    def clear_pending_confirmation(self):
        """Clear pending confirmation"""
        self.pending_confirmation = None

    def confirm_action(self):
        """
        Confirm and return the pending action

        Returns:
            dict: Confirmed command or None
        """
        if self.pending_confirmation:
            confirmed = {
                'action': self.pending_confirmation['action'],
                'params': self.pending_confirmation['params']
            }
            self.clear_pending_confirmation()
            return confirmed
        return None

    def set_alarm(self, seconds, callback):
        """
        Set an alarm/reminder

        Args:
            seconds (int): Seconds until alarm
            callback (function): Function to call when alarm triggers
        """
        def alarm_thread():
            time.sleep(seconds)
            callback()

        thread = threading.Thread(target=alarm_thread, daemon=True)
        thread.start()
        self.alarm_threads.append(thread)

    def calculate_seconds(self, value, unit):
        """
        Calculate seconds from value and unit

        Args:
            value (int): Time value
            unit (str): Time unit (second, minute, hour)

        Returns:
            int: Total seconds
        """
        unit = unit.lower()
        if unit.startswith('second'):
            return value
        elif unit.startswith('minute'):
            return value * 60
        elif unit.startswith('hour'):
            return value * 3600
        return value

    def needs_confirmation(self, action):
        """
        Check if an action needs confirmation

        Args:
            action (str): Action name

        Returns:
            bool: True if confirmation needed
        """
        sensitive_actions = ['open_app', 'alarm', 'reminder']
        return action in sensitive_actions

    def get_history_summary(self):
        """
        Get a summary of recent commands

        Returns:
            list: List of recent commands
        """
        return [
            {
                'action': item['command']['action'],
                'timestamp': item['timestamp'].strftime("%H:%M:%S")
            }
            for item in self.command_history
        ]
