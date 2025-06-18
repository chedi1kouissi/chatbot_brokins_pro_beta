# agents/brokins_agent.py
# -*- coding: utf-8 -*-
import os
import logging
from typing import Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor

import google.generativeai as genai

from .base_interface import BaseInsurerAgent
from config import INSURER_AGENT_MODEL, GEMINI_API_KEY
from prompt import BROKINS_AGENT_PROMPT

C_CYAN = '\033[96m'
C_END = '\033[0m'

class BrokinsAgent(BaseInsurerAgent):
    """Agent specialized in answering questions about the Brokins company."""

    def __init__(self, file_path: str):
        """Initializes the agent with its data file path."""
        super().__init__(insurer_name="brokins", model_name=INSURER_AGENT_MODEL)
        self.file_path = file_path
        self._company_info = None
        self.executor = ThreadPoolExecutor(max_workers=1)

    def load_contract(self) -> str:
        """Loads the Brokins company information from the data file."""
        if self._company_info is None:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._company_info = f.read()
            except FileNotFoundError:
                logging.error(f"Data file not found for {self.insurer_name} at {self.file_path}")
                self._company_info = "Le fichier d'information sur Brokins est introuvable."
        return self._company_info

    def _sync_get_snippet(self, question: str) -> str:
        """
        Analyzes the company info synchronously to generate a direct answer.
        """
        company_info = self.load_contract()
        prompt = BROKINS_AGENT_PROMPT.format(
            contract_text=company_info,
            question=question,
        )

        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            answer = response.text.strip()
            logging.info(f"[Agent/{self.insurer_name.upper()}] Answer generated: '{answer[:100]}...'")
            return answer
        except Exception as e:
            logging.error(f"[Agent/{self.insurer_name.upper()}] Error during answer generation: {e}")
            return f"Une erreur est survenue lors de la génération de la réponse pour {self.insurer_name.upper()}."

    async def get_snippet(self, question: str) -> Dict[str, any]:
        """
        Generates a direct answer to the user's question about Brokins,
        using a thread pool to run the synchronous analysis.
        The returned snippet is the full, direct answer.
        """
        logging.info(f"{C_CYAN}[Agent] Running {self.insurer_name.upper()}...{C_END}")
        loop = asyncio.get_event_loop()
        # The result of _sync_get_snippet is the final answer string
        final_answer = await loop.run_in_executor(self.executor, self._sync_get_snippet, question)
        
        return {
            "insurer": self.insurer_name,
            "can_answer": True,
            "snippet": final_answer,
        }
