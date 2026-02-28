"""
utils/db.py
───────────
Thin database layer — provides a context-managed MySQL connection
and a helper that executes a query and returns results.
"""

import mysql.connector
from mysql.connector import Error
from config import config


def get_connection():
    """Return a new MySQL connection using the active config."""
    return mysql.connector.connect(
        host     = config.DB_HOST,
        port     = config.DB_PORT,
        user     = config.DB_USER,
        password = config.DB_PASSWORD,
        database = config.DB_NAME
    )


def execute_query(query: str, params: tuple = (), fetch: str = "none"):
    """
    Execute a SQL query and optionally return results.

    Parameters
    ----------
    query  : SQL string (use %s placeholders)
    params : tuple of values
    fetch  : "one"  → fetchone()
             "all"  → fetchall()
             "none" → no fetch (INSERT / UPDATE / DELETE)

    Returns
    -------
    Depends on `fetch`:
      "one"  → dict or None
      "all"  → list[dict]
      "none" → {"affected_rows": int, "lastrowid": int}
    """
    conn   = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)   # rows as dicts
        cursor.execute(query, params)

        if fetch == "one":
            return cursor.fetchone()

        if fetch == "all":
            return cursor.fetchall()

        # DML — commit and return metadata
        conn.commit()
        return {
            "affected_rows": cursor.rowcount,
            "lastrowid":     cursor.lastrowid
        }

    except Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Database error: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def execute_transaction(queries: list):
    """
    Execute multiple (query, params) pairs atomically.

    Parameters
    ----------
    queries : list of (sql_string, params_tuple)

    Returns
    -------
    list of lastrowid for each query
    """
    conn   = None
    cursor = None
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        results = []

        for query, params in queries:
            cursor.execute(query, params)
            results.append(cursor.lastrowid)

        conn.commit()
        return results

    except Error as e:
        if conn:
            conn.rollback()
        raise Exception(f"Transaction failed: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
