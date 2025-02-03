from celodocs.scraper import extract_document_links, extract_soup_tags
from bs4 import Tag
import unittest

class TestScraperModule(unittest.TestCase):
    def setUp(self):
        return super().setUp()
    
    def test_extract_document_links(self):
        document_links = extract_document_links()
        self.assertIsInstance(document_links, list)
        self.assertIsInstance(document_links[0], str)
        self.assertTrue('getting-started-with-the-celonis-platform.html' in document_links)

    def test_extract_soup_tags(self):
        link = 'power.html'
        soup_tags = extract_soup_tags(link)
        self.assertIsInstance(soup_tags, list)
        self.assertIsInstance(soup_tags[0], Tag)
        self.assertEqual(soup_tags[0].name, 'h5')
        self.assertEqual(soup_tags[0].text, 'POWER')