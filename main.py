import os
import platform
import timeit
import sequential
import multiprocess
import multithreading


def clean_screen():
	if platform.system() == "Windows":
		os.system('cls')
	else:
		os.system('clear')

def execute_and_time(function, name):
		clean_screen()
		print(f"You've chosen {name} option.\n")
		function()
		print(f"Downloading of videos in {name} mode was completed. \n")

def get_thread_count():
		while True:
			try:
				count = int(input("Enter the number of threads (4, 8, 16): "))
				if count in [4, 8, 16]:
					return count
				else:
					print("Invalid input. Please enter 4, 8, or 16.")
			except ValueError:
				print("Invalid input. Please enter a number.")

def sequentialOption():
	execute_and_time(sequential.main, "Sequential")

def multithreadingOption():
	thread_count = get_thread_count()
	execute_and_time(lambda: multithreading.main(thread_count), "Multithreading")

def multiprocessingOption():
	process_count = get_thread_count()
	execute_and_time(lambda: multiprocess.main(process_count), "Multiprocessing")

def salir():
	clean_screen()
	print("Has elegido salir. Adiós!")

def main():
	opciones = {"1": sequentialOption, "2": multithreadingOption, "3": multiprocessingOption, "4": salir}

	while True:
		print("\nChoose how you want to download the videos.  \nMake sure you have the channels in the 'to_download.json' file!!!.\n")
		print("1. Secuencial")
		print("2. Multithreading")
		print("3. Multiprocessing")
		print("4. Salir")

		opcion = input("Elige una opción: ")

		if opcion in opciones:
			if opcion == "4":
				break
			opciones[opcion]()
			break
		else:
			clean_screen()
			print("Opción inválida. Por favor, elige una opción entre 1 y 4.\n")


if __name__ == "__main__":
		main()

# {
# 	"channels": [
# 		"https://www.youtube.com/@memeshub8452",
# 		"https://www.youtube.com/@SiHayCine",
# 		"https://www.youtube.com/@AdamEschborn",
# 		"https://www.youtube.com/@JoeJWalker",
# 		"https://www.youtube.com/@WarnerBrosPictures"
# 	]
# }