import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- General Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Model Configuration ---
ROUTER_MODEL = "gemini-2.5-flash-preview-05-20"
AGGREGATOR_MODEL = "gemini-2.5-flash-preview-05-20"
INSURER_AGENT_MODEL = "gemini-2.5-pro-preview-05-06"

# --- File Paths ---
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# --- Agent Configuration ---
# Maps insurer names (keys) to their respective agent classes and contract files.
# This is the central registry for all insurer agents in the system.
INSURER_AGENTS = {
    "cardif": {
        "agent_class": "CardifAgent",
        "file_path": os.path.join(DATA_DIR, "cardif.txt")
    },
    "generali": {
        "agent_class": "GeneraliAgent",
        "file_path": os.path.join(DATA_DIR, "generali.txt")
    },
    "april": {
        "agent_class": "AprilAgent",
        "file_paths": [
            os.path.join(DATA_DIR, "april1.txt"),
            os.path.join(DATA_DIR, "april2.txt")
        ]
    },
    "afi-esca": {
        "agent_class": "AFIESCAAgent",
        "file_path": os.path.join(DATA_DIR, "afi-esca.txt")
    },
    "apicil": {
        "agent_class": "ApicilAgent",
        "file_path": os.path.join(DATA_DIR, "apicil.txt")
    },
    "apivia": {
        "agent_class": "ApiviaAgent",
        "file_path": os.path.join(DATA_DIR, "apivia.txt")
    },
    "harmonie": {
        "agent_class": "HarmonieAgent",
        "file_path": os.path.join(DATA_DIR, "harmonie.txt")
    },
    "metlife": {
        "agent_class": "MetLifeAgent",
        "file_path": os.path.join(DATA_DIR, "metlife.txt")
    },
    "utwin": {
        "agent_class": "UTwinAgent",
        "file_path": os.path.join(DATA_DIR, "utwin.txt")
    },
    "zenioo-mncap": {
        "agent_class": "ZeniooMncapAgent",
        "file_path": os.path.join(DATA_DIR, "zenioo-mncap.txt")
    },
    "brokins": {
        "agent_class": "BrokinsAgent",
        "file_path": os.path.join(DATA_DIR, "brokins.txt")
    }
}
