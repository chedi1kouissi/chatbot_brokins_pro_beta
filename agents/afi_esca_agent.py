# -*- coding: utf-8 -*-
import os
import logging
from typing import Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor

import google.generativeai as genai

from .base_interface import BaseInsurerAgent
from config import INSURER_AGENT_MODEL, GEMINI_API_KEY
from prompt import INSURER_AGENT_PROMPT

C_CYAN = '\033[96m'
C_END = '\033[0m'

class AfiEscaAgent(BaseInsurerAgent):
    """Agent specialized in handling Afi-Esca insurance contracts."""

    def __init__(self, file_path: str):
        """Initializes the agent with its contract file path."""
        super().__init__(insurer_name="afi-esca", model_name=INSURER_AGENT_MODEL)
        self.file_path = file_path
        self._contract_text = None
        self.executor = ThreadPoolExecutor(max_workers=1)

    def load_contract(self) -> str:
        """Loads the Afi-Esca contract text from the corresponding data file."""
        if self._contract_text is None:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._contract_text = f.read()
            except FileNotFoundError:
                logging.error(f"Contract file not found for {self.insurer_name} at {self.file_path}")
                self._contract_text = "Le fichier de contrat est introuvable."
        return self._contract_text

    def _sync_get_snippet(self, question: str) -> Dict[str, any]:
        """
        Analyzes the contract synchronously to find a relevant snippet.
        """
        contract_text = self.load_contract()
        prompt = INSURER_AGENT_PROMPT.format(
            insurer_name=self.insurer_name.upper(),
            contract_text=contract_text,
            question=question,
        )

        try:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            snippet = response.text.strip()
            logging.info(f"[Agent/{self.insurer_name.upper()}] Snippet found: '{snippet[:100]}...'")
            
            can_answer = snippet != "AUCUNE INFORMATION PERTINENTE"
            
            return {
                "insurer": self.insurer_name,
                "can_answer": can_answer,
                "snippet": f"Pour {self.insurer_name.upper()} : {snippet}" if can_answer else "Aucune information pertinente trouvée.",
            }
        except Exception as e:
            logging.error(f"[Agent/{self.insurer_name.upper()}] Error during snippet generation: {e}")
            return {
                "insurer": self.insurer_name,
                "can_answer": False,
                "snippet": f"Une erreur est survenue lors de l'analyse du contrat {self.insurer_name.upper()}.",
            }

    async def get_snippet(self, question: str) -> Dict[str, any]:
        """
        Analyzes the contract to find a relevant snippet for the user's question,
        using a thread pool to run the synchronous analysis.
        """
        logging.info(f"{C_CYAN}[Agent] Running {self.insurer_name.upper()}...{C_END}")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._sync_get_snippet, question)
