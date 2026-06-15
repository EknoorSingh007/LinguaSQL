from sqlalchemy import Table, MetaData, Column, Integer, String, inspect, insert, select, delete, update
from backend.db.database import engine

from sqlalchemy import inspect
from backend.db.database import engine

def list_tables() -> list[str]:
    """Return a list of all table names in the SQLite database."""
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_columns(table_name: str) -> dict[str, str]:
    """
    Return a mapping of column_name → SQL type (as string),
    e.g. { "id": "INTEGER", "name": "TEXT" }.
    """
    inspector = inspect(engine)
    cols = inspector.get_columns(table_name)
    return {col["name"]: str(col["type"]) for col in cols}

def list_collections():
    """
    Return all table names in the database.
    """
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_table(table_name: str):
    """
    Reflect a table definition from the database.
    """
    meta = MetaData()
    return Table(table_name, meta, autoload_with=engine)

def insert_record(table_name: str, document: dict) -> int:
    """
    Insert a new row; returns the new primary key.
    """
    table = get_table(table_name)
    with engine.begin() as conn:
        result = conn.execute(insert(table).values(**document))
        return result.inserted_primary_key[0]

def find_records(table_name: str, filters: dict) -> list[dict]:
    """
    SELECT * FROM table WHERE filters...
    """
    table = get_table(table_name)
    stmt = select(table)
    for k, v in filters.items():
        stmt = stmt.where(table.c[k] == v)
    with engine.begin() as conn:
        rows = conn.execute(stmt).all()
        return [dict(r._mapping) for r in rows]

def delete_records(table_name: str, filters: dict) -> int:
    """
    DELETE FROM table WHERE filters...
    Returns number of rows deleted.
    """
    table = get_table(table_name)
    stmt = delete(table)
    for k, v in filters.items():
        stmt = stmt.where(table.c[k] == v)
    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.rowcount

def update_records(table_name: str, filters: dict, new_data: dict) -> int:
    """
    UPDATE table SET new_data WHERE filters...
    Returns number of rows updated.
    """
    table = get_table(table_name)
    stmt = update(table).values(**new_data)
    for k, v in filters.items():
        stmt = stmt.where(table.c[k] == v)
    with engine.begin() as conn:
        result = conn.execute(stmt)
        return result.rowcount
