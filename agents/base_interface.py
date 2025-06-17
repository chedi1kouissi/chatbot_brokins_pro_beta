# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod

class BaseInsurerAgent(ABC):
    """Abstract base class for all insurer-specific agents."""

    def __init__(self, insurer_name: str, model_name: str):
        """
        Initializes the agent.

        Args:
            insurer_name (str): The name of the insurer (e.g., 'Cardif').
            model_name (str): The Gemini model to use for analysis.
        """
        self.insurer_name = insurer_name
        self.model_name = model_name

    @abstractmethod
    def load_contract(self) -> str:
        """Loads the contract text from the corresponding file(s)."""
        pass

    @abstractmethod
    async def get_snippet(self, question: str) -> dict:
        """
        Analyzes the contract to find a relevant snippet for the user's question.

        Args:
            question (str): The user's question.

        Returns:
            dict: A dictionary containing insurer, can_answer, and snippet.
        """
        pass
