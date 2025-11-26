"""
Speech recognition and text-to-speech engine for Jarvis
"""

import threading
import queue
import pyttsx3
import speech_recognition as sr
from config import (
    VOICE_STYLES, DEFAULT_VOICE_STYLE,
    RECOGNITION_TIMEOUT, RECOGNITION_PHRASE_LIMIT,
    MAX_RECOGNITION_RETRIES
)


class SpeechEngine:
    """Handles all speech input and output operations"""

    def __init__(self):
        """Initialize speech recognition and TTS engine"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Initialize TTS engine
        self.tts_engine = pyttsx3.init()

        # Voice settings
        self.is_muted = False
        self.base_volume = 0.9

        self.current_voice_style = DEFAULT_VOICE_STYLE
        self._apply_voice_style(self.current_voice_style)

        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

    def _apply_voice_style(self, style):
        """
        Apply a voice style to the TTS engine

        Args:
            style (str): Voice style name (formal, casual, robotic)
        """
        if style in VOICE_STYLES:
            settings = VOICE_STYLES[style]
            self.tts_engine.setProperty('rate', settings['rate'])
            self.tts_engine.setProperty('volume', settings['volume'] * self.base_volume)
            self.current_voice_style = style

    def speak(self, text):
        """
        Convert text to speech

        Args:
            text (str): Text to speak
        """
        if not self.is_muted and text:
            print(f"Jarvis: {text}")
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"TTS Error: {e}")

    def listen(self):
        """
        Listen for voice input with retry mechanism

        Returns:
            tuple: (success: bool, text: str, error_message: str)
        """
        retries = 0

        while retries < MAX_RECOGNITION_RETRIES:
            try:
                with self.microphone as source:
                    print("Listening...")
                    audio = self.recognizer.listen(
                        source,
                        timeout=RECOGNITION_TIMEOUT,
                        phrase_time_limit=RECOGNITION_PHRASE_LIMIT
                    )

                print("Processing...")
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return True, text.lower(), None

            except sr.WaitTimeoutError:
                retries += 1
                if retries < MAX_RECOGNITION_RETRIES:
                    print(f"No speech detected. Retry {retries}/{MAX_RECOGNITION_RETRIES}")
                else:
                    return False, None, "timeout"

            except sr.UnknownValueError:
                retries += 1
                if retries < MAX_RECOGNITION_RETRIES:
                    print(f"Could not understand. Retry {retries}/{MAX_RECOGNITION_RETRIES}")
                else:
                    return False, None, "unknown"

            except sr.RequestError as e:
                return False, None, f"network_error: {e}"

            except Exception as e:
                return False, None, f"error: {e}"

        return False, None, "max_retries"

    def change_voice_style(self, style):
        """
        Change the voice style

        Args:
            style (str): New voice style

        Returns:
            bool: Success status
        """
        if style in VOICE_STYLES:
            self._apply_voice_style(style)
            return True
        return False

    def adjust_volume(self, adjustment):
        """
        Adjust volume level

        Args:
            adjustment (str): 'louder', 'softer', or 'mute'
        """
        if adjustment == 'louder':
            self.base_volume = min(1.0, self.base_volume + 0.2)
            self._apply_voice_style(self.current_voice_style)
        elif adjustment == 'softer':
            self.base_volume = max(0.2, self.base_volume - 0.2)
            self._apply_voice_style(self.current_voice_style)
        elif adjustment == 'mute':
            self.is_muted = not self.is_muted

    def get_manual_input(self):
        """
        Get text input from user manually

        Returns:
            str: User input text
        """
        try:
            text = input("You: ").strip()
            return text.lower() if text else None
        except Exception as e:
            print(f"Input error: {e}")
            return None
