import json
import os
from datetime import datetime
import timeit
import concurrent.futures
import threading


class NoVideosFoundError(Exception):
	pass

yt_dlp_executable = "yt-dlp"
lock = threading.Lock()

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

# ---------------------------------------------------------------------------- #

def get_latest_videos(channel_url: str) -> list[str]:
	"""
	Get the last five videos URL of a YouTube channel.

	Args:
		channel_url (str): the YouTube channel you want to get the last
			five videos URl.

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
			if is_from_new_channel:
					if channel_name not in downloaded_channels:
							downloaded_channels.append(channel_name)
							downloaded_videos.append([])
					channel_downloaded_index = downloaded_channels.index(channel_name)
			else:
					channel_downloaded_index = downloaded_channels.index(channel_name)

			downloaded_videos[channel_downloaded_index].append(video)


def download_video(url: str) -> None:
	"""
	Downloads a video from the given URL and saves it to the appropriate directory.

	Args:
		url (str): the URL of the video to be downloaded.

	Returns:
		None
	"""
	is_from_new_channel = False
	video_information = json.loads(os.popen(f"{yt_dlp_executable} --no-warnings --dump-json \"{url}\"").read())
	channel = video_information["channel"]
	title = video_information["title"]
	upload_date = video_information["upload_date"]

	channel_folder_name = channel.replace(" ", "_")
	path = f"downloads/{channel_folder_name}"

	with lock:
		if not channel in downloaded_channels: # os.path.exists(path)
			is_from_new_channel = True
			os.makedirs(path, exist_ok=True)
  
	file_name = f"{title}-{upload_date}"
	os.popen(f"{yt_dlp_executable} --output \"{file_name}\" --no-warnings --extract-audio --audio-format mp3 --paths {path} \"{url}\"").read()

	register_video(is_from_new_channel, channel, title, upload_date)

# ---------------------------------------------------------------------------- #

def main(NUM_MAX_WORKERS: int = 4):
	start1 = timeit.default_timer()
	with concurrent.futures.ThreadPoolExecutor(NUM_MAX_WORKERS) as executor:
			futures = [executor.submit(get_latest_videos, channel) for channel in to_download_channels]
			for future in futures:
					to_download_videos.extend(future.result())
	end1 = timeit.default_timer()
	print(f"Time to get latest videos: {end1 - start1} seconds")

	print(f"Lenght of to_download_videos: {len(to_download_videos)}")

	start2 = timeit.default_timer()
	with concurrent.futures.ThreadPoolExecutor(NUM_MAX_WORKERS) as executor:
			futures = [executor.submit(download_video, url) for url in to_download_videos]
			for future in futures:
					future.result()
	end2 = timeit.default_timer()
	print(f"Time to download videos: {end2 - start2} seconds")

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
    # start = timeit.default_timer()
    main()
    # end = time