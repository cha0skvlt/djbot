import sqlite3
import os

DB_MAPPING = {
    "pulse": "pulse.db",
    "beat": "beat.db"
}

def init_databases():
    for playlist, db_file in DB_MAPPING.items():
        if not os.path.exists(db_file):
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            c.execute(
                '''
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    title TEXT NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''
            )
            conn.commit()
            conn.close()


def add_track(playlist_name: str, file_path: str, title: str):
    db_file = DB_MAPPING.get(playlist_name)
    if not db_file:
        raise ValueError("Неправильное имя плейлиста")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        'INSERT INTO tracks (file_path, title) VALUES (?, ?)',
        (file_path, title)
    )
    conn.commit()
    conn.close()


def get_last_tracks(playlist_name: str, limit: int = 3):
    db_file = DB_MAPPING.get(playlist_name)
    if not db_file or not os.path.exists(db_file):
        return []
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        'SELECT file_path, title FROM tracks ORDER BY added_at DESC LIMIT ?',
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return [{"file_path": row[0], "title": row[1]} for row in rows]


def get_all_tracks(playlist_name: str):
    """Return all tracks for radio mode ordered by added_at."""
    db_file = DB_MAPPING.get(playlist_name)
    if not db_file or not os.path.exists(db_file):
        return []
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(
        'SELECT file_path, title FROM tracks ORDER BY added_at'
    )
    rows = c.fetchall()
    conn.close()
    return [{"file_path": row[0], "title": row[1]} for row in rows]


def get_full_playlist(playlist_name: str):
    """Return list of file paths for the whole playlist."""
    db_file = DB_MAPPING.get(playlist_name)
    if not db_file or not os.path.exists(db_file):
        return []
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('SELECT file_path FROM tracks ORDER BY added_at')
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows if os.path.exists(row[0])]
