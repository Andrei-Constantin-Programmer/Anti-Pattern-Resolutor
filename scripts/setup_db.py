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
# Loading the fix AP text file and splitting it into chunks
ap_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "ap.txt")
loader = TextLoader(ap_file, encoding="utf-8")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    length_function=len
)
split_docs = text_splitter.split_documents(docs)

# Loading the Researched Anti Pattern JSON files

antipatterns_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "antipatterns")
srp_documents = []

for filename in os.listdir(antipatterns_dir):
    if filename.endswith(".json"):
        file_path = os.path.join(antipatterns_dir, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file {file_path}: {e}")
                continue
            
            for entry in data:
                #Flatten into string when file is entered
                content_parts = [f"{k.capitalize()}: {', '.join(v) if isinstance(v, list) else v}" for k, v in entry.items()]
                content = "\n".join(content_parts)
                srp_documents.append(Document(page_content=content, metadata={"source": filename}))

# Combining all the documents 

all_docs = split_docs + srp_documents

print("Number of documents loaded: ", len(all_docs))
# Store the split documents in a vector database
embedding = OllamaEmbeddings(model=settings.EMBEDDING_MODEL)
persist_dir = str(settings.VECTOR_DB_DIR)
if not os.path.exists(persist_dir):
    os.makedirs(persist_dir)
vectordb = Chroma(
    embedding_function=embedding,
    persist_directory=persist_dir
)
vectordb.add_documents(all_docs)
vectordb.persist()

print("Successful! Chunk number: ", vectordb._collection.count())