import json
import os
from datetime import datetime


def load_json_file(file_name: str) -> dict:
	try:
		with open(file_name, 'r') as file:
			file_content = json.load(file)
			channels = file_content["channels"]
			videos = file_content["videos"]

			if len(channels) != len(videos):
				raise ValueError()
	except ValueError:
		print("Error: the number of channels does not match the number of videos")

	return (channels, videos)

(downloaded_channels, downloaded_videos) = load_json_file("downloaded.json")
(to_download_channels, to_download_videos) = load_json_file("to_download.json")

# ---------------------------------------------------------------------------- #

def create_folders(channels: list[str]) -> None:
	for channel_name in channels:
		new_channel_name = channel_name.replace(" ", "_")
		path = f"downloads/{new_channel_name}"

		if not os.path.exists(path):
			os.makedirs(path)

def register_video(channel_index: int, video_title: str, release_date: str) -> None:
	video = {
		"title": video_title,
		"upload_date": release_date,
		"download_date": datetime.now().strftime("%Y-%m-%d")
	}

	downloaded_videos[channel_index].append(video)

def download_video(channel_downloaded_index: int, url: str) -> None: # Index in the to_download or downloaded?
	channel = downloaded_channels[channel_downloaded_index]
	path = f"downloads/{channel.replace(" ", "_")}"

	executable = "G:\yt-dlp\yt-dlp.exe"

	video_information = json.loads(os.popen(f"{executable} --no-warnings --dump-json \"{url}\"").read())
	title = video_information["title"]
	upload_date = video_information["upload_date"]

	file_name = f"{title}-{upload_date}"
	output = os.popen(f"{executable} -o \"{file_name}\" --extract-audio --audio-format mp3 --paths {path} \"{url}\"").read()
	print(output)

	register_video(channel_downloaded_index, title, upload_date)

def download_videos() -> None:
	channel_downloaded_index = -1

	for i in range (len(to_download_channels)):
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

def extract_audio(video) -> None:
	print(f"Extracting audio from video {video}")

# ---------------------------------------------------------------------------- #

def main():
	create_folders(to_download_channels)
	print(downloaded_channels)
	print(downloaded_videos)
	download_videos()
	print(downloaded_channels)
	print(downloaded_videos)

if __name__ == "__main__":
	main()
