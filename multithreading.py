import json
import os
import concurrent.futures
import threading
from datetime import datetime

NUM_THREADS = 16
lock = threading.Lock()

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
to_download_videos = load_json_file("to_download.json")["videos"]

# ---------------------------------------------------------------------------- #

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
		if is_from_new_channel:
			downloaded_channels.append(channel_name)
			downloaded_videos.append([])
			channel_downloaded_index = len(downloaded_channels) - 1
		else:
			channel_downloaded_index = downloaded_channels.index(channel_name)

		downloaded_videos.append(video)

def download_video(url: str) -> None:
	"""
	Downloads a video from the given URL and saves it to the appropriate directory.

	Args:
		url (str): the URL of the video to be downloaded.

	Returns:
		None
	"""
	executable = "yt-dlp"

	is_from_new_channel = False
	video_information = json.loads(os.popen(f"{executable} --no-warnings --dump-json \"{url}\"").read())
	channel = video_information["channel"]
	title = video_information["title"]
	upload_date = video_information["upload_date"]

	path = f"downloads/{channel.replace(" ", "_")}"

	if not channel in downloaded_channels: # os.path.exists(path)
		is_from_new_channel = True
		os.makedirs(path)

	file_name = f"{title}-{upload_date}"
	os.popen(f"{executable} -o \"{file_name}\" --no-warnings --extract-audio --audio-format mp3 --paths {path} \"{url}\"").read()

	register_video(is_from_new_channel, channel, title, upload_date)

# ---------------------------------------------------------------------------- #

def main():

	with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
		futures = []

		for video_url in to_download_videos:
			futures.append(executor.submit(download_video, video_url))

		concurrent.futures.wait(futures)

	new_content = {
		"channels": downloaded_channels,
		"videos": downloaded_videos
	}

	with open("downloaded.json", "w") as file:
		json.dump(new_content, file, indent=4)

	new_content = {
		"videos": []
	}

	with open("to_download.json", "w") as file:
		json.dump(new_content, file, indent=4)

if __name__ == "__main__":
	main()
