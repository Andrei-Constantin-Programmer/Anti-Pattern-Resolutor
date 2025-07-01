import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings

def setup_vectorstore(doc_path: str, persist_dir: str):
    loader = TextLoader(doc_path, encoding="utf-8")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
    split_docs = text_splitter.split_documents(docs)

    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)

    embedding = OllamaEmbeddings(model="nomic-embed-text")
    vectordb = Chroma(embedding_function=embedding, persist_directory=persist_dir)
    vectordb.add_documents(split_docs)
    vectordb.persist()

    return vectordb
