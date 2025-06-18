# -*- coding: utf-8 -*-
import os
import asyncio
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

import google.generativeai as genai

from config import GEMINI_API_KEY
from prompt import GREETING_RESPONSE, OFF_TOPIC_RESPONSE
from router import Router
from agents.all_insurers_agent import AllInsurersAgent
from aggregator import Aggregator

# --- Pre-init ---

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# --- App Initialization ---
# Centralized check for API key
if not GEMINI_API_KEY:
    raise ValueError("FATAL: GEMINI_API_KEY environment variable is not set.")
genai.configure(api_key=GEMINI_API_KEY)

# Instantiate core components
router = Router()
all_insurers_agent = AllInsurersAgent()
aggregator = Aggregator()
# --- End Initialization ---


@app.route('/')
def index():
    """Serves the frontend chat interface."""
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    """Main endpoint to receive and process user questions."""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415

    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    def run_async_task():
        """Creates and manages a new event loop for the async task."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Run the async handler and get the result
            result = loop.run_until_complete(handle_request_async(question))
            return result
        finally:
            # Ensure the loop is closed
            loop.close()

    try:
        answer = run_async_task()
        return jsonify({"answer": answer})

    except Exception as e:
        logging.error(f"An unexpected error occurred in /ask endpoint: {e}", exc_info=True)
        return jsonify({"error": "Une erreur interne est survenue. Veuillez réessayer."}), 500


async def handle_request_async(question: str):
    """Handles the actual logic of the request asynchronously."""
    # 1. Classify the user's question
    route = await router.classify_question(question)
    route_type = route.get('type')

    # 2. Handle simple cases directly
    if route_type == 'greeting':
        return GREETING_RESPONSE
    if route_type == 'off_topic':
        return OFF_TOPIC_RESPONSE
    
    # Handle Brokins inquiry by calling the dedicated agent and returning its response directly
    if route_type == 'brokins_inquiry':
        brokins_snippets = await all_insurers_agent.get_snippets(question, agent_names=['brokins'])
        if brokins_snippets and brokins_snippets[0].get("can_answer"):
            return brokins_snippets[0]['snippet']
        else:
            return "Désolé, je n'ai pas pu récupérer les informations sur Brokins pour le moment."

    # 3. For insurance queries, run the appropriate agent(s)
    snippets = []
    if route_type == 'specific_inquiry':
        target_insurers = route.get('insurers', [])
        if target_insurers:
            snippets = await all_insurers_agent.get_snippets(question, agent_names=target_insurers)
    
    elif route_type == 'general_inquiry':
        snippets = await all_insurers_agent.get_snippets(question)

    if not snippets:
        return "Désolé, aucun agent n'a pu traiter votre demande ou trouver une information."

    # 4. Aggregate the results into a final, synthesized answer
    final_answer = await aggregator.synthesize(question, snippets)
    
    return final_answer


if __name__ == '__main__':
    # For production, use a production-ready WSGI server like Gunicorn or Waitress
    logging.info("Starting Flask application...")
    app.run(debug=True, port=5000)