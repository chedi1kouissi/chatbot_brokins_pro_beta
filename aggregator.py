# -*- coding: utf-8 -*-
import logging
import google.generativeai as genai
from typing import List, Dict

from config import AGGREGATOR_MODEL
from prompt import AGGREGATOR_PROMPT

# ANSI escape codes for colors
C_YELLOW = '\033[93m'
C_GREEN = '\033[92m'
C_END = '\033[0m'

class Aggregator:
    """
    Aggregates and synthesizes responses from multiple insurance agents.
    """

    def __init__(self):
        """Initialize the Aggregator."""
        pass

    def _format_snippets(self, snippets: List[Dict]) -> str:
        """
        Formats the snippets from different agents into a structured string.

        Args:
            snippets: A list of structured responses from the agents.

        Returns:
            A formatted string of all snippets.
        """
        formatted_snippets = []
        for snippet in snippets:
            insurer = snippet.get("insurer", "Unknown").upper()
            if snippet.get("can_answer"):
                content = snippet.get("snippet", "No snippet provided.")
                formatted_snippets.append(f"--- Information de {insurer} ---\n{content}\n")
            else:
                formatted_snippets.append(
                    f"--- Information de {insurer} ---\n"
                    "Cet assureur n'a pas trouvé d'information pertinente.\n"
                )
        return "\n".join(formatted_snippets)

    async def synthesize(self, question: str, snippets: List[Dict]) -> str:
        """
        Synthesizes a final response from multiple agent snippets using the Gemini API.

        Args:
            question: The original user question.
            snippets: A list of structured responses from the agents.

        Returns:
            A synthesized, professional response in French.
        """
        logging.info(f"{C_YELLOW}[Aggregator] Synthesizing answer...{C_END}")
        logging.info(f"[Aggregator] Received {len(snippets)} snippets for question: '{question}'")

        if not any(s.get("can_answer") for s in snippets):
            logging.warning("[Aggregator] No snippets contained a valid answer.")
            return "Désolé, aucun de nos assureurs partenaires n'a pu fournir d'information pertinente pour répondre à votre question."

        formatted_snippets = self._format_snippets(snippets)
        prompt = AGGREGATOR_PROMPT.format(
            question=question, snippets=formatted_snippets
        )
        logging.info(f"[Aggregator] Prompt: {prompt[:300]}...") # Log first 300 chars

        try:
            model = genai.GenerativeModel(AGGREGATOR_MODEL) # Create model inside the async method
            response = await model.generate_content_async(prompt)
            final_answer = response.text.strip()
            logging.info(f"{C_GREEN}[Aggregator] Synthesis successful.{C_END}")
            return final_answer
        except Exception as e:
            logging.error(f"[Aggregator] Error during synthesis: {e}. Falling back to simple aggregation.")
            return self._simple_aggregation(snippets)

    def _simple_aggregation(self, snippets: List[Dict]) -> str:
        """
        Provides a simple fallback aggregation if the synthesis model fails.

        Args:
            snippets: A list of structured responses from the agents.

        Returns:
            A simple concatenated response.
        """
        relevant_snippets = [s for s in snippets if s.get("can_answer")]
        
        if not relevant_snippets:
            return "Désolé, aucune information pertinente n'a pu être extraite."

        responses = [s.get("snippet", "") for s in relevant_snippets]
        return "\n\n".join(responses)