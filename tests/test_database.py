import os
import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / 'bot'))
import database


def test_add_and_get_tracks(tmp_path, monkeypatch):
    db_map = {
        'pulse': tmp_path / 'pulse.db',
        'beat': tmp_path / 'beat.db'
    }
    monkeypatch.setattr(database, 'DB_MAPPING', {k: str(v) for k, v in db_map.items()})
    database.init_databases()

    database.add_track('pulse', '/tmp/track.mp3', 'Song1')
    database.add_track('pulse', '/tmp/track2.mp3', 'Song2')
    tracks = database.get_last_tracks('pulse', 3)
    titles = [t['title'] for t in tracks]
    assert len(titles) == 2
    assert 'Song1' in titles and 'Song2' in titles
