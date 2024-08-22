import os
import pytest

from images.views import CURRENT_IMAGES_DIRECTORY


@pytest.fixture
def create_image_file():
    os.makedirs(CURRENT_IMAGES_DIRECTORY, exist_ok=True)
    test_image_path = os.path.join(CURRENT_IMAGES_DIRECTORY, "test_image.png")
    with open(test_image_path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\xf3\xff\xff\x00\x00\x00\x00IEND\xAEB`\x82')
    yield
    os.remove(test_image_path)

async def test_show_image_success(client, create_image_file):
    response = await client.get('/image/test_image.png')
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'

async def test_show_image_not_found(client):
    response = await client.get('/image/non_existent_image.png')
    assert response.status_code == 404
