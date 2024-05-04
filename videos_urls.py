import json
import subprocess
import os

def get_latest_videos(channel_urls):
    videos = []
    for url in channel_urls:
        try:
            command = f"yt-dlp --get-id --skip-download --max-downloads 5 {url}"
            output = subprocess.run(command, shell=True, capture_output=True, text=True)
            video_ids = output.stdout.splitlines()
            for vid in video_ids:
                videos.append(f"https://www.youtube.com/watch?v={vid}")
        except subprocess.CalledProcessError as e:
            print(f"Error al obtener videos del canal {url}: {e}")
    return videos

def main():
    channel_urls = [
        "https://www.youtube.com/@Kassiapiano",
        "https://www.youtube.com/@Rousseau",
        "https://www.youtube.com/@Lord_Vinheteiro",
        "https://www.youtube.com/@claramxx",
        "https://www.youtube.com/@vangroovehoven"
    ]

    try:
        videos = get_latest_videos(channel_urls)

        data = {
            "channels": channel_urls,
            "videos": videos
        }

        with open('downloaded.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)

        with open("to_download.json", "w") as json_file:
            json.dump({"videos": videos}, json_file, indent=4)

        print("El proceso se ha completado satisfactoriamente. Se extrajeron los enlaces correspondientes.")

        # Ejecutar main.py si todo sale bien
        os.system("python main.py")

    except Exception as e:
        print(f"Ocurrió un error durante el proceso: {e}")
        

if __name__ == "__main__":
    main()















