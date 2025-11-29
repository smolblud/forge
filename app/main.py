from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.rag import get_rag_chain
import uvicorn

app = FastAPI(title="Forge AI Writing Coach")

class CritiqueRequest(BaseModel):
    text: str

class CritiqueResponse(BaseModel):
    critique: str
    sources: list

# Initialize chain at module level
try:
    rag_chain = get_rag_chain()
    print("RAG Chain initialized successfully.")
except Exception as e:
    print(f"Error initializing RAG Chain: {e}")
    rag_chain = None

@app.post("/critique", response_model=CritiqueResponse)
async def generate_critique(request: CritiqueRequest):
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG Chain not initialized")
    
    try:
        # The new retrieval chain expects 'input'.
        response = rag_chain.invoke({"input": request.text})
        
        critique = response['answer']
        source_docs = response.get('context', [])
        sources = [doc.metadata.get('title', 'Unknown') for doc in source_docs]
        
        return CritiqueResponse(critique=critique, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False, loop="asyncio")
