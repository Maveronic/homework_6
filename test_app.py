import pytest
import json
from app import app, USER_FILE, hash_password

# Fixture for testing the Flask application
@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    # Ensure a clean user database before testing
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)

    yield client

    # Cleanup after tests
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)

# Test: Home Route
def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"This is the homepage for the first homework." in response.data

# Test: User Registration (via form)
def test_register_user(client):
    response = client.post('/register', data={
        "email": "test@example.com",
        "age": "30",
        "password": "securepassword"
    })
    assert response.status_code == 200
    assert b"User registered successfully!" in response.data

    # Attempt duplicate registration
    response = client.post('/register', data={
        "email": "test@example.com",
        "age": "30",
        "password": "securepassword"
    })
    assert response.status_code == 200
    assert b"User already exists." in response.data

# Test: Add User API
def test_add_user(client):
    response = client.post('/add_user', json={
        "email": "test@example.com",
        "age": 30,
        "password": "securepassword"
    })
    assert response.status_code == 201
    assert response.json["message"] == "User registered successfully!"

    # Attempt duplicate registration
    response = client.post('/add_user', json={
        "email": "test@example.com",
        "age": 30,
        "password": "securepassword"
    })
    assert response.status_code == 400
    assert response.json["error"] == "User already exists."

# Test: Get User API
def test_get_user(client):
    # Add a user
    client.post('/add_user', json={
        "email": "test@example.com",
        "age": 30,
        "password": "securepassword"
    })

    # Retrieve the user
    response = client.get('/get_user/test@example.com', headers={
        "Password": "securepassword"
    })
    assert response.status_code == 200
    assert response.json["email"] == "test@example.com"
    assert response.json["age"] == 30

    # Attempt to retrieve non-existent user
    response = client.get('/get_user/nonexistent@example.com', headers={
        "Password": "securepassword"
    })
    assert response.status_code == 404  # User not found
    assert response.json["error"] == "User not found"

    # Attempt with incorrect password
    response = client.get('/get_user/test@example.com', headers={
        "Password": "wrongpassword"
    })
    assert response.status_code == 403  # Unauthorized access
    assert response.json["error"] == "Unauthorized access."


# Test: Update User API
def test_update_user(client):
    # Add a user
    client.post('/add_user', json={
        "email": "test@example.com",
        "age": 30,
        "password": "securepassword"
    })

    # Update the user's age
    response = client.put('/update_user/test@example.com', json={
        "age": 35
    }, headers={"Password": "securepassword"})
    assert response.status_code == 200
    assert response.json["message"] == "User updated successfully!"
    assert response.json["user"]["age"] == 35

    # Attempt update with incorrect password
    response = client.put('/update_user/test@example.com', json={
        "age": 40
    }, headers={"Password": "wrongpassword"})
    assert response.status_code == 403
    assert response.json["error"] == "Unauthorized access."

# Test: Delete User API
def test_delete_user(client):
    # Add a user
    client.post('/add_user', json={
        "email": "test@example.com",
        "age": 30,
        "password": "securepassword"
    })

    # Delete the user
    response = client.delete('/delete_user/test@example.com', headers={
        "Password": "securepassword"
    })
    assert response.status_code == 200
    assert response.json["message"] == "User deleted successfully!"

    # Attempt to retrieve deleted user
    response = client.get('/get_user/test@example.com', headers={
        "Password": "securepassword"
    })
    assert response.status_code == 404  # User not found
    assert response.json["error"] == "User not found"

    # Attempt delete with incorrect password
    response = client.delete('/delete_user/test@example.com', headers={
        "Password": "wrongpassword"
    })
    assert response.status_code == 403  # Unauthorized access
    assert response.json["error"] == "Unauthorized access."

