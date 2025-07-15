from fastapi import APIRouter, Request
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
import os

router = APIRouter()

# Setup OpenAI + Chroma
embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory="chroma_index", embedding_function=embeddings)
qa_chain = RetrievalQA.from_chain_type(llm=OpenAI(), retriever=db.as_retriever())

@router.post("/query")
async def run_rag(request: Request):
    body = await request.json()
    query = body.get("query")
    if not query:
        return {"error": "Query required"}
    
    response = qa_chain.run(query)
    return {"query": query, "response": response}
