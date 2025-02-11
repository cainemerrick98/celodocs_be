from celodocs.embeddings import create_embeddings
from celodocs.scraper import scrape_celonis_documentation, extract_pql_function_documents
import os

EXAMPLES_PATH = r'tests\test_examples'
OUTPUTS_PATH = r'tests\test_page_outputs'



if __name__ == '__main__':
    links = extract_pql_function_documents()
    documents = scrape_celonis_documentation(links)
    print('scraped')
    create_embeddings(documents)

    