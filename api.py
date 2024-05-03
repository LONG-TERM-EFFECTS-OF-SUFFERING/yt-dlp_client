from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import subprocess
import json
from channels_id import obtener_ids_canales

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Accede a la clave de API de YouTube desde las variables de entorno
api_key = os.getenv("YOUTUBE_API_KEY")

# Crear un servicio de la API de YouTube
youtube = build("youtube", "v3", developerKey=api_key)

# Lista de URLs de canales de YouTube
urls_canales = [
    "https://www.youtube.com/@Kassiapiano",
    "https://www.youtube.com/@Rousseau",
    "https://www.youtube.com/@Lord_Vinheteiro",
	"https://www.youtube.com/@claramxx",
	"https://www.youtube.com/@vangroovehoven"
    # Agrega más URLs de canales aquí
]

# Obtener los IDs de los canales
channel_ids = obtener_ids_canales(urls_canales)

# channel_ids = ["UCPmCaKjzYF3pXYLfaRhacwA", "UCPZUQqtVDmcjm4NY5FkzqLA", "UCuJZfTHsMILxdb_XBQzaeQg", "UCLafIQZHZ4XxuOxK5ah6A9w", "UCSE6yilNScIz1SLTNQvrXMw"]

# Lista para almacenar las URL de los videos
video_urls = []

# Obtener los últimos 5 videos de cada canal por su ID
for channel_id in channel_ids:
    try:
        # Hacer la solicitud para obtener los últimos 5 videos del canal
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=5,
            order="date"
        )
        response = request.execute()

        # Almacenar las URL de los videos en la lista
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_urls.append(video_url)
    except Exception as e:
        print(f"Error al obtener los videos del canal con ID '{channel_id}': {e}")

# Imprimir la lista de URL de los videos
print("URLs de los videos:")
for url in video_urls:
    print(url)

# Escribir la lista de URL de los videos en un archivo JSON
with open("downloaded.json", "w") as json_file:
    json.dump({"videos": video_urls, "channels": channel_ids}, json_file, indent=4)

with open("to_download.json", "w") as json_file:
    json.dump({"videos": video_urls}, json_file, indent=4)

print("Archivo 'downloaded.json' y 'to_download.json' generados con éxito.")

# pip install google-api-python-client
# pip install python-dotenv

# Ejecutar el comando en la consola
subprocess.run(["python", "main.py"])