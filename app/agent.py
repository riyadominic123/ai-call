import httpx
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

from app.config import CHROMA_DB_PATH

# Ollama API configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "travel-ai-fast:latest"

# Load the embeddings model
try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
except Exception as e:
    print(f"Error loading embeddings model for RAG: {e}")
    embeddings = None

# Load the Chroma vector store
try:
    vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
except Exception as e:
    print(f"Error loading Chroma vector store: {e}")
    vectorstore = None
    retriever = None

# System prompt for the feedback caller
SYSTEM_PROMPT = """You are a friendly travel feedback caller from Paradise Holidays. 
Use the trip details below to personalize your conversation. 
Keep your response to 1-2 short sentences, suitable for a phone call."""


def warm_up_ollama():
    """
    Sends a dummy request to Ollama to pre-load the model into GPU memory.
    This eliminates the cold start delay on the first real request.
    """
    try:
        print(f"Warming up Ollama model '{OLLAMA_MODEL}'...")
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": "Hello",
                    "stream": False,
                    "options": {
                        "num_predict": 1,  # Minimal tokens just to load the model
                    }
                }
            )
            response.raise_for_status()
        print(f"Ollama model '{OLLAMA_MODEL}' is warm and ready on GPU!")
    except Exception as e:
        print(f"Warning: Failed to warm up Ollama model: {e}")


def get_rag_response(query: str) -> str:
    """
    Generates a feedback-oriented response using RAG context + Ollama.
    """
    if retriever is None:
        return "RAG system not initialized. Cannot generate context-aware reply."
    
    try:
        # Retrieve relevant context from the vector store
        docs = retriever.invoke(query)
        context = "\n".join([doc.page_content for doc in docs])
        
        # Build the prompt with RAG context
        prompt = f"""{SYSTEM_PROMPT}

Trip Details: {context}

Customer said: {query}
Your response:"""

        # Call Ollama API directly (fast, model already warm on GPU)
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 64,  # Keep response short for phone calls
                        "temperature": 0.7,
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()

    except httpx.TimeoutException:
        return "Error: Ollama request timed out."
    except Exception as e:
        return f"Error generating RAG response: {e}"


if __name__ == "__main__":
    warm_up_ollama()
    if retriever:
        print("RAG system loaded successfully. Testing feedback response...")
        test_query = "The hotel was really nice but the food could have been better."
        response = get_rag_response(test_query)
        print(f"Customer: {test_query}")
        print(f"AI Response: {response}")
    else:
        print("RAG system failed to load. Cannot run test.")
