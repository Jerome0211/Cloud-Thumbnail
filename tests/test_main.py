import io
from fastapi.testclient import TestClient
from PIL import Image
from main import app

client = TestClient(app)

def generate_test_image_bytes() -> bytes:
    """生成一张 1000x1000 的纯色测试图片"""
    file_obj = io.BytesIO()
    image = Image.new("RGB", (1000, 1000), color="red")
    image.save(file_obj, format="JPEG")
    file_obj.seek(0)
    return file_obj.read()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_thumbnail_with_preset():
    image_bytes = generate_test_image_bytes()
    response = client.post(
        "/thumbnails/",
        data={"preset": "small"},
        files={"files": ("test.jpg", image_bytes, "image/jpeg")}
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 1
    
    metadata = data[0]
    assert metadata["width"] == 150
    assert metadata["height"] == 150
    assert "id" in metadata

def test_create_thumbnail_with_custom_dimensions():
    image_bytes = generate_test_image_bytes()
    response = client.post(
        "/thumbnails/",
        data={"width": 400, "height": 200},
        files={"files": ("test.jpg", image_bytes, "image/jpeg")}
    )
    assert response.status_code == 201
    data = response.json()
    assert data[0]["width"] == 200
    assert data[0]["height"] == 200

def test_missing_dimensions():
    image_bytes = generate_test_image_bytes()
    response = client.post(
        "/thumbnails/",
        files={"files": ("test.jpg", image_bytes, "image/jpeg")}
    )
    assert response.status_code == 400 

def test_get_nonexistent_thumbnail():
    response = client.get("/thumbnails/fake-id")
    assert response.status_code == 404
