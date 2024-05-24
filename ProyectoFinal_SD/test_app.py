# test_app.py
import pytest
import requests
import requests_mock
from app import (
    obtener_token,
    obtener_clima,
    obtener_codigo_iata,
    listar_hoteles_por_ciudad,
    obtener_coordenadas_ciudad,
    buscar_tours_por_ciudad,
    buscar_tours,
    convertir_divisas,
    obtener_precio_vuelo
)

@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as m:
        yield m

def test_obtener_token(mock_requests):
    client_id = 'MzyUPLsXSzKhjEqy0WP0AYVW5BqFrUYJ'
    client_secret = 'kRRtByvKB14WB7sP'
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    mock_requests.post(url, json={"access_token": "test_token"})

    token = obtener_token(client_id, client_secret)
    assert token == "test_token"

def test_obtener_clima(mock_requests):
    ciudad = "Madrid"
    url_clima = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid=dd3d973ae64650832a986fe508a0d055&units=metric"
    mock_requests.get(url_clima, json={
        "main": {"temp": 20},
        "wind": {"speed": 5},
        "coord": {"lat": 40.4168, "lon": -3.7038},
        "weather": [{"description": "clear sky"}]
    })

    clima_info = obtener_clima(ciudad)
    assert clima_info == {
        "temp": 20,
        "vel_viento": 5,
        "latitud": 40.4168,
        "longitud": -3.7038,
        "descripcion": "Clear sky"
    }

def test_obtener_codigo_iata(mock_requests):
    ciudad = "Madrid"
    url = "https://test.api.amadeus.com/v1/reference-data/locations"
    mock_requests.get(url, json={"data": [{"iataCode": "MAD"}]})

    codigo_iata = obtener_codigo_iata(ciudad)
    assert codigo_iata == "MAD"

def test_listar_hoteles_por_ciudad(mock_requests):
    ciudad = "Madrid"
    url = "https://test.api.amadeus.com/v1/reference-data/locations"
    mock_requests.get(url, json={"data": [{"iataCode": "MAD"}]})

    url_hoteles = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    mock_requests.get(url_hoteles, json={"data": [{"name": "Hotel Madrid", "address": {"countryCode": "ES"}}]})

    hoteles_info = listar_hoteles_por_ciudad(ciudad)
    assert hoteles_info == [{"nombre": "Hotel Madrid", "direccion": "ES"}]

def test_obtener_coordenadas_ciudad(mock_requests):
    ciudad = "Madrid"
    url = "https://test.api.amadeus.com/v1/reference-data/locations"
    mock_requests.get(url, json={"data": [{"geoCode": {"latitude": 40.4168, "longitude": -3.7038}}]})

    lat, lon = obtener_coordenadas_ciudad(ciudad)
    assert lat == 40.4168
    assert lon == -3.7038

def test_buscar_tours_por_ciudad(mock_requests):
    ciudad = "Madrid"
    url = "https://test.api.amadeus.com/v1/reference-data/locations"
    mock_requests.get(url, json={"data": [{"geoCode": {"latitude": 40.4168, "longitude": -3.7038}}]})

    url_tours = "https://test.api.amadeus.com/v1/shopping/activities"
    mock_requests.get(url_tours, json={"data": [{"name": "Tour Madrid", "shortDescription": "Amazing tour", "price": {"amount": 50}}]})

    tours_info = buscar_tours_por_ciudad(ciudad)
    assert tours_info == [{"name": "Tour Madrid", "descripcion": "Amazing tour", "price": 50}]

def test_convertir_divisas(mock_requests):
    cantidad = 100
    moneda_origen = "USD"
    moneda_destino = "EUR"
    url_divisas = f"https://v6.exchangerate-api.com/v6/0ca3dd8e54ad837f52817dfc/pair/{moneda_origen}/{moneda_destino}/{cantidad}"
    mock_requests.get(url_divisas, json={"conversion_result": 85})

    cantidad_convertida = convertir_divisas(cantidad, moneda_origen, moneda_destino)
    assert cantidad_convertida == 85

def test_obtener_precio_vuelo(mock_requests):
    ciudad_origen = "Madrid"
    ciudad_destino = "Paris"
    fecha = "2023-05-24"
    moneda = "EUR"
    solo_ida = True

    url_iata = "https://test.api.amadeus.com/v1/reference-data/locations"
    mock_requests.get(url_iata, json={"data": [{"iataCode": "MAD"}]})
    mock_requests.get(url_iata, json={"data": [{"iataCode": "PAR"}]})

    url_vuelo = "https://test.api.amadeus.com/v1/analytics/itinerary-price-metrics"
    mock_requests.get(url_vuelo, json={"data": {"price": 150}})

    precio_vuelo = obtener_precio_vuelo(ciudad_origen, ciudad_destino, fecha, moneda, solo_ida)
    assert precio_vuelo == {"data": {"price": 150}}
