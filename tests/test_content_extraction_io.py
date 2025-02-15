import os
import bs4
from celodocs.core.document_collection import ContentExtractor
from celodocs.core.document_collection import DocumentCollector

EXAMPLES_PATH = r'tests\test_examples'
OUTPUTS_PATH = r'tests\test_page_outputs'

def read_html(file_name: str) -> bs4.BeautifulSoup:
    """Read an HTML file and return a BeautifulSoup object."""
    with open(os.path.join(os.getcwd(), EXAMPLES_PATH, file_name), 'r') as file:
        data = file.read()
    return bs4.BeautifulSoup(data, 'html.parser')

def write_text(file_name: str, data: str) -> None:
    """Write text content to a file in the outputs directory."""
    with open(os.path.join(os.getcwd(), OUTPUTS_PATH, file_name), 'w') as file:
        file.write(data)
    return None

def process_test_case(input_file: str, output_file: str) -> None:
    """Process an HTML test case by extracting content and writing to output.
    
    Args:
        input_file: Name of the HTML file in test_examples directory
        output_file: Name of the output file to write in test_page_outputs directory
    """
    # Read the HTML
    soup = read_html(input_file)
    
    # Create content extractor and extract content
    extractor = ContentExtractor()
    content = extractor.extract_content(DocumentCollector()._extract_content_tags(soup))
    
    # Write to output file
    write_text(output_file, content)
    return None 

if __name__ == "__main__":
    process_test_case('pu_avg.html', 'pu_avg_output.txt')
    process_test_case('match_process.html', 'match_process_output.txt')
    process_test_case('round_year.html', 'round_year_output.txt')
    process_test_case('action_flow_modules.html', 'action_flow_module_output.txt')

