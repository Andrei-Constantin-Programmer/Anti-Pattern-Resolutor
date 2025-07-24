from tinydb import TinyDB, Query
from config.settings import settings
import os
from typing import List, Dict, Any

class Document:
    """Simple Document class to mimic LangChain Document structure"""
    def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

class TinyDBManager:
    def __init__(self, db_path=None):
        # Default path to 'tinydb.json' at root of static directory
        self.db_path = db_path or os.path.join(str(settings.DATA_DIR), "tinydb.json")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.db = TinyDB(self.db_path)

    def get_db(self):
        """
        Get the TinyDB instance.
        Returns:
            TinyDB: The database instance.
        """
        return self.db

    def add_documents(self, documents):
        """
        Add documents to the TinyDB.
        Args:
            documents (list[dict]): List of dicts representing documents.
        """
        try:
            self.db.insert_multiple(documents)
            print("Documents added successfully.")
        except Exception as e:
            print(f"Error adding documents: {e}")

    def query_documents(self, field, value):
        """
        Query documents from the DB by field and value.
        Args:
            field (str): Field name to match.
            value (Any): Value to match against.
        Returns:
            list[dict]: Matching documents.
        """
        try:
            Doc = Query()
            return self.db.search(Doc[field] == value)
        except Exception as e:
            print(f"Error querying documents: {e}")
            return []

    def clear(self):
        """Wipe the database clean."""
        self.db.truncate()

    def as_retriever(self):
        """Return self as retriever for LangChain compatibility"""
        return self

    def get_relevant_documents(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform keyword search on documents
        Compatible with LangChain retriever interface
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
        Returns:
            list[dict]: Matching documents wrapped in LangChain-compatible format
        """
        if not query.strip():
            return []

        # Split query into keywords and clean them
        keywords = [word.lower().strip() for word in query.split() if word.strip()]

        # Search function that checks if any keyword appears in document content
        def keyword_match(doc):
            # Combine all text fields for searching (adjust these based on your document structure)
            searchable_text = ""
            for field in ['content', 'text', 'description', 'title', 'body', 'page_content']:
                if field in doc:
                    searchable_text += str(doc[field]).lower() + " "

            return any(keyword in searchable_text for keyword in keywords)

        try:
            # Query the database - get all documents and filter manually
            all_docs = self.db.all()
            results = [doc for doc in all_docs if keyword_match(doc)]

            # Score results by number of keyword matches
            scored_results = []
            for doc in results:
                searchable_text = ""
                for field in ['content', 'text', 'description', 'title', 'body', 'page_content']:
                    if field in doc:
                        searchable_text += str(doc[field]).lower() + " "

                score = sum(1 for keyword in keywords if keyword in searchable_text)
                scored_results.append((score, doc))

            # Sort by score and return top results
            scored_results.sort(key=lambda x: x[0], reverse=True)
            raw_results = [doc for score, doc in scored_results[:max_results]]

            # Wrap results in LangChain-compatible Document objects
            wrapped_results = []
            for doc in raw_results:
                # Create a Document object that has .page_content attribute
                page_content = doc.get('content', doc.get('text', str(doc)))
                metadata = doc.get('metadata', doc.copy())  # Use original doc as metadata if no metadata field

                document = Document(page_content=page_content, metadata=metadata)
                wrapped_results.append(document)

            return wrapped_results

        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []

    def search(self, query: str, max_results: int = 5):
        """Direct search method (alias for get_relevant_documents)"""
        return self.get_relevant_documents(query, max_results)

    def invoke(self, input_data, **kwargs):
        """
        LangChain-style invoke method for compatibility
        Args:
            input_data: Can be a string query or dict with 'input' key
        Returns:
            list[dict]: Retrieved documents
        """
        if isinstance(input_data, str):
            query = input_data
        elif isinstance(input_data, dict) and 'input' in input_data:
            query = input_data['input']
        else:
            query = str(input_data)

        return self.get_relevant_documents(query)
