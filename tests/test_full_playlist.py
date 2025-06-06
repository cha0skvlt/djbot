import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / 'bot'))
import database


def test_get_full_playlist(tmp_path, monkeypatch):
    db_map = {
        'pulse': tmp_path / 'pulse.db',
    }
    monkeypatch.setattr(database, 'DB_MAPPING', {k: str(v) for k, v in db_map.items()})
    database.init_databases()
    sample = tmp_path / 'song.mp3'
    sample.touch()
    database.add_track('pulse', str(sample), 'Song')
    files = database.get_full_playlist('pulse')
    assert files == [str(sample)]
