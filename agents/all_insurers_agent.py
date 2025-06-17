# -*- coding: utf-8 -*-
import asyncio
import importlib
from typing import List, Dict

from config import INSURER_AGENTS
from agents.base_interface import BaseInsurerAgent


class AllInsurersAgent:
    """
    Coordinates parallel execution of multiple insurer agents.
    """

    def __init__(self):
        """Dynamically loads and instantiates all registered agents."""
        self.agents = self._load_agents()

    def _load_agents(self) -> List[BaseInsurerAgent]:
        """
        Dynamically imports and instantiates agent classes based on config.
        """
        loaded_agents = []
        for name, config in INSURER_AGENTS.items():
            try:
                module_name = f"agents.{name.replace('-', '_')}_agent"
                class_name = config['agent_class']
                module = importlib.import_module(module_name)
                agent_class = getattr(module, class_name)

                # Pass file paths from config to agent constructor
                if 'file_paths' in config:  # For agents with multiple files (e.g., April)
                    instance = agent_class(file_paths=config['file_paths'])
                elif 'file_path' in config:  # For standard agents with a single file
                    instance = agent_class(file_path=config['file_path'])
                else:
                    raise ValueError(f"Configuration for agent '{name}' is missing 'file_path' or 'file_paths'.")

                loaded_agents.append(instance)
                print(f"Successfully loaded agent: {class_name}")

            except (ImportError, AttributeError, KeyError, ValueError) as e:
                print(f"Critical error loading agent '{name}': {e}")
        
        return loaded_agents

    async def get_snippets(self, question: str, agent_names: List[str] = None) -> List[Dict]:
        """
        Runs the specified insurer agents in parallel to get snippets.

        If no agent_names are provided, runs all loaded agents.

        Args:
            question: The user's question.
            agent_names: A list of specific agent names (e.g., ['cardif', 'generali']) to run.

        Returns:
            A list of structured responses from the agents.
        """
        if agent_names:
            # Filter agents to run based on the provided names
            agents_to_run = [
                agent for agent in self.agents if agent.insurer_name in agent_names
            ]
        else:
            # Use all loaded agents
            agents_to_run = self.agents

        if not agents_to_run:
            print("Warning: No agents were selected to run for the question.")
            return []

        # Create async tasks for all selected agents
        tasks = [agent.get_snippet(question) for agent in agents_to_run]
        
        # Execute all tasks in parallel and return results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_results = [res for res in results if not isinstance(res, Exception)]
        if len(valid_results) != len(results):
            print(f"Warning: {len(results) - len(valid_results)} agent(s) failed during execution.")
        
        return valid_results