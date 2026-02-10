from llama_cpp import Llama
import os

# Determine the base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "phi-2.gguf") # Adjust if using llama-3b.gguf

# Load the LLM model
try:
    llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_gpu_layers=-1) # n_gpu_layers=-1 to offload all layers to GPU
except Exception as e:
    print(f"Error loading LLM model: {e}")
    llm = None

def generate_reply(prompt: str) -> str:
    """
    Generates a reply from the loaded LLM model based on the given prompt.
    """
    if llm is None:
        return "LLM model not loaded. Cannot generate reply."
    try:
        output = llm(prompt, max_tokens=250, stop=["\n", " Human:", " AI:"], echo=False)
        return output["choices"][0]["text"].strip()
    except Exception as e:
        return f"Error generating reply: {e}"

if __name__ == "__main__":
    # Simple test to ensure the model loads and responds
    if llm:
        print("LLM model loaded successfully. Testing generate_reply...")
        test_prompt = "Hello, how are you today?"
        response = generate_reply(test_prompt)
        print(f"Prompt: {test_prompt}")
        print(f"Response: {response}")
    else:
        print("LLM model failed to load. Cannot run test.")