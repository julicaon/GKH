"""Ensure lightweight schema patches for MVP (no Alembic required)."""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine


def ensure_schema_patches(engine: Engine) -> None:
    """Add columns introduced after first create_all (idempotent)."""
    statements = [
        "ALTER TABLE tickets ADD COLUMN cancel_reason TEXT",
    ]
    with engine.begin() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
            except Exception:
                # Column already exists (Postgres/SQLite) — ignore
                pass
