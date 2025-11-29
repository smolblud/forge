import json
import os
from langchain_community.vectorstores import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

DATA_PATH = "data/guides.json"
DB_PATH = "data/chroma_db"

def ingest():
    if not os.path.exists(DATA_PATH):
        print(f"Data file not found at {DATA_PATH}")
        return

    print("Loading data...")
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    documents = []
    for item in data:
        doc = Document(
            page_content=f"{item['title']}: {item['content']}",
            metadata={"title": item['title']}
        )
        documents.append(doc)

    print(f"Loaded {len(documents)} documents.")

    print("Initializing embeddings...")
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    print("Creating/Updating Vector Store...")
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest()
