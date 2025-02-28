from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
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

embeddings = load_embeddings()
documents = load_documents()
client = load_client()
    

@app.post("/chat", response_model=Answer)
def chat(query: str):
    rqs = refine_query(query, client)
        
    queries = eval(rqs)

    retirevals = []
    for q in queries:
        index = query_embeddings(q)
        retirevals.extend(retrieve_documents(index))

    retirevals = list(set(retirevals)) #remove duplicates

    relevant = []
    for r in retirevals:
        if eval(assert_document_relevance(query, r, client)):
            relevant.append(r)

    response = ""
    for chunk in answer_query(query, relevant):
        response += chunk.data.choices[0].delta.content
    
    sources = []
    for r in retirevals:
        sources.append(Source(title=r['title'], link=r['link']))

    return Answer(answer=response, sources=sources)


if __name__ == "__main__":
    uvicorn.run('app:app', host="0.0.0.0", port=8000, reload=True)
