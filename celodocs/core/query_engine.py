import numpy as np
import os
import json
from mistralai import Mistral
from sentence_transformers import SentenceTransformer
from celodocs.core.document_collection import Document
from celodocs.settings.config import settings

def load_embeddings():
    return np.load(os.path.join(os.getcwd(), 'embeddings.npy'))

def load_documents():
    with open(os.path.join(os.getcwd(), 'documents.json'), 'r') as file:
        documents = json.load(file)
    return documents

def load_client():
    print(f"Loading client with key: {settings.mistral_key}")
    return Mistral(api_key=settings.mistral_key)

def query_embeddings(query:str, embeddings:np.ndarray, model:SentenceTransformer, n=10) -> np.ndarray:
    """
    returns the index of the top n matching embeddings
    """
    query = model.encode([query])
    query = query / np.linalg.norm(query)
    cosine_similarities = np.dot(embeddings, query.T).squeeze()
    return np.argsort(cosine_similarities)[-n:][::-1]

def retrieve_documents(index:np.ndarray, documents:list[Document]) -> list[Document]:
    return [documents[i] for i in index]

def refine_query(query:str, client:Mistral) -> list[str]:
    prompt = f"""
    You are an AI assistant that improves user queries to ensure the correct documents are returned from a database. If the query is too broad break it into subqueries, if the query is phrased poorly for retireval based on semantic similarity then rephrase it.

    The user queries will be based on the Celonis product technical documentation. Here are some examples queries and how we expect you to refine them.

    Example 1:
    Original Query: "How do I create a data pool."
    Refined Query: ["How do I create a data pool."]

    Example 2:
    Original Query: "How do I create and configure the annotation builder."
    Refined Query: ["How to create the annotation builder", "How to configure the annotation builder"]

    Example 3: 
    Original Query: "Debug this PQL query. PU_AVG(DOMAIN_TABLE("o_custom_SalesOrder"."CustomerName"), "o_custom_SalesOrder"."Amount")
    Refined Query: ["What is the PU_AVG function", "What is the DOMAIN_TABLE function"]

    Now, refine the following query

    Original Query:
    {query}

    Provide your answer in the following format:
    ["query1", "query2"]
    """
    return client.chat.complete(
        model = settings.mistral_model,
        messages=[
            {"role":"system", "content":prompt}
        ]
    ).choices[0].message.content

def assert_document_relevance(query:str, document:str, client:Mistral) -> str:
    prompt = f"""
    You are an AI assisstant that decides if a retrieved document is relevant for the answering of a query.
    
    The user queries will be based on the Celonis product technical documentation. Here are some examples queries and the answer we expect.

    Example 1:
    Query: Debug the following PQL statement PU_AVG("o_custom_SalesOrder", "o_custom_SalesOrderItem"."ID")
    
    Document 1: The PU_AVG function works aggregates... 
    Answer: True 
    Reason: We need to know how the PU_AVG function works to debug

    Document 2: As the complexity of the PQL queries grows, you might experience a decline in query performance. 
    Answer: False
    Reason: Query performance is not related to debugging

    Example 2:
    Query: How do I set up a data pool in celonis
    
    Document 1: The first stage when integrating your source systems with the Celonis Platform is to create a data pool. A data pool is the main structural element of your data integration workflow, acting as a container for your data sources, data jobs, and monitoring. Creating data pools Data pools are created and managed on a Celonis Platform team level Click Data - Data Integration.
    Answer: True 
    Reason: Is a set instructions about creating data pools

    Document 2: You can share data between data pools within the same Celonis Platform team by exporting their data connections and then importing them into the target data pool. By sharing data, you can both granularly control permissions to it and can make use of commonly used data for different business reasons or processes.
    Answer: True
    Reason: Although you might not always need to know this it might be nice to know

    Example 3:
    Query: How do I write a PQL query to match a process that begins with activity a and ends with acitivity b
    
    Document 1: Description: Here MATCH_PROCESS flags all cases in which one activity A is followed directly by activity B with a 1.
                Queries: "Activities_CASES"."CASE_ID",MATCH_PROCESS("Activities"."ACTIVITY", NODE['A'] as src, NODE['B'] as tgt CONNECTED BY DIRECT[ src, tgt])
                Input tables:
                CASE_ID: string,ACTIVITY: string,TIMESTAMP: date
                '1','A',Tue Jan 01 2019 13:00:00.000
                '1','B',Tue Jan 01 2019 13:01:00.000
                '1','C',Tue Jan 01 2019 13:02:00.000
                '2','A',Tue Jan 01 2019 13:00:00.000
                '2','C',Tue Jan 01 2019 13:02:00.000
                '2','B',Tue Jan 01 2019 13:03:00.000
                CASE_ID: string,ACTIVITY: string,TIMESTAMP: date
                '1','A',Tue Jan 01 2019 13:00:00.000
                '1','B',Tue Jan 01 2019 13:01:00.000
                '1','C',Tue Jan 01 2019 13:02:00.000
                '2','A',Tue Jan 01 2019 13:00:00.000
                '2','C',Tue Jan 01 2019 13:02:00.000
                '2','B',Tue Jan 01 2019 13:03:00.000
                CASE_ID: string
                '1'
                '2'
                Activities.CASE_ID,Activities_CASES.CASE_ID
                Output:
                Column1: string,Column2: int
                '1',1
                '2',0
    Answer: True 
    Reason: This is a PQL example

    Now assess if the document is relevant to the query

    Original Query:
    {query}

    document:
    {document}

    return only True or False. Do not return reason. For example, 'True'
    """
    return client.chat.complete(
        model = settings.mistral_model,
        messages=[
            {"role":"system", "content":prompt}
        ]
    ).choices[0].message.content

def answer_query(query:str, documents:list[str], client:Mistral):
    documents = '\n\n'.join(documents)
    prompt = f"""
    You are an AI assisstant that answers a user query based on the retrieved documents. 
    Other AI assistants have already asserted that the documents are relevant.
    The user queries will be based on the Celonis product technical documentation.
    Only use the documents provided to answer the query. 
    

    Retrieved Documents
    ___________________
    {documents}
    ___________________

    Query: {query}

    Provide an answer.
    """
    return client.chat.stream(
        model = settings.mistral_model,
        messages=[
            {"role":"system", "content":prompt}
        ]
    )

def process_query(query:str, embeddings:np.ndarray, model:SentenceTransformer, documents:list[Document], client:Mistral):
    print(f"query: {query}")
    refined_queries = eval(refine_query(query, client))

    print(f"refined_queries: {len(refined_queries)}")
    print(f"refined_queries: {refined_queries}")

    all_retrievals = []
    for refined_query in refined_queries:
        print(f"refined_query: {refined_query}")
        index = query_embeddings(refined_query, embeddings, model)
        print(f"index: {index}")
        all_retrievals.extend(retrieve_documents(index, documents))
    
    print(f"all_retrievals: {len(all_retrievals)}")
    print(f"all_retrievals: {[i['title'] for i in all_retrievals]}")
    unique_retrievals = list({doc['content']:doc for doc in all_retrievals}.values())

    print(f"unique_retrievals: {len(unique_retrievals)}")

    relevant_docs = [
        doc for doc in unique_retrievals
        if eval(assert_document_relevance(query, doc['content'], client))
    ]
    print(f"relevant_docs: {len(relevant_docs)}")
    return relevant_docs
        
        
        
