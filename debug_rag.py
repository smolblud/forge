from app.rag import get_rag_chain
import sys

print("Initializing RAG chain...")
try:
    chain = get_rag_chain()
    print("RAG chain initialized.")
except Exception as e:
    print(f"Error initializing chain: {e}")
    sys.exit(1)

print("Invoking chain...")
try:
    response = chain.invoke({"input": "How do I write better?"})
    print("Response received.")
    print(response)
except Exception as e:
    print(f"Error invoking chain: {e}")
    sys.exit(1)
