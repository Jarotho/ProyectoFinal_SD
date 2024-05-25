# test_integration.py
import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import app as flask_app
from api import app as api_app
import json
import bcrypt

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def api():
    yield api_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def api_client(api):
    return api.test_client()

def test_redirigir_a_login(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.location == 'http://localhost/login'

def test_login_get(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_post_success(client):
    response = client.post('/login', data={'username': 'usuario1', 'password': 'contraseña1'})
    assert response.status_code == 200
    assert b'Credenciales validas' in response.data

def test_login_post_failure(client):
    response = client.post('/login', data={'username': 'usuario1', 'password': 'incorrecto'})
    assert response.status_code == 200
    assert b'Credenciales invalidas' in response.data

def test_obtener_clima(client, monkeypatch):
    class MockResponse:
        @staticmethod
        def json():
            return {
                "main": {"temp": 25},
                "wind": {"speed": 5},
                "coord": {"lat": 40.7128, "lon": -74.0060},
                "weather": [{"description": "clear sky"}]
            }
        @staticmethod
        def raise_for_status():
            pass
    
    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr('requests.get', mock_get)
    response = client.post('/',
        data={'ciudad': 'New York',
              'radius': 5,
              'min_stars': 1,
              'max_stars': 5,
              'amenities': ['wifi'],
              'cantidad': 100,
              'moneda_origen': 'USD',
              'moneda_destino': 'EUR',
              'ciudad_origen': 'New York',
              'ciudad_destino': 'Los Angeles',
              'fecha': '2024-12-31',
              'moneda': 'USD',
              'solo_ida': 'true'})
    assert response.status_code == 200
    assert b'New York' in response.data

def test_api_login_success(api_client):
    response = api_client.post('/login', json={'username': 'usuario1', 'password': 'contraseña1'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data

def test_api_login_failure(api_client):
    response = api_client.post('/login', json={'username': 'usuario1', 'password': 'incorrecto'})
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Credenciales inválidas'

def test_api_protected_route(api_client, monkeypatch):
    response = api_client.post('/login', json={'username': 'usuario1', 'password': 'contraseña1'})
    data = response.get_json()
    token = data['access_token']

    headers = {'Authorization': f'Bearer {token}'}
    
    def mock_get_clima(*args, **kwargs):
        return {"temperatura": 25, "descripcion": "Soleado"}

    monkeypatch.setattr('api.obtener_clima_api', mock_get_clima)

    response = api_client.get('/api/clima/New York', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['temperatura'] == 25
    assert data['descripcion'] == 'Soleado'

    response = api_client.post('/api/operacion', json={}, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['mensaje'] == 'Operación realizada con éxito'

