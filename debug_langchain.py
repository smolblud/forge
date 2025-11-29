import sys
import os
try:
    import langchain
    print(f"Langchain path: {langchain.__path__}")
    try:
        print(f"Langchain version: {langchain.__version__}")
    except:
        print("Langchain version not found")
        
    import langchain.chains
    print("langchain.chains imported successfully")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")

print(f"Sys path: {sys.path}")
