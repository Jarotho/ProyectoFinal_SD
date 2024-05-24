from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Credenciales de la API de Amadeus
client_id = 'MzyUPLsXSzKhjEqy0WP0AYVW5BqFrUYJ'
client_secret = 'kRRtByvKB14WB7sP'

def obtener_token(client_id, client_secret):
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    
    token = response.json().get('access_token')
    return token

# Obtén el token de acceso al iniciar la aplicación
token = obtener_token(client_id, client_secret)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Capturar campos del formulario
        ciudad = request.form["ciudad"]
        radius = int(request.form.get("radius", 1))
        min_stars = int(request.form.get("min_stars", 1))
        max_stars = int(request.form.get("max_stars", 5))
        amenities = request.form.getlist("amenities")
        cantidad = float(request.form.get("cantidad", 1))
        moneda_origen = request.form.get("moneda_origen", "USD")
        moneda_destino = request.form.get("moneda_destino", "EUR")
        ciudad_origen = request.form["ciudad_origen"]
        ciudad_destino = request.form["ciudad_destino"]
        fecha = request.form["fecha"]
        moneda = request.form.get("moneda", "EUR")
        solo_ida = request.form.get("solo_ida", "true") == "true"
        
        # Realizar la conversión de divisas
        cantidad_convertida = convertir_divisas(cantidad, moneda_origen, moneda_destino)
        
        # Obtener información de clima, hoteles, tours, etc.
        clima_info = obtener_clima(ciudad)
        hoteles_info = listar_hoteles_por_ciudad(ciudad=ciudad, radius=radius, min_stars=min_stars, max_stars=max_stars, amenities=amenities)
        tours_info = buscar_tours_por_ciudad(ciudad, radius)
        
        
        # Obtener precios de vuelo
        precio_vuelo = obtener_precio_vuelo(ciudad_origen, ciudad_destino, fecha, moneda, solo_ida)
        
        return render_template("resultados.html", ciudad=ciudad, clima_info=clima_info, radius=radius, min_stars=min_stars, max_stars=max_stars, amenities=amenities, hoteles_info=hoteles_info, tours_info=tours_info, cantidad_convertida=cantidad_convertida, cantidad=cantidad, moneda_origen=moneda_origen, moneda_destino=moneda_destino, precio_vuelo=precio_vuelo, ciudad_origen=ciudad_origen, ciudad_destino=ciudad_destino, fecha=fecha, solo_ida=solo_ida, moneda=moneda)
    
    return render_template("index.html")


def obtener_clima(ciudad):
    api_key_clima = "dd3d973ae64650832a986fe508a0d055"
    url_clima = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key_clima}&units=metric"
    
    try:
        res = requests.get(url_clima)
        res.raise_for_status()  
        datos = res.json()
        
        if 'main' in datos:
            temp = datos["main"]["temp"]
            vel_viento = datos["wind"]["speed"]
            latitud = datos["coord"]["lat"]
            longitud = datos["coord"]["lon"]
            descripcion = datos["weather"][0]["description"]
            
            clima_info = {
                "temp": temp,
                "vel_viento": vel_viento,
                "latitud": latitud,
                "longitud": longitud,
                "descripcion": descripcion.capitalize()
            }
            return clima_info
        else:
            return None
        
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"Error HTTP: {http_err}"}
    except requests.exceptions.RequestException as err:
        return {"error": f"Error: No se pudo obtener datos del clima. {err}"}

def obtener_codigo_iata(ciudad):
    url = "https://test.api.amadeus.com/v1/reference-data/locations"
    params = {
        'keyword': ciudad,
        'subType': 'CITY'
    }
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and data['data']:
            return data['data'][0]['iataCode']
        else:
            return None
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"Error HTTP: {http_err}"}
    except requests.exceptions.RequestException as err:
        return {"error": f"Error: No se pudo completar la solicitud. {err}"}

def listar_hoteles_por_ciudad(ciudad, radius=5, amenities=None, min_stars=1, max_stars=5):
    codigo_iata = obtener_codigo_iata(ciudad)
    if codigo_iata:
        url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
        params = {
            'cityCode': codigo_iata,
            'radius': radius
        }
        
        if amenities:
            params['amenities'] = ','.join(amenities)
        
        params['ratings'] = ','.join(map(str, range(min_stars, max_stars + 1)))
        
        try:
            headers = {
                'Authorization': f'Bearer {token}'
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if 'data' in data and data['data']:
                hoteles_info = []
                for hotel in data['data']:
                    hotel_info = {
                        "nombre": hotel['name'],
                        "direccion": hotel['address']['countryCode']
                    }
                    hoteles_info.append(hotel_info)
                return hoteles_info
            else:
                return None
        except requests.exceptions.HTTPError as http_err:
            return {"error": f"Error HTTP: {http_err}"}
        except requests.exceptions.RequestException as err:
            return {"error": f"Error: No se pudo completar la solicitud. {err}"}

def obtener_coordenadas_ciudad(ciudad):
    url = "https://test.api.amadeus.com/v1/reference-data/locations"
    params = {
        'keyword': ciudad,
        'subType': 'CITY'
    }
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if 'data' in data and data['data']:
            location = data['data'][0]['geoCode']
            return location['latitude'], location['longitude']
        else:
            return None, None
    except requests.exceptions.HTTPError as http_err:
        return None, None
    except requests.exceptions.RequestException as err:
        return None, None

def buscar_tours_por_ciudad(ciudad, radius=1):
    latitude, longitude = obtener_coordenadas_ciudad(ciudad)
    if latitude and longitude:
        return buscar_tours(latitude, longitude, radius)
    else:
        return None

def buscar_tours(latitude, longitude, radius=1):
    url = "https://test.api.amadeus.com/v1/shopping/activities"
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'radius': radius
    }
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if 'data' in data:
            tours_info = []
            for tour in data['data']:
                tour_info = {
                    'name': tour['name'],
                    'descripcion': tour.get('shortDescription', 'Descripción no disponible'),
                    'price': tour['price'].get('amount', 'N/A') if 'price' in tour else 'N/A',
                }
                tours_info.append(tour_info)
            return tours_info
        else:
            return None
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"Error HTTP: {http_err}"}
    except requests.exceptions.RequestException as err:
        return {"error": f"Error: No se pudo completar la solicitud. {err}"}

def convertir_divisas(cantidad, moneda_origen, moneda_destino):
    api_key_divisas = "0ca3dd8e54ad837f52817dfc"
    url_divisas = f"https://v6.exchangerate-api.com/v6/{api_key_divisas}/pair/{moneda_origen}/{moneda_destino}/{cantidad}"
    
    try:
        response = requests.get(url_divisas)
        response.raise_for_status()
        datos = response.json()
        if 'conversion_result' in datos:
            return datos['conversion_result']
        else:
            return None
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"Error HTTP: {http_err}"}
    except requests.exceptions.RequestException as err:
        return {"error": f"Error: No se pudo obtener la conversión. {err}"}
    
def obtener_precio_vuelo(ciudad_origen, ciudad_destino, fecha, moneda, solo_ida):
    origen_iata = obtener_codigo_iata(ciudad_origen)
    destino_iata = obtener_codigo_iata(ciudad_destino)
    if not origen_iata or not destino_iata:
        return {"error": "No se pudo obtener el código IATA de una o ambas ciudades"}
    
    url = "https://test.api.amadeus.com/v1/analytics/itinerary-price-metrics"
    params = {
        'originIataCode': origen_iata,
        'destinationIataCode': destino_iata,
        'departureDate': fecha,
        'currencyCode': moneda,
        'oneWay': solo_ida
    }
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"Error HTTP: {http_err}"}
    except requests.exceptions.RequestException as err:
        return {"error": f"Error: No se pudo completar la solicitud. {err}"}
    

        
if __name__ == "__main__":
    app.run(debug=True)
