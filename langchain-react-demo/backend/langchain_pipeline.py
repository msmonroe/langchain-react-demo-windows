import json
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import OpenAI
from langchain.chains import RetrievalQA

def load_texts():
    with open("drug_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return [f"{row.get('name','')}: {row.get('description','')}" for row in data]

def ask_question(query: str):
    texts = load_texts()
    embeddings = OpenAIEmbeddings()
    # In-memory Chroma for demo
    db = Chroma.from_texts(texts, embeddings)
    retriever = db.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(temperature=0),
        retriever=retriever
    )
    return qa_chain.run(query)
