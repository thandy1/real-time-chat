import pytest
import os
# Must be set before app is imported. This ensures the test database is used from the start.
os.environ["DATABASE_FILE"] = "test.db" 

from app import app as flask_app
from app.database import get_database_connection, initialize_database


@pytest.fixture
def app():
    """Creates a fresh test app instance with a clean database for each test."""
    flask_app.config["TESTING"] = True  # Propagate exceptions instead of returning errors
    flask_app.config["SECRET_KEY"] = "test-secret-key"    

    # Set up -- create tables
    initialize_database()

    yield flask_app   # run the test

    # Tear down -- delete test database after test finishes
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture
def client(app):
    """Provides a test HTTP client for making requests to the app without running the server. Used for testing public routes."""
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Provides an already logged in test client for testing protected routes."""
    # Register a test user
    client.post("/register", data={
        "username": "testuser",
        "email": "test@test.com",
        "password": "testpassword"
    })
    # Log them in
    client.post("/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    return client