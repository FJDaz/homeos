#!/usr/bin/env python3
"""
brs_storage.py — Mission 46
Couche de persistance SQLite pour le Brainstorming (BRS).
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger

class BRSStorage:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initialise les tables si elles n'existent pas."""
        logger.info(f"[BRS] Initializing SQLite storage at {self.db_path}")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table Sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    prompt TEXT,
                    buffer_answers TEXT,
                    created_at TEXT
                )
            """)
            
            # Table Messages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    provider TEXT,
                    role TEXT,
                    content TEXT,
                    created_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            
            # FTS5 — migration auto si schema obsolète
            try:
                cursor.execute("SELECT session_id FROM messages_fts LIMIT 1")
            except sqlite3.OperationalError:
                # Ancien schema sans session_id → drop + recreate
                cursor.execute("DROP TABLE IF EXISTS messages_fts")
                try:
                    cursor.execute("""
                        CREATE VIRTUAL TABLE messages_fts
                        USING fts5(session_id UNINDEXED, provider UNINDEXED, content)
                    """)
                except sqlite3.OperationalError as e:
                    logger.warning(f"[BRS] FTS5 not supported: {e}")

            # Table Nuggets (Pépites)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nuggets (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    provider TEXT,
                    text TEXT,
                    created_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            
            # Table Documents (PRD, etc.)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    type TEXT,
                    path TEXT,
                    content TEXT,
                    created_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id)
                )
            """)
            
            conn.commit()

    def save_session(self, session_id: str, prompt: str, buffer_answers: Dict[str, str], user_id: str = "default"):
        """Sauvegarde ou met à jour une session."""
        created_at = datetime.now().isoformat()
        buffer_json = json.dumps(buffer_answers)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (id, user_id, prompt, buffer_answers, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET 
                    prompt=excluded.prompt,
                    buffer_answers=excluded.buffer_answers
            """, (session_id, user_id, prompt, buffer_json, created_at))
            conn.commit()

    def save_message(self, session_id: str, provider: str, role: str, content: str):
        """Sauvegarde un message (accumulé ou unitaire)."""
        msg_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (id, session_id, provider, role, content, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (msg_id, session_id, provider, role, content, created_at))
            # Alimentation FTS5 (role=assistant uniquement — pas besoin d'indexer les prompts user)
            if role == "assistant":
                cursor.execute(
                    "INSERT INTO messages_fts(session_id, provider, content) VALUES (?, ?, ?)",
                    (session_id, provider, content)
                )
            conn.commit()

    def save_nugget(self, session_id: str, provider: str, text: str) -> Dict[str, Any]:
        """Sauvegarde une pépite."""
        nugget_id = str(uuid.uuid4())[:8]
        created_at = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO nuggets (id, session_id, provider, text, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (nugget_id, session_id, provider, text, created_at))
            conn.commit()
            
        return {
            "id": nugget_id,
            "text": text,
            "provider": provider,
            "timestamp": created_at
        }

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les données d'une session."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data["buffer_answers"] = json.loads(data["buffer_answers"])
                return data
        return None

    def get_messages(self, session_id: str, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère l'historique d'une session (filtrable par provider)."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            sql = "SELECT provider, role, content, created_at FROM messages WHERE session_id = ?"
            params = [session_id]
            
            if provider:
                sql += " AND provider = ?"
                params.append(provider)
                
            sql += " ORDER BY created_at ASC"
            
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def search(self, query: str, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Recherche plein texte dans les messages (FTS5)."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # snippet() : colonne 2 = content, balises highlight, extrait 20 tokens
            sql = """
                SELECT
                    session_id,
                    provider,
                    snippet(messages_fts, 2, '<b>', '</b>', '...', 20) as excerpt
                FROM messages_fts
                WHERE content MATCH ?
            """
            params = [query]
            if user_id:
                sql += " AND session_id IN (SELECT id FROM sessions WHERE user_id = ?)"
                params.append(user_id)
            sql += " ORDER BY rank LIMIT 20"
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_basket(self, session_id: str) -> List[Dict[str, Any]]:
        """Récupère toutes les pépites d'une session."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, text, provider, created_at as timestamp FROM nuggets WHERE session_id = ? ORDER BY created_at DESC", (session_id,))
            return [dict(row) for row in cursor.fetchall()]

    def save_document(self, session_id: str, doc_type: str, path: str, content: str):
        """Sauvegarde un document généré."""
        doc_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO documents (id, session_id, type, path, content, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (doc_id, session_id, doc_type, path, content, created_at))
            conn.commit()

# Singleton logic
BASE_DIR = Path(__file__).parent.parent.parent.parent
db_file = BASE_DIR / "exports" / "brs" / "brs_sessions.db"
storage = BRSStorage(str(db_file))
