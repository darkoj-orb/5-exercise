"""Tests for the basic FastAPI endpoints."""

import pytest


class TestRootEndpoint:
    """Tests for the root GET / endpoint."""

    def test_root_redirect(self, client):
        """Test that GET / returns a redirect to the static HTML file."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_follow_redirect(self, client):
        """Test that following the redirect from GET / returns the HTML file."""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_success(self, client):
        """Test that GET /activities returns a 200 response with all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
    
    def test_get_activities_contains_required_keys(self, client):
        """Test that each activity contains required keys."""
        response = client.get("/activities")
        data = response.json()
        
        required_keys = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)
            assert required_keys.issubset(activity_data.keys())
    
    def test_get_activities_participants_format(self, client):
        """Test that participants list exists and is a list."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)
            for email in activity_data["participants"]:
                assert isinstance(email, str)
                assert "@" in email
    
    def test_get_activities_contains_chess_club(self, client):
        """Test that Chess Club is in the activities list."""
        response = client.get("/activities")
        data = response.json()
        
        assert "Chess Club" in data
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert len(chess_club["participants"]) >= 2
    
    def test_get_activities_contains_programming_class(self, client):
        """Test that Programming Class is in the activities list."""
        response = client.get("/activities")
        data = response.json()
        
        assert "Programming Class" in data
        programming = data["Programming Class"]
        assert "programming" in programming["description"].lower()
        assert programming["max_participants"] == 20
