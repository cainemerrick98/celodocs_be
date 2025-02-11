from sentence_transformers import SentenceTransformer
import numpy as np
import os
import json

if __name__ == '__main__':
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = np.load(os.path.join(os.getcwd(), 'embeddings.npy'))
    documents = json.load(os.path.join(os.getcwd(), 'documents.json'))
    print('Enter a query and see the top documents')
    while True:
        query = input('')
        query = model.encode([query])
        cosine_similarities = np.dot(embeddings, query.T) / (np.linalg.norm(embeddings, axis=1)) * np.linalg.norm(query)
        best_matches = np.argpartition(cosine_similarities, -10)[-10:]