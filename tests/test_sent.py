from nltk.tokenize import sent_tokenize
import unittest


class TestSent(unittest.TestCase):

    def test_1(self):
        text = 'hello, how are you. The things is real\nbut I am not. a,b,c,\n1,2,3\n4,5,6\n\n'
        print(sent_tokenize(text))
