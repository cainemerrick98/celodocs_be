import unittest
import celodocs.embeddings as embeddings

class TestSpecialPatterns(unittest.TestCase):

    def setUp(self):
        return super().setUp()
    
    def test_special_pattern_table(self):
        table_ptrn = '<table>1,2,3,4,5</table>'
        splits = embeddings.SpecialPatterns.table.split(table_ptrn)
        self.assertTrue(splits[1], '1,2,3,4,5')
    
    def test_special_pattern_split_produces_no_empties(self):
        table_ptrn = '1,2,3,4,5'
        splits = embeddings.SpecialPatterns.table.split(table_ptrn)
        self.assertTrue(splits[0], '1,2,3,4,5')

    def test_special_pattern_pql_example(self):
        table_ptrn = '<pql_example>1,2,3,4,5</pql_example>'
        splits = embeddings.SpecialPatterns.pql_example.split(table_ptrn)
        self.assertTrue(splits[1], '1,2,3,4,5')
    
    def test_special_pattern_match_true(self):
        table_ptrn = 'before the pql example<pql_example>1,2,3,4,5</pql_example>after the pql example'
        self.assertTrue(embeddings.SpecialPatterns.match(table_ptrn))

    def test_special_pattern_extract_elements(self):
        document = '<pql_example>1,2,3,4,5</pql_example>Hi its caine here<table>1,2,3,4,5</table>Hi again'
        elements = embeddings.SpecialPatterns.extract_elements(document)
        self.assertEqual(len(elements), 4)
        self.assertEqual(elements[3], 'Hi again')

class TestEmbeddings(unittest.TestCase):

    def setUp(self):
        return super().setUp()
    
    def test_chunk_simple_text(self):
        text = 'Hello this should be easy to chunk. But is it'
        chunks = embeddings.chunk_document(text)
        self.assertIsInstance(chunks, list)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

    def test_chunk_with_pql_example(self):
        document = 'Hello. <pql_example>1,2,3,4</pql_example>Im final chunk'
        chunks = embeddings.chunk_document(document)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0], 'Hello.')
        self.assertEqual(chunks[1], '1,2,3,4')
        self.assertEqual(chunks[2], 'Im final chunk')
