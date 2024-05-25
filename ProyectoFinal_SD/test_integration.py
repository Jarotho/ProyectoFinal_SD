import pytest
from app import app as flask_app
from api import app as api_app
import bcrypt

# Configuración de pytest-flask para usar la aplicación Flask de app.py y api.py
@pytest.fixture
def client():
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client

@pytest.fixture
def api_client():
    with api_app.test_client() as client:
        with api_app.app_context():
            yield client

# Prueba de redirección a /login
def test_redirigir_a_login(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/login'

# Prueba de login con credenciales válidas
def test_login_success(client):
    response = client.post('/login', data={'username': 'usuario1', 'password': 'contraseña1'})
    assert response.status_code == 200
    assert b'Credenciales validas' in response.data

# Prueba de login con credenciales inválidas
def test_login_failure(client):
    response = client.post('/login', data={'username': 'usuario1', 'password': 'wrongpassword'})
    assert response.status_code == 200
    assert b'Credenciales invalidas' in response.data

# Prueba de autenticación de API y obtención de token
def test_api_login(api_client):
    response = api_client.post('/login', json={'username': 'usuario1', 'password': 'contraseña1'})
    assert response.status_code == 200
    assert 'access_token' in response.get_json()

# Prueba de acceso a endpoint protegido de clima con token válido
def test_protected_clima_endpoint(api_client):
    login_response = api_client.post('/login', json={'username': 'usuario1', 'password': 'contraseña1'})
    token = login_response.get_json()['access_token']
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = api_client.get('/api/clima/Madrid', headers=headers)
    assert response.status_code == 200
    assert 'temperatura' in response.get_json()

# Prueba de acceso a endpoint protegido de clima sin token
def test_protected_clima_endpoint_no_token(api_client):
    response = api_client.get('/api/clima/Madrid')
    assert response.status_code == 401

# Prueba de convertir divisas
def test_convertir_divisas(client):
    with client:
        response = client.post('/', data={
            'ciudad': 'Madrid',
            'radius': 5,
            'min_stars': 3,
            'max_stars': 5,
            'amenities': ['SWIMMING_POOL'],
            'cantidad': 100,
            'moneda_origen': 'USD',
            'moneda_destino': 'EUR',
            'ciudad_origen': 'Londres',
            'ciudad_destino': 'Madrid',
            'fecha': '2024-06-01',
            'solo_ida': 'true'
        })
        assert response.status_code == 200
        assert b'cantidad_convertida' in response.data

# Prueba de obtener clima para una ciudad
def test_obtener_clima(client):
    with client:
        response = client.post('/', data={
            'ciudad': 'Madrid',
            'radius': 5,
            'min_stars': 3,
            'max_stars': 5,
            'amenities': ['SWIMMING_POOL'],
            'cantidad': 100,
            'moneda_origen': 'USD',
            'moneda_destino': 'EUR',
            'ciudad_origen': 'Londres',
            'ciudad_destino': 'Madrid',
            'fecha': '2024-06-01',
            'solo_ida': 'true'
        })
        assert response.status_code == 200
        assert b'clima_info' in response.data
