from bs4 import BeautifulSoup, Tag
import requests
import regex as re
from typing import List, Optional
from dataclasses import dataclass
from celodocs.settings.config import settings

@dataclass
class Document:
    title: str
    content: str
    link: str

class BaseExtractor:
    def can_handle(self, url:str) -> bool:
        raise NotImplementedError("Subclasses must implement this method")
    
    def extract(self, url:str, **kwargs) -> List[str]:
        raise NotImplementedError("Subclasses must implement this method")
    
    def _clean_text(self, tag:Tag) -> str:
        text = re.sub(r'\s([^\w\s])', r'\1', tag.get_text(separator=' ', strip=True))
        text = text.replace('\n', '')
        return re.sub(r'\s+', ' ', text).strip()
    
class TextExtractor(BaseExtractor):
    def can_handle(self, tag:Tag) -> bool:
        return tag.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'code', 'pre']
    
    def extract(self, tag:Tag) -> List[str]:
        return self._clean_text(tag)

class ListExtractor(BaseExtractor):
    def can_handle(self, tag:Tag) -> bool:
        return tag.name in ['ul', 'ol']
    
    def extract(self, tag:Tag) -> List[str]:
        return ', '.join([self._clean_text(item) for item in tag.find_all('li')])

class TableExtractor(BaseExtractor):
    def can_handle(self, tag:Tag) -> bool:
        return tag.name == 'table'
    
    def extract(self, tag:Tag) -> List[str]:
        rows = []
        for row in tag.find_all('tr'):
            cells = [self._clean_text(cell) for cell in row.find_all(['th', 'td'])]
            rows.append(','.join(cells))
        return '\n'.join(rows)

class PQLExampleExtractor(BaseExtractor):
    def can_handle(self, tag:Tag) -> bool:
        if tag.name != 'table':
            return False
        nested_table = tag.find('table')
        if not nested_table:
            return False
        th = nested_table.find('th')
        if not th:
            return False
        return th.text.strip() == 'Query'
    
    def extract(self, tag:Tag) -> List[str]:
        description = self._clean_text(tag.find_all('p')[1])
        queries = [self._clean_text(item) for item in tag.find_all('pre')]
        # Get all nested tables from the example
        sub_tables = tag.find_next('table').find_next('table').find_all('table')
        # Extract input tables (all but last) and output table (last one)
        input_tables = []
        # Find the td containing all input tables
        input_td = tag.find_next('table').find_next('table').find('td')
        # Get all p tags that precede tables
        table_name_tags = input_td.find_all('p')

        for i, table in enumerate(sub_tables[:-1]):
            table_content = []
            if i < len(table_name_tags):
                table_name = self._clean_text(table_name_tags[i])
                table_content.append(table_name)
            
            rows = []
            for row in table.find_all('tr'):
                cells = [self._clean_text(cell) for cell in row.find_all(['th', 'td'])]
                rows.append(','.join(cells))
            table_content.append('\n'.join(rows))
            input_tables.append('\n'.join(table_content))
        
        # Process output table
        output_rows = []
        for row in sub_tables[-1].find_all('tr'):
            cells = [self._clean_text(cell) for cell in row.find_all(['th', 'td'])]
            output_rows.append(','.join(cells))
        output_table = '\n'.join(output_rows)
        
        return (
            "Description: " + description + "\n"
            "Queries: " + ", ".join(queries) + "\n"
            "Input Tables: " + "\n" + "\n".join(input_tables) + "\n"
            "Output Table: " + "\n" + output_table + "\n"
        )

class ContentExtractor:
    """
    Coordinates the extraction of content from tags.
    """
    def __init__(self):
        self.extractors = [
            TextExtractor(),
            ListExtractor(),
            PQLExampleExtractor(),
            TableExtractor()
        ]   
    
    def extract_content(self, tags: List[Tag]) -> str:
        content_parts = []
        for tag in tags:
            for extractor in self.extractors:
                if extractor.can_handle(tag):
                    content = extractor.extract(tag)
                    if content:
                        content_parts.append(content)
                    break
        return '\n'.join(content_parts)

class DocumentCollector:
    """Main class for collecting and processing documents"""
    def __init__(self):
        self.content_extractor = ContentExtractor()
    
    def collect_documents(self) -> List[Document]:
        """Collects and processes all documents"""
        links = self._extract_document_links()
        return [self._collect_single_document(link) for link in links]

    def _extract_document_links(self) -> List[str]:
        """Extracts all relevant document links from the main page"""
        soup = self._get_soup(settings.links_url)
        sidebar = soup.find('ul', attrs={'class': ['toc', 'nav', 'nav-site-sidebar']})
        links = [a.get('href') for a in sidebar.find_all('a', recursive=True)]
        return [link for link in links if self._is_wanted_link(link)]

    def _collect_single_document(self, link: str) -> Document:
        print(f"Collecting document: {link}")
        """Collects and processes a single document"""
        full_url = f"{settings.base_url}{link}"
        soup = self._get_soup(full_url)
        
        # Extract title and main content
        title = self._extract_title(soup)
        content_tags = self._extract_content_tags(soup)
        content = self.content_extractor.extract_content(content_tags)
        
        return Document(content=content, link=full_url, title=title)

    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extracts the document title"""
        title_tag = soup.find('h1')
        return title_tag.get_text(strip=True) if title_tag else None

    def _extract_content_tags(self, soup: BeautifulSoup) -> List[Tag]:
        """Extracts relevant content tags from the document"""
        root = soup.find('section')
        if not root:
            return []
        
        tags = []
        for tag in root.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                                'p', 'pre', 'code', 'table', 'ul', 'ol']):
            if self._should_include_tag(tag):
                tags.append(tag)
        return tags

    def _should_include_tag(self, tag: Tag) -> bool:
        """Determines if a tag should be included in the content"""
        if tag.name in ['p', 'code', 'pre'] and tag.find_parent(['li', 'ul', 'ol', 'table']):
            return False
        if tag.name == 'table' and tag.find_parent('table'):
            return False
        return True

    def _is_wanted_link(self, link: str) -> bool:
        """Checks if a link should be processed"""
        return link and all(path not in link for path in settings.unwanted_paths)

    @staticmethod
    def _get_soup(url: str) -> BeautifulSoup:
        """Fetches and parses a URL into BeautifulSoup"""
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

