import json
import sqlite3
import time
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

RULE_TTL_SECONDS = 6 * 3600       # 6 hours
TEXT_TTL_SECONDS = 7 * 24 * 3600  # 7 days

_SCHEMA = """
CREATE TABLE IF NOT EXISTS rules (
    document_id TEXT PRIMARY KEY,
    raw_json TEXT NOT NULL,
    fetched_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS rule_texts (
    document_id TEXT PRIMARY KEY,
    full_text TEXT,
    ria_text TEXT,
    parsed_at REAL NOT NULL
);
"""


class Cache:
    def __init__(self, db_path: str = ":memory:"):
        self._conn = sqlite3.connect(db_path)
        self._conn.executescript(_SCHEMA)

    def get_cached_rule(self, document_id: str) -> Optional[dict]:
        row = self._conn.execute(
            "SELECT raw_json, fetched_at FROM rules WHERE document_id = ?",
            (document_id,),
        ).fetchone()
        if row is None:
            return None
        raw_json, fetched_at = row
        if time.time() - fetched_at > RULE_TTL_SECONDS:
            return None
        return json.loads(raw_json)

    def cache_rule(self, document_id: str, raw_json: dict) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO rules (document_id, raw_json, fetched_at) VALUES (?, ?, ?)",
            (document_id, json.dumps(raw_json), time.time()),
        )
        self._conn.commit()

    def get_cached_texts(self, document_id: str) -> Tuple[Optional[str], Optional[str]]:
        row = self._conn.execute(
            "SELECT full_text, ria_text, parsed_at FROM rule_texts WHERE document_id = ?",
            (document_id,),
        ).fetchone()
        if row is None:
            return None, None
        full_text, ria_text, parsed_at = row
        if time.time() - parsed_at > TEXT_TTL_SECONDS:
            return None, None
        return full_text, ria_text

    def cache_texts(self, document_id: str, full_text: Optional[str], ria_text: Optional[str]) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO rule_texts (document_id, full_text, ria_text, parsed_at) VALUES (?, ?, ?, ?)",
            (document_id, full_text, ria_text, time.time()),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
