from datetime import datetime, timezone

from app.models.spotify_snapshot import SpotifySnapshot
from app.models.spotify_snapshot_artist import SpotifySnapshotArtist
from app.services.spotify_snapshot_service import compare_artist_snapshots


def create_test_snapshot():
    return SpotifySnapshot(
        captured_at=datetime.now(timezone.utc),
        time_range="medium_term",
    )

def test_compare_artist_snapshots_same():

    previous_snapshot = create_test_snapshot()

    previous_artist = SpotifySnapshotArtist(
        spotify_artist_id="annalisa",
        name="Annalisa",
        rank=1,
    )

    previous_snapshot.artists = [previous_artist]

    current_snapshot = create_test_snapshot()

    current_artist = SpotifySnapshotArtist(
        spotify_artist_id="annalisa",
        name="Annalisa",
        rank=1,
    )

    current_snapshot.artists = [current_artist]

    result = compare_artist_snapshots(current_snapshot, previous_snapshot)

    assert len(result) == 1
    assert result[0]["current_rank"] == 1
    assert result[0]["previous_rank"] == 1  
    assert result[0]["rank_change"] == 0
    assert result[0]["status"] == "same"

def test_compare_artist_snapshots_up():
    
    previous_snapshot = create_test_snapshot()

    previous_artist = SpotifySnapshotArtist(
        spotify_artist_id="annalisa",
        name="Annalisa",
        rank=2,
    )

    previous_snapshot.artists = [previous_artist]

    current_snapshot = create_test_snapshot()

    current_artist = SpotifySnapshotArtist(
        spotify_artist_id="annalisa",
        name="Annalisa",
        rank=1,
    )

    current_snapshot.artists = [current_artist]

    result = compare_artist_snapshots(current_snapshot, previous_snapshot)

    assert len(result) == 1
    assert result[0]["current_rank"] == 1
    assert result[0]["previous_rank"] == 2  
    assert result[0]["rank_change"] == 1
    assert result[0]["status"] == "up"

def test_compare_artist_snapshots_down():
    
    previous_snapshot = create_test_snapshot()

    previous_artist = SpotifySnapshotArtist(
        spotify_artist_id="annalisa",
        name="Annalisa",
        rank=1,
    )

    previous_snapshot.artists = [previous_artist]

    current_snapshot = create_test_snapshot()

    current_artist = SpotifySnapshotArtist(
        spotify_artist_id="annalisa",
        name="Annalisa",
        rank=2,
    )

    current_snapshot.artists = [current_artist]

    result = compare_artist_snapshots(current_snapshot, previous_snapshot)

    assert len(result) == 1
    assert result[0]["current_rank"] == 2
    assert result[0]["previous_rank"] == 1  
    assert result[0]["rank_change"] == -1
    assert result[0]["status"] == "down"

def test_compare_artist_snapshots_new():
    
    previous_snapshot = create_test_snapshot()
    previous_snapshot.artists = []

    current_snapshot = create_test_snapshot()

    current_artist = SpotifySnapshotArtist(
        spotify_artist_id="annalisa",
        name="Annalisa",
        rank=2,
    )

    current_snapshot.artists = [current_artist]

    result = compare_artist_snapshots(current_snapshot, previous_snapshot)

    assert len(result) == 1
    assert result[0]["current_rank"] == 2
    assert result[0]["spotify_artist_id"] == "annalisa"
    assert result[0]["previous_rank"] is None
    assert result[0]["rank_change"] is None
    assert result[0]["status"] == "new"

def test_compare_artist_snapshots_out():
    
    previous_snapshot = create_test_snapshot()

    previous_artist = SpotifySnapshotArtist(
        spotify_artist_id="annalisa",
        name="Annalisa",
        rank=1,
    )

    previous_snapshot.artists = [previous_artist]

    current_snapshot = create_test_snapshot()

    current_snapshot.artists = []

    result = compare_artist_snapshots(current_snapshot, previous_snapshot)

    assert len(result) == 1
    assert result[0]["current_rank"] is None
    assert result[0]["spotify_artist_id"] == "annalisa"
    assert result[0]["previous_rank"] == 1
    assert result[0]["rank_change"] is None
    assert result[0]["status"] == "out"