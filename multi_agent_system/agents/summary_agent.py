from .base_agent import BaseAgent

class SummaryAgent(BaseAgent):
    """
    Agent responsible for generating a summary based on the collected data
    from other agents (e.g., SpaceX launch details and weather conditions).
    """

    def execute(self, data: dict) -> dict:
        """
        Generates a summary string from the input data and adds it to the dictionary.

        Args:
            data: A dictionary containing data from previous agents.
                  Expected keys from SpaceXAgent:
                    'spacex_mission_name', 'spacex_launch_date_utc',
                    'spacex_rocket_name', 'spacex_launch_site_name'.
                  Expected keys from WeatherAgent:
                    'weather_conditions', 'weather_temperature_celsius',
                    'weather_wind_speed_mps', 'weather_rain_1h_mm'.

        Returns:
            The data dictionary enriched with a 'summary_text' key.
        """
        try:
            # --- Extract SpaceX Data ---
            mission_name = data.get("spacex_mission_name", "N/A")
            launch_date_utc = data.get("spacex_launch_date_utc", "N/A")
            rocket_name = data.get("spacex_rocket_name", "N/A") # Recall this is "Rocket ID: <id>"
            launch_site_name = data.get("spacex_launch_site_name", "N/A")

            # --- Extract Weather Data ---
            weather_conditions = data.get("weather_conditions", "N/A")
            temp_celsius = data.get("weather_temperature_celsius") # Can be None
            wind_speed_mps = data.get("weather_wind_speed_mps")   # Can be None
            rain_1h_mm = data.get("weather_rain_1h_mm", 0)        # Defaults to 0 if not present

            # --- Build Summary String ---
            summary_parts = []

            if mission_name != "N/A":
                summary_parts.append(f"The next SpaceX mission, '{mission_name}', is scheduled to launch the {rocket_name} from {launch_site_name} on {launch_date_utc}.")
            else:
                summary_parts.append("Information about the next SpaceX launch is currently unavailable.")
                data["summary_text"] = " ".join(summary_parts)
                data["summary_agent_status"] = "Partial Data" # Or success, as it summarized what it could
                return data


            if weather_conditions != "N/A":
                weather_desc = f"Current weather at the launch site: {weather_conditions}"
                if temp_celsius is not None:
                    weather_desc += f", with a temperature of {temp_celsius}°C"
                if wind_speed_mps is not None:
                    weather_desc += f" and wind speeds of {wind_speed_mps} m/s"
                if rain_1h_mm > 0:
                    weather_desc += f". There has been {rain_1h_mm}mm of rain in the last hour"
                weather_desc += "."
                summary_parts.append(weather_desc)
            else:
                summary_parts.append("Weather data for the launch site is currently unavailable.")

            # --- Potential Delay Logic (Simple) ---
            delay_assessment = "No immediate weather concerns for delay noted."
            # Thresholds for potential delay - these are illustrative
            RAIN_THRESHOLD_MM = 0.5  # e.g., more than 0.5mm of rain
            WIND_THRESHOLD_MPS = 10  # e.g., wind speed over 10 m/s (approx 22 mph / 36 kph)

            potential_delay_reasons = []
            if rain_1h_mm > RAIN_THRESHOLD_MM:
                potential_delay_reasons.append(f"significant rain ({rain_1h_mm}mm/hr)")

            if wind_speed_mps is not None and wind_speed_mps > WIND_THRESHOLD_MPS:
                potential_delay_reasons.append(f"high wind speeds ({wind_speed_mps} m/s)")

            if "thunderstorm" in weather_conditions.lower():
                 potential_delay_reasons.append("thunderstorms")
            if "heavy rain" in weather_conditions.lower():
                 potential_delay_reasons.append("heavy rain")


            if potential_delay_reasons:
                delay_assessment = f"Potential for launch delay due to: {', '.join(potential_delay_reasons)}."

            summary_parts.append(delay_assessment)

            data["summary_text"] = " ".join(summary_parts)
            data["summary_agent_status"] = "Success"

        except Exception as e:
            print(f"SummaryAgent Error: An unexpected error occurred: {e}")
            data["summary_text"] = "Could not generate summary due to an internal error."
            data["summary_agent_status"] = "Error"
            data["summary_agent_error_message"] = str(e)

        return data

if __name__ == '__main__':
    # Example usage for testing the agent directly
    agent = SummaryAgent()

    test_data_ideal = {
        "spacex_mission_name": "Starlink Group 6-2",
        "spacex_launch_date_utc": "2023-10-26T12:00:00Z",
        "spacex_rocket_name": "Falcon 9", # Actual agent gives "Rocket ID: <id>"
        "spacex_launch_site_name": "SLC-40, Cape Canaveral",
        "weather_conditions": "few clouds",
        "weather_temperature_celsius": 25.5,
        "weather_wind_speed_mps": 5.0,
        "weather_rain_1h_mm": 0.0
    }
    result_ideal = agent.execute(test_data_ideal.copy())
    print("Summary Agent Result (Ideal Case):")
    print(result_ideal.get("summary_text"))
    print(f"Status: {result_ideal.get('summary_agent_status')}\n")

    test_data_delay_rain = {
        "spacex_mission_name": "Lunar Gateway Logistics",
        "spacex_launch_date_utc": "2023-11-15T18:30:00Z",
        "spacex_rocket_name": "Falcon Heavy",
        "spacex_launch_site_name": "LC-39A, Kennedy Space Center",
        "weather_conditions": "moderate rain",
        "weather_temperature_celsius": 22.0,
        "weather_wind_speed_mps": 7.0,
        "weather_rain_1h_mm": 2.5 # Above threshold
    }
    result_delay_rain = agent.execute(test_data_delay_rain.copy())
    print("Summary Agent Result (Rain Delay Case):")
    print(result_delay_rain.get("summary_text"))
    print(f"Status: {result_delay_rain.get('summary_agent_status')}\n")

    test_data_delay_wind = {
        "spacex_mission_name": "Oneweb Mission 15",
        "spacex_launch_date_utc": "2023-12-01T09:00:00Z",
        "spacex_rocket_name": "Falcon 9",
        "spacex_launch_site_name": "Vandenberg SFB",
        "weather_conditions": "clear sky",
        "weather_temperature_celsius": 18.0,
        "weather_wind_speed_mps": 15.0, # Above threshold
        "weather_rain_1h_mm": 0.0
    }
    result_delay_wind = agent.execute(test_data_delay_wind.copy())
    print("Summary Agent Result (Wind Delay Case):")
    print(result_delay_wind.get("summary_text"))
    print(f"Status: {result_delay_wind.get('summary_agent_status')}\n")

    test_data_missing_weather = {
        "spacex_mission_name": "GPS III SV07",
        "spacex_launch_date_utc": "2024-01-10T14:00:00Z",
        "spacex_rocket_name": "Falcon 9",
        "spacex_launch_site_name": "SLC-40, Cape Canaveral",
        # Weather data is missing
    }
    result_missing_weather = agent.execute(test_data_missing_weather.copy())
    print("Summary Agent Result (Missing Weather Data):")
    print(result_missing_weather.get("summary_text"))
    print(f"Status: {result_missing_weather.get('summary_agent_status')}\n")

    test_data_missing_spacex = {
        # SpaceX data is missing
        "weather_conditions": "overcast clouds",
        "weather_temperature_celsius": 20.0,
        "weather_wind_speed_mps": 3.0,
        "weather_rain_1h_mm": 0.0
    }
    result_missing_spacex = agent.execute(test_data_missing_spacex.copy())
    print("Summary Agent Result (Missing SpaceX Data):")
    print(result_missing_spacex.get("summary_text")) # Should indicate SpaceX info unavailable
    print(f"Status: {result_missing_spacex.get('summary_agent_status')}\n")

    test_data_empty = {}
    result_empty = agent.execute(test_data_empty.copy())
    print("Summary Agent Result (Empty Data):")
    print(result_empty.get("summary_text"))
    print(f"Status: {result_empty.get('summary_agent_status')}\n")

```
