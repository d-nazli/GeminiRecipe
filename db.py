import sqlite3
from fastapi import HTTPException



def get_db():
    conn = None
    try:
        conn = sqlite3.connect("greenmirror.db", check_same_thread=False, timeout=10)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"DB bağlantı hatası: {str(e)}")
    finally:
        if conn:
            conn.close()
