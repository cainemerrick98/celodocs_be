from sentence_transformers import SentenceTransformer
import numpy as np
import regex as re
from nltk.tokenize import sent_tokenize
from nltk import download
import json

download('punkt_tab')

#TODO rename to preprocessor
class SpecialPatterns():
    table = re.compile(r"(<table>.*?</table>)", re.DOTALL)
    pql_example = re.compile(r"(<pql_example>.*?</pql_example>)", re.DOTALL)

    @classmethod
    def match(cls, string:str):
        return cls.table.search(string) or cls.pql_example.search(string)

    @classmethod
    def extract_elements(cls, document:str) -> list[str]:
        elements = cls.table.split(document)
        split_elements = []

        for elem in elements:
            split_elems = cls.pql_example.split(elem)
            split_elements.extend(filter(None, split_elems))
        
        final_elements = []
        for elem in split_elements: 
            if not cls.match(elem):
                final_elements.extend(sent_tokenize(elem))
            else:
                final_elements.append(elem)
        
        return final_elements

def chunk_document(document:str, max_tokens=256, overlap=50):
    processed_document = SpecialPatterns.extract_elements(document)

    chunks = []
    current_chunk = []
    token_count = 0
    for elem in processed_document:

        if SpecialPatterns.match(elem):
            elem = re.sub(r"</?[^<>]+>", "", elem)
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
            
            chunks.append(elem)
            token_count = 0
        
        else:
            if token_count + len(elem.split()) > max_tokens:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                token_count = 0
                
            current_chunk.append(elem)
            token_count += len(elem.split())
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def create_embeddings(documents:list[str]):
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc)
        all_chunks.extend(chunks)
    
    embeddings = model.encode(all_chunks)

    np.save("embeddings.npy", embeddings)
    with open("documents.json", "w") as file:
        json.dump(all_chunks, file)

        

