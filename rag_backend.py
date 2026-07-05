"""
APEX - RAG Backend (Reference Library)

What this file does:
1. Defines which models are used (embeddings locally, LLM locally via Ollama).
2. Reads the 11 PDFs from the data/ folder.
3. Builds a local vector database (ChromaDB) ONCE and stores it.
4. Runs a test question and shows the answer + the sources it used.

From the second run onward, the database is only loaded, not rebuilt.

NOTE: This version runs the language model fully locally via Ollama -
no API key, no internet connection, and no usage limits needed once the
model has been downloaded (via 'ollama pull gpt-oss:20b').
"""

import chromadb

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    Settings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore


# 1) Define the models
#    - Embedding model: runs locally and free of charge, no internet needed
#    - LLM: gpt-oss:20b, running fully locally via Ollama (no API key needed)
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
Settings.llm = Ollama(
    model="gpt-oss:20b",
    request_timeout=300.0,  # local inference is slower than a cloud API - give it room
    additional_kwargs={"num_predict": 4096},  # Ollama's equivalent of max_tokens
)

# 2) Create/open the persistent database in the ./chroma_db folder
db = chromadb.PersistentClient(path="./chroma_db")
collection = db.get_or_create_collection("apex_db_a")
vector_store = ChromaVectorStore(chroma_collection=collection)

# 3) Build the database ONLY ONCE, then just load it
if collection.count() == 0:
    print("Building the Reference Library index for the first time - this may take a few minutes...")
    documents = SimpleDirectoryReader("data").load_data()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    print(f"Done. {len(documents)} pages/sections read from your PDFs.")
else:
    print("Loading the existing Reference Library index...")
    index = VectorStoreIndex.from_vector_store(vector_store)


# 4) Run a test question (only runs when this file is started directly)
if __name__ == "__main__":
    query_engine = index.as_query_engine(similarity_top_k=6)

    question = "What are the FAIR principles for research data?"
    print("\nQuestion:", question)
    print("(Running locally via Ollama - this may take a bit longer than a cloud API)")

    answer = query_engine.query(question)
    print("\nAnswer:\n", answer)

    print("\nSources used:")
    seen = set()
    for node in answer.source_nodes:
        name = node.metadata.get("file_name", "unknown")
        if name not in seen:
            print(" -", name)
            seen.add(name)
