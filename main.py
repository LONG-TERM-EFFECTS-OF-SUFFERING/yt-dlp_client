import multiprocess
import multithreading
import os
import platform
import sequential
import timeit


def clear_screen() -> None:
	if platform.system() == "Windows":
		os.system("cls")
	else:
		os.system("clear")

def execute_and_time(function: function, mode: str) -> None:
		clear_screen()
		print(f"You have chosen {mode} mode\n")
		start = timeit.default_timer()
		function()
		end = timeit.default_timer()
		print(f"Mode: {mode}\tTime:{end - start}")

def get_processing_units() -> int:
		while True:
			try:
				count = int(input("Enter the number of processing units (threads or processes) (4, 8, 16): "))
				if count in [4, 8, 16]:
					return count
				else:
					print("Error: invalid number")
			except ValueError:
				print("Erro: invalid input")

def sequential_mode() -> None:
	execute_and_time(sequential.main, "Sequential")

def multithreading_mode() -> None:
	thread_count = get_processing_units()
	execute_and_time(lambda: multithreading.main(thread_count), "Multithreading")

def multiprocessing_mode() -> None:
	process_count = get_processing_units()
	execute_and_time(lambda: multiprocess.main(process_count), "Multiprocessing")

def main() -> None:
	opciones = { "1": sequential_mode, "2": multithreading_mode, "3": multiprocessing_mode, "4": None }

	while True:
		print("""
		Choose how you want to download the videos.
		Make sure you have the channels in the \"to_download.json\" file!\n

		1. Sequential.
		2. Multithreading.
		3. Multiprocessing.
		4. Exit
		""")

		option = input("Write an option: ")

		if option in opciones:
			if option == "4":
				break
			opciones[option]()
			break
		else:
			clear_screen()
			print("Error: invalid option")


if __name__ == "__main__":
		main()
