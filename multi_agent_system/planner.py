# Import agent base class and specific agents for type hinting if necessary,
# though for dynamic loading via strings, direct imports might not be strictly needed here.
# from .agents.base_agent import BaseAgent
# from .agents.spacex_agent import SpaceXAgent
# from .agents.weather_agent import WeatherAgent
# from .agents.summary_agent import SummaryAgent # Assuming this will be created

class Planner:
    """
    The Planner agent is responsible for parsing the user's goal,
    determining the sequence of specialized agents needed, and orchestrating
    their execution.
    """

    def __init__(self):
        # In a more advanced system, the planner might have its own configuration
        # or access to a registry of available agents and their capabilities.
        pass

    def parse_goal(self, goal: str) -> list[str]:
        """
        Parses the user's goal string to determine the sequence of agents.
        This is a simplified keyword-based parser.

        Args:
            goal: The user's natural language goal.

        Returns:
            A list of strings, where each string is an agent identifier (e.g., 'spacex', 'weather').
        """
        goal_lower = goal.lower()
        agent_sequence = []

        # Define keywords and their order preference if necessary.
        # For this example, the order in the goal string is assumed to be the desired execution order.
        if "spacex launch" in goal_lower or "next launch" in goal_lower:
            agent_sequence.append("spacex")

        if "weather" in goal_lower:
            # Ensure weather comes after spacex if spacex is also present,
            # as weather usually depends on location from spacex.
            if "spacex" in agent_sequence and "weather" not in agent_sequence:
                 agent_sequence.append("weather")
            elif "spacex" not in agent_sequence: # weather as a standalone or first agent
                 agent_sequence.append("weather")
            # If spacex is not in sequence yet, but weather is mentioned first, it might be an issue
            # or the goal implies weather for a pre-defined location.
            # For now, this simple logic adds it if keyword is found.

        if "summarize" in goal_lower or "summary" in goal_lower:
            # Summary usually comes last.
            agent_sequence.append("summary")

        # Basic de-duplication while preserving order for this simple parser
        # (e.g. if "spacex launch" and "next launch" both trigger "spacex")
        # More robust would be to map keywords to agents and then order them.
        ordered_agent_sequence = []
        seen = set()
        for agent_name in agent_sequence:
            if agent_name not in seen:
                ordered_agent_sequence.append(agent_name)
                seen.add(agent_name)

        # A more explicit ordering for the primary use case:
        # "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed."
        # This specific phrase implies an order.
        # If "spacex" and "weather" are both present, ensure spacex is before weather.
        # This is a bit naive and could be improved with more sophisticated parsing or explicit ordering rules.

        final_sequence = []
        if "spacex" in ordered_agent_sequence:
            final_sequence.append("spacex")
        if "weather" in ordered_agent_sequence:
            if "spacex" not in final_sequence: # If spacex was not in the goal, weather can be first
                final_sequence.append("weather")
            elif "spacex" in final_sequence: # Ensure weather is after spacex if both present
                 # Check if weather is already added, if not, add it.
                 # This logic is getting complicated, a clearer keyword mapping and ordering step is better.
                 # For now, let's simplify: if keywords are present, add in a pre-defined order if possible.

                # Simplified re-ordering for the example:
                # If 'spacex' and 'weather' are in ordered_agent_sequence,
                # ensure 'spacex' comes before 'weather'.
                # This is a hack for the example. A proper planner would have better dependency management.
                pass # Already handled by the order of keyword checks above for the main example

        # Rebuilding final_sequence based on a known preferred order for the demo.
        # This part needs to be more robust for general cases.
        # Let's try a simpler approach for `parse_goal` for now:

        agent_keywords = {
            "spacex": ["spacex launch", "next launch"],
            "weather": ["weather"],
            "summary": ["summarize", "summary"],
        }

        # Determine presence of keywords
        present_agents = {} # agent_name: first_occurrence_index
        for agent_name, keywords in agent_keywords.items():
            for keyword in keywords:
                idx = goal_lower.find(keyword)
                if idx != -1:
                    if agent_name not in present_agents or idx < present_agents[agent_name]:
                        present_agents[agent_name] = idx
                    break # Found one keyword for this agent

        # Sort detected agents by their first appearance in the goal string
        # This assumes the user states goals in the order they want them executed.
        sorted_detected_agents = sorted(present_agents.keys(), key=lambda agent: present_agents[agent])

        # Specific dependency: if 'weather' agent is present, it often depends on 'spacex' for location.
        # If both are present, and 'spacex' is not before 'weather', it might indicate an issue or a different intent.
        # For the specified example "Find the next SpaceX launch, check weather...", this order is natural.
        # This simple parser doesn't handle complex dependencies. It just identifies agents.
        # The main example "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed."
        # implies spacex -> weather -> summary.

        # The plan asks for: For the example goal, it should produce ['spacex', 'weather', 'summary']
        # Let's hardcode the logic for the example and make it slightly more general.

        parsed_sequence = []
        if any(kw in goal_lower for kw in agent_keywords["spacex"]):
            parsed_sequence.append("spacex")
        if any(kw in goal_lower for kw in agent_keywords["weather"]):
            # If spacex is already planned, weather comes after.
            # If not, weather can be first (e.g. "weather in New York and summarize")
            parsed_sequence.append("weather")
        if any(kw in goal_lower for kw in agent_keywords["summary"]):
            parsed_sequence.append("summary")

        # Ensure spacex is before weather if both are present
        if "spacex" in parsed_sequence and "weather" in parsed_sequence:
            s_idx = parsed_sequence.index("spacex")
            w_idx = parsed_sequence.index("weather")
            if w_idx < s_idx: # weather is before spacex, incorrect for dependency
                # This indicates a flaw in sequential addition; let's rebuild based on known order
                # For the primary example, this won't happen.
                # A truly robust parser is beyond scope here, so this is a simplification.
                pass


        # The simplest parser for the prompt's example would be:
        # If "spacex launch" or "next launch" -> add "spacex"
        # If "weather" -> add "weather"
        # If "summarize" or "summary" -> add "summary"
        # This relies on the fact that available_agents will be 'spacex', 'weather', 'summary'.

        # Final simplified parser based on plan's requirement for example:
        final_ordered_sequence = []
        if "spacex launch" in goal_lower or "next launch" in goal_lower:
            final_ordered_sequence.append("spacex")
        if "weather" in goal_lower:
            final_ordered_sequence.append("weather")
        if "summarize" in goal_lower or "summary" in goal_lower:
            final_ordered_sequence.append("summary")

        # Remove duplicates if keywords are too general / overlap, maintaining order
        unique_sequence = []
        for agent_key in final_ordered_sequence:
            if agent_key not in unique_sequence:
                unique_sequence.append(agent_key)

        return unique_sequence


    def execute_plan(self, goal: str, available_agents: dict) -> dict:
        """
        Executes the plan based on the parsed goal by calling agents in sequence.

        Args:
            goal: The user's natural language goal.
            available_agents: A dictionary mapping agent identifiers (strings)
                              to agent instances (e.g., {'spacex': SpaceXAgent(), ...}).

        Returns:
            A dictionary containing the accumulated data after all agents
            in the plan have executed.
        """
        print(f"Planner received goal: '{goal}'")

        agent_sequence = self.parse_goal(goal)
        if not agent_sequence:
            print("Planner: Could not determine any agents for the goal.")
            return {"status": "error", "message": "No agents identified for the goal."}

        print(f"Planner determined agent sequence: {agent_sequence}")

        current_data = {}  # Initialize data accumulator

        for agent_key in agent_sequence:
            agent_instance = available_agents.get(agent_key)
            if not agent_instance:
                print(f"Planner Error: Agent '{agent_key}' not found in available_agents.")
                # Decide: stop, or skip and continue? For now, let's record error and stop.
                current_data["planner_error"] = f"Agent '{agent_key}' not found."
                current_data["status"] = "error"
                return current_data

            print(f"Planner: Executing agent '{agent_key}'...")
            try:
                # Each agent's execute method should handle its own errors gracefully
                # and return the updated data dictionary.
                current_data = agent_instance.execute(current_data)
                # Optionally, check agent-specific status if agents add it
                agent_status_key = f"{agent_key}_agent_status"
                if current_data.get(agent_status_key) == "Error":
                    print(f"Planner: Agent '{agent_key}' reported an error. Halting plan.")
                    # The error message should be within current_data from the agent itself.
                    current_data["status"] = f"error_in_{agent_key}_agent"
                    return current_data

            except Exception as e:
                print(f"Planner Error: An unexpected error occurred while executing agent '{agent_key}': {e}")
                current_data["planner_error"] = f"Unexpected error during {agent_key} execution: {str(e)}"
                current_data["status"] = "error"
                return current_data

            print(f"Planner: Agent '{agent_key}' execution complete.")
            # print(f"Planner: Current data after {agent_key}: {current_data}") # For debugging

        print("Planner: All agents executed successfully.")
        current_data["status"] = "success"
        return current_data

if __name__ == '__main__':
    # This is a placeholder for testing.
    # To test planner.py directly, we'd need mock agents.
    # The actual test will be done via main.py with real agents.

    class MockAgent:
        def __init__(self, name):
            self.name = name
        def execute(self, data):
            print(f"MockAgent '{self.name}' executing with data: {data}")
            data[f"{self.name}_data"] = f"results from {self.name}"
            data[f"{self.name}_agent_status"] = "Success"
            return data

    planner = Planner()

    # Test parse_goal
    goal1 = "Find the next SpaceX launch, check weather at that location, then summarize if it may be delayed."
    sequence1 = planner.parse_goal(goal1)
    print(f"Goal 1: '{goal1}' -> Parsed sequence: {sequence1}") # Expected: ['spacex', 'weather', 'summary']

    goal2 = "What's the weather like and summarize the situation?"
    sequence2 = planner.parse_goal(goal2)
    print(f"Goal 2: '{goal2}' -> Parsed sequence: {sequence2}") # Expected: ['weather', 'summary']

    goal3 = "Tell me about the next spacex launch."
    sequence3 = planner.parse_goal(goal3)
    print(f"Goal 3: '{goal3}' -> Parsed sequence: {sequence3}") # Expected: ['spacex']

    goal4 = "Summarize the launch status." # Assumes prior context, or needs specific agent
    sequence4 = planner.parse_goal(goal4)
    print(f"Goal 4: '{goal4}' -> Parsed sequence: {sequence4}") # Expected: ['summary']

    goal5 = "Just give me a summary."
    sequence5 = planner.parse_goal(goal5)
    print(f"Goal 5: '{goal5}' -> Parsed sequence: {sequence5}") # Expected: ['summary']

    goal_unknown = "Book a flight."
    sequence_unknown = planner.parse_goal(goal_unknown)
    print(f"Goal Unknown: '{goal_unknown}' -> Parsed sequence: {sequence_unknown}") # Expected: []

    # Test execute_plan with mock agents
    mock_agents = {
        "spacex": MockAgent("spacex"),
        "weather": MockAgent("weather"),
        "summary": MockAgent("summary")
    }

    print("\nTesting execute_plan with Goal 1:")
    final_data1 = planner.execute_plan(goal1, mock_agents)
    print(f"Final data for Goal 1: {final_data1}")

    print("\nTesting execute_plan with Goal 2 (spacex agent missing from available):")
    # final_data2 = planner.execute_plan(goal2, {"weather": MockAgent("weather"), "summary": MockAgent("summary")})
    # print(f"Final data for Goal 2: {final_data2}")

    print("\nTesting execute_plan with Goal 2 (all mock agents available):")
    final_data_goal2_all_mocks = planner.execute_plan(goal2, mock_agents)
    print(f"Final data for Goal 2 with all mocks: {final_data_goal2_all_mocks}")


    print("\nTesting execute_plan with unknown goal:")
    final_data_unknown = planner.execute_plan(goal_unknown, mock_agents)
    print(f"Final data for unknown goal: {final_data_unknown}")

    class FailingMockAgent:
        def __init__(self, name):
            self.name = name
        def execute(self, data):
            print(f"FailingMockAgent '{self.name}' executing, will report error.")
            data[f"{self.name}_agent_status"] = "Error"
            data[f"{self.name}_error_message"] = "Mock failure"
            return data

    mock_agents_with_failure = {
        "spacex": MockAgent("spacex"),
        "weather": FailingMockAgent("weather"), # Weather agent will fail
        "summary": MockAgent("summary")
    }
    print("\nTesting execute_plan with a failing agent (weather):")
    final_data_failure = planner.execute_plan(goal1, mock_agents_with_failure)
    print(f"Final data with failing agent: {final_data_failure}")

```
