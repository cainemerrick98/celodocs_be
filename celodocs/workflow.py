from celodocs.embeddings import create_embeddings
from celodocs.scraper import scrape_celonis_documentation, extract_pql_function_documents
import os

EXAMPLES_PATH = r'tests\test_examples'
OUTPUTS_PATH = r'tests\test_page_outputs'


def write_to_text_file(file_name:str, data:str) -> None:
    with open(os.path.join(os.getcwd(), OUTPUTS_PATH, file_name), 'w') as file:
        file.write(data)
    return None

if __name__ == '__main__':
    links = extract_pql_function_documents()
    links = list(filter(lambda x: x == 'and.html', links))
    documents = scrape_celonis_documentation(links)
    write_to_text_file('and.txt', documents[0])



    print('scraped')
    create_embeddings(documents)

    