import os
from dotenv import load_dotenv

# Load environment variables from .env file (optional)
load_dotenv()

# Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini model config
GEMINI_MODEL_NAME = "gemini-2.0-flash"
MAX_TOKENS = 4096

# Chunk config
CHUNK_FOLDER = "data/pdf_chunks"
NUM_SUBMODELS = 6
CHUNKS_PER_MODEL = 4
