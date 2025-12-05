from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_community.embeddings import OllamaEmbeddings

# Re-export for use in main.py
__all__ = ['get_rag_chain', 'Chroma', 'Ollama', 'ChatOllama', 'OllamaEmbeddings']

DB_PATH = "data/chroma_db"

def get_rag_chain():
    # 1. Initialize Embeddings using Ollama
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

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
    prompt = ChatPromptTemplate.from_template(template)

    # 5. Create Chain using LCEL
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
    )

    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "input": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)
    
    return rag_chain_with_source