"""
SANDEEP Memory — SQLite-backed persistent context store.
Tracks current project, folder, app, recent commands, and user preferences.
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sandeep_memory.db")


class Memory:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._init_db()

    def _init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT,
                result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def set(self, key: str, value):
        val_str = json.dumps(value)
        self.cursor.execute(
            "INSERT INTO state (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, val_str)
        )
        self.conn.commit()

    def get(self, key: str, default=None):
        self.cursor.execute("SELECT value FROM state WHERE key=?", (key,))
        row = self.cursor.fetchone()
        if row:
            try:
                return json.loads(row[0])
            except json.JSONDecodeError:
                return row[0]
        return default

    def add_history(self, command: str, result: str):
        self.cursor.execute("INSERT INTO history (command, result) VALUES (?, ?)", (command, result))
        self.conn.commit()

    def get_recent_history(self, limit: int = 10) -> list:
        self.cursor.execute("SELECT command, result, timestamp FROM history ORDER BY id DESC LIMIT ?", (limit,))
        return [{"command": r[0], "result": r[1], "timestamp": r[2]} for r in self.cursor.fetchall()]

    def clear(self):
        self.cursor.execute("DELETE FROM state")
        self.cursor.execute("DELETE FROM history")
        self.conn.commit()


# Singleton
memory = Memory()
