# Forge - Local-First AI Writing Coach

Forge is a 100% offline, local-first AI writing coach designed to help users improve their writing through constructive critique and feedback. It leverages Retrieval-Augmented Generation (RAG) to provide context-aware advice based on a library of writing guides, all running locally on your machine using Ollama.

## 🚀 Features

*   **Local-First & Private**: Runs entirely on your device. No data leaves your machine.
*   **AI Writing Coach**: Uses the Phi-3 model (via Ollama) to analyze text and offer improvements.
*   **RAG-Powered**: Retrieves relevant writing advice from a local knowledge base (ChromaDB) to ground its feedback.
*   **FastAPI Backend**: A lightweight and fast API to interact with the agent.

## 🛠️ Prerequisites

*   **Python 3.10+**
*   **[Ollama](https://ollama.com/)**: Must be installed and running.

## 📦 Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\Activate
    # Linux/Mac
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Pull the required Ollama models**:
    ```bash
    ollama pull phi3
    ollama pull mxbai-embed-large
    ```

## 🏃‍♂️ Usage

### 1. Ingest Knowledge Base
First, you need to populate the local vector database with writing guides.
```bash
python app/ingest.py
```

### 2. Start the API Server
Run the FastAPI server.
```bash
python -m app.main
```
The server will start at `http://127.0.0.1:8000`.

### 3. Test the Agent
You can test the endpoint using the provided script:
```bash
python test_api.py
```
Or send a POST request manually:
```bash
curl -X POST "http://127.0.0.1:8000/critique" \
     -H "Content-Type: application/json" \
     -d '{"text": "He was very angry and said loudly that he wanted to leave."}'
```

## ww Project Structure

*   `app/`: Contains the application source code.
    *   `main.py`: FastAPI entry point.
    *   `rag.py`: RAG pipeline implementation using LangChain.
    *   `ingest.py`: Script to ingest data into ChromaDB.
*   `data/`: Stores the knowledge base and vector database.
    *   `guides.json`: Source data for writing guides.
    *   `chroma_db/`: Persisted ChromaDB vector store.
*   `requirements.txt`: Python dependencies.
