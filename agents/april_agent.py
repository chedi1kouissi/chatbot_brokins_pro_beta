# agents/april_agent.py
# -*- coding: utf-8 -*-
import os
import logging
from typing import Dict, List
import asyncio
from concurrent.futures import ThreadPoolExecutor

from agents.base_interface import BaseInsurerAgent
import google.generativeai as genai
from prompt import INSURER_AGENT_PROMPT
from config import INSURER_AGENT_MODEL, GEMINI_API_KEY, INSURER_AGENTS

C_CYAN = '\033[96m'
C_END = '\033[0m'

class AprilAgent(BaseInsurerAgent):
    """
    Agent for April, handling two contract files separately and running analysis in parallel.
    """

    def __init__(self, file_paths: List[str]):
        """Initializes the agent with its contract file paths."""
        super().__init__(insurer_name="april", model_name=INSURER_AGENT_MODEL)
        self.file_paths = file_paths
        self._contract_chunks = None
        # Use a thread pool to run sync calls in an async context
        self.executor = ThreadPoolExecutor(max_workers=2)

    def load_contract(self) -> str:
        """
        Loads and concatenates both April contract texts.
        This method is implemented to satisfy the abstract base class. The core
        logic in `get_snippet` handles the files as separate chunks for parallel processing.
        """
        full_text = []
        for path in self.file_paths:
            full_text.append(self._load_chunk(path))
        return "\n\n--- SEPARATE DOCUMENT ---\n\n".join(full_text)

    def _load_chunk(self, file_path: str) -> str:
        """Loads a single contract file (chunk)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logging.error(f"Contract file not found for April at {file_path}")
            return f"Le fichier de contrat est introuvable: {os.path.basename(file_path)}"
        except Exception as e:
            return f"Erreur de lecture du document {os.path.basename(file_path)}: {e}"

    def _sync_analyze_chunk(self, question: str, contract_text: str, source_name: str) -> str:
        """Analyzes a single contract chunk synchronously."""
        prompt = INSURER_AGENT_PROMPT.format(
            insurer_name=f"{self.insurer_name.upper()} ({source_name})",
            contract_text=contract_text,
            question=question
        )
        logging.info(f"[Agent/APRIL] Analyzing chunk: {source_name}")
        try:
            # Re-configure for the new thread
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt) # Sync call
            snippet = response.text.strip()
            logging.info(f"[Agent/APRIL/{source_name}] Snippet found: '{snippet[:100]}...'")
            return snippet
        except Exception as e:
            logging.error(f"Error getting snippet from Gemini for chunk {source_name}: {e}")
            return "Erreur lors de l'analyse du document."

    async def get_snippet(self, question: str) -> dict:
        """
        Loads contract chunks, analyzes them in parallel using a thread pool, and combines the results.
        """
        logging.info(f"{C_CYAN}[Agent] Running {self.insurer_name.upper()} (in parallel)...{C_END}")
        contract_chunks = {
            os.path.basename(path): self._load_chunk(path) for path in self.file_paths
        }

        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(self.executor, self._sync_analyze_chunk, question, text, name)
            for name, text in contract_chunks.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)

        snippets = []
        for result, name in zip(results, contract_chunks.keys()):
            if isinstance(result, Exception):
                logging.error(f"Error processing future for {name}: {result}")
                snippets.append(f"Source ({name}): Erreur d'analyse.")
            elif "AUCUNE INFORMATION PERTINENTE" not in result:
                snippets.append(f"Source ({name}): {result}")

        if not snippets:
            final_snippet = "Aucune information pertinente trouvée dans les documents April."
            can_answer = False
        else:
            final_snippet = "\n".join(snippets)
            can_answer = True

        return {
            "insurer": self.insurer_name,
            "can_answer": can_answer,
            "snippet": f"Pour {self.insurer_name.upper()}:\n{final_snippet}" if can_answer else final_snippet,
        }