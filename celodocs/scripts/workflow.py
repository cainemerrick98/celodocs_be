from celodocs.core.document_collection import DocumentCollector
from celodocs.core.embeddings import DocumentEmbedder


if __name__ == '__main__':
    print("Starting workflow...")
    collector = DocumentCollector()
    documents = collector.collect_documents()
    print(f"Collected {len(documents)} documents")
    embedder = DocumentEmbedder()
    embeddings = embedder.create_embeddings(documents)
    print(f"Created {len(embeddings)} embeddings")
    

    