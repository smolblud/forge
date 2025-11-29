import langchain.chains
print(f"Chains dir: {dir(langchain.chains)}")
try:
    from langchain.chains import RetrievalQA
    print("RetrievalQA found")
except:
    print("RetrievalQA NOT found")
