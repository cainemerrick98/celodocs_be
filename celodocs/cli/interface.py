from sentence_transformers import SentenceTransformer
from celodocs.core.query_engine import load_embeddings, load_documents, load_client, query_embeddings, retrieve_documents, refine_query, assert_document_relevance, answer_query

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = load_embeddings()
documents = load_documents()
client = load_client()


if __name__ == '__main__':
    print('---WELCOME TO CELODOCS API---')
    while True:
        query = input('User: ')
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
        

        print('Agent:\n')
        for chunk in answer_query(query, relevant):
            print(chunk.data.choices[0].delta.content, end='', flush=True)
        print('\n')

        print('Sources:')
        for r in retirevals:
            print(r.link, end=', ')

        

        
            
        
