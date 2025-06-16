from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system.
    Each agent is responsible for a specific task and enriches the data
    it receives.
    """

    @abstractmethod
    def execute(self, data: dict) -> dict:
        """
        Executes the agent's task.

        Args:
            data: A dictionary containing data from previous agents or initial input.

        Returns:
            A dictionary containing the original data enriched with the results
            of this agent's task.
        """
        pass
