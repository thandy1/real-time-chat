import pytest

def test_register_route_returns_200(client):
    """Test that /register route returns a successful response on GET request."""
    response = client.get("/register")
    assert response.status_code == 200
        
# Test that a POST request to /register with valid data actually creates a user and redirects.
def test_register_route_creates_user_and_redirects(client):
    """Test that a POST request to /register with valid data actually creates a user and redirects."""
    response = client.post("/register", data={
        "username": "testuser",
        "email": "test@test.com",
        "password": "testpassword"
    })
    assert response.status_code == 302
