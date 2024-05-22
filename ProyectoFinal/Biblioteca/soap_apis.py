from zeep import Client

# Aquí define las URLs de las APIs SOAP
API_SOAP_1 = 'URL_DE_API_SOAP_1'
API_SOAP_2 = 'URL_DE_API_SOAP_2'
API_SOAP_3 = 'URL_DE_API_SOAP_3'

def get_book_info_soap(query, search_type):
    results = []
    
    # API SOAP 1
    client_1 = Client(API_SOAP_1)
    response_1 = client_1.service.MethodName(search_type=query)
    # Extrae la información relevante de response_1
    results.append(response_1)
    
    # API SOAP 2
    client_2 = Client(API_SOAP_2)
    response_2 = client_2.service.MethodName(search_type=query)
    # Extrae la información relevante de response_2
    results.append(response_2)
    
    # API SOAP 3
    client_3 = Client(API_SOAP_3)
    response_3 = client_3.service.MethodName(search_type=query)
    # Extrae la información relevante de response_3
    results.append(response_3)
    
    return results
