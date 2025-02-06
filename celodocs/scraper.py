from bs4 import BeautifulSoup, Tag
from celodocs.extraction import extract_page_content
import requests

BASE_URL = r'https://docs.celonis.com/en/'
LINKS_URL = r'https://docs.celonis.com/en/getting-started-with-the-celonis-platform.html'
UNWANTED = ['Release Notes']

def scrape_celonis_documentation(document_links:list[str]):
    for link in document_links:
        soup_tags = extract_soup_tags(link)
        page_content = extract_page_content(soup_tags)
        yield page_content

def extract_document_links() -> list[str]:
    resp = requests.get(LINKS_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    sidebar = soup.find('ul', attrs={'class':['toc', 'nav', 'nav-site-sidebar']})
    return list(map(lambda x: x.get('href'), sidebar.find_all('a', recursive=True)))

def extract_soup_tags(link):
    resp = requests.get(rf'{BASE_URL + link}')    
    soup = BeautifulSoup(resp.text, 'html.parser')
    root = soup.find('section')
    return extract_main_content_tags(root)

def extract_main_content_tags(root:Tag):
    tags = []
    for tag in root.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'code', 'table', 'ul', 'ol']):
        if tag.name in ['p', 'code', 'pre'] and tag.find_parent(['li', 'ul', 'ol', 'table']):
            continue 
        elif tag.name == 'table' and tag.find_parent('table'):
            continue
        else:
            tags.append(tag)
    
    return tags
