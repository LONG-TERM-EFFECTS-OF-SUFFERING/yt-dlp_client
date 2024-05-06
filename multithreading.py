import json
import os
import concurrent.futures
import threading
from datetime import datetime
import timeit

# ---------------------------------------------------------------------------- #

NUM_THREADS = 4
lock = threading.Lock()

# ---------------------------------------------------------------------------- #


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
	with open(file_name, "r") as file:
		file_content = json.load(file)
		return file_content


(downloaded_channels, downloaded_videos) = (
	load_json_file("downloaded.json")["channels"],
	load_json_file("downloaded.json")["videos"],
)
to_download_channels = load_json_file("to_download.json")["channels"]
to_download_videos = []

# ---------------------------------------------------------------------------- #


def get_latest_videos(channel_url: str) -> list[str]:
	"""
	Get the last five videos URL of a YouTube channel.

	Args:
		channel_url (str): the YouTube channel you want to get the lastfive videos URl.

	Returns:
		list[str]: the last five videos URL.
	"""
	videos = []

	try:
		command = f'{yt_dlp_executable} --no-warnings --get-id --skip-download --max-downloads 5 "{channel_url}"'
		video_ids = os.popen(command).read().split()

		if not video_ids:
			raise NoVideosFoundError("no videos found")
		else:
			for video_id in video_ids:
				videos.append(f"https://www.youtube.com/watch?v={video_id}")
	except NoVideosFoundError as e:
		print(f"Error: {e}")

	return videos


# ---------------------------------------------------------------------------- #


def register_video(
	is_from_new_channel: bool, channel_name: str, video_title: str, upload_date: str
) -> None:
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
		"download_date": datetime.now().strftime("%Y-%m-%d"),
	}

	try:
		with lock:
			if is_from_new_channel:
				downloaded_channels.append(channel_name)
				downloaded_videos.append([])
				channel_downloaded_index = len(downloaded_channels) - 1
			else:
				channel_downloaded_index = downloaded_channels.index(channel_name)

			downloaded_videos[channel_downloaded_index].append(video)
	except Exception as e:
		print(f"Error registering video: {e}")


# ---------------------------------------------------------------------------- #


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
			print(f"Error: Could not decode the JSON output for the URL: {url}")
		except Exception as e:
			print(f"Unknown error processing URL {url}: {e}")


# ---------------------------------------------------------------------------- #


def main(NUM_THREADS_PARAMETER: int = 4):
	with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS_PARAMETER) as executor:
			results = list(executor.map(get_latest_videos, to_download_channels))

	for result in results:
			to_download_videos.extend(result)

	print(f"Lenght of to_download_videos: {len(to_download_videos)}")

	contador = 0

	with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
			futures = []

			for video_url in to_download_videos:
					futures.append(executor.submit(download_video, video_url))
					contador += 1

			concurrent.futures.wait(futures)

	print(f"Number of videos downloaded: {contador}")
	
	new_content = {"channels": downloaded_channels, "videos": downloaded_videos}

	with open("downloaded.json", "w") as file:
		json.dump(new_content, file, indent=4)

	new_content = {"channels": []}

	with open("to_download.json", "w") as file:
		json.dump(new_content, file, indent=4)


if __name__ == "__main__":
	main()
