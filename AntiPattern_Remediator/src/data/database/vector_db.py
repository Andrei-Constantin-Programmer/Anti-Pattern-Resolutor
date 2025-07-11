from langchain_chroma import Chroma

from src.core.llm_models.create_embedding import EmbeddingCreator
from config.settings import settings

class VectorDBManager:
    """
    Database manager for vector databases.
    This class is responsible for managing the connection to the vector database.
    """

    def __init__(self, persist_dir=None):
        # Initialize the database connection
        self.persist_dir = persist_dir or str(settings.VECTOR_DB_DIR)
        print(self.persist_dir)
        self.embedding = EmbeddingCreator.create_embedding(
            provider=settings.LLM_PROVIDER,
            model_name=settings.EMBEDDING_MODEL
        )
        self.db = Chroma(
            embedding_function=self.embedding,
            persist_directory=self.persist_dir
        )
    
    def get_db(self):
        """
        Get the vector database instance.
        
        Returns:
            Chroma: The vector database instance.
        """
        return self.db

    def add_documents(self, documents):
        """
        Add documents to the vector database.
        
        Args:
            documents: List of documents to add.
        """
        try:
            self.db.add_documents(documents)
            self.db.persist()
            print("Documents added successfully.")
        except Exception as e:
            print(f"Error adding documents: {e}")