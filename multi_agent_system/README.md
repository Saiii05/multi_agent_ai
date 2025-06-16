# Multi-Agent System

This project implements a multi-agent system that can take a user goal, create a plan, and route data between specialized agents to achieve the goal.

## Features
- **Planner Agent:** Interprets user goals and creates an execution plan.
- **Enrichment Agents:** Perform specific tasks (e.g., fetching data from APIs).
- **Sequential Data Processing:** Each agent enriches data from the previous one.
- **API Integration:** Demonstrates usage of public APIs (SpaceX, OpenWeatherMap).

## Project Structure
```
multi_agent_system/
├── main.py                 # Main entry point, orchestrator
├── planner.py              # Planner agent logic
├── agents/                 # Directory for enrichment agents
│   ├── __init__.py
│   ├── base_agent.py       # Abstract base class for agents
│   ├── spacex_agent.py     # Agent for SpaceX API
│   └── weather_agent.py    # Agent for Weather API (and potentially others)
├── utils/                  # Utility functions
│   └── api_helpers.py      # For loading API keys from .env
├── evals/                  # Evaluation scripts and notes
├── .env                    # Actual API key configuration (gitignored)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup

1.  **Clone the repository (if applicable):**
    ```bash
    # git clone https://github.com/Saiii05/multi_agent_ai.git
    # cd multi_agent_ai
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys:**
    *   This project uses the OpenWeatherMap API, which requires an API key.
    *   Copy the example `.env.example` file to a new file named `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Open the `.env` file and add your OpenWeatherMap API key:
        ```
        OPENWEATHER_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
        ```
    *   You can obtain an OpenWeatherMap API key by registering on their website: [https://openweathermap.org/appid](https://openweathermap.org/appid)
    *   The SpaceX API used in this project does not require an API key for the public endpoints accessed.

## Usage

To run the multi-agent system:

1.  Ensure you have completed all steps in the [Setup](#setup) section (virtual environment activated, dependencies installed, `.env` file created with your `OPENWEATHER_API_KEY`).
2.  Navigate to the `multi_agent_system` directory in your terminal.
3.  Run the main script:

    ```bash
    python main.py
    ```

4.  The script will process a predefined goal (currently: "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed.") and print the detailed JSON output, followed by a concise summary.

## Agent Logic and Data Flow

The system processes a user goal by routing it through a sequence of specialized agents. The `Planner` agent first determines this sequence based on keywords in the goal.

### 1. Planner Agent (`planner.py`)
*   **Logic:** Parses the user's natural language goal to identify a sequence of required tasks (agents). For the primary example, it identifies "spacex", "weather", and "summary" in that order.
*   **Input:** User goal string (e.g., "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed.") and a dictionary of available agent instances.
*   **Output:** A dictionary containing all data accumulated from the executed agents, including the final summary.
*   **Orchestration:** Calls the `execute` method of each agent in the determined sequence, passing the output data from one agent to the next.

### 2. SpaceX Agent (`agents/spacex_agent.py`)
*   **Logic:** Fetches details about the next upcoming SpaceX launch.
*   **API Used:** [SpaceX API v4](https://github.com/r-spacex/SpaceX-API/tree/master/docs/v4)
    *   Endpoint for next launch: `https://api.spacexdata.com/v4/launches/next`
    *   Endpoint for launchpad details (to get coordinates): `https://api.spacexdata.com/v4/launchpads/{id}`
*   **Input:** An initial data dictionary (usually empty from the planner).
*   **Output Data (added to dictionary):**
    *   `spacex_mission_name`: Name of the mission.
    *   `spacex_launch_date_utc`: Launch date in UTC.
    *   `spacex_rocket_name`: Simplified to "Rocket ID: {rocket_id}". (A full implementation might fetch the actual rocket name via another API call).
    *   `spacex_launch_site_name`: Name of the launch site.
    *   `spacex_launch_pad_latitude`: Latitude of the launchpad.
    *   `spacex_launch_pad_longitude`: Longitude of the launchpad.
    *   `spacex_agent_status`: "Success" or "Error".

### 3. Weather Agent (`agents/weather_agent.py`)
*   **Logic:** Fetches current weather conditions for a given geographical location (latitude and longitude).
*   **API Used:** [OpenWeatherMap Current Weather Data API](https://openweathermap.org/current)
    *   Endpoint: `https://api.openweathermap.org/data/2.5/weather`
*   **Input:** Data dictionary containing `spacex_launch_pad_latitude` and `spacex_launch_pad_longitude` (typically from the `SpaceXAgent`). Requires `OPENWEATHER_API_KEY` to be set in the `.env` file.
*   **Output Data (added to dictionary):**
    *   `weather_conditions`: Textual description of weather (e.g., "clear sky", "few clouds").
    *   `weather_temperature_celsius`: Temperature in Celsius.
    *   `weather_humidity_percent`: Humidity percentage.
    *   `weather_wind_speed_mps`: Wind speed in meters per second.
    *   `weather_rain_1h_mm`: Rain volume in the last hour in millimeters (defaults to 0 if no rain).
    *   `weather_agent_status`: "Success" or "Error".

### 4. Summary Agent (`agents/summary_agent.py`)
*   **Logic:** Generates a concise, human-readable summary based on the information gathered by previous agents (SpaceX launch details and weather conditions). It also provides a simple assessment of potential launch delays due to weather.
*   **Input:** Data dictionary containing information from `SpaceXAgent` and `WeatherAgent`.
*   **Output Data (added to dictionary):**
    *   `summary_text`: The generated textual summary.
    *   `summary_agent_status`: "Success", "Partial Data", or "Error".

### Example Data Flow (for the primary goal)

1.  **User Goal:** "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed."
2.  **Planner:** Determines agent sequence: `['spacex', 'weather', 'summary']`.
3.  **SpaceXAgent executes:**
    *   Input: `{}`
    *   Output (example): `{"spacex_mission_name": "Starlink XYZ", ..., "spacex_launch_pad_latitude": 28.56, "spacex_launch_pad_longitude": -80.57, ...}`
4.  **WeatherAgent executes:**
    *   Input: Data from SpaceXAgent.
    *   Output (example): `{"spacex_mission_name": "Starlink XYZ", ..., "weather_conditions": "scattered clouds", "weather_temperature_celsius": 26, ...}`
5.  **SummaryAgent executes:**
    *   Input: Data from SpaceXAgent and WeatherAgent.
    *   Output (example): `{"spacex_mission_name": ..., "weather_conditions": ..., "summary_text": "The next SpaceX mission 'Starlink XYZ' ... Weather ... No immediate weather concerns..."}`
6.  **Final Output:** The complete dictionary from the SummaryAgent is returned by the Planner.

## APIs Used

*   **SpaceX API (v4):** Used by `SpaceXAgent` to fetch launch information.
    *   Documentation: [https://github.com/r-spacex/SpaceX-API/tree/master/docs/v4](https://github.com/r-spacex/SpaceX-API/tree/master/docs/v4)
    *   No API key required for the endpoints used.
*   **OpenWeatherMap API (Current Weather Data):** Used by `WeatherAgent` to fetch weather conditions.
    *   Documentation: [https://openweathermap.org/current](https://openweathermap.org/current)
    *   Requires an API key. You can get one by signing up at [https://openweathermap.org/appid](https://openweathermap.org/appid). This key should be stored in the `.env` file as `OPENWEATHER_API_KEY`.

```
