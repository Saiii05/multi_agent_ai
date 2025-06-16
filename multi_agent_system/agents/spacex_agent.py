import requests
from .base_agent import BaseAgent

class SpaceXAgent(BaseAgent):
    """
    Agent responsible for fetching information about the next SpaceX launch.
    """
    API_URL_NEXT_LAUNCH = "https://api.spacexdata.com/v4/launches/next"
    API_URL_LAUNCHPADS = "https://api.spacexdata.com/v4/launchpads/{id}"

    def execute(self, data: dict) -> dict:
        """
        Fetches the next SpaceX launch details and adds them to the data dictionary.

        Args:
            data: A dictionary, potentially containing data from previous agents.

        Returns:
            A dictionary enriched with SpaceX launch information.
            Expected keys: `spacex_mission_name`, `spacex_launch_date_utc`,
                           `spacex_rocket_name`, `spacex_launch_site_name`,
                           `spacex_launch_pad_latitude`, `spacex_launch_pad_longitude`.
        """
        try:
            response = requests.get(self.API_URL_NEXT_LAUNCH)
            response.raise_for_status()  # Raise an exception for HTTP errors
            launch_data = response.json()

            mission_name = launch_data.get("name", "N/A")
            launch_date_utc = launch_data.get("date_utc", "N/A")
            rocket_id = launch_data.get("rocket") # This is an ID, need to fetch rocket name
            launchpad_id = launch_data.get("launchpad") # This is an ID

            # Placeholder for rocket name - actual API might require another call or parsing
            # For now, let's assume we can't get the rocket name directly from /next if it's not expanded
            # and we are not making a second call for rocket details in this version.
            # Students might need to fetch rocket details: GET https://api.spacexdata.com/v4/rockets/{rocket_id}
            rocket_name = f"Rocket ID: {rocket_id}" # Simplified for now

            launch_site_name = "N/A"
            latitude = None
            longitude = None

            if launchpad_id:
                pad_response = requests.get(self.API_URL_LAUNCHPADS.format(id=launchpad_id))
                pad_response.raise_for_status()
                pad_data = pad_response.json()
                launch_site_name = pad_data.get("full_name", pad_data.get("name", "N/A"))
                latitude = pad_data.get("latitude")
                longitude = pad_data.get("longitude")

            data["spacex_mission_name"] = mission_name
            data["spacex_launch_date_utc"] = launch_date_utc
            data["spacex_rocket_name"] = rocket_name # This will be "Rocket ID: <id>"
            data["spacex_launch_site_name"] = launch_site_name
            data["spacex_launch_pad_latitude"] = latitude
            data["spacex_launch_pad_longitude"] = longitude
            data["spacex_agent_status"] = "Success"

        except requests.exceptions.RequestException as e:
            print(f"SpaceXAgent Error: Could not fetch data from SpaceX API: {e}")
            data["spacex_agent_status"] = "Error"
            data["spacex_agent_error_message"] = str(e)
        except Exception as e:
            print(f"SpaceXAgent Error: An unexpected error occurred: {e}")
            data["spacex_agent_status"] = "Error"
            data["spacex_agent_error_message"] = str(e)
            # Ensure keys exist even in error to maintain structure, if desired
            data.setdefault("spacex_mission_name", "Error fetching data")
            data.setdefault("spacex_launch_date_utc", "Error fetching data")
            # ... and so on for other keys

        return data

if __name__ == '__main__':
    # Example usage for testing the agent directly
    agent = SpaceXAgent()
    test_data = {}
    result = agent.execute(test_data)
    print("SpaceX Agent Result:")
    import json
    print(json.dumps(result, indent=2))

    # Test with an existing launchpad ID (example: Falcon 9 Block 5 Starlink Group 4-2)
    # Launchpad for Starlink Group 4-2 (launch 5eb87d4effa4a100069e91f9) is SLC-40 (5e9e4502f509094188566f88)
    # Direct pad data for SLC-40:
    # {
    #   "name": "SLC-40",
    #   "full_name": "Space Launch Complex 40",
    #   "latitude": 28.56194122,
    #   "longitude": -80.57735635
    # }
    # This part is just for illustration; direct execution logic might be different based on actual API responses.
