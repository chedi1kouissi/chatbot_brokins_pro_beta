from flask import Flask, render_template, request, jsonify
from flask_session import Session
import logging
import os

from app.gemini_router import get_answer_from_gemini

# --- Setup ---
app = Flask(__name__)
app.config.update(
    SESSION_TYPE="filesystem",
    SECRET_KEY=os.urandom(24),
    TEMPLATES_AUTO_RELOAD=True,
)
Session(app)

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Routes ---
@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/ask_question/", methods=["POST"])
def ask_question():
    try:
        question = request.form.get("question", "").strip()
        logger.info(f"📨 Question: {question}")

        if not question:
            return jsonify({"response": "Veuillez entrer une question."})

        answer = get_answer_from_gemini(question)
        return jsonify({"response": answer})
    except Exception as e:
        logger.error(f"❌ Erreur : {e}")
        return jsonify({"error": str(e)}), 500

# --- Run server ---
if __name__ == "__main__":
    app.run(debug=True)
