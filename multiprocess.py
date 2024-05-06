import json
import os
from datetime import datetime
from multiprocessing import Pool, Lock
import timeit


class NoVideosFoundError(Exception):
    pass

yt_dlp_executable = "yt-dlp"

# ---------------------------------------------------------------------------- #

def load_json_file(file_name: str) -> dict:
    """
    Load a JSON file and return its content as a dictionary.

    Args:
        file_name (str): the name of the JSON file to load.

    Returns:
        dict: the content of the JSON file as a dictionary.
    """
    with open(file_name, 'r') as file:
        file_content = json.load(file)
        return file_content


(downloaded_channels, downloaded_videos) = (load_json_file("downloaded.json")["channels"], load_json_file("downloaded.json")["videos"])
to_download_channels = load_json_file("to_download.json")["channels"]
to_download_videos = []
lock = Lock() # Create a lock for synchronization

# ---------------------------------------------------------------------------- #

def get_latest_videos(channel_url: str) -> list[str]:
    """
    Get the last five videos URL of a YouTube channel.

    Args:
        channel_url (str): the YouTube channel you want to get the last five videos URl.

    Returns:
        list[str]: the last five videos URL.
    """
    videos = []

    try:
        
        command = f"{yt_dlp_executable} --no-warnings --get-id --skip-download --max-downloads 5 \"{channel_url}\""
        video_ids = os.popen(command).read().split()

        if not video_ids:
            raise NoVideosFoundError("no videos found")
        else:
            for video_id in video_ids:
                videos.append(f"https://www.youtube.com/watch?v={video_id}")
    except NoVideosFoundError as e:
        print(f"Error: {e}")

    return videos

def register_video(is_from_new_channel: bool, channel_name: str, video_title: str, upload_date: str) -> None:
    """
    Registers a video in the system.

    Args:
        is_from_new_channel (bool): indicates whether the video is from a new channel.
        channel_name (str): the name of the channel the video belongs to.
        video_title (str): the title of the video.
        upload_date (str): the date the video was uploaded.

    Returns:
        None
    """
    video = {
        "title": video_title,
        "upload_date": upload_date,
        "download_date": datetime.now().strftime("%Y-%m-%d")
    }

    with lock:
        try:
            channel_downloaded_index = downloaded_channels.index(channel_name)
        except ValueError:
            # Si el canal no está en la lista, lo agregamos
            downloaded_channels.append(channel_name)
            downloaded_videos.append([])
            channel_downloaded_index = len(downloaded_channels) - 1
        
        downloaded_videos[channel_downloaded_index] = video

def download_video(url: str) -> None:
    """
    Downloads a video from the given URL and saves it to the appropriate directory.

    Args:
        url (str): the URL of the video to be downloaded.

    Returns:
        None
    """
    
    # Ejecuta yt-dlp para obtener información sobre el video
    command_output = os.popen(f"{yt_dlp_executable} --no-warnings --dump-json \"{url}\"").read()

    if command_output.strip():
        try:
            is_from_new_channel = False
            video_information = json.loads(command_output)
            channel = video_information["channel"]
            title = video_information["title"]
            upload_date = video_information["upload_date"]

            channel_folder_name = channel.replace(" ", "_")
            path = f"downloads/{channel_folder_name}"

            if not os.path.exists(path):  # Check if directory exists before creating
                with lock:  # Use lock to ensure synchronization
                    os.makedirs(path)
                is_from_new_channel = True

            file_name = f"{title}-{upload_date}"
            os.popen(f"{yt_dlp_executable} --output \"{file_name}\" --no-warnings --extract-audio --audio-format mp3 --paths {path} \"{url}\"").read()

            register_video(is_from_new_channel, channel, title, upload_date)

        except json.decoder.JSONDecodeError:
            print(f"Error: No se pudo decodificar la salida JSON para la URL: {url}")
        except Exception as e:
            print(f"Error desconocido al procesar la URL {url}: {e}")

# ---------------------------------------------------------------------------- #

def main(NUM_PROCESS_PARAMETER: int = 8):
    start1 = timeit.default_timer()
    with Pool(processes=NUM_PROCESS_PARAMETER) as pool:
        # Paraleliza la llamada a get_latest_videos
        results = pool.map(get_latest_videos, to_download_channels)
    end1 = timeit.default_timer()
    print(f"Tiempo de ejecución con multiprocessing first part: {end1 - start1}")

    for result in results:
        to_download_videos.extend(result)

    start2 = timeit.default_timer()
    with Pool(processes=NUM_PROCESS_PARAMETER) as pool:
        pool.map(download_video, to_download_videos)
    end2 = timeit.default_timer()
    print(f"Tiempo de ejecución con multiprocessing first part: {end2 - start2}")

    new_content = {
        "channels": downloaded_channels,
        "videos": downloaded_videos
    }

    with open("downloaded.json", "w") as file:
        json.dump(new_content, file, indent=4)

    new_content = {
        "channels": []
    }

    with open("to_download.json", "w") as file:
        json.dump(new_content, file, indent=4)


if __name__ == "__main__":
    start = timeit.default_timer()
    main()
    end = timeit.default_timer()
    print(f"Tiempo de ejecución con multiprocessing full program: {end - start}")