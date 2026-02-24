import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from PIL import Image
from main import app

client = TestClient(app)

# Helper function to generate a dummy image for testing
def generate_test_image_bytes():
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='red')
    image.save(file, 'jpeg')
    file.seek(0)
    return file.read()

# Helper function to get an auth token
def get_auth_token():
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword"}
    )
    return response.json()["access_token"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_thumbnail_with_auth():
    token = get_auth_token()
    image_bytes = generate_test_image_bytes()
    
    response = client.post(
        "/thumbnails/",
        headers={"Authorization": f"Bearer {token}"},
        data={"width": 300, "height": 300},
        files={"files": ("test.jpg", image_bytes, "image/jpeg")}
    )
    # Note: If your router returns 200, change 201 to 200
    assert response.status_code in [200, 201]

def test_unauthorized_access():
    image_bytes = generate_test_image_bytes()
    # Sending request without Authorization header
    response = client.post(
        "/thumbnails/",
        data={"width": 300, "height": 300},
        files={"files": ("test.jpg", image_bytes, "image/jpeg")}
    )
    assert response.status_code == 401
