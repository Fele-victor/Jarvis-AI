"""
Main Jarvis AI Controller
"""

from core.speech_engine import SpeechEngine
from core.command_processor import CommandProcessor
from core.session_manager import SessionManager
from functions.system_functions import SystemFunctions
from utils.logger import Logger
from config import MODE_VOICE, MODE_MANUAL


class Jarvis:
    """Main Jarvis AI Assistant Controller"""

    def __init__(self):
        """Initialize Jarvis with all components"""
        print("Initializing Jarvis AI...")

        # Initialize components
        self.speech = SpeechEngine()
        self.processor = CommandProcessor()
        self.session = SessionManager()
        self.functions = SystemFunctions()
        self.logger = Logger()

        # State management
        self.current_mode = MODE_VOICE
        self.is_running = False
        self.continuous_listening = False

        print("Jarvis initialized successfully!")

    def start(self):
        """Start Jarvis with greeting"""
        self.is_running = True

        # Greeting
        greeting = "Hello! I am Jarvis, your AI assistant. I'm currently in voice mode."
        self.speech.speak(greeting)

        help_msg = "Say 'help' to know what I can do."
        self.speech.speak(help_msg)

        # Main loop
        self.run()

    def run(self):
        """Main execution loop"""
        while self.is_running:
            try:
                # Check for pending confirmation
                if self.session.get_pending_confirmation():
                    self._handle_pending_confirmation()
                    continue

                # Get input based on mode
                if self.current_mode == MODE_VOICE:
                    success, text, error = self.speech.listen()

                    if not success:
                        self._handle_speech_error(error)
                        continue

                else:  # Manual mode
                    self.speech.speak("Type your command:")
                    text = self.speech.get_manual_input()

                    if not text:
                        continue

                # Process command
                command = self.processor.process(text)

                # Log command
                self.logger.log_command(text, self.current_mode)

                # Execute command
                self._execute_command(command)

            except KeyboardInterrupt:
                self.speech.speak("Shutting down. Goodbye!")
                self.is_running = False
                break

            except Exception as e:
                print(f"Error: {e}")
                self.speech.speak("I encountered an error. Please try again.")

    def _execute_command(self, command):
        """
        Execute a processed command

        Args:
            command (dict): Processed command with action and params
        """
        action = command['action']
        params = command['params']

        # Add to history
        self.session.add_to_history(command)

        # Check if needs confirmation
        if self.session.needs_confirmation(action) and not self.session.get_pending_confirmation():
            self._request_confirmation(command)
            return

        # Execute action
        if action == 'time':
            response = self.functions.get_time()
            self.speech.speak(response)

        elif action == 'date':
            response = self.functions.get_date()
            self.speech.speak(response)

        elif action == 'weather':
            success, message = self.functions.get_weather(params.get('city'))
            self.speech.speak(message)

        elif action == 'search':
            success, message = self.functions.google_search(params['query'])
            self.speech.speak(message)

        elif action == 'wikipedia':
            success, message = self.functions.get_wikipedia_summary(params['query'])
            self.speech.speak(message)

        elif action == 'system_status':
            status_type = params.get('type')
            message = self.functions.get_system_status(status_type)
            self.speech.speak(message)

        elif action == 'open_app':
            success, message = self.functions.open_application(params['app'])
            self.speech.speak(message)

        elif action == 'alarm':
            self._set_alarm(params)

        elif action == 'reminder':
            self._set_reminder(params)

        elif action == 'voice_style':
            style = params['style']
            if self.speech.change_voice_style(style):
                self.speech.speak(f"Voice changed to {style} style")
            else:
                self.speech.speak(f"Voice style {style} not available")

        elif action == 'volume':
            adjustment = params['adjustment']
            self.speech.adjust_volume(adjustment)

            if adjustment == 'mute':
                status = "muted" if self.speech.is_muted else "unmuted"
                self.speech.speak(f"Voice {status}")
            else:
                self.speech.speak(f"Volume adjusted")

        elif action == 'mode_switch':
            self._switch_mode(params['mode'])

        elif action == 'help':
            self._show_help()

        elif action == 'repeat':
            self._handle_repeat(params)

        elif action == 'exit':
            self.speech.speak("Goodbye! Shutting down.")
            self.is_running = False

        elif action == 'listening':
            self._handle_listening_mode(params['mode'])

        else:
            self.speech.speak("I didn't understand that command. Say 'help' for available commands.")

    def _handle_speech_error(self, error):
        """
        Handle speech recognition errors

        Args:
            error (str): Error type or message
        """
        if error == 'timeout':
            self.speech.speak("I didn't hear anything. Switching to manual mode.")
            self.current_mode = MODE_MANUAL

        elif error == 'unknown':
            self.speech.speak("I couldn't understand that. Switching to manual mode.")
            self.current_mode = MODE_MANUAL

        elif 'network_error' in error:
            self.speech.speak("Network error detected. Switching to manual mode.")
            self.current_mode = MODE_MANUAL

        elif error == 'max_retries':
            self.speech.speak("Maximum retries reached. Switching to manual mode.")
            self.current_mode = MODE_MANUAL

        else:
            self.speech.speak(f"Error: {error}")

    def _switch_mode(self, mode):
        """
        Switch between voice and manual mode

        Args:
            mode (str): Target mode
        """
        if mode == MODE_VOICE:
            self.current_mode = MODE_VOICE
            self.speech.speak("Switched to voice mode")
        elif mode == MODE_MANUAL:
            self.current_mode = MODE_MANUAL
            self.speech.speak("Switched to manual mode")

    def _show_help(self):
        """Show available commands"""
        help_text = """
        Here's what I can do:
        - Tell time and date
        - Get weather information
        - Search Google
        - Get Wikipedia summaries
        - Check system status
        - Open applications
        - Set alarms and reminders
        - Change voice style: formal, casual, or robotic
        - Adjust volume: louder, softer, or mute
        - Switch modes: voice mode or manual mode
        - Remember recent commands: say 'repeat that' or 'undo'
        - Say 'exit' to quit
        """
        self.speech.speak(help_text)

    def _set_alarm(self, params):
        """Set an alarm"""
        value = params['value']
        unit = params['unit']
        seconds = self.session.calculate_seconds(value, unit)

        def alarm_callback():
            self.speech.speak(f"Alarm! {value} {unit} has passed!")

        self.session.set_alarm(seconds, alarm_callback)
        self.speech.speak(f"Alarm set for {value} {unit}")

    def _set_reminder(self, params):
        """Set a reminder"""
        value = params['value']
        unit = params['unit']
        message = params['message']
        seconds = self.session.calculate_seconds(value, unit)

        def reminder_callback():
            self.speech.speak(f"Reminder: {message}")

        self.session.set_alarm(seconds, reminder_callback)
        self.speech.speak(f"Reminder set for {value} {unit}")

    def _handle_repeat(self, params):
        """Handle repeat/undo commands"""
        repeat_type = params['type']

        if repeat_type == 'repeat':
            last_command = self.session.get_last_command()
            if last_command:
                self.speech.speak("Repeating last command")
                self._execute_command(last_command)
            else:
                self.speech.speak("No previous command to repeat")

        elif repeat_type == 'undo':
            prev_command = self.session.get_previous_command(2)
            if prev_command:
                self.speech.speak("Executing previous command")
                self._execute_command(prev_command)
            else:
                self.speech.speak("No previous command found")

    def _request_confirmation(self, command):
        """Request confirmation for sensitive actions"""
        action = command['action']
        params = command['params']

        if action == 'open_app':
            message = f"Do you want me to open {params['app']}? Say yes or no."
        elif action == 'alarm':
            message = f"Do you want me to set an alarm for {params['value']} {params['unit']}? Say yes or no."
        elif action == 'reminder':
            message = f"Do you want me to set a reminder for {params['message']}? Say yes or no."
        else:
            message = "Do you want me to continue? Say yes or no."

        self.session.set_pending_confirmation(action, params, message)
        self.speech.speak(message)

    def _handle_pending_confirmation(self):
        """Handle pending confirmation response"""
        pending = self.session.get_pending_confirmation()

        if not pending:
            return

        # Get response
        if self.current_mode == MODE_VOICE:
            success, text, error = self.speech.listen()
            if not success:
                self.speech.speak("I didn't hear you. Please say yes or no.")
                return
        else:
            self.speech.speak("Type yes or no:")
            text = self.speech.get_manual_input()

        # Process response
        if text and ('yes' in text or 'yeah' in text or 'sure' in text):
            confirmed_command = self.session.confirm_action()
            if confirmed_command:
                self.speech.speak("Confirmed")
                self._execute_command(confirmed_command)
        else:
            self.session.clear_pending_confirmation()
            self.speech.speak("Cancelled")

    def _handle_listening_mode(self, mode):
        """Handle continuous listening mode toggle"""
        if mode == 'start':
            self.continuous_listening = True
            self.speech.speak("Starting continuous listening mode")
        elif mode == 'stop':
            self.continuous_listening = False
            self.speech.speak("Stopping continuous listening mode")


def main():
    """Main entry point"""
    try:
        jarvis = Jarvis()
        jarvis.start()
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"Fatal error: {e}")


if __name__ == "__main__":
    main()
