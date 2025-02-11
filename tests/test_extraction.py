import bs4
import celodocs.extraction as extraction
import unittest
import os
from celodocs.scraper import extract_main_content_tags

EXAMPLES_PATH = r'tests\test_examples'
OUTPUTS_PATH = r'tests\test_page_outputs'

def get_html_example(file_name:str) -> bs4.BeautifulSoup:
    print(os.path.join(os.getcwd(), EXAMPLES_PATH, file_name))
    with open(os.path.join(os.getcwd(), EXAMPLES_PATH, file_name), 'r') as file:
        data = file.read()
        
    return bs4.BeautifulSoup(data, 'html.parser')

def write_to_text_file(file_name:str, data:str) -> None:
    with open(os.path.join(os.getcwd(), OUTPUTS_PATH, file_name), 'w') as file:
        file.write(data)
    return None

class TestExtractionModule(unittest.TestCase):

    def setUp(self):
        return super().setUp()
    
    def test_is_text_element(self):
        p = bs4.Tag(name='p')
        self.assertTrue(extraction.is_text_element(p))

        pre = bs4.Tag(name='pre')
        self.assertTrue(extraction.is_text_element(pre))

        code = bs4.Tag(name='code')
        self.assertTrue(extraction.is_text_element(code))

        table = bs4.Tag(name='table')
        self.assertFalse(extraction.is_text_element(table))

    def test_is_list_element(self):
        ol = bs4.Tag(name='ol')
        self.assertTrue(extraction.is_list_element(ol))

        ul = bs4.Tag(name='ul')
        self.assertTrue(extraction.is_list_element(ul))

        code = bs4.Tag(name='code')
        self.assertFalse(extraction.is_list_element(code))
    
    def test_is_table_element(self):
        table = bs4.Tag(name='table')
        self.assertTrue(extraction.is_table_element(table))

        ul = bs4.Tag(name='ul')
        self.assertFalse(extraction.is_table_element(ul))

    def test_is_pql_example_1(self):
        soup = bs4.BeautifulSoup("<body><table><thead><th>Example</th><thead><tbody><tr><td><table><thead><tr><th>Query</th></tr></thead></table></td></tr></tbody></table></body>",
                                        'html.parser')
        pql_example = soup.find('table')

        self.assertTrue(extraction.is_pql_example(pql_example))
        
        table = bs4.Tag(name='table')
        self.assertFalse(extraction.is_pql_example(table))

    def test_extract_pql_example(self):
        pql_example = get_html_example('pu_sum_example_1.html')
        table = pql_example.find('table')
        self.assertTrue(extraction.is_pql_example(table))
        #use print to validate format.
        print(extraction.extract_pql_example(table))
    
    def test_action_flow_modules_html(self):
        afm = get_html_example('action_flow_modules.html')
        tags = extract_main_content_tags(afm)
        page_content = extraction.extract_page_content(tags)
        write_to_text_file('action_flow_modules.txt', page_content)

    def test_pu_avg_html(self):
        pu_avg = get_html_example('pu_avg.html')
        tags = extract_main_content_tags(pu_avg)
        page_content = extraction.extract_page_content(tags)
        write_to_text_file('pu_avg.txt', page_content)
    
    def test_round_year_html(self):
        pu_avg = get_html_example('round_year.html')
        tags = extract_main_content_tags(pu_avg)
        page_content = extraction.extract_page_content(tags)
        write_to_text_file('round_year.txt', page_content)

    