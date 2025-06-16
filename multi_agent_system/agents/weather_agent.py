import os
import requests
from .base_agent import BaseAgent
# We'll assume a utility function will handle loading .env,
# but for now, os.getenv will work if the variable is set.
# from dotenv import load_dotenv # Typically you'd load this in main.py or a config module
# load_dotenv() # Call it to load .env variables

class WeatherAgent(BaseAgent):
    """
    Agent responsible for fetching weather information from OpenWeatherMap API
    based on geographical coordinates.
    """
    API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key: str = None):
        """
        Initializes the WeatherAgent.
        Args:
            api_key: The OpenWeatherMap API key. If None, it tries to fetch from
                     the environment variable OPENWEATHER_API_KEY.
        """
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            # In a real application, you might raise an error or have a fallback.
            # For this assignment, we'll print a warning. The agent will likely fail
            # if execute is called without an API key.
            print("Warning: OPENWEATHER_API_KEY not found in environment or provided.")

    def execute(self, data: dict) -> dict:
        """
        Fetches weather data for the given latitude and longitude and adds it
        to the data dictionary.

        Args:
            data: A dictionary expecting 'spacex_launch_pad_latitude' and
                  'spacex_launch_pad_longitude' keys.

        Returns:
            A dictionary enriched with weather information.
            Expected keys: `weather_conditions`, `weather_temperature_celsius`,
                           `weather_humidity_percent`, `weather_wind_speed_mps`,
                           `weather_rain_1h_mm` (if available).
        """
        latitude = data.get("spacex_launch_pad_latitude")
        longitude = data.get("spacex_launch_pad_longitude")

        if latitude is None or longitude is None:
            data["weather_agent_status"] = "Error"
            data["weather_agent_error_message"] = "Latitude or longitude missing in input data."
            print("WeatherAgent Error: Latitude or longitude missing.")
            return data

        if not self.api_key:
            data["weather_agent_status"] = "Error"
            data["weather_agent_error_message"] = "OpenWeatherMap API key is missing."
            print("WeatherAgent Error: API key missing.")
            return data

        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "metric"  # For Celsius
        }

        try:
            response = requests.get(self.API_BASE_URL, params=params)
            response.raise_for_status()
            weather_data = response.json()

            # Extract relevant weather information
            # Main weather description
            if weather_data.get("weather") and len(weather_data["weather"]) > 0:
                data["weather_conditions"] = weather_data["weather"][0].get("description", "N/A")
            else:
                data["weather_conditions"] = "N/A"

            # Temperature
            if weather_data.get("main"):
                data["weather_temperature_celsius"] = weather_data["main"].get("temp")
                data["weather_humidity_percent"] = weather_data["main"].get("humidity")
            else:
                data["weather_temperature_celsius"] = None
                data["weather_humidity_percent"] = None

            # Wind
            if weather_data.get("wind"):
                data["weather_wind_speed_mps"] = weather_data["wind"].get("speed")
            else:
                data["weather_wind_speed_mps"] = None

            # Rain (rain.1h is rain volume for the last 1 hour in mm)
            if weather_data.get("rain") and "1h" in weather_data["rain"]:
                data["weather_rain_1h_mm"] = weather_data["rain"]["1h"]
            else:
                data["weather_rain_1h_mm"] = 0 # Assume 0 if not present

            data["weather_agent_status"] = "Success"

        except requests.exceptions.RequestException as e:
            print(f"WeatherAgent Error: Could not fetch data from OpenWeatherMap API: {e}")
            data["weather_agent_status"] = "Error"
            data["weather_agent_error_message"] = str(e)
        except Exception as e:
            print(f"WeatherAgent Error: An unexpected error occurred: {e}")
            data["weather_agent_status"] = "Error"
            data["weather_agent_error_message"] = str(e)
            # Ensure keys exist even in error
            data.setdefault("weather_conditions", "Error fetching data")
            # ... and so on

        return data

if __name__ == '__main__':
    # Example usage for testing the agent directly
    # You need to set OPENWEATHER_API_KEY environment variable for this to work.
    # For example, Cape Canaveral coordinates: Latitude: 28.56194122, Longitude: -80.57735635
    print("Attempting WeatherAgent direct test...")
    if not os.getenv("OPENWEATHER_API_KEY"):
        print("Skipping WeatherAgent test: OPENWEATHER_API_KEY not set.")
    else:
        agent = WeatherAgent() # API key will be loaded from env
        test_data_cape = {
            "spacex_launch_pad_latitude": 28.5619,
            "spacex_launch_pad_longitude": -80.5773
        }
        result = agent.execute(test_data_cape)
        print("\nWeather Agent Result (Cape Canaveral):")
        import json
        print(json.dumps(result, indent=2))

        test_data_invalid = {
            "spacex_launch_pad_latitude": None,
            "spacex_launch_pad_longitude": -80.5773
        }
        result_invalid = agent.execute(test_data_invalid)
        print("\nWeather Agent Result (Invalid Coords):")
        print(json.dumps(result_invalid, indent=2))

        # Test with no API key (by temporarily unsetting or passing None)
        # This would require modifying the agent instantiation for a direct test,
        # or running in an env where the key is truly absent.
        # agent_no_key = WeatherAgent(api_key="INVALID_KEY_TEST") # Or force it to be None
        # result_no_key = agent_no_key.execute(test_data_cape.copy())
        # print("\nWeather Agent Result (Invalid API Key):")
        # print(json.dumps(result_no_key, indent=2))
