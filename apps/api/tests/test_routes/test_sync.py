import shutil
from pathlib import Path
from unittest.mock import patch


def test_sync_returns_stats(client):
    fake_stats = {
        "files_checked": 3,
        "files_processed": 2,
        "sessions_upserted": 2,
        "providers": [{"name": "claude", "processed": 2}],
    }
    with patch("devlens.routers.sync.SyncEngine") as MockEngine:
        MockEngine.return_value.run.return_value = fake_stats
        response = client.post("/api/sync")

    assert response.status_code == 200
    data = response.json()
    assert data["files_checked"] == 3
    assert data["files_processed"] == 2
    assert data["sessions_upserted"] == 2


def test_sync_method_is_post(client):
    with patch("devlens.routers.sync.SyncEngine") as MockEngine:
        MockEngine.return_value.run.return_value = {
            "files_checked": 0,
            "files_processed": 0,
            "sessions_upserted": 0,
            "providers": [],
        }
        response = client.get("/api/sync")

    assert response.status_code == 405  # Method Not Allowed
