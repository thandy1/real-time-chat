def test_register_route_returns_200(client):
    """Test that /register route returns a successful response on GET request."""
    response = client.get("/register")
    assert response.status_code == 200
        

def test_register_route_creates_user_and_redirects(client):
    """Test that a POST request to /register with valid data actually creates a user and redirects."""
    response = client.post("/register", data={
        "username": "testuser",
        "email": "test@test.com",
        "password": "testpassword"
    })
    assert response.status_code == 302


def test_unauth_user_redirects_to_login(client):
    """Test that '/' (Homepage) redirects to login when no user is logged in."""
    response = client.get("/")
    assert response.status_code == 302


def test_auth_user_has_access_to_createRoom(auth_client):
    """Test that an authenticated user can successfully access /create_room."""
    response = auth_client.get("/create_room",)
    assert response.status_code == 200


def test_auth_user_post_to_create_room(auth_client):
    """Test that posting to /create_room with auth_client creates a room and redirects."""
    response = auth_client.post("/create_room", data={
        "room-name": "dummy-room"
    })
    assert response.status_code == 302


def test_auth_user_fetch_rooms_list(auth_client):
    """Test /rooms_list, an authenticated user can fetch the rooms list and it returns 200."""
    response = auth_client.get("/rooms_list")
    assert response.status_code == 200


# TODO: test when chat.html template is created.
def test_room_creation_fetch_chat_page_and_contains_room_data(auth_client):
    """Test /chat/<int:room_id>, creating a room fetches the chat page and verify it returns 200 and contains the room data."""
    response1 = auth_client.post("/create_room", data={
        "room-name": "test_room"
    })
    response2 = auth_client.get("/chat/1")
    assert response2.status_code == 200
