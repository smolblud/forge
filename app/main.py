# --- Agent C: Coach ---
import difflib

class AgentCCoach:
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = (
            "You are a writing coach. Strictly do NOT rewrite or summarize user text. Only provide critique, questions, and advice."
        )

    def synthesize_prompt(self, user_text, tips):
        tips_str = "\n".join([f"- {tip}" for tip in tips])
        prompt = (
            f"{self.system_prompt}\n\nUser Text:\n{user_text}\n\nAdvice:\n{tips_str}\n\nRespond with critique and questions only."
        )
        return prompt

    def check_guardrails(self, user_text, output):
        # Block if output contains large contiguous blocks of user text (>50% similarity)
        seq = difflib.SequenceMatcher(None, user_text, output)
        if seq.quick_ratio() > 0.5:
            return False
        return True

    async def critique(self, user_text, tips):
        prompt = self.synthesize_prompt(user_text, tips)
        response = await self.llm.ainvoke(prompt)
        if not self.check_guardrails(user_text, response):
            return "[Blocked: Output too similar to user text. Rewrite attempt detected.]"
        return response
# --- Agent B: Librarian ---
class AgentBLibrarian:
    def __init__(self, retriever):
        self.retriever = retriever

    def dimension_to_query(self, dimension):
        # Map critique dimension to conceptual search query
        mapping = {
            "Pacing": "how to fix slow pacing",
            "Dialogue": "how to improve dialogue",
            "Show-Don't-Tell": "how to show not tell"
        }
        return mapping.get(dimension, f"writing advice about {dimension}")

    def retrieve_tips(self, dimensions):
        tips = []
        for dim in dimensions:
            query = self.dimension_to_query(dim)
            docs = self.retriever.invoke(query)
            for doc in docs[:1]:  # Only take top result per dimension for brevity
                tips.append(doc.page_content)
        return tips

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.rag import get_rag_chain, Chroma, Ollama
import uvicorn
import re

# --- Agent A: Planner ---
class AgentAPlanner:
    def __init__(self):
        # Dimensions for critique
        self.dimensions = ["Pacing", "Dialogue", "Show-Don't-Tell"]

    def classify(self, text: str):
        word_count = len(re.findall(r'\w+', text))
        if word_count < 50:
            return {"type": "question", "dimensions": []}
        else:
            return {"type": "submission", "dimensions": self.dimensions}

    def plan(self, text: str):
        result = self.classify(text)
        return {
            "input": text,
            "classification": result["type"],
            "dimensions": result["dimensions"]
        }

app = FastAPI(title="Forge AI Writing Coach")

# Initialize dependencies for agents
try:
    rag_chain = get_rag_chain()
    # For agentic flow, get retriever and llm separately
    embeddings = None
    try:
        from langchain_community.embeddings import OllamaEmbeddings
        embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    except Exception:
        pass
    vectorstore = Chroma(persist_directory="data/chroma_db", embedding_function=embeddings) if embeddings else None
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) if vectorstore else None
    llm = Ollama(model="phi3")
    planner = AgentAPlanner()
    librarian = AgentBLibrarian(retriever)
    coach = AgentCCoach(llm)
    print("Agentic flow initialized successfully.")
except Exception as e:
    print(f"Error initializing agentic flow: {e}")
    rag_chain = None
    retriever = None
    llm = None
    planner = None
    librarian = None
    coach = None

@app.post("/critique")
async def critique(request: Request):
    data = await request.json()
    user_text = data.get("text", "")
    if not (planner and librarian and coach):
        return JSONResponse({"error": "Agentic flow not initialized."}, status_code=500)
    if not user_text:
        return JSONResponse({"error": "No text provided."}, status_code=400)
    # Step 1: Plan
    plan = planner.plan(user_text)
    dimensions = plan.get("dimensions", [])
    # Step 2: Retrieve tips
    tips = librarian.retrieve_tips(dimensions)
    # Step 3: Critique
    critique_text = await coach.critique(user_text, tips)
    return JSONResponse({
        "plan": plan,
        "tips": tips,
        "critique": critique_text
    })

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False, loop="asyncio")
