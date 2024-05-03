import requests
from bs4 import BeautifulSoup
import re

# def obtener_id_canal(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
#         # Buscar el primer enlace con un atributo href que comience con el patrón de URL del canal de YouTube
#         enlace_canal = soup.find('href', href=re.compile(r'^https://www.youtube.com/channel/'))
#         if enlace_canal:
#             # Extraer el ID del canal del enlace
#             canal_id = enlace_canal['href'].split('/')[-1]
#             return canal_id
#         else:
#             print("No se encontró ningún enlace al canal en la URL:", url)
#             return None
#     else:
#         print("Error al obtener el canal:", response.status_code)
#         return None


def obtener_id_canal(url):
    # Hacer la solicitud GET a la URL del canal
    response = requests.get(url)
    
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Analizar el HTML de la página
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar el ID del canal en el código fuente de la página
        match = re.search(r'\"channelId\":\"([a-zA-Z0-9_-]+)\"', str(soup))
        if match:
            return match.group(1)
        else:
            return None
    else:
        print("Error al obtener el canal:", response.status_code)
        return None

def obtener_ids_canales(urls):
    ids_canales = []
    for url in urls:
        canal_id = obtener_id_canal(url)
        if canal_id:
            ids_canales.append(canal_id)
    return ids_canales

# Lista de URLs de canales de YouTube
urls_canales = [
    "https://www.youtube.com/@Kassiapiano",
    "https://www.youtube.com/@Rousseau",
    "https://www.youtube.com/@Lord_Vinheteiro",
	"https://www.youtube.com/@claramxx",
	"https://www.youtube.com/@vangroovehoven",
    # Agrega más URLs de canales aquí
]

# Obtener los IDs de los canales
channel_ids = obtener_ids_canales(urls_canales)

print(channel_ids)
# pip install requests beautifulsoup4