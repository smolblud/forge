# Project Forge: Technical Implementation Guide

**Version:** 1.0  
**Project Goal:** To build a local-first, sustainable, agentic AI writing coach that runs on consumer hardware (4GB VRAM).

## 1. Executive Summary

"Forge" is an offline desktop application designed to assist writers by providing Socratic critique and domain-specific writing advice. It addresses the environmental cost of cloud AI and the educational risks of generative writing by enforcing a "coach, not ghostwriter" philosophy. The system leverages a 3-layer architecture: a generic UI, a custom logic server (the "Brain"), and a local inference engine (the "Muscle").

## 2. System Architecture

The application runs entirely on localhost.

### 2.1 The Three Layers

**Interface Layer (Frontend):**
- Tool: Open WebUI
- Role: Chat interface, history management, markdown rendering
- Connection: Connects via API to the Logic Layer (not directly to the LLM)

**Logic Layer (The Middle Brain):**
- Tool: Python (FastAPI + LangChain)
- Role: Request routing, RAG orchestration, prompt construction, guardrail enforcement
- Storage: ChromaDB (embedded vector store) for the knowledge base

**Inference Layer (The Muscle):**
- Tool: Ollama
- Role: Loads and runs the quantized LLM
- Model: Phi-3-mini-4k-instruct (Q4_K_M GGUF) + Custom LoRA Adapter
- Embeddings: nomic-embed-text-v1.5 (via Ollama)

## 3. Data Strategy

We require two distinct datasets sourced from high-quality communities (e.g., r/writing, r/screenwriting).

| Dataset | Purpose | Content Type | Processing |
|---------|---------|--------------|------------|
| **Knowledge Library** | RAG (Retrieval) | "How-to" guides, essays on technique, rule explanations | Chunked into 500-token segments, vectorized into ChromaDB |
| **Persona Dataset** | Fine-Tuning | Threads where users ask for critique and receive helpful feedback | Formatted as Instruction/Input/Output pairs. Filtered to remove "rewrites." |

## 4. Agentic Design (The Logic Layer)

The Python backend will implement three distinct "agents" (classes) to handle the workflow.

### Agent A: The Planner (Router)
- **Input:** Raw user message
- **Logic:**
  - If text length < 50 words: Classify as Question
  - If text length > 50 words: Classify as Submission
  - Submission Logic: Break analysis into 3 dimensions: Pacing, Dialogue, Show-Don't-Tell
- **Output:** A structured plan object

### Agent B: The Librarian (Retriever)
- **Input:** Analysis dimensions (from Planner)
- **Logic:** Generates search queries for concepts, not user text
  - User text: "He walked sadly." → Search Query: "How to show sadness without telling."
- **Action:** Queries ChromaDB using cosine similarity
- **Output:** Top 3 relevant chunks of writing advice

### Agent C: The Coach (Synthesizer)
- **Input:** User Text + Retrieved Advice + Persona Instructions
- **Logic:** Constructs the final prompt
  - System Prompt: "You are Forge, a tough but fair writing coach. You NEVER rewrite text. You only ask questions..."
- **Action:** Calls Ollama API
- **Guardrail:** Regex check on output. If output contains "Here is a rewrite:" or is >80% similar to input, reject and retry

## 5. Implementation Roadmap

---

### Phase 1: Environment & Tools
- [x] **Install Ollama:** `curl -fsSL https://ollama.com/install.sh`
- [x] **Pull Base Models:**
  - `ollama pull phi3:mini-4k-instruct-q4_K_M` (currently using `phi3`)
  - `ollama pull nomic-embed-text` (currently using `mxbai-embed-large`)
- [x] **Python Setup:** Create venv, install fastapi, uvicorn, langchain, chromadb

**Status:** ✅ **COMPLETE** - All dependencies installed, requirements.txt created

---

 - [x] **Scripting:** Write a Python script using Tavily
 - [x] **Target:** Scrape top 500 "Resources" posts from r/writing for the Knowledge Library
 - [x] **Target:** Scrape top 1,000 "Critique" threads for the Persona Dataset
 - [ ] **Cleaning:** Remove URLs, deleted comments, and non-ASCII characters

**Status:** ✅ **COMPLETE** - Tavily-based scraping scripts for Reddit and other websites implemented
### Other Writing Tip Sources (Prioritized)

1. writersdigest.com
2. writingforward.com
3. nybookeditors.com
4. thewritepractice.com
5. scribophile.com
6. writershelpingwriters.net

These sites are scraped using Tavily and merged into guides.json for the knowledge base.

---

### Phase 3: The Knowledge Base (RAG)
- [x] **Vector Store:** Initialize a persistent ChromaDB client in Python
- [x] **Ingestion:**
  - [x] Load "Knowledge Library" text files
  - [x] Split into chunks (RecursiveCharacterTextSplitter, chunk_size=500) - *Not implemented yet, using full documents*
  - [x] Embed chunks using OllamaEmbeddings (pointing to `mxbai-embed-large`)
  - [ ] Store in ChromaDB - *Ingest script exists but DB not yet created*
- [x] **RAG Chain:** Basic RAG chain implemented in `app/rag.py`

**Status:** ⚠️ **PARTIAL** - Code complete, needs to run `ingest.py` to create the vector database

---

### Phase 4: Fine-Tuning (The Persona)
- [ ] **Preparation:** Convert "Persona Dataset" to JSONL format compatible with QLoRA
- [ ] **Training:** Use Unsloth or AutoTrain libraries in Colab
  - [ ] Base Model: Phi-3-mini
  - [ ] Technique: QLoRA (4-bit)
  - [ ] Prompt Template: "Below is a writing submission. Provide a critique."
- [ ] **Export:** Save the adapter weights (adapter.safetensors)
- [ ] **Conversion:** Convert adapter to GGUF format and import into Ollama as a "Modelfile"

**Status:** ❌ **NOT STARTED** - Depends on Phase 2 data collection

---


### Phase 5: The "Middle Brain" API
- [x] **FastAPI App:** Create server.py (implemented as `app/main.py`)
- [x] **Endpoint:** POST /critique (implemented as `/critique`)
- [x] **Ollama Connection:** Use LangChain's ChatOllama (using `Ollama` from langchain-community)
- [ ] **Logic:** Implement the Planner → Librarian → Coach flow
  - [ ] Agent A: Planner/Router (classify text, identify dimensions)
  - [ ] Agent B: Librarian (conceptual search queries)
  - [ ] Agent C: Coach (synthesis + guardrails)

**Status:** ⚠️ **PARTIAL** - Basic RAG endpoint works, but 3-agent architecture not implemented

---

### Phase 6: Frontend Integration
- [ ] **Open WebUI:** Install via Docker
- [ ] **Configuration:** Set "OpenAI API Base URL" to point to FastAPI server
- [ ] **Testing:** Verify that typing "Critique this..." triggers the full chain

**Status:** ❌ **NOT STARTED** - No UI layer connected yet

---

## 6. Hardware Constraints & Optimization

- **Target VRAM:** 4GB
- **Model Selection:** We strictly use the Q4_K_M quantization of Phi-3 Mini (approx 2.4GB VRAM)
- **Context Window:** Limit to 4096 tokens to prevent KV Cache overflow
- **Offloading:** If VRAM fills, Ollama automatically offloads layers to system RAM. This is acceptable for a "Coach" where speed is less critical than quality.

---

## 7. Safety & Guardrails

- **System Prompt:** Explicit instruction: "Refuse to generate creative narrative. If asked to write a story, explain your educational mission."
- **Output Parsing:** The Logic Layer will calculate a generic "diff" between input and output. If the system detects extensive copying/rewriting, it flags the response.

**Status:** ⚠️ **PARTIAL** - System prompt exists but no output validation/guardrails implemented

---

## 📊 Project Status Summary

### ✅ Completed
1. ✅ Python environment setup with FastAPI, LangChain, ChromaDB
2. ✅ Basic FastAPI server with `/critique` endpoint
3. ✅ RAG chain implementation using LCEL
4. ✅ Sample knowledge base (guides.json)
5. ✅ Ingest script for vectorizing documents
6. ✅ Ollama integration with Phi-3

### ⚠️ In Progress / Needs Work
1. ⚠️ Run ingest.py to create ChromaDB vector database
2. ⚠️ Implement 3-agent architecture (Planner, Librarian, Coach)
3. ⚠️ Add output guardrails and rewrite detection
4. ⚠️ Expand knowledge base with real scraped data

### ❌ Not Started
1. ❌ Data scraping from Reddit (Tavily)
2. ❌ Persona dataset collection for fine-tuning
3. ❌ Model fine-tuning with QLoRA
4. ❌ Frontend integration (Open WebUI)
5. ❌ End-to-end testing with UI

---

## 🎯 Next Steps (Priority Order)

1. **Run the ingest script** to populate ChromaDB with existing guides
2. **Test the basic RAG pipeline** to ensure it works end-to-end
3. **Implement the 3-agent architecture** (Planner → Librarian → Coach)
4. **Add guardrails** to prevent text rewriting
5. **Set up data scraping** for larger knowledge base
6. **Connect a UI layer** for user interaction