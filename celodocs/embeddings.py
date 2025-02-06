from sentence_transformers import SentenceTransformer
import numpy as np


def chunk_document(document:str, max_token=256):
    chunks = []

    #identify pql example, table etc...