"""Tests for activity signup and unregister endpoints."""

import pytest


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, sample_email):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert sample_email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant(self, client, sample_email):
        """Test that signup actually adds the participant to the activity."""
        # Get initial state
        activities_before = client.get("/activities").json()
        participants_before = activities_before["Chess Club"]["participants"]
        
        # Signup
        client.post(
            "/activities/Chess Club/signup",
            params={"email": sample_email}
        )
        
        # Check that participant was added
        activities_after = client.get("/activities").json()
        participants_after = activities_after["Chess Club"]["participants"]
        
        assert sample_email in participants_after
        assert len(participants_after) == len(participants_before) + 1
    
    def test_signup_duplicate_email(self, client, existing_email):
        """Test that signing up with an email already in the activity fails."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": existing_email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_invalid_activity(self, client, sample_email):
        """Test that signing up for a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_missing_email_parameter(self, client):
        """Test that signup without email parameter fails."""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # Unprocessable entity (missing parameter)
    
    def test_signup_multiple_activities(self, client, sample_email):
        """Test that a student can sign up for multiple activities."""
        # Sign up for first activity
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": sample_email}
        )
        assert response2.status_code == 200
        
        # Verify both signups worked
        activities = client.get("/activities").json()
        assert sample_email in activities["Chess Club"]["participants"]
        assert sample_email in activities["Programming Class"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client, existing_email):
        """Test successful unregister from an activity."""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": existing_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert existing_email in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_unregister_removes_participant(self, client, existing_email):
        """Test that unregister actually removes the participant from the activity."""
        # Get initial state
        activities_before = client.get("/activities").json()
        participants_before = activities_before["Chess Club"]["participants"]
        
        # Unregister
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": existing_email}
        )
        
        # Check that participant was removed
        activities_after = client.get("/activities").json()
        participants_after = activities_after["Chess Club"]["participants"]
        
        assert existing_email not in participants_after
        assert len(participants_after) == len(participants_before) - 1
    
    def test_unregister_not_signed_up(self, client, sample_email):
        """Test that unregistering when not signed up fails."""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_invalid_activity(self, client, existing_email):
        """Test that unregistering from a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            params={"email": existing_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_missing_email_parameter(self, client):
        """Test that unregister without email parameter fails."""
        response = client.post("/activities/Chess Club/unregister")
        assert response.status_code == 422  # Unprocessable entity (missing parameter)
    
    def test_signup_then_unregister(self, client, sample_email):
        """Test the full flow: signup then unregister."""
        # Sign up
        signup_response = client.post(
            "/activities/Chess Club/signup",
            params={"email": sample_email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup worked
        activities = client.get("/activities").json()
        assert sample_email in activities["Chess Club"]["participants"]
        
        # Unregister
        unregister_response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": sample_email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister worked
        activities_after = client.get("/activities").json()
        assert sample_email not in activities_after["Chess Club"]["participants"]
