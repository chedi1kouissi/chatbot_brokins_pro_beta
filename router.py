# -*- coding: utf-8 -*-
import json
import logging
from typing import Dict, List, Union

import google.generativeai as genai

from config import ROUTER_MODEL, INSURER_AGENTS
from prompt import ROUTER_PROMPT

# ANSI escape codes for colors
C_BLUE = '\033[94m'
C_GREEN = '\033[92m'
C_END = '\033[0m'

class Router:
    """Routes user questions to appropriate insurance agents using Gemini Flash."""

    def __init__(self):
        """Initializes the Router with the list of insurer names."""
        self.insurer_names = list(INSURER_AGENTS.keys())

    async def classify_question(self, question: str) -> Dict[str, Union[str, List[str]]]:
        """
        Classifies the user's question using the Gemini API.

        Args:
            question (str): The user's question in French.

        Returns:
            A dictionary containing the classification type and target insurers.
        """
        model = genai.GenerativeModel(ROUTER_MODEL)
        prompt = ROUTER_PROMPT.format(
            insurer_names=self.insurer_names, question=question
        )
        logging.info(f"{C_BLUE}[Router] Classifying question...{C_END}")
        logging.info(f"[Router] Prompt: {prompt[:200]}...") # Log first 200 chars

        try:
            response = await model.generate_content_async(prompt)
            # Clean up the response to ensure it's valid JSON
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            route = json.loads(cleaned_response)

            logging.info(f"{C_GREEN}[Router] Classification successful: {route}{C_END}")

            # Basic validation of the returned structure
            if 'type' not in route or 'insurers' not in route:
                raise ValueError("Invalid format from router model")
            
            return route

        except Exception as e:
            logging.error(f"[Router] Error during classification: {e}")
            return {"type": "general_inquiry", "insurers": []}