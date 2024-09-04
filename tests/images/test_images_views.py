import logging
import os
import shutil
from io import BytesIO
from unittest.mock import patch
import pytest
from images.views import CURRENT_IMAGES_DIRECTORY

@pytest.fixture(autouse=True)
def clean_upload():
    logging.info('Создание директории для тестов')
    os.makedirs(CURRENT_IMAGES_DIRECTORY, exist_ok=True)
    yield
    logging.info('Удаление директории для тестов')
    shutil.rmtree(CURRENT_IMAGES_DIRECTORY, ignore_errors=True)

@pytest.fixture(scope='function')
async def create_host(client):
    response = await client.post('/monitor/hosts/', json={
        "host_id": 1,
        "column": 3,
        "name": "superhost"
})
    yield response
    await client.delete('/monitor/hosts/1')

@pytest.fixture
def create_image_file():
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
    assert response.json() == {"detail": "Файл не найден"}

async def test_upload_image_success(client, create_host):
    image_file = BytesIO(b'test image content')
    response = await client.post('/image/upload', files={'image': ("test_image.jpg", image_file, "image/jpeg")}, data={'host-id': '1'})
    assert response.status_code == 200
    assert response.json() == {'error': '', 'success': 'test_image.jpg'}

async def test_upload_image_missing_host_id(client):
    with patch('images.views.get_host', return_value=True), \
        patch('images.views.update_host_image'):

        image_file = BytesIO(b'test image content')
        response = await client.post('/image/upload', files={'image': ("test_image.jpg", image_file, "image/jpeg")})
        assert response.status_code == 200
        assert response.json() == {'error': 'Невозможно получить host_id'}

async def test_upload_image_db_error(client):
    with patch('images.views.get_host', return_value=False):
        image_file = BytesIO(b'test image content')
        response = await client.post('/image/upload', files={'image': ("test_image.jpg", image_file, "image/jpeg")}, data={'host-id': '1'})
        assert response.status_code == 200
        assert response.json() == {'error': 'Ошибка БД'}

