from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os

from app.config import CHROMA_DB_PATH, PHI2_MODEL_PATH, LLAMA3B_MODEL_PATH

# Load the LLM model (using LlamaCpp for GGUF)
# Ensure you have either phi-2.gguf or llama-3b.gguf in the models/ directory
try:
    # Choose the model you want to use
    model_path = PHI2_MODEL_PATH # Or LLAMA3B_MODEL_PATH
    
    llm = LlamaCpp(
        model_path=model_path,
        n_ctx=1024, # Increased slightly to fit context
        n_gpu_layers=-1, # Offload all layers to GPU if available
        n_batch=512, # Process tokens in batches
        max_tokens=64, # Hard limit on generation length
        verbose=False, # Suppress verbose output
    )
except Exception as e:
    print(f"Error loading LLM model for RAG: {e}")
    llm = None

# Load the embeddings model
try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
except Exception as e:
    print(f"Error loading embeddings model for RAG: {e}")
    embeddings = None

# Load the Chroma vector store
try:
    vectorstore = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2}) # Retrieve fewer docs to save tokens
except Exception as e:
    print(f"Error loading Chroma vector store: {e}")
    vectorstore = None
    retriever = None

# Create the RAG chain
qa_chain = None
if llm and retriever:
    prompt_template = """Use the following pieces of context to answer the question at the end. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    Keep the answer extremely concise (under 2 sentences).

    Context: {context}

    Question: {question}
    Answer:"""
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    chain_type_kwargs = {"prompt": PROMPT}
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=retriever, 
        chain_type_kwargs=chain_type_kwargs
    )

def get_rag_response(query: str) -> str:
    """
    Generates a response using the RAG system based on the knowledge base.
    """
    if qa_chain is None:
        return "RAG system not initialized. Cannot generate context-aware reply."
    try:
        result = qa_chain.invoke({"query": query})
        return result["result"]
    except Exception as e:
        return f"Error generating RAG response: {e}"

if __name__ == "__main__":
    # Simple test for RAG system
    if qa_chain:
        print("RAG system loaded successfully. Testing get_rag_response...")
        test_query = "What is the core technology used for STT?"
        response = get_rag_response(test_query)
        print(f"Query: {test_query}")
        print(f"Response: {response}")
    else:
        print("RAG system failed to load. Cannot run test.")
