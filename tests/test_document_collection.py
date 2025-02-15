import unittest
from bs4 import BeautifulSoup, Tag
from unittest.mock import patch, Mock
from celodocs.core.document_collection import (
    Document,
    DocumentCollector,
    TextExtractor,
    ListExtractor,
    TableExtractor,
    PQLExampleExtractor,
    ContentExtractor
)

class TestDocumentCollector(unittest.TestCase):
    def setUp(self):
        self.collector = DocumentCollector()
        
    @patch('celodocs.core.document_collection.requests.get')
    def test_extract_document_links(self, mock_get):
        # Mock the HTML response
        mock_html = '''
        <ul class="toc nav nav-site-sidebar">
            <li><a href="getting-started.html">Getting Started</a></li>
            <li><a href="release-notes.html">Release Notes</a></li>
            <li><a href="power.html">Power</a></li>
        </ul>
        '''
        mock_response = Mock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response
        
        links = self.collector._extract_document_links()
        
        self.assertIsInstance(links, list)
        self.assertIn('getting-started.html', links)
        self.assertIn('power.html', links)
        self.assertNotIn('release-notes.html', links)  # Should be filtered out

    @patch('celodocs.core.document_collection.requests.get')
    def test_collect_single_document(self, mock_get):
        # Mock the HTML response
        mock_html = '''
        <section>
            <h1>Test Document</h1>
            <p>Test content</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
        </section>
        '''
        mock_response = Mock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response
        
        document = self.collector._collect_single_document('test.html')
        
        self.assertIsInstance(document, Document)
        self.assertEqual(document.title, 'Test Document')
        self.assertIn('Test content', document.content)
        self.assertTrue(document.link.endswith('test.html'))

class TestContentExtractors(unittest.TestCase):
    def setUp(self):
        self.soup = BeautifulSoup('<html></html>', 'html.parser')
        
    def test_text_extractor(self):
        extractor = TextExtractor()
        
        # Test paragraph
        p_tag = self.soup.new_tag('p')
        p_tag.string = 'Test paragraph'
        self.assertTrue(extractor.can_handle(p_tag))
        self.assertEqual(extractor.extract(p_tag), 'Test paragraph')
        
        # Test heading
        h1_tag = self.soup.new_tag('h1')
        h1_tag.string = 'Test heading'
        self.assertTrue(extractor.can_handle(h1_tag))
        self.assertEqual(extractor.extract(h1_tag), 'Test heading')

    def test_list_extractor(self):
        extractor = ListExtractor()
        
        # Create a list
        ul_tag = self.soup.new_tag('ul')
        for item in ['Item 1', 'Item 2']:
            li = self.soup.new_tag('li')
            li.string = item
            ul_tag.append(li)
            
        self.assertTrue(extractor.can_handle(ul_tag))
        self.assertEqual(extractor.extract(ul_tag), 'Item 1, Item 2')

    def test_table_extractor(self):
        extractor = TableExtractor()
        
        # Create a simple table
        table_html = '''
        <table>
            <tr><th>Header 1</th><th>Header 2</th></tr>
            <tr><td>Data 1</td><td>Data 2</td></tr>
        </table>
        '''
        table = BeautifulSoup(table_html, 'html.parser').find('table')
        
        self.assertTrue(extractor.can_handle(table))
        extracted = extractor.extract(table)
        self.assertIn('Header 1,Header 2', extracted)
        self.assertIn('Data 1,Data 2', extracted)

    def test_pql_example_extractor(self):
        extractor = PQLExampleExtractor()
        
        # Create a PQL example table based on pu_avg.html example
        pql_html = '''
        <div>
            <table>
                <tr>
                    <td>
                        <p>[1]</p>
                        <p>Calculate the average of the case table values for each company code:</p>
                    </td>
                </tr>
                <tr>
                    <td>
                        <div class="informaltable">
                            <table>
                                <thead>
                                    <tr><th>Query</th></tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>
                                            <p>Column1</p>
                                            <pre>"companyDetail"."companyCode"</pre>
                                            <p>Column2</p>
                                            <pre>PU_AVG ( "companyDetail" , "caseTable"."value" )</pre>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>
                        <div class="informaltable">
                            <table>
                                <thead>
                                    <tr><th>Input</th><th>Output</th></tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>
                                            <p>caseTable</p>
                                            <table>
                                                <thead>
                                                    <tr><th>caseId : int</th><th>companyCode : string</th><th>value : int</th></tr>
                                                </thead>
                                                <tbody>
                                                    <tr><td>1</td><td>'001'</td><td>600</td></tr>
                                                    <tr><td>2</td><td>'001'</td><td>400</td></tr>
                                                    <tr><td>3</td><td>'001'</td><td>200</td></tr>
                                                    <tr><td>4</td><td>'002'</td><td>300</td></tr>
                                                    <tr><td>5</td><td>'002'</td><td>300</td></tr>
                                                    <tr><td>6</td><td>'003'</td><td>200</td></tr>
                                                </tbody>
                                            </table>
                                            <p>companyDetail</p>
                                            <table>
                                                <thead>
                                                    <tr><th>companyCode : string</th><th>country : string</th></tr>
                                                </thead>
                                                <tbody>
                                                    <tr><td>'001'</td><td>'DE'</td></tr>
                                                    <tr><td>'002'</td><td>'DE'</td></tr>
                                                    <tr><td>'003'</td><td>'US'</td></tr>
                                                </tbody>
                                            </table>
                                            <p>Foreign Keys</p>
                                            <table>
                                                <tbody>
                                                    <tr>
                                                        <td>caseTable.companyCode</td>
                                                        <td>companyDetail.companyCode</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </td>
                                        <td>
                                            <p>Result</p>
                                            <table>
                                                <thead>
                                                    <tr><th>Column1 : string</th><th>Column2 : float</th></tr>
                                                </thead>
                                                <tbody>
                                                    <tr><td>'001'</td><td>400.0</td></tr>
                                                    <tr><td>'002'</td><td>300.0</td></tr>
                                                    <tr><td>'003'</td><td>200.0</td></tr>
                                                </tbody>
                                            </table>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </td>
                </tr>
            </table>
        </div>
        '''
        
        pql_table = BeautifulSoup(pql_html, 'html.parser').find('table')
        self.assertTrue(extractor.can_handle(pql_table))
        extracted = extractor.extract(pql_table)

        print(extracted)
        
        # Test that all key components are present
        self.assertIn('Calculate the average of the case table values for each company code', extracted)
        self.assertIn('"companyDetail"."companyCode"', extracted)
        self.assertIn('PU_AVG("companyDetail","caseTable"."value")', extracted)
        self.assertIn('caseTable', extracted)
        self.assertIn('companyDetail', extracted)
        self.assertIn('caseId: int,companyCode: string,value: int', extracted)
        self.assertIn("1,'001',600", extracted)
        self.assertIn("6,'003',200", extracted)

class TestContentExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = ContentExtractor()
        self.soup = BeautifulSoup('<html></html>', 'html.parser')

    def test_extract_content(self):
        # Create a mix of content
        content_html = '''
        <div>
            <h1>Test Document</h1>
            <p>Test paragraph</p>
            <ul>
                <li>List item 1</li>
                <li>List item 2</li>
            </ul>
            <table>
                <tr><th>Header</th></tr>
                <tr><td>Data</td></tr>
            </table>
        </div>
        '''
        soup = BeautifulSoup(content_html, 'html.parser')
        tags = soup.find_all(['h1', 'p', 'ul', 'table'])
        
        content = self.extractor.extract_content(tags)
        
        self.assertIn('Test Document', content)
        self.assertIn('Test paragraph', content)
        self.assertIn('List item 1', content)
        self.assertIn('Header', content)
        self.assertIn('Data', content)

if __name__ == '__main__':
    unittest.main() 