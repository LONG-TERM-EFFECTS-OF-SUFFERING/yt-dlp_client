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
    print(f"You've chosen {name} option.")
    start = timeit.default_timer()
    function()
    end = timeit.default_timer()
    time_in_seconds = end - start
    clean_screen()
    print(f"Downloading of videos in {name} mode was completed. Elapsed time: {time_in_seconds:.2f} seconds.\n")

def sequentialOption():
    execute_and_time(sequential.main, "Sequential")

def multithreadingOption():
    execute_and_time(multithreading.main, "Multithreading")

def multiprocessingOption():
    execute_and_time(multiprocess.main, "Multiprocessing")

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
			opciones[opcion]()
			if opcion == "4":
				break
		else:
			clean_screen()
			print("Opción inválida. Por favor, elige una opción entre 1 y 4.\n")


if __name__ == "__main__":
    main()
