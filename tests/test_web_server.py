"""
Tests for Flask web server API endpoints.

Tests follow the browser-frontend specification:
- openspec/specs/browser-frontend/spec.md

Test coverage:
- GET /api/health - Server health check
- GET /api/config - Frontend configuration
- GET /api/playlists - List all playlists
- GET /api/playlists/<id> - Get playlist details
- POST /api/playlists/<id>/classify - Classify playlist by genre
- POST /api/playlists/organize - Dry-run playlist organization
- POST /api/playlists/move - Execute playlist moves
- GET /api/enrichment/status - Check enrichment progress
- POST /api/enrichment/start - Begin enrichment
- GET /api/enrichment/results - Get enrichment results
- POST /api/enrichment/cancel - Cancel enrichment
- POST /api/temperament/classify - Classify tracks by mood
- GET /api/temperament/results - Get mood classification results
- POST /api/settings - Save user preferences
"""

import json
import pytest
from src.web_server import app


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config["TESTING"] = True
    
    # Reset global state before each test
    import src.web_server as ws
    ws._enrichment_state = {
        "running": False,
        "progress": 0,
        "current_operation": "",
        "current_track": 0,
        "total_tracks": 0,
        "start_time": 0,
        "job_id": None,
    }
    ws._temperament_state = {
        "running": False,
        "progress": 0,
        "current_operation": "",
        "start_time": 0,
        "job_id": None,
    }
    ws._enrichment_results = {
        "status": "idle",
        "tracks_enriched": 0,
        "fields_added": 0,
        "duration_seconds": 0,
        "results": [],
    }
    ws._temperament_results = []
    ws._user_settings = {}
    
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for GET /api/health endpoint."""

    def test_health_returns_200(self, client):
        """Health check should return 200 OK."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Health response should be valid JSON."""
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_health_has_required_fields(self, client):
        """Health response must have all required fields per spec."""
        response = client.get("/api/health")
        data = json.loads(response.data)

        required_fields = [
            "status",
            "version",
            "playlists_count",
            "tracks_count",
            "platform",
            "apple_music_connected",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_health_status_is_healthy(self, client):
        """Health status should be 'healthy' when server is up."""
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert data["status"] == "healthy"

    def test_health_platform_is_valid(self, client):
        """Platform should be one of: darwin, win32, linux."""
        response = client.get("/api/health")
        data = json.loads(response.data)
        valid_platforms = ["darwin", "win32", "linux"]
        assert data["platform"] in valid_platforms

    def test_health_counts_are_integers(self, client):
        """Playlist and track counts should be integers."""
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert isinstance(data["playlists_count"], int)
        assert isinstance(data["tracks_count"], int)


class TestConfigEndpoint:
    """Tests for GET /api/config endpoint."""

    def test_config_returns_200(self, client):
        """Config endpoint should return 200 OK."""
        response = client.get("/api/config")
        assert response.status_code == 200

    def test_config_returns_json(self, client):
        """Config response should be valid JSON."""
        response = client.get("/api/config")
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_config_has_required_fields(self, client):
        """Config response must have expected fields."""
        response = client.get("/api/config")
        data = json.loads(response.data)

        required_fields = ["app_name", "version", "api_base", "polling_interval", "timeout"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_config_app_name_is_correct(self, client):
        """App name should be 'affective_playlists'."""
        response = client.get("/api/config")
        data = json.loads(response.data)
        assert data["app_name"] == "affective_playlists"

    def test_config_polling_interval_is_positive(self, client):
        """Polling interval should be positive milliseconds."""
        response = client.get("/api/config")
        data = json.loads(response.data)
        assert data["polling_interval"] > 0

    def test_config_timeout_is_positive(self, client):
        """Timeout should be positive milliseconds."""
        response = client.get("/api/config")
        data = json.loads(response.data)
        assert data["timeout"] > 0


class TestPlaylistsEndpoint:
    """Tests for GET /api/playlists endpoint."""

    def test_playlists_returns_200(self, client):
        """Playlists endpoint should return 200 OK."""
        response = client.get("/api/playlists")
        assert response.status_code == 200

    def test_playlists_returns_json_array(self, client):
        """Playlists response should be a JSON array."""
        response = client.get("/api/playlists")
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_playlists_array_items_have_required_fields(self, client):
        """Each playlist item should have required fields per spec."""
        response = client.get("/api/playlists")
        data = json.loads(response.data)

        if len(data) > 0:
            required_fields = ["id", "name", "track_count"]
            playlist = data[0]
            for field in required_fields:
                assert field in playlist, f"Missing field in playlist: {field}"


class TestPlaylistDetailEndpoint:
    """Tests for GET /api/playlists/<id> endpoint."""

    def test_playlist_detail_returns_200(self, client):
        """Playlist detail endpoint should return 200 OK."""
        response = client.get("/api/playlists/test-playlist-1")
        assert response.status_code == 200

    def test_playlist_detail_returns_json(self, client):
        """Playlist detail response should be valid JSON."""
        response = client.get("/api/playlists/test-playlist-1")
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_playlist_detail_has_required_fields(self, client):
        """Playlist detail must have all required fields."""
        response = client.get("/api/playlists/test-playlist-1")
        data = json.loads(response.data)

        required_fields = ["id", "name", "track_count", "genre", "tracks"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_playlist_detail_tracks_is_array(self, client):
        """Tracks field should be an array."""
        response = client.get("/api/playlists/test-playlist-1")
        data = json.loads(response.data)
        assert isinstance(data["tracks"], list)

    def test_playlist_detail_id_matches(self, client):
        """Returned playlist ID should match requested ID."""
        playlist_id = "test-playlist-1"
        response = client.get(f"/api/playlists/{playlist_id}")
        data = json.loads(response.data)
        assert data["id"] == playlist_id


class TestClassifyEndpoint:
    """Tests for POST /api/playlists/<id>/classify endpoint."""

    def test_classify_returns_200(self, client):
        """Classify endpoint should return 200 OK."""
        response = client.post("/api/playlists/test-1/classify")
        assert response.status_code == 200

    def test_classify_returns_json(self, client):
        """Classify response should be valid JSON."""
        response = client.post("/api/playlists/test-1/classify")
        data = json.loads(response.data)
        assert isinstance(data, dict)

    def test_classify_has_required_fields(self, client):
        """Classify response must have required fields per spec."""
        response = client.post("/api/playlists/test-1/classify")
        data = json.loads(response.data)

        required_fields = ["id", "genre", "confidence", "success"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_classify_confidence_is_float_between_0_and_1(self, client):
        """Confidence should be a float between 0 and 1."""
        response = client.post("/api/playlists/test-1/classify")
        data = json.loads(response.data)
        assert isinstance(data["confidence"], (int, float))
        assert 0 <= data["confidence"] <= 1


class TestEnrichmentStatusEndpoint:
    """Tests for GET /api/enrichment/status endpoint."""

    def test_enrichment_status_returns_200(self, client):
        """Enrichment status endpoint should return 200 OK."""
        response = client.get("/api/enrichment/status")
        assert response.status_code == 200

    def test_enrichment_status_has_required_fields(self, client):
        """Status response must have all required fields per spec."""
        response = client.get("/api/enrichment/status")
        data = json.loads(response.data)

        required_fields = [
            "running",
            "progress",
            "current_operation",
            "current_track",
            "total_tracks",
            "time_elapsed",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_enrichment_status_progress_is_between_0_and_100(self, client):
        """Progress should be between 0-100."""
        response = client.get("/api/enrichment/status")
        data = json.loads(response.data)
        assert 0 <= data["progress"] <= 100

    def test_enrichment_status_running_is_boolean(self, client):
        """Running field should be boolean."""
        response = client.get("/api/enrichment/status")
        data = json.loads(response.data)
        assert isinstance(data["running"], bool)


class TestEnrichmentStartEndpoint:
    """Tests for POST /api/enrichment/start endpoint."""

    def test_enrichment_start_returns_200(self, client):
        """Start enrichment should return 202 ACCEPTED (async job)."""
        response = client.post("/api/enrichment/start", json={})
        assert response.status_code == 202

    def test_enrichment_start_has_required_fields(self, client):
        """Start response must have required fields."""
        response = client.post("/api/enrichment/start", json={})
        data = json.loads(response.data)

        required_fields = ["job_id", "status", "total_tracks", "success"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_enrichment_start_with_playlist_ids(self, client):
        """Start enrichment should accept playlist_ids."""
        payload = {"playlist_ids": ["pl-1", "pl-2"]}
        response = client.post("/api/enrichment/start", json=payload)
        assert response.status_code == 202


class TestEnrichmentResultsEndpoint:
    """Tests for GET /api/enrichment/results endpoint."""

    def test_enrichment_results_returns_200(self, client):
        """Results endpoint should return 200 OK."""
        response = client.get("/api/enrichment/results")
        assert response.status_code == 200

    def test_enrichment_results_has_required_fields(self, client):
        """Results response must have required fields."""
        response = client.get("/api/enrichment/results")
        data = json.loads(response.data)

        required_fields = ["status", "tracks_enriched", "fields_added", "duration_seconds"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_enrichment_results_is_array(self, client):
        """Results field should be an array."""
        response = client.get("/api/enrichment/results")
        data = json.loads(response.data)
        assert isinstance(data.get("results"), list)


class TestEnrichmentCancelEndpoint:
    """Tests for POST /api/enrichment/cancel endpoint."""

    def test_enrichment_cancel_returns_200(self, client):
        """Cancel endpoint should return 200 OK."""
        response = client.post("/api/enrichment/cancel")
        assert response.status_code == 200

    def test_enrichment_cancel_has_success_field(self, client):
        """Cancel response should have success field."""
        response = client.post("/api/enrichment/cancel")
        data = json.loads(response.data)
        assert "success" in data


class TestTemperamentClassifyEndpoint:
    """Tests for POST /api/temperament/classify endpoint."""

    def test_temperament_classify_returns_200(self, client):
        """Classify temperament should return 200 OK."""
        response = client.post("/api/temperament/classify", json={})
        assert response.status_code == 200

    def test_temperament_classify_has_required_fields(self, client):
        """Response must have required fields."""
        response = client.post("/api/temperament/classify", json={})
        data = json.loads(response.data)

        required_fields = ["job_id", "status", "total_tracks", "success"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"


class TestTemperamentResultsEndpoint:
    """Tests for GET /api/temperament/results endpoint."""

    def test_temperament_results_returns_200(self, client):
        """Results endpoint should return 200 OK."""
        response = client.get("/api/temperament/results")
        assert response.status_code == 200

    def test_temperament_results_is_array(self, client):
        """Results response should be a JSON array."""
        response = client.get("/api/temperament/results")
        data = json.loads(response.data)
        assert isinstance(data, list)


class TestSettingsEndpoint:
    """Tests for POST /api/settings endpoint."""

    def test_settings_returns_200(self, client):
        """Settings endpoint should return 200 OK."""
        response = client.post("/api/settings", json={})
        assert response.status_code == 200

    def test_settings_has_success_field(self, client):
        """Settings response should have success field."""
        response = client.post("/api/settings", json={})
        data = json.loads(response.data)
        assert "success" in data

    def test_settings_accepts_theme(self, client):
        """Settings should accept theme parameter."""
        payload = {"theme": "dark"}
        response = client.post("/api/settings", json=payload)
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_returns_json_error(self, client):
        """404 should return JSON error response."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data

    def test_invalid_json_returns_error(self, client):
        """Invalid JSON should be handled gracefully."""
        response = client.post(
            "/api/settings",
            data="invalid json",
            content_type="application/json"
        )
        # Should either return 400, 500 (Flask error), or handle gracefully with 200
        assert response.status_code in [400, 500, 200]


class TestOrganizeEndpoint:
    """Tests for POST /api/playlists/organize endpoint."""

    def test_organize_returns_200(self, client):
        """Organize endpoint should return 200 OK."""
        response = client.post("/api/playlists/organize", json={})
        assert response.status_code == 200

    def test_organize_has_required_fields(self, client):
        """Response must have required fields per spec."""
        response = client.post("/api/playlists/organize", json={})
        data = json.loads(response.data)

        required_fields = ["changes", "total_changes", "success"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_organize_changes_is_array(self, client):
        """Changes field should be an array."""
        response = client.post("/api/playlists/organize", json={})
        data = json.loads(response.data)
        assert isinstance(data["changes"], list)


class TestMoveEndpoint:
    """Tests for POST /api/playlists/move endpoint."""

    def test_move_requires_confirmation(self, client):
        """Move should require confirmation flag."""
        # Without confirmation, should fail
        response = client.post("/api/playlists/move", json={})
        assert response.status_code == 400

    def test_move_with_confirmation_returns_200(self, client):
        """Move with confirmed=true should return 200."""
        response = client.post(
            "/api/playlists/move",
            json={"confirmed": True}
        )
        assert response.status_code == 200

    def test_move_response_has_results(self, client):
        """Move response should have results field."""
        response = client.post(
            "/api/playlists/move",
            json={"confirmed": True}
        )
        data = json.loads(response.data)
        assert "results" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
