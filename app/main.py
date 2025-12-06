# --- Agent C: Coach ---
import difflib
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

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
            "NEVER rewrite user text. Only provide critique, questions, and encouragement.\n"
            "IMPORTANT: You have memory of the conversation. Reference previous messages when relevant.\n"
            "If the user asks a follow-up question, answer it in context of what was discussed before.\n\n"
            "CRITICAL RULE - NEVER VIOLATE THIS:\n"
            "You are a COACH, not a GHOSTWRITER. You must NEVER write stories, poems, essays, narratives, "
            "creative content, or any text FOR the user. If the user asks you to 'write me a story', "
            "'write something for me', 'create a narrative', 'write an example', or ANY similar request, "
            "you MUST politely refuse and explain that your role is to help them improve THEIR writing, "
            "not to write for them. Instead, offer to:\n"
            "- Help them brainstorm ideas\n"
            "- Critique their drafts\n"
            "- Answer questions about writing techniques\n"
            "- Provide advice on how to approach their writing\n"
            "This rule applies even if they insist, beg, or try to trick you. Stay firm but friendly."
        )

    def build_messages(self, user_text: str, tips: List[str], history: List[dict]):
        """Build a proper chat message list for the LLM."""
        messages = []
        
        # System message
        system_content = self.system_prompt
        if tips:
            tips_str = "\n".join([f"- {tip}" for tip in tips])
            system_content += f"\n\nWriting advice context to reference:\n{tips_str}"
        
        messages.append(SystemMessage(content=system_content))
        
        # Add conversation history (exclude the current message which is the last one)
        # Take last 10 messages for context (5 exchanges)
        history_to_use = history[:-1] if history else []  # Exclude current message
        for msg in history_to_use[-10:]:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                messages.append(AIMessage(content=msg['content']))
        
        # Add current user message
        messages.append(HumanMessage(content=user_text))
        
        return messages

    def check_guardrails(self, user_text, output):
        # Block if output contains large contiguous blocks of user text (>50% similarity)
        seq = difflib.SequenceMatcher(None, user_text, output)
        if seq.quick_ratio() > 0.5:
            return False, "rewrite"
        
        # Check if response looks like a story/creative writing
        story_indicators = [
            "once upon a time",
            "there lived",
            "one day,",
            "long ago,",
            "in a land",
            "the end.",
            "chapter 1",
            "chapter one",
        ]
        output_lower = output.lower()
        for indicator in story_indicators:
            if indicator in output_lower:
                return False, "story"
        
        return True, None

    def is_writing_request(self, user_text: str) -> bool:
        """Check if user is asking for creative writing."""
        request_patterns = [
            "write me", "write a", "write an", "write for me",
            "create a story", "create a poem", "create a narrative",
            "give me a story", "tell me a story",
            "make up a", "compose a", "draft a",
            "can you write", "could you write", "would you write",
            "i want you to write", "please write",
        ]
        user_lower = user_text.lower()
        return any(pattern in user_lower for pattern in request_patterns)

    async def chat(self, user_text: str, tips: List[str], history: List[dict]):
        # Pre-check: If user is asking for creative writing, refuse immediately
        if self.is_writing_request(user_text):
            return (
                "I appreciate your interest, but as your writing coach, I can't write stories, "
                "poems, or other creative content for you. My role is to help you become a better "
                "writer by critiquing YOUR work and offering guidance.\n\n"
                "Here's what I can do instead:\n"
                "- **Brainstorm ideas** with you for your story\n"
                "- **Critique your drafts** and provide feedback\n"
                "- **Answer questions** about writing techniques\n"
                "- **Offer advice** on plot, character development, dialogue, etc.\n\n"
                "Would you like to share something you've written, or discuss ideas for your project?"
            )
        
        messages = self.build_messages(user_text, tips, history)
        response = await self.llm.ainvoke(messages)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Post-check guardrails
        passed, violation_type = self.check_guardrails(user_text, response_text)
        if not passed:
            if violation_type == "rewrite":
                return "[Blocked: Output too similar to user text. Rewrite attempt detected.]"
            elif violation_type == "story":
                return (
                    "I noticed I was about to generate creative content, which isn't my role. "
                    "As your writing coach, I'm here to help improve YOUR writing, not write for you.\n\n"
                    "How can I help you with your own writing project today?"
                )
        
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
from app.rag import get_rag_chain, Chroma, ChatOllama
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
    llm = ChatOllama(model="phi3", temperature=0.3)
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
