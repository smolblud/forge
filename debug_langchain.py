import sys
import os
try:
    import langchain
    print(f"Langchain path: {langchain.__path__}")
    
    try:
        from langchain.chains import create_retrieval_chain
        print("Imported create_retrieval_chain from langchain.chains")
    except ImportError:
        print("Failed to import create_retrieval_chain from langchain.chains")
        
    try:
        from langchain.chains.retrieval import create_retrieval_chain
        print("Imported create_retrieval_chain from langchain.chains.retrieval")
    except ImportError:
        print("Failed to import create_retrieval_chain from langchain.chains.retrieval")

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
