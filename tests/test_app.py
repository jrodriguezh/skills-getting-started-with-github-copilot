"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities(self):
        """Test fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Check a known activity exists
        assert "Basketball" in activities
        assert "Swimming" in activities
        
    def test_activities_have_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity(self):
        """Test signing up a student for an activity"""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
    def test_signup_duplicate_fails(self):
        """Test that signing up the same student twice fails"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
        
    def test_signup_invalid_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Invalid Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_participant(self):
        """Test unregistering a student from an activity"""
        email = "tounregister@mergington.edu"
        
        # First signup
        client.post(
            "/activities/Art Club/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.post(
            "/activities/Art Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
    def test_unregister_not_registered(self):
        """Test unregistering someone who isn't registered"""
        response = client.post(
            "/activities/Drama Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
        
    def test_unregister_invalid_activity(self):
        """Test unregistering from a non-existent activity"""
        response = client.post(
            "/activities/Invalid Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects(self):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
