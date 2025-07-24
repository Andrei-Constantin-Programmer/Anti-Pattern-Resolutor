import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.settings import settings
from src.data.database import TinyDBManager


def main():
    # Load and split `ap.json`
    ap_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "ap.json")
    with open(ap_file, "r", encoding="utf-8") as f:
        try:
            ap_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {ap_file}: {e}")
            sys.exit(1)

    # Split content using LangChain text splitter
    split_docs = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len
    )

    for entry in ap_data:
        content = entry.get("content", "")
        if content:
            chunks = text_splitter.split_text(content)
            split_docs.extend(chunks)

    # Wrap chunks in dicts for TinyDB
    split_dicts = [
        {
            "type": "ap_chunk",
            "content": chunk,
            "source": "ap.json"
        }
        for chunk in split_docs
    ]

    # Load anti-patterns from JSON files
    antipatterns_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "antipatterns")
    srp_dicts = []

    for filename in os.listdir(antipatterns_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(antipatterns_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from {file_path}: {e}")
                    continue

                for entry in data:
                    entry["type"] = "antipattern"
                    entry["source_file"] = filename
                    srp_dicts.append(entry)

    # Combine all records
    all_records = split_dicts + srp_dicts
    print(f"Seeding {len(all_records)} records into TinyDB...")

    # Insert into TinyDB
    db_manager = TinyDBManager()
    db_manager.clear()  # Optional: clean slate
    db_manager.add_documents(all_records)

    print("TinyDB seeding complete!")
