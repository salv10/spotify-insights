from datetime import datetime, timezone

import pytest

from app.models.spotify_snapshot import SpotifySnapshot
from app.models.spotify_snapshot_artist import SpotifySnapshotArtist
from app.models.spotify_snapshot_track import SpotifySnapshotTrack
from app.services.spotify_snapshot_service import compare_artist_snapshots, compare_track_snapshots


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

@pytest.mark.parametrize(
    "previous_rank,current_rank,expected_change,expected_status",
    [
        (1, 1, 0, "same"),
        (2, 1, 1, "up"),
        (1, 2, -1, "down"),
    ],
)
def test_compare_track_snapshots_rank_change(
    previous_rank, current_rank, expected_change, expected_status
):
    previous_snapshot = create_test_snapshot()

    previous_track = SpotifySnapshotTrack(
        spotify_track_id="track1",
        name="Track test",
        artist_name="Artist test",
        rank=previous_rank,
    )

    previous_snapshot.tracks = [previous_track]

    current_snapshot = create_test_snapshot()

    current_track = SpotifySnapshotTrack(
        spotify_track_id="track1",
        name="Track test",
        artist_name="Artist test",
        rank=current_rank,
    )
    current_snapshot.tracks = [current_track]

    result = compare_track_snapshots(current_snapshot, previous_snapshot)

    assert len(result) == 1
    assert result[0]["current_rank"] == current_rank
    assert result[0]["previous_rank"] == previous_rank
    assert result[0]["rank_change"] == expected_change
    assert result[0]["status"] == expected_status
    assert result[0]["spotify_track_id"] == "track1"
    assert result[0]["name"] == "Track test"
    assert result[0]["artist_name"] == "Artist test"

def test_compare_track_snapshots_new():
    previous_snapshot = create_test_snapshot()
    previous_snapshot.tracks = []

    current_snapshot = create_test_snapshot()

    current_track = SpotifySnapshotTrack(
        spotify_track_id="track1",
        name="Track test",
        artist_name="Artist test",
        rank=1,
    )

    current_snapshot.tracks = [current_track]

    result = compare_track_snapshots(current_snapshot, previous_snapshot)

    assert len(result) == 1
    assert result[0]["current_rank"] == 1
    assert result[0]["spotify_track_id"] == "track1"
    assert result[0]["previous_rank"] is None
    assert result[0]["rank_change"] is None
    assert result[0]["status"] == "new"
    assert result[0]["name"] == "Track test"
    assert result[0]["artist_name"] == "Artist test"

def test_compare_track_snapshots_out():
    previous_snapshot = create_test_snapshot()

    previous_track = SpotifySnapshotTrack(
        spotify_track_id="track1",
        name="Track test",
        artist_name="Artist test",
        rank=1,
    )

    previous_snapshot.tracks = [previous_track]

    current_snapshot = create_test_snapshot()

    current_snapshot.tracks = []

    result = compare_track_snapshots(current_snapshot, previous_snapshot)

    assert len(result) == 1
    assert result[0]["current_rank"] is None
    assert result[0]["spotify_track_id"] == "track1"
    assert result[0]["previous_rank"] == 1
    assert result[0]["rank_change"] is None
    assert result[0]["status"] == "out"
    assert result[0]["name"] == "Track test"
    assert result[0]["artist_name"] == "Artist test"
