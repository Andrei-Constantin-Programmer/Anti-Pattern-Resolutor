import os
import json
from pathlib import Path
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OllamaEmbeddings

def load_json_documents(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    for item in data:
        meta = {
            "name": item.get("name", "Unknown"),
            "category": item.get("category", "General"),
            "language": item.get("language", "Java"),
            "severity": item.get("severity", "Unknown"),
        }
        documents.append(Document(page_content=item["description"], metadata={**meta, "type": "description"}))
        if "problem" in item:
            documents.append(Document(page_content=item["problem"], metadata={**meta, "type": "problem"}))
        if "remediation" in item:
            documents.append(Document(page_content=item["remediation"], metadata={**meta, "type": "remediation"}))
        if "limitation" in item:
            documents.append(Document(page_content=item["limitation"], metadata={**meta, "type": "limitation"}))
        for ex in item.get("examples", []):
            documents.append(Document(page_content=ex["code"], metadata={**meta, "type": "example", "reason": ex.get("reason", "")}))
    return documents

def main():
    data_dir = Path("data")
    persist_dir = "vector_store"
    embedding = OllamaEmbeddings(model="nomic-embed-text")
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding)

    all_docs = []
    for file in data_dir.glob("*.json"):
        print(f"📥 Seeding: {file.name}")
        docs = load_json_documents(file)
        vectordb.add_documents(docs)
        all_docs.extend(docs)

    vectordb.persist()
    print(f"✅ Seeded {len(all_docs)} documents from {len(list(data_dir.glob('*.json')))} JSON files.")

if __name__ == "__main__":
    main()
