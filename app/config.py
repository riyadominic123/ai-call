import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "data", "knowledge_base.md")
CHROMA_DB_PATH = os.path.join(BASE_DIR, "embeddings", "chroma_db")
MODEL_DIR = os.path.join(BASE_DIR, "models")
PHI2_MODEL_PATH = os.path.join(MODEL_DIR, "phi-2.Q4_K_M.gguf")
LLAMA3B_MODEL_PATH = os.path.join(MODEL_DIR, "llama-3b.gguf")

AUDIO_UPLOAD_DIR = os.path.join(BASE_DIR, "audio_uploads")
AUDIO_OUTPUT_DIR = os.path.join(BASE_DIR, "audio_output")

# Twilio Credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
NGROK_URL = os.getenv("NGROK_URL", "https://your-ngrok-url.ngrok-free.app")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
YOUR_PHONE_NUMBER = os.getenv("YOUR_PHONE_NUMBER")

# Ensure directories exist
for d in [AUDIO_UPLOAD_DIR, AUDIO_OUTPUT_DIR]:
    os.makedirs(d, exist_ok=True)
