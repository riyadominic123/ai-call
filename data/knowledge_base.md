# AI Call Agent - Knowledge Base

## Project Overview
This document contains the core information for the AI Voice Agent. The agent is designed to handle voice calls, understand user queries, retrieve relevant information from this knowledge base, and respond in a synthesized voice. It's a modular, locally-run system built for flexibility and privacy.

## Core Technologies
The agent is built using a stack of modern, open-source tools:
- **Speech-to-Text (STT):** Faster Whisper for high-performance, local transcription.
- **Language Model (LLM):** Phi-2 or LLaMA 3B, running locally via `llama.cpp` for efficient inference.
- **Retrieval-Augmented Generation (RAG):** LangChain and FAISS are used to create a vector index of this knowledge base, allowing the LLM to answer questions with specific, up-to-date information.
- **Text-to-Speech (TTS):** Coqui TTS or Piper for generating natural-sounding speech from the LLM's text response.
- **Backend:** A FastAPI server provides the API endpoints to connect all components.
- **VoIP Integration:** Twilio is used to handle the telephone call layer, connecting users to the agent.

## Key Features
- **Voice Interaction:** End-to-end voice communication.
- **Knowledge Retrieval:** Can answer specific questions based on the content in this file.
- **Local First:** All core AI models (STT, LLM, TTS) run on local hardware, ensuring data privacy.
- **Modular Design:** Each component (STT, LLM, etc.) is a separate module, making it easy to swap, upgrade, or debug.

## How to Interact
- Speak clearly when the agent is listening.
- You can ask about the project's features, the technologies it uses, or its overall purpose.
- Example questions:
  - "Tell me about the technologies used in this project."
  - "How does the speech-to-text work?"
  - "What is the purpose of the RAG system?"
