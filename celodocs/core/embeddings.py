from sentence_transformers import SentenceTransformer
import numpy as np
import regex as re
from nltk.tokenize import sent_tokenize
from nltk import download
import json
from celodocs.settings.config import settings
from celodocs.core.document_collection import Document
from dataclasses import asdict

download('punkt_tab')

class DocumentPreprocessor:
    table = re.compile(r"(<table>.*?</table>)", re.DOTALL)
    pql_example = re.compile(r"(<pql_example>.*?</pql_example>)", re.DOTALL)

    @classmethod
    def match(cls, string: str):
        return cls.table.search(string) or cls.pql_example.search(string)

    @classmethod
    def extract_elements(cls, content: str) -> list[str]:
        elements = cls.table.split(content)
        split_elements = []

        for elem in elements:
            split_elems = cls.pql_example.split(elem)
            split_elements.extend(filter(None, [i.strip() for i in split_elems]))

        
        final_elements = []
        for elem in split_elements: 
            if not cls.match(elem):
                final_elements.extend(sent_tokenize(elem)) 
            else:
                final_elements.append(elem)
        
        return final_elements

class DocumentEmbedder:
    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
        self.max_tokens = settings.max_tokens
        self.overlap = settings.overlap
        self.preprocessor = DocumentPreprocessor()

    def chunk_document(self, document: Document) -> list[str]:
        processed_document = self.preprocessor.extract_elements(document.content)

        chunks = []
        current_chunk = []
        token_count = 0
        for elem in processed_document:

            if self.preprocessor.match(elem):
                elem = re.sub(r"</?[^<>]+>", "", elem)
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                
                chunks.append(elem)
                token_count = 0
            
            else:
                if token_count + len(elem.split()) > self.max_tokens:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    token_count = 0
                
                current_chunk.append(elem)
                token_count += len(elem.split())
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def create_embeddings(
        self,
        documents: list[Document],
        embeddings_path: str = settings.embeddings_path,
        documents_path: str = settings.documents_path
    ):
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            for chunk in chunks:
                all_chunks.append(Document(title=doc.title, content=chunk, link=doc.link))
                
        
        embeddings = self.model.encode([chunk.content for chunk in all_chunks])

        np.save(embeddings_path, embeddings)
        with open(documents_path, "w") as file:
            json.dump([asdict(chunk) for chunk in all_chunks], file)
        
        return embeddings, all_chunks

        

