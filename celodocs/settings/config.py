from typing import List
class Settings:
    base_url: str = 'https://docs.celonis.com/en/'
    links_url: str = 'https://docs.celonis.com/en/getting-started-with-the-celonis-platform.html'
    unwanted_paths: List[str] = ('release-notes', 'planned-releases')

    # Embedding settings
    embedding_model: str = 'all-MiniLM-L6-v2'
    max_tokens: int = 256
    overlap: int = 50
    embeddings_path: str = "embeddings.npy"
    documents_path: str = "documents.json"

settings = Settings()

