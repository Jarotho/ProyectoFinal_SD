import requests

# Aquí define las URLs de las APIs REST
API_REST_1 = 'URL_DE_API_REST_1'
API_REST_2 = 'URL_DE_API_REST_2'
API_REST_3 = 'URL_DE_API_REST_3'

def get_book_info_rest(query, search_type):
    results = []
    
    # API REST 1
    response_1 = requests.get(API_REST_1, params={search_type: query})
    if response_1.status_code == 200:
        data_1 = response_1.json()
        # Extrae la información relevante de data_1
        results.append(data_1)
    
    # API REST 2
    response_2 = requests.get(API_REST_2, params={search_type: query})
    if response_2.status_code == 200:
        data_2 = response_2.json()
        # Extrae la información relevante de data_2
        results.append(data_2)
    
    # API REST 3
    response_3 = requests.get(API_REST_3, params={search_type: query})
    if response_3.status_code == 200:
        data_3 = response_3.json()
        # Extrae la información relevante de data_3
        results.append(data_3)
    
    return results
