from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

DB_PATH = "data/chroma_db"

class ManualRAG:
    def __init__(self, llm, retriever, template):
        self.llm = llm
        self.retriever = retriever
        self.template = template

    def invoke(self, inputs):
        query = inputs.get("input") or inputs.get("query")
        # get_relevant_documents is deprecated in favor of invoke, but let's use invoke if available or get_relevant_documents
        try:
            docs = self.retriever.invoke(query)
        except:
            docs = self.retriever.get_relevant_documents(query)
            
        context = "\n\n".join([d.page_content for d in docs])
        prompt_text = self.template.format(context=context, input=query)
        
        # Ollama invoke returns string usually
        response = self.llm.invoke(prompt_text)
        
        return {"answer": response, "context": docs}

def get_rag_chain():
    # 1. Initialize Embeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 2. Load Vector Store
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # 3. Initialize LLM (Ollama)
    llm = Ollama(model="phi3")

    # 4. Define Prompt
    template = """
    You are a helpful and expert writing coach named Forge. 
    Your goal is to help the user improve their writing by providing constructive critique and tips.
    
    Use the following pieces of retrieved context (writing guides) to analyze the user's text and provide specific feedback.
    If the context doesn't apply, rely on your general knowledge but prioritize the guides.
    
    Context:
    {context}
    
    User Text:
    {input}
    
    Critique:
    """
    
    return ManualRAG(llm, retriever, template)
