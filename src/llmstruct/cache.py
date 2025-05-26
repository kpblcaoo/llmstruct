# cache.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class JSONCache:
    def __init__(self, db_path: str = "cache.db", cache_dir: str = None, max_size: int = 100, ttl: int = 3600):
        """Initialize SQLite cache for JSON files."""
        # Handle legacy parameter compatibility
        if cache_dir is not None:
            # If cache_dir is provided, use it to construct db_path
            cache_path = Path(cache_dir)
            cache_path.mkdir(exist_ok=True)
            self.db_path = str(cache_path / "cache.db")
        else:
            self.db_path = db_path
            
        self.max_size = max_size
        self.ttl = ttl
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """Create tables for metadata and file paths."""
        with self.conn:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS json_metadata (
                    artifact_id TEXT PRIMARY KEY,
                    path TEXT,
                    summary TEXT,
                    tags TEXT,
                    hash TEXT
                )
            """
            )
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS json_files (
                    artifact_id TEXT PRIMARY KEY,
                    file_path TEXT,
                    FOREIGN KEY (artifact_id) REFERENCES json_metadata(artifact_id)
                )
            """
            )

    def cache_json(
        self,
        json_path: str,
        artifact_id: str,
        summary: str = "",
        tags: List[str] = None,
    ):
        """Cache JSON metadata and store full file path."""
        json_file = Path(json_path)
        if not json_file.exists():
            logging.error(f"JSON file not found: {json_path}")
            return

        with open(json_file, "r", encoding="utf-8") as f:
            content = f.read()
            content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        with self.conn:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO json_metadata
                (artifact_id, path, summary, tags, hash)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    artifact_id,
                    str(json_file),
                    summary,
                    json.dumps(tags or []),
                    content_hash,
                ),
            )
            self.conn.execute(
                """
                INSERT OR REPLACE INTO json_files (artifact_id, file_path)
                VALUES (?, ?)
            """,
                (artifact_id, str(json_file)),
            )
        logging.info(f"Cached JSON: {json_path} with artifact_id: {artifact_id}")

    def get_metadata(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve metadata by artifact_id."""
        cursor = self.conn.execute(
            """
            SELECT path, summary, tags, hash FROM json_metadata WHERE artifact_id = ?
        """,
            (artifact_id,),
        )
        result = cursor.fetchone()
        if result:
            return {
                "path": result[0],
                "summary": result[1],
                "tags": json.loads(result[2]),
                "hash": result[3],
            }
        return None

    def get_full_json(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Load full JSON by artifact_id."""
        cursor = self.conn.execute(
            """
            SELECT file_path FROM json_files WHERE artifact_id = ?
        """,
            (artifact_id,),
        )
        result = cursor.fetchone()
        if result:
            file_path = result[0]
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load JSON {file_path}: {e}")
        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM json_metadata")
        total_entries = cursor.fetchone()[0]
        
        cursor = self.conn.execute("SELECT COUNT(*) FROM json_files")
        total_files = cursor.fetchone()[0]
        
        # Get database file size
        db_path = Path(self.db_path)
        db_size = db_path.stat().st_size if db_path.exists() else 0
        
        return {
            "total_entries": total_entries,
            "total_files": total_files,
            "max_size": self.max_size,
            "ttl": self.ttl,
            "db_path": self.db_path,
            "db_size_bytes": db_size,
            "db_size_mb": round(db_size / (1024 * 1024), 2)
        }

    def clear(self):
        """Clear all cache entries."""
        with self.conn:
            self.conn.execute("DELETE FROM json_files")
            self.conn.execute("DELETE FROM json_metadata")
        logging.info("Cache cleared")

    def close(self):
        """Close database connection."""
        self.conn.close()
