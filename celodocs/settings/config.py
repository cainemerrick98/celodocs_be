from typing import List
class Settings:
    base_url: str = 'https://docs.celonis.com/en/'
    links_url: str = 'https://docs.celonis.com/en/getting-started-with-the-celonis-platform.html'
    unwanted_paths: List[str] = ('release-notes', 'planned-releases')

settings = Settings()

