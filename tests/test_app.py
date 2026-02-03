"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice basketball skills and compete in inter-school games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "liam@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve swimming techniques and train for competitions",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Explore theater arts and perform in school plays",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["isabella@mergington.edu", "mia@mergington.edu"]
        },
        "Art Studio": {
            "description": "Create visual art with various mediums including painting and sculpture",
            "schedule": "Wednesdays, 3:00 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ethan@mergington.edu", "charlotte@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Prepare for science competitions and conduct experiments",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["william@mergington.edu", "amelia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through debates",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["benjamin@mergington.edu", "harper@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_get_activities_includes_activity_details(self, client):
        """Test that activity details are included"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_success(self, client):
        """Test successful signup of a new student"""
        email = "newstudent@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for Chess Club"
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup to non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_already_registered(self, client):
        """Test signup when student is already registered"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_multiple_activities(self, client):
        """Test student can sign up for multiple different activities"""
        email = "multitasker@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from Chess Club"
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_not_registered(self, client):
        """Test unregister when student is not registered"""
        email = "notregistered@mergington.edu"
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not registered for this activity"
    
    def test_unregister_and_resign_up(self, client):
        """Test that a student can re-sign up after unregistering"""
        email = "michael@mergington.edu"
        
        # Unregister
        unregister_response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Re-sign up
        signup_response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify student is back
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]


class TestActivityWorkflow:
    """Integration tests for complete activity workflows"""
    
    def test_complete_signup_workflow(self, client):
        """Test a complete workflow of signing up and unregistering"""
        email = "workflow@mergington.edu"
        activity = "Drama Club"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify added
        after_signup = client.get("/activities")
        after_signup_data = after_signup.json()
        assert len(after_signup_data[activity]["participants"]) == initial_count + 1
        assert email in after_signup_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify removed
        after_unregister = client.get("/activities")
        after_unregister_data = after_unregister.json()
        assert len(after_unregister_data[activity]["participants"]) == initial_count
        assert email not in after_unregister_data[activity]["participants"]
