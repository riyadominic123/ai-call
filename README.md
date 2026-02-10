# 🚀 Update: Dynamic TTS Output Length (v2025-07-22)

**🧠 How does the agent work?**
- 📞 On each call, the first AI voice response is limited to **200 characters** for a concise intro.
- 🔄 All following responses in the same call are limited to **100 characters** each.
- ⏱️ This prevents long (1.5+ minute) TTS outputs and Twilio timeouts.
- ⚙️ You can easily change these limits in `app/main.py` (`max_tts_length`).

**❓ Why?**
- 🗣️ Previously, long LLM outputs caused TTS to generate very long audio, leading to Twilio timeouts and failed calls.
- ✅ With this update, the system is robust, responsive, and Twilio-friendly by default.

---

# 🤖 AI Call Agent

This is a modular local AI Call Agent built using FastAPI, Faster Whisper, Llama.cpp (for LLM), LangChain, FAISS, Coqui TTS, and Twilio.

## 🗂️ Project Structure

```
ai-agent-voice/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entrypoint
│   ├── stt.py               # Speech-to-text
│   ├── tts.py               # Text-to-speech
│   ├── llm.py               # LLM wrapper
│   ├── vector_search.py     # RAG/FAISS logic
│   ├── agent.py             # LangChain agent logic (Placeholder for future use)
│   └── config.py            # Central config
├── data/
│   └── knowledge_base.md    # Your course info
├── embeddings/
│   └── chroma_db/           # Vector index
├── models/
│   └── phi-2.gguf           # or llama-3b.gguf
├── logs/
│   └── agent.log
├── requirements.txt
├── run.sh                   # Launch script
└── README.md
```

## ⚡ Setup and Running Instructions

Follow these steps to set up and run the AI Call Agent:

### 1️⃣ Clone the Repository (if not already done)

```bash
git clone <repository_url>
cd ai-agent-voice
```

### 2️⃣ Python Environment Setup

Ensure you have Python 3.9+ installed. Create and activate a virtual environment:

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4️⃣ Download LLM Model

Ensure your chosen LLM model (e.g., `phi-2.gguf`) is placed in the `models/` directory. You can download it from Hugging Face or similar sources.

### 5️⃣ Build RAG Knowledge Base Index

This step processes your `data/knowledge_base.md` and creates a vector index. This might take some time as it downloads the embedding model.

```bash
python -m app.vector_search
```

### 6️⃣ Run the FastAPI Application

To start the FastAPI server, use the `run.sh` script (or `run.ps1` on Windows):

```bash
# On Windows (PowerShell):
.\run.ps1

# On macOS/Linux:
./run.sh
```

**💡 Manual Execution (Windows):**
If you prefer to run the commands manually in PowerShell or Command Prompt:
1. Activate the environment: `.venv\Scripts\activate`
2. Run the server: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

The application will typically run on `http://0.0.0.0:8000`. You can access the FastAPI documentation at `http://localhost:8000/docs`.

### 7️⃣ Twilio Integration (for Voice Calls)

For Twilio integration, you will need to:

- 🌐 **Expose your local server:** Use `ngrok` or a similar tool to expose your local FastAPI server to the internet. For example:
    ```bash
    ngrok http 8000
    ```
    This will give you a public URL (e.g., `https://your-ngrok-url.ngrok-free.app`).
- 🔗 **Configure Twilio Webhook:** In your Twilio phone number's configuration, set the Voice & Fax webhook URL to `https://your-ngrok-url.ngrok-free.app/twilio_voice` (replace `your-ngrok-url.ngrok-free.app` with your actual ngrok URL).
- 📝 **Update Configuration:** You no longer need to edit `app/main.py`. Just update your `NGROK_URL` in the `.env` file.

## 🔑 Environment Variables (.env)

Create a `.env` file in the project root with the following content (do NOT commit this file):

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NGROK_URL=https://your-ngrok-url.ngrok-free.app
```

You can copy the template from `.env.example`.

## ⚠️ Security Notice
- **Never commit your real Twilio credentials, API keys, or model files to the repository.**
- The `.gitignore` file is set up to exclude sensitive and large files.

## 📝 Logging

Application logs will be stored in `logs/agent.log`.
