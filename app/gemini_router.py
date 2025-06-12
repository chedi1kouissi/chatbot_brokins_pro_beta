import os
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
from app.config import GEMINI_API_KEY, GEMINI_MODEL_NAME, CHUNK_FOLDER, NUM_SUBMODELS
from app.prompts import (
    SUBMODEL_PROMPT,
    FINAL_MODEL_PROMPT,
    format_submodel_input,
    format_final_model_input,
)

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)

# Load submodel and final model with system instructions
sub_model = genai.GenerativeModel(
    "gemini-2.5-flash-preview-04-17",
    system_instruction=SUBMODEL_PROMPT
)
final_model = genai.GenerativeModel(
    "gemini-2.0-flash",
    system_instruction=FINAL_MODEL_PROMPT
)

# Load all chunk texts
def load_chunks():
    chunks = []
    files = sorted(os.listdir(CHUNK_FOLDER))
    for file in files:
        with open(os.path.join(CHUNK_FOLDER, file), "r", encoding="utf-8") as f:
            chunks.append(f.read())
    return chunks

# Submodel task: handle a chunk and return relevant extract
def run_submodel_on_chunk(chunk_text, question):
    prompt = format_submodel_input(chunk_text, question)
    try:
        response = sub_model.generate_content(
            prompt,
            generation_config={"temperature": 0.6, "max_output_tokens": 1024}
        )
        return response.text.strip()
    except Exception as e:
        return f"❌ ERREUR: {e}"

# Final model call
def run_final_model(extracts, question):
    final_input = format_final_model_input(extracts, question)
    try:
        response = final_model.generate_content(
            final_input,
            generation_config={"temperature": 0.5, "max_output_tokens": 2048}
        )
        return response.text.strip()
    except Exception as e:
        return f"❌ ERREUR (final model): {e}"

# Orchestration logic
def get_answer_from_gemini(question):
    chunks = load_chunks()
    print(f"🔍 Loaded {len(chunks)} chunks.")

    # Run sub-models in parallel
    with ThreadPoolExecutor(max_workers=NUM_SUBMODELS) as executor:
        futures = [executor.submit(run_submodel_on_chunk, chunk, question) for chunk in chunks]
        results = [f.result() for f in futures]

    # Filter relevant outputs
    relevant_extracts = [res for res in results if "AUCUNE INFORMATION PERTINENTE" not in res.upper() and not res.startswith("❌")]

    print(f"✅ {len(relevant_extracts)} submodels returned relevant info.")
    return run_final_model(relevant_extracts, question)