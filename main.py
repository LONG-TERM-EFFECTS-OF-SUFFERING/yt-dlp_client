import json
import os
from datetime import datetime


def load_json_file(file_name: str) -> tuple[list[str], list[str]]:
	"""
	Load a JSON file and extract the channels and videos from its content.

	Args:
		file_name (str): the name of the JSON file to load.

	Returns:
		tuple[list[str], list[str]]: a tuple containing the channels and videos list.

	Raises:
		ValueError: if the number of channels does not match the number of videos in the file.
	"""
	try:
		with open(file_name, 'r') as file:
			file_content = json.load(file)
			channels = file_content["channels"]
			videos = file_content["videos"]

			if len(channels) != len(videos):
				raise ValueError("Error: the number of channels does not match the number of videos")
	except ValueError as e:
		print(str(e))

	return (channels, videos)

def save_json_file(file_name: str, channels: list[str], videos: list[str]) -> None:
	"""
	Save the given channels and videos to a JSON file.

	Args:
		file_name (str): the name of the JSON file to save.
		channels (list[str]): the list of channel names.
		videos (list[str]): the list of video names.

	Returns:
		None
	"""
	new_content = {
		"channels": channels,
		"videos": videos
	}

	with open(file_name, "w") as file:
		json.dump(new_content, file, indent=4)

(downloaded_channels, downloaded_videos) = load_json_file("downloaded.json")
(to_download_channels, to_download_videos) = load_json_file("to_download.json")

# ---------------------------------------------------------------------------- #

def create_folders(to_download_channels: list[str]) -> None:
	"""
	Create folders for each channel in the "downloads" directory.

	Args:
		to_download_channels (list[str]): a list of the channels from which the videos will be downloaded.

	Returns:
		None
	"""
	for channel_name in to_download_channels:
		new_channel_name = channel_name.replace(" ", "_")
		path = f"downloads/{new_channel_name}"

		if not os.path.exists(path):
			os.makedirs(path)

def register_video(channel_index: int, video_title: str, upload_date: str) -> None:
	"""
	Registers a video in the downloaded_videos list.

	Args:
		channel_index (int): the index of the channel in the "downloaded_videos" list.
		video_title (str): the title of the video.
		upload_date (str): the upload date of the video in the format "YYYYMMDD".

	Returns:
		None
	"""
	video = {
		"title": video_title,
		"upload_date": upload_date,
		"download_date": datetime.now().strftime("%Y-%m-%d")
	}

	downloaded_videos[channel_index].append(video)

def download_video(downloaded_channel_index: int, url: str) -> None:
	"""
	Downloads a video from the given URL and saves it to the appropriate channel's directory.

	Args:
		downloaded_channel_index (int): The index of the downloaded channel in the "downloaded_channels" list.
		url (str): The URL of the video to be downloaded.

	Returns:
		None
	"""
	channel = downloaded_channels[downloaded_channel_index]
	path = f"downloads/{channel.replace(" ", "_")}"

	executable = "G:\\yt-dlp\\yt-dlp.exe"

	video_information = json.loads(os.popen(f"{executable} --no-warnings --dump-json \"{url}\"").read())
	title = video_information["title"]
	upload_date = video_information["upload_date"]

	file_name = f"{title}-{upload_date}"
	os.popen(f"{executable} -o \"{file_name}\" --no-warnings --extract-audio --audio-format mp3 --paths {path} \"{url}\"").read()

	register_video(downloaded_channel_index, title, upload_date)

def download_videos() -> None:
	"""
	Downloads videos from the specified channels.

	This function iterates over the "to_download_channels" list and downloads videos from each channel.
	If a channel has already been downloaded, it skips the channel and moves to the next one.
	The downloaded videos are stored in the "downloaded_videos" list.

	Parameters:
		None

	Returns:
		None
	"""
	channel_downloaded_index = -1

	for i in range(len(to_download_channels)):
		channel_to_download = to_download_channels[i]

		if not channel_to_download in downloaded_channels:
			downloaded_channels.append(channel_to_download)
			downloaded_videos.append([])
			channel_downloaded_index = len(downloaded_channels) - 1
		else:
			channel_downloaded_index = downloaded_channels.find(channel_to_download)

		videos_url = to_download_videos[i]

		for url in videos_url:
			download_video(channel_downloaded_index, url)

# ---------------------------------------------------------------------------- #

def main():
	create_folders(to_download_channels)
	download_videos()
	save_json_file("downloaded.json", downloaded_channels, downloaded_videos)
	#save_json_file("to_download.json", [], [])


if __name__ == "__main__":
	main()
