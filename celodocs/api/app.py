from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from celodocs.core.query_engine import (
    answer_query,
    refine_query, 
    assert_document_relevance, 
    query_embeddings, 
    retrieve_documents,
    load_embeddings,
    load_documents,
    load_client
)
load_dotenv()


class Source(BaseModel):
    title: str
    link: str

class Answer(BaseModel):
    answer: str
    sources: list[Source]

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = load_embeddings()
documents = load_documents()
client = load_client()
    

@app.post("/chat", response_model=Answer)
async def chat(request: Request):
    query = await request.json()
    print(query)
    rqs = refine_query(query, client)
        
    queries = eval(rqs)

    retirevals = []
    for q in queries:
        index = query_embeddings(q, embeddings, model)
        retirevals.extend(retrieve_documents(index, documents))

    # retirevals = retirevals #remove duplicates

    relevant = []
    for r in retirevals:
        if eval(assert_document_relevance(query, r['content'], client)):
            relevant.append(r)

    response = ""
    relevant_docs = [r['content'] for r in relevant]
    for chunk in answer_query(query, relevant_docs, client):
        response += chunk.data.choices[0].delta.content
    
    sources = []
    for r in relevant:
        sources.append(Source(title=r['title'], link=r['link']))

    print(sources)

    print(response)
    return Answer(answer=response, sources=sources)


if __name__ == "__main__":
    uvicorn.run('celodocs.api.app:app', host="0.0.0.0", port=8000, reload=True)
