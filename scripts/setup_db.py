import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

from config.settings import settings
# Fix file path
ap_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "ap.txt")
loader = TextLoader(ap_file, encoding="utf-8")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    length_function=len
)
split_docs = text_splitter.split_documents(docs)
print("Number of documents loaded: ", len(docs))
# Store the split documents in a vector database
embedding = OllamaEmbeddings(model=settings.EMBEDDING_MODEL)
persist_dir = str(settings.VECTOR_DB_DIR)
if not os.path.exists(persist_dir):
    os.makedirs(persist_dir)
vectordb = Chroma(
    embedding_function=embedding,
    persist_directory=persist_dir
)
vectordb.add_documents(split_docs)
vectordb.persist()

print("Successful! Chunk number: ", vectordb._collection.count())