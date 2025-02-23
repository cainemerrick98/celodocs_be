import unittest
from celodocs.core.embeddings import DocumentPreprocessor, DocumentEmbedder
from celodocs.core.document_collection import Document
import os

class TestDocumentPreprocessor(unittest.TestCase):
    def setUp(self):
        self.preprocessor = DocumentPreprocessor()

    def test_match_table(self):
        text = "Some text <table>table content</table> more text"
        self.assertTrue(DocumentPreprocessor.match(text))
        
    def test_match_pql(self):
        text = "Some text <pql_example>SELECT *</pql_example> more text"
        self.assertTrue(DocumentPreprocessor.match(text))
        
    def test_no_match(self):
        text = "Regular text without special elements"
        self.assertFalse(DocumentPreprocessor.match(text))

    def test_extract_elements_simple(self):
        text = "First sentence. Second sentence."
        elements = DocumentPreprocessor.extract_elements(text)
        self.assertEqual(elements, ["First sentence.", "Second sentence."])

    def test_extract_elements_with_table(self):
        text = "Before table. <table>table content</table> After table."
        elements = DocumentPreprocessor.extract_elements(text)
        self.assertEqual(elements, ["Before table.", "<table>table content</table>", "After table."])

    def test_extract_elements_with_pql(self):
        text = "Before PQL. <pql_example>SELECT *</pql_example> After PQL."
        elements = DocumentPreprocessor.extract_elements(text)
        self.assertEqual(elements, ["Before PQL.", "<pql_example>SELECT *</pql_example>", "After PQL."])

    def test_extract_elements_complex(self):
        text = "Start. <table>T1</table> Middle. <pql_example>Q1</pql_example> End."
        elements = DocumentPreprocessor.extract_elements(text)
        self.assertEqual(elements, [
            "Start.",
            "<table>T1</table>",
            "Middle.",
            "<pql_example>Q1</pql_example>",
            "End."
        ])


class TestDocumentEmbedder(unittest.TestCase):
    def setUp(self):
        self.embedder = DocumentEmbedder()

    def test_chunk_document_simple(self):
        doc = Document(content="Short document for testing.", title="Test", link="http://test.com")
        chunks = self.embedder.chunk_document(doc)
        self.assertEqual(chunks, ["Short document for testing."])

    def test_chunk_document_with_table(self):
        doc = Document(content="Before. <table>content</table> After.", title="Test", link="http://test.com")
        chunks = self.embedder.chunk_document(doc)
        self.assertEqual(chunks, ["Before.", "content", "After."])

    def test_chunk_document_long(self):
        # Create a long document that exceeds max_tokens
        long_text = " ".join(["word"] * 300)  # Should exceed default max_tokens of 256
        doc = Document(content=long_text, title="Test", link="http://test.com")
        chunks = self.embedder.chunk_document(doc)
        self.assertTrue(len(chunks) > 1)  # Should be split into multiple chunks

    def test_create_embeddings(self):
        documents = [
            Document(content="Test document one.", title="Test 1", link="http://test1.com"),
            Document(content="Test document two.", title="Test 2", link="http://test2.com")
        ]
        embeddings_path = "test_embeddings.npy"
        documents_path = "test_documents.json"
        
        try:
            embeddings, chunks = self.embedder.create_embeddings(
                documents,
                embeddings_path=embeddings_path,
                documents_path=documents_path
            )
            
            # Check if files were created
            self.assertTrue(os.path.exists(embeddings_path))
            self.assertTrue(os.path.exists(documents_path))
            
            # Check embeddings shape
            self.assertEqual(len(embeddings), len(chunks))
            self.assertEqual(embeddings.shape[1], 384)  # MiniLM-L6-v2 produces 384-dimensional embeddings
            
        finally:
            # Cleanup
            if os.path.exists(embeddings_path):
                os.remove(embeddings_path)
            if os.path.exists(documents_path):
                os.remove(documents_path)
