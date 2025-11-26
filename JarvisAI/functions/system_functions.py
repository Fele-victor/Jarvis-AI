"""
System functions for Jarvis - time, date, weather, system status, etc.
"""

import os
import platform
import webbrowser
from datetime import datetime
import requests
import psutil
import wikipedia
from config import WEATHER_API_KEY, WEATHER_API_URL


class SystemFunctions:
    """Handles system-level operations and information retrieval"""

    def __init__(self):
        """Initialize system functions"""
        self.safe_apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'browser': self._get_default_browser,
            'chrome': 'chrome' if platform.system() != 'Windows' else 'chrome.exe',
            'firefox': 'firefox',
        }

    def get_time(self):
        """
        Get current time

        Returns:
            str: Formatted time string
        """
        now = datetime.now()
        return now.strftime("It's %I:%M %p")

    def get_date(self):
        """
        Get current date

        Returns:
            str: Formatted date string
        """
        now = datetime.now()
        return now.strftime("Today is %A, %B %d, %Y")

    def get_weather(self, city=None):
        """
        Get weather information

        Args:
            city (str): City name (optional)

        Returns:
            tuple: (success: bool, message: str)
        """
        if not WEATHER_API_KEY:
            return False, "Weather API is not configured. I need an API key to fetch weather data."

        try:
            city = city or "London"  # Default city
            params = {
                'q': city,
                'appid': WEATHER_API_KEY,
                'units': 'metric'
            }

            response = requests.get(WEATHER_API_URL, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                return True, f"The weather in {city} is {description} with a temperature of {temp} degrees Celsius"
            else:
                return False, f"Could not fetch weather for {city}"

        except requests.RequestException:
            return False, "I'm having trouble connecting to the weather service. Please check your internet connection."
        except Exception as e:
            return False, f"Weather error: {str(e)}"

    def get_system_status(self, status_type=None):
        """
        Get system status information

        Args:
            status_type (str): Type of status (cpu, battery, network, or None for all)

        Returns:
            str: System status message
        """
        try:
            if status_type == 'cpu':
                cpu_percent = psutil.cpu_percent(interval=1)
                return f"CPU usage is at {cpu_percent} percent"

            elif status_type == 'battery':
                battery = psutil.sensors_battery()
                if battery:
                    percent = battery.percent
                    plugged = "plugged in" if battery.power_plugged else "on battery"
                    return f"Battery is at {percent} percent and {plugged}"
                else:
                    return "Battery information is not available on this system"

            elif status_type == 'network':
                # Simple check if we can make a request
                try:
                    requests.get('https://www.google.com', timeout=2)
                    return "Network connection is active"
                except:
                    return "Network connection appears to be down"

            else:
                # Return all status
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                status_msg = f"System Status: CPU usage is {cpu_percent} percent, Memory usage is {memory.percent} percent"

                battery = psutil.sensors_battery()
                if battery:
                    status_msg += f", Battery is at {battery.percent} percent"

                return status_msg

        except Exception as e:
            return f"Error getting system status: {str(e)}"

    def open_application(self, app_name):
        """
        Open a safe application

        Args:
            app_name (str): Application name

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            app_name = app_name.lower().strip()

            if app_name in self.safe_apps:
                app_command = self.safe_apps[app_name]

                if callable(app_command):
                    app_command()
                    return True, f"Opening {app_name}"
                else:
                    os.system(app_command)
                    return True, f"Opening {app_name}"
            else:
                return False, f"I cannot open {app_name}. It's not in my safe applications list."

        except Exception as e:
            return False, f"Error opening application: {str(e)}"

    def google_search(self, query):
        """
        Perform a Google search

        Args:
            query (str): Search query

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return True, f"Searching Google for {query}"
        except Exception as e:
            return False, f"Error performing search: {str(e)}"

    def get_wikipedia_summary(self, query):
        """
        Get Wikipedia summary

        Args:
            query (str): Search query

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Set number of sentences
            wikipedia.set_lang("en")
            summary = wikipedia.summary(query, sentences=3)
            return True, summary

        except wikipedia.exceptions.DisambiguationError as e:
            options = ', '.join(e.options[:3])
            return False, f"Multiple results found. Please be more specific. Options: {options}"

        except wikipedia.exceptions.PageError:
            return False, f"I couldn't find any Wikipedia page for {query}"

        except requests.exceptions.RequestException:
            return False, "I'm offline and cannot access Wikipedia right now"

        except Exception as e:
            return False, f"Wikipedia error: {str(e)}"

    def _get_default_browser(self):
        """Open default browser"""
        webbrowser.open("https://www.google.com")
