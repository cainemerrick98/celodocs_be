from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json

if __name__ == '__main__':
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = np.load(os.path.join(os.getcwd(), 'embeddings.npy'))
    with open(os.path.join(os.getcwd(), 'documents.json'), 'r') as file:
        documents = json.load(file)

    print('Enter a query and see the top documents')
    while True:
        query = input('')
        query = model.encode([query])
        query = query / np.linalg.norm(query)  # Normalize query vector
        
        cosine_similarities = np.dot(embeddings, query.T).squeeze()
        top_index = np.argsort(cosine_similarities)[-10:][::-1]

        print('\n')
        for i in top_index:
            print(documents[i])
            print('\n')
        
        
