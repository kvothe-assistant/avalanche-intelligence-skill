"""Document store for structured data using SQLite."""

import sqlite3
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os


class DocumentStore:
    """Document store for structured data persistence."""

    def __init__(self, db_path: str = "data/documents/intelligence.db"):
        """Initialize document store.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = None

        # Create database directory
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self._init_db()

    def _init_db(self):
        """Initialize SQLite database and create tables."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Create documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                type TEXT,
                content TEXT NOT NULL,
                author TEXT,
                timestamp TEXT NOT NULL,
                entities TEXT,
                metadata TEXT,
                url TEXT,
                created_at TEXT NOT NULL
            )
        ''')

        # Create signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                entity TEXT,
                confidence REAL,
                data TEXT,
                triggered_at TEXT NOT NULL,
                acknowledged BOOLEAN DEFAULT 0
            )
        ''')

        # Create projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                status TEXT,
                description TEXT,
                tvl REAL,
                launch_date TEXT,
                updated_at TEXT NOT NULL
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON documents(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON documents(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON documents(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entity ON signals(entity)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category ON projects(category)')

        self.conn.commit()

    def add_document(self, document: Dict[str, Any]) -> bool:
        """Add a document to the store.

        Args:
            document: Document object

        Returns:
            Success status
        """
        if not document or "id" not in document:
            return False

        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO documents
                (id, source, type, content, author, timestamp, entities, metadata, url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                document.get("id"),
                document.get("source"),
                document.get("type"),
                document.get("content"),
                json.dumps(document.get("author", {})),
                document.get("timestamp"),
                json.dumps(document.get("entities", [])),
                json.dumps(document.get("metadata", {})),
                document.get("url"),
                datetime.now().isoformat(),
            ))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding document: {e}")
            self.conn.rollback()
            return False

    def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Add multiple documents to the store.

        Args:
            documents: List of document objects

        Returns:
            Number of documents added
        """
        if not documents:
            return 0

        added = 0
        for document in documents:
            if self.add_document(document):
                added += 1

        return added

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Document object or None
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return self._row_to_document(row)

        except Exception as e:
            print(f"Error getting document: {e}")
            return None

    def search_documents(
        self,
        query: str,
        source: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search documents by content.

        Args:
            query: Search query
            source: Filter by source (optional)
            limit: Maximum results

        Returns:
            List of matching documents
        """
        try:
            cursor = self.conn.cursor()

            # Build query
            sql = 'SELECT * FROM documents WHERE content LIKE ?'
            params = [f'%{query}%']

            if source:
                sql += ' AND source = ?'
                params.append(source)

            sql += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [self._row_to_document(row) for row in rows]

        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    def get_recent_documents(
        self,
        hours: int = 24,
        source: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent documents from time range.

        Args:
            hours: Hours back from now
            source: Filter by source (optional)
            limit: Maximum results

        Returns:
            List of recent documents
        """
        try:
            cursor = self.conn.cursor()

            cutoff_time = (datetime.now() - datetime.timedelta(hours=hours)).isoformat()

            sql = 'SELECT * FROM documents WHERE timestamp > ?'
            params = [cutoff_time]

            if source:
                sql += ' AND source = ?'
                params.append(source)

            sql += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [self._row_to_document(row) for row in rows]

        except Exception as e:
            print(f"Error getting recent documents: {e}")
            return []

    def add_signal(self, signal: Dict[str, Any]) -> bool:
        """Add a signal to the store.

        Args:
            signal: Signal object

        Returns:
            Success status
        """
        if not signal or "id" not in signal:
            return False

        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO signals
                (id, type, entity, confidence, data, triggered_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                signal.get("id"),
                signal.get("type"),
                signal.get("entity"),
                signal.get("confidence"),
                json.dumps(signal.get("data", {})),
                datetime.now().isoformat(),
            ))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding signal: {e}")
            self.conn.rollback()
            return False

    def get_signals(
        self,
        hours: int = 24,
        acknowledged: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get signals from time range.

        Args:
            hours: Hours back from now
            acknowledged: Filter by acknowledged status
            limit: Maximum results

        Returns:
            List of signals
        """
        try:
            cursor = self.conn.cursor()

            cutoff_time = (datetime.now() - datetime.timedelta(hours=hours)).isoformat()

            sql = 'SELECT * FROM signals WHERE triggered_at > ?'
            params = [cutoff_time]

            if acknowledged is not None:
                sql += ' AND acknowledged = ?'
                params.append(1 if acknowledged else 0)

            sql += ' ORDER BY triggered_at DESC LIMIT ?'
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [self._row_to_signal(row) for row in rows]

        except Exception as e:
            print(f"Error getting signals: {e}")
            return []

    def acknowledge_signal(self, signal_id: str) -> bool:
        """Acknowledge a signal.

        Args:
            signal_id: Signal ID

        Returns:
            Success status
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE signals SET acknowledged = 1 WHERE id = ?',
                (signal_id,)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error acknowledging signal: {e}")
            self.conn.rollback()
            return False

    def add_project(self, project: Dict[str, Any]) -> bool:
        """Add a project to the store.

        Args:
            project: Project object

        Returns:
            Success status
        """
        if not project or "id" not in project:
            return False

        try:
            cursor = self.conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO projects
                (id, name, category, status, description, tvl, launch_date, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project.get("id"),
                project.get("name"),
                project.get("category"),
                project.get("status"),
                project.get("description"),
                project.get("tvl"),
                project.get("launch_date"),
                datetime.now().isoformat(),
            ))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding project: {e}")
            self.conn.rollback()
            return False

    def get_projects(
        self,
        category: str = None,
        status: str = None
    ) -> List[Dict[str, Any]]:
        """Get projects from the store.

        Args:
            category: Filter by category (optional)
            status: Filter by status (optional)

        Returns:
            List of projects
        """
        try:
            cursor = self.conn.cursor()

            sql = 'SELECT * FROM projects WHERE 1=1'
            params = []

            if category:
                sql += ' AND category = ?'
                params.append(category)

            if status:
                sql += ' AND status = ?'
                params.append(status)

            sql += ' ORDER BY updated_at DESC'
            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [self._row_to_project(row) for row in rows]

        except Exception as e:
            print(f"Error getting projects: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Statistics dictionary
        """
        try:
            cursor = self.conn.cursor()

            # Count documents
            cursor.execute('SELECT COUNT(*) FROM documents')
            doc_count = cursor.fetchone()[0]

            # Count signals
            cursor.execute('SELECT COUNT(*) FROM signals WHERE acknowledged = 0')
            signal_count = cursor.fetchone()[0]

            # Count projects
            cursor.execute('SELECT COUNT(*) FROM projects')
            project_count = cursor.fetchone()[0]

            # Get database size
            db_size = os.path.getsize(self.db_path)

            return {
                "document_count": doc_count,
                "active_signal_count": signal_count,
                "project_count": project_count,
                "db_size_bytes": db_size,
                "db_size_mb": db_size / (1024 * 1024),
            }

        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

    def _row_to_document(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to document object."""
        return {
            "id": row["id"],
            "source": row["source"],
            "type": row["type"],
            "content": row["content"],
            "author": json.loads(row["author"]) if row["author"] else {},
            "timestamp": row["timestamp"],
            "entities": json.loads(row["entities"]) if row["entities"] else [],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            "url": row["url"],
            "created_at": row["created_at"],
        }

    def _row_to_signal(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to signal object."""
        return {
            "id": row["id"],
            "type": row["type"],
            "entity": row["entity"],
            "confidence": row["confidence"],
            "data": json.loads(row["data"]) if row["data"] else {},
            "triggered_at": row["triggered_at"],
            "acknowledged": bool(row["acknowledged"]),
        }

    def _row_to_project(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert database row to project object."""
        return {
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "status": row["status"],
            "description": row["description"],
            "tvl": row["tvl"],
            "launch_date": row["launch_date"],
            "updated_at": row["updated_at"],
        }

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
