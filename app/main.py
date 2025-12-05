# --- Agent C: Coach ---
import difflib
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class AgentCCoach:
    def __init__(self, llm):
        self.llm = llm
        self.system_prompt = (
            "You are Forge, a friendly AI writing coach. You can:\n"
            "- Have normal conversations and answer questions about yourself\n"
            "- Provide constructive critique on writing submissions\n"
            "- Offer writing advice and answer writing-related questions\n\n"
            "When users submit writing (50+ words), analyze it for Pacing, Dialogue, and Show-Don't-Tell.\n"
            "When users ask general questions, respond naturally and helpfully.\n"
            "NEVER rewrite user text. Only provide critique, questions, and encouragement."
        )

    def synthesize_prompt(self, user_text, tips, history: List[dict]):
        tips_str = "\n".join([f"- {tip}" for tip in tips])
        
        history_str = ""
        if history:
            history_str = "Conversation History:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]]) + "\n\n"

        prompt = (
            f"{self.system_prompt}\n\n"
            f"{history_str}"
            f"User Text:\n{user_text}\n\n"
            f"Advice Context:\n{tips_str}\n\n"
            "Respond appropriately based on the user's intent (conversation or critique)."
        )
        return prompt

    def check_guardrails(self, user_text, output):
        # Block if output contains large contiguous blocks of user text (>50% similarity)
        seq = difflib.SequenceMatcher(None, user_text, output)
        if seq.quick_ratio() > 0.5:
            return False
        return True

    async def chat(self, user_text, tips, history: List[dict]):
        prompt = self.synthesize_prompt(user_text, tips, history)
        response = await self.llm.ainvoke(prompt)
        response_text = response if isinstance(response, str) else str(response)
        
        # Only check guardrails if it looks like a critique (long response)
        if len(user_text) > 50 and not self.check_guardrails(user_text, response_text):
             return "[Blocked: Output too similar to user text. Rewrite attempt detected.]"
        
        return response_text

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

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.rag import get_rag_chain, Chroma, Ollama
from app.database import engine, Base, get_db
from app import models
import uvicorn
import re

# Initialize Database
models.Base.metadata.create_all(bind=engine)

# --- Agent A: Planner ---
class AgentAPlanner:
    def __init__(self):
        # Dimensions for critique
        self.dimensions = ["Pacing", "Dialogue", "Show-Don't-Tell"]

    def classify(self, text: str):
        word_count = len(re.findall(r'\w+', text))
        
        # Simple heuristic for now, can be improved with LLM classification
        if word_count < 50:
            lower_text = text.lower()
            if any(greeting in lower_text for greeting in ["hello", "hi", "hey", "greetings"]):
                return {"type": "greeting", "dimensions": []}
            elif "forge" in lower_text or "who are you" in lower_text or "what do you do" in lower_text:
                return {"type": "question_about_forge", "dimensions": []}
            else:
                return {"type": "conversation", "dimensions": []}
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

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# Pydantic Models
class MessageBase(BaseModel):
    role: str
    content: str

class Message(MessageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []

    class Config:
        from_attributes = True

class SubmitRequest(BaseModel):
    text: str
    conversation_id: Optional[int] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Forge AI Writing Coach API is running"}

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "ok",
        "agents": {
            "planner": planner is not None,
            "librarian": librarian is not None,
            "coach": coach is not None
        }
    }

# --- Chat Persistence Endpoints ---

@app.get("/chats", response_model=List[Conversation])
def get_chats(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    chats = db.query(models.Conversation).order_by(models.Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    return chats

@app.get("/chats/{chat_id}", response_model=Conversation)
def get_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(models.Conversation).filter(models.Conversation.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return chat

@app.post("/chats", response_model=Conversation)
def create_chat(chat: ConversationCreate, db: Session = Depends(get_db)):
    db_chat = models.Conversation(title=chat.title)
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):
    chat = db.query(models.Conversation).filter(models.Conversation.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(chat)
    db.commit()
    return {"status": "success"}

# --- Main Interaction Endpoint ---

@app.post("/submit")
async def submit(request: SubmitRequest, db: Session = Depends(get_db)):
    user_text = request.text
    conversation_id = request.conversation_id

    if not (planner and librarian and coach):
        return JSONResponse({"error": "Agentic flow not initialized."}, status_code=500)
    if not user_text:
        return JSONResponse({"error": "No text provided."}, status_code=400)

    # Get or create conversation
    if conversation_id:
        conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
        if not conversation:
            # Fallback to creating new if ID invalid
            conversation = models.Conversation(title=user_text[:30] + "...")
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
    else:
        conversation = models.Conversation(title=user_text[:30] + "...")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    conversation_id = conversation.id

    # Save User Message
    user_msg = models.Message(conversation_id=conversation_id, role="user", content=user_text)
    db.add(user_msg)
    db.commit()

    # Retrieve History
    history_msgs = db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.created_at).all()
    history = [{"role": m.role, "content": m.content} for m in history_msgs]

    # Step 1: Plan
    plan = planner.plan(user_text)
    classification = plan.get("classification")
    dimensions = plan.get("dimensions", [])

    # Step 2: Retrieve Tips (if needed)
    tips = []
    if classification == "submission":
        tips = librarian.retrieve_tips(dimensions)

    # Step 3: Generate Response
    response_text = await coach.chat(user_text, tips, history)

    # Save Assistant Message
    assistant_msg = models.Message(conversation_id=conversation_id, role="assistant", content=response_text)
    db.add(assistant_msg)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    db.commit()

    return JSONResponse({
        "conversation_id": conversation_id,
        "plan": plan,
        "tips": tips,
        "response": response_text
    })

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False, loop="asyncio")
