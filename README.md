# Forge - Local-First AI Writing Coach

Forge is a 100% offline, local-first AI writing coach designed to help users improve their writing through constructive critique and feedback. It uses a **"Coach, Not Ghostwriter"** philosophy—Forge will never rewrite your text, only provide critique, questions, and encouragement.

The system leverages Retrieval-Augmented Generation (RAG) with a three-agent architecture (Planner, Librarian, Coach) to provide context-aware writing advice, all running locally on your machine using Ollama.

## Features

- **Local-First & Private**: Runs entirely on your device. No data leaves your machine.
- **AI Writing Coach**: Uses the Phi-3 model (via Ollama) to analyze text and offer improvements.
- **RAG-Powered**: Retrieves relevant writing advice from a local ChromaDB knowledge base.
- **Conversational Memory**: Maintains context across messages in the same chat session.
- **Modern Web UI**: Beautiful Next.js frontend with real-time chat interface.
- **Chat Persistence**: Conversations are saved locally in SQLite for future reference.

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 15, React, Tailwind CSS, shadcn/ui |
| **Backend** | Python 3.10+, FastAPI, LangChain |
| **LLM** | Ollama (Phi-3 model) |
| **Embeddings** | mxbai-embed-large (via Ollama) |
| **Vector DB** | ChromaDB (embedded) |
| **Database** | SQLite (chat persistence) |

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** (for frontend)
- **[Ollama](https://ollama.com/)**: Must be installed and running

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/smolblud/forge.git
cd forge
```

### 2. Backend Setup

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .\.venv\Scripts\Activate  # Windows

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Pull Ollama Models

```bash
ollama pull phi3
ollama pull mxbai-embed-large
```

### 4. Ingest Knowledge Base

Populate the local vector database with writing guides:

```bash
python app/ingest.py
```

### 5. Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend Server

```bash
# From the project root
python -m app.main
```

The API server will start at `http://127.0.0.1:8000`.

### Start the Frontend

```bash
# From the frontend directory
cd frontend
npm run dev
```

The web UI will be available at `http://localhost:3000`.

## Usage

1. Open `http://localhost:3000` in your browser
2. Click "Begin Your Journey" to start
3. Paste your writing, ask questions, or chat with Forge
4. Use the sidebar to manage and revisit previous conversations

### Writing Submissions

Submit 50+ words of your writing to receive structured critique on:
- **Pacing**: Flow and rhythm of your narrative
- **Dialogue**: Natural conversation and character voice
- **Show-Don't-Tell**: Descriptive techniques and sensory details

### Conversational Mode

For shorter messages or questions, Forge will respond conversationally, answering questions about writing techniques, offering advice, or discussing your work.

## Project Structure

```
forge/
├── app/                    # Backend source code
│   ├── main.py            # FastAPI application & agents
│   ├── rag.py             # RAG pipeline (LangChain)
│   ├── database.py        # SQLite database setup
│   ├── models.py          # SQLAlchemy models
│   └── ingest.py          # Knowledge base ingestion
├── frontend/              # Next.js frontend
│   ├── app/               # Next.js app router
│   ├── components/        # React components
│   └── lib/               # API utilities
├── data/                  # Data storage
│   ├── guides.json        # Writing guides source
│   ├── chroma_db/         # Vector database
│   └── forge.db           # SQLite chat database
└── requirements.txt       # Python dependencies
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health status |
| `/submit` | POST | Submit text for critique/chat |
| `/chats` | GET | List all conversations |
| `/chats` | POST | Create new conversation |
| `/chats/{id}` | GET | Get conversation with messages |
| `/chats/{id}` | DELETE | Delete conversation |

## License

MIT
