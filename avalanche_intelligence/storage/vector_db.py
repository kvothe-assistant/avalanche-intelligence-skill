"""Vector database for semantic search using ChromaDB."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


class VectorDatabase:
    """Vector database for semantic search and deduplication."""

    def __init__(self, db_path: str = "data/vector_db"):
        """Initialize vector database.

        Args:
            db_path: Path to store database
        """
        self.db_path = db_path
        self.collection = None
        self.client = None

        if CHROMADB_AVAILABLE:
            self._init_db()

    def _init_db(self):
        """Initialize ChromaDB client and collection."""
        os.makedirs(self.db_path, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name="intelligence")
        except:
            self.collection = self.client.create_collection(
                name="intelligence",
                metadata={"hnsw:space": "cosine"}
            )

    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        ids: List[str] = None,
        batch_size: int = 100
    ) -> int:
        """Add documents to vector database.

        Args:
            documents: List of documents to add
            ids: List of document IDs (optional, auto-generated if None)
            batch_size: Batch size for insertion

        Returns:
            Number of documents added
        """
        if not CHROMADB_AVAILABLE or not self.collection:
            return 0

        if not documents:
            return 0

        # Generate IDs if not provided
        if ids is None:
            ids = [f"doc_{datetime.now().timestamp()}_{i}" for i in range(len(documents))]

        # Prepare data for ChromaDB
        embeddings = []
        texts = []
        metadatas = []

        for doc in documents:
            text = doc.get("content", "")
            texts.append(text)
            metadatas.append({
                "source": doc.get("source", ""),
                "timestamp": doc.get("timestamp", ""),
                "author": doc.get("author", {}).get("username", ""),
                "type": doc.get("type", ""),
            })

        # Add in batches
        added = 0
        for i in range(0, len(texts), batch_size):
            batch_end = min(i + batch_size, len(texts))
            batch_ids = ids[i:batch_end]
            batch_texts = texts[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]

            try:
                self.collection.add(
                    ids=batch_ids,
                    documents=batch_texts,
                    metadatas=batch_metadatas
                )
                added += len(batch_ids)
            except Exception as e:
                print(f"Error adding batch to vector DB: {e}")

        return added

    def search(
        self,
        query: str,
        n_results: int = 10,
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents.

        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Metadata filters

        Returns:
            List of similar documents with scores
        """
        if not CHROMADB_AVAILABLE or not self.collection:
            return []

        results = []

        try:
            if filter_metadata:
                query_results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=filter_metadata
                )
            else:
                query_results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results
                )

            # Parse results
            for i in range(len(query_results["ids"][0])):
                results.append({
                    "id": query_results["ids"][0][i],
                    "document": query_results["documents"][0][i],
                    "metadata": query_results["metadatas"][0][i],
                    "distance": query_results["distances"][0][i],
                    "similarity": 1 - query_results["distances"][0][i],  # Convert to similarity
                })

        except Exception as e:
            print(f"Error searching vector DB: {e}")

        return results

    def delete(self, ids: List[str]) -> int:
        """Delete documents by IDs.

        Args:
            ids: List of document IDs to delete

        Returns:
            Number of documents deleted
        """
        if not CHROMADB_AVAILABLE or not self.collection:
            return 0

        try:
            self.collection.delete(ids=ids)
            return len(ids)
        except Exception as e:
            print(f"Error deleting from vector DB: {e}")
            return 0

    def count(self) -> int:
        """Get total number of documents in database.

        Returns:
            Document count
        """
        if not CHROMADB_AVAILABLE or not self.collection:
            return 0

        try:
            return self.collection.count()
        except Exception as e:
            print(f"Error counting vector DB: {e}")
            return 0

    def clear(self) -> bool:
        """Clear all documents from database.

        Returns:
            Success status
        """
        if not CHROMADB_AVAILABLE or not self.collection:
            return False

        try:
            self.client.delete_collection(name="intelligence")
            self.collection = self.client.create_collection(
                name="intelligence",
                metadata={"hnsw:space": "cosine"}
            )
            return True
        except Exception as e:
            print(f"Error clearing vector DB: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Statistics dictionary
        """
        stats = {
            "available": CHROMADB_AVAILABLE,
            "path": self.db_path,
            "count": self.count(),
        }

        if not CHROMADB_AVAILABLE:
            stats["error"] = "ChromaDB not installed"

        return stats
