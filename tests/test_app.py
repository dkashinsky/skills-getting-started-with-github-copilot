"""
Test suite for Mergington High School Activities API

Tests the FastAPI application endpoints using TestClient and AAA pattern:
- Arrange: Set up test data and client
- Act: Execute the API call
- Assert: Verify the response
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Verify that GET /activities returns all activities with correct structure"""
        # Arrange
        expected_keys = {"Chess Club", "Programming Class", "Gym Class", "Soccer Team",
                        "Basketball Club", "Art Workshop", "Dance Club", "Science Club", "Debate Team"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert set(activities.keys()) == expected_keys

    def test_get_activities_contains_required_fields(self, client):
        """Verify that each activity contains all required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert set(activity_data.keys()) == required_fields
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupEndpoint:
    """Test POST /activities/{name}/signup endpoint"""

    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "test@example.com"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_activity_not_found(self, client):
        """Test signup fails when activity doesn't exist"""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@example.com"

        # Act
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate(self, client):
        """Test signup fails when student is already signed up"""
        # Arrange
        activity_name = "Chess Club"
        email = "duplicate@example.com"

        # Act - First signup
        response1 = client.post(f"/activities/{activity_name}/signup", params={"email": email})
        assert response1.status_code == 200

        # Act - Second signup with same email
        response2 = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response2.status_code == 400
        data = response2.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]


class TestRemoveEndpoint:
    """Test DELETE /activities/{name}/signup endpoint"""

    def test_remove_successful(self, client):
        """Test successful removal of a participant"""
        # Arrange
        activity_name = "Programming Class"
        email = "remove@example.com"

        # First add the participant
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_remove_activity_not_found(self, client):
        """Test removal fails when activity doesn't exist"""
        # Arrange
        activity_name = "Fake Activity"
        email = "test@example.com"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_remove_participant_not_found(self, client):
        """Test removal fails when participant is not signed up"""
        # Arrange
        activity_name = "Chess Club"
        email = "notsignedup@example.com"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that GET / redirects to static files"""
        # Arrange

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"