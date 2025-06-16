import json
import os # For WeatherAgent to fetch API_KEY if not passed directly

# Utility to load .env file first
from utils.api_helpers import load_api_keys, get_api_key

# Import Agents
from agents.base_agent import BaseAgent # Not strictly needed here, but good for context
from agents.spacex_agent import SpaceXAgent
from agents.weather_agent import WeatherAgent
from agents.summary_agent import SummaryAgent

# Import Planner
from planner import Planner

def main():
    """
    Main function to orchestrate the multi-agent system.
    """
    # Load API keys from .env file into environment variables
    # This should be one of the first things your application does.
    if load_api_keys():
        print("main.py: .env file loaded successfully.")
    else:
        print("main.py: .env file not found or not loaded. WeatherAgent might fail if API key not set in environment otherwise.")

    # Retrieve the API key for OpenWeatherMap
    # The WeatherAgent itself also tries os.getenv("OPENWEATHER_API_KEY")
    # if no key is passed to its constructor.
    # Passing it explicitly makes the dependency clearer here.
    openweathermap_api_key = get_api_key("OPENWEATHER_API_KEY")
    if not openweathermap_api_key:
        print("main.py: Warning - OPENWEATHER_API_KEY not found in environment. Weather agent may not work.")
        # The WeatherAgent has its own warning if the key is missing.

    # 1. Instantiate Agents
    print("\nInitializing agents...")
    try:
        spacex_agent = SpaceXAgent()
        # WeatherAgent can take api_key directly, or load from env.
        # If openweathermap_api_key is None here, WeatherAgent will try os.getenv() again.
        weather_agent = WeatherAgent(api_key=openweathermap_api_key)
        summary_agent = SummaryAgent()
        print("Agents initialized.")
    except Exception as e:
        print(f"Error during agent initialization: {e}")
        return

    # 2. Create available_agents dictionary
    # The keys ('spacex', 'weather', 'summary') must match what the Planner's parse_goal produces.
    available_agents = {
        "spacex": spacex_agent,
        "weather": weather_agent,
        "summary": summary_agent
    }

    # 3. Instantiate Planner
    print("\nInitializing planner...")
    try:
        planner = Planner()
        print("Planner initialized.")
    except Exception as e:
        print(f"Error during planner initialization: {e}")
        return

    # 4. Define User Goal
    # Using the example goal from the assignment
    user_goal = "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed."
    # user_goal = "What's the weather and summarize?" # Test another goal
    # user_goal = "Next SpaceX launch details please."

    print(f"\nProcessing goal: '{user_goal}'")

    # 5. Execute Plan
    final_result = {}
    try:
        print("\nPlanner executing plan...")
        final_result = planner.execute_plan(user_goal, available_agents)
        print("Plan execution finished.")
    except Exception as e:
        print(f"An unexpected error occurred during plan execution: {e}")
        final_result = {"status": "error", "message": f"Critical error in main: {str(e)}"}


    # 6. Print Results
    print("\n--- Final Result ---")
    # Pretty print the JSON output
    print(json.dumps(final_result, indent=2))

    if final_result.get("status") == "success" and "summary_text" in final_result:
        print("\n--- Summary Text ---")
        print(final_result["summary_text"])
    elif "summary_text" in final_result: # Even if overall status not success, summary might exist
        print("\n--- Partial Summary / Error Summary ---")
        print(final_result["summary_text"])
    else:
        print("\nNo summary text produced or an error occurred before summary generation.")

if __name__ == "__main__":
    main()
```
