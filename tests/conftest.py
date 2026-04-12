import pytest
import os
from app.database import initialize_database
from app import app as test_flask_app

@pytest.fixture()
def app():
    """
    Provides a test instance of the Flask app. Sets the app in testing mode and initializes the database.
    The database is removed after the test is finished.
    """
    test_flask_app.config["TESTING"] = True  
    test_flask_app.config["SECRET_KEY"] = "test-secret-key"    
    initialize_database()
    yield test_flask_app  
    if os.path.exists("tests/test.db"):
        os.remove("tests/test.db")


@pytest.fixture
def client(app):
    """Provides a test HTTP client for making requests to the app without running the server. Used for testing public routes."""
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """
    Provides a test HTTP client for making requests to the app without running the server.
    The client is logged in as a test user after registration.
    """
    client.post("/register", data={
        "username": "testuser",
        "email": "test@test.com",
        "password": "testpassword"
    })
    client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    return client