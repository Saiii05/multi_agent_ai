import os
from dotenv import load_dotenv

def load_api_keys():
    """
    Loads environment variables from a .env file in the project root.
    This function should ideally be called once at the beginning of the application.
    """
    # dotenv_path = find_dotenv() # find_dotenv will search for .env
    # if not dotenv_path:
    #     print("Warning: .env file not found.")
    # else:
    #     load_dotenv(dotenv_path)
    #     print(f".env file loaded from {dotenv_path}")

    # Simplification: Assume .env is in the same directory as where script is run from, or parent.
    # load_dotenv() will search for .env.
    # If this script is in utils/, and .env is in multi_agent_system/,
    # load_dotenv() should find it if main.py (in multi_agent_system/) calls this.
    # For robustness, one might specify path: load_dotenv(Path('.') / '.env')

    loaded = load_dotenv()
    # if loaded:
    #     print("Environment variables from .env loaded.")
    # else:
    #     print("No .env file found or it is empty.") # Or it might load system env vars anyway
    return loaded # Returns True if .env was found and loaded, False otherwise.

def get_api_key(key_name: str) -> str | None:
    """
    Retrieves an API key from environment variables.

    Args:
        key_name: The name of the environment variable storing the API key.

    Returns:
        The API key string if found, otherwise None.
    """
    return os.getenv(key_name)

if __name__ == '__main__':
    # This demonstrates how to use the functions.
    # Create a dummy .env file in the same directory as this script for this test,
    # or ensure your actual .env is discoverable from here.
    # For example, if .env is in multi_agent_system/ and you run this from multi_agent_system/utils:
    # You might need to adjust path for load_dotenv e.g. load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

    print("Attempting to load .env (may require .env in this directory or project root depending on execution context)")
    if load_api_keys():
        print(".env loaded successfully for test.")
    else:
        print("Warning: .env file not found or not loaded during test. API key retrieval might fail.")

    # Example: Retrieve OpenWeatherMap API key
    owm_key = get_api_key("OPENWEATHER_API_KEY")
    if owm_key:
        print(f"OpenWeatherMap API Key (first 5 chars): {owm_key[:5]}...")
    else:
        print("OpenWeatherMap API Key not found in environment variables.")

    # Example: Retrieve a non-existent key
    dummy_key = get_api_key("NON_EXISTENT_KEY")
    if dummy_key:
        print("Non-existent key found (unexpected).")
    else:
        print("Non-existent key not found (as expected).")
