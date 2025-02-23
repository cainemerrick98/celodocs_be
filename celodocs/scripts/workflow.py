from celodocs.core.document_collection import DocumentCollector
from celodocs.core.embeddings import DocumentEmbedder


if __name__ == '__main__':
    collector = DocumentCollector()
    documents = collector.collect_documents()
    embedder = DocumentEmbedder()
    embeddings = embedder.create_embeddings(documents)
    

    