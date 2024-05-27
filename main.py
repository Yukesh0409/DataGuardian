import os
import pandas as pd

def list_files_in_order(directory):
    try:
        all_entries = os.listdir(directory)
        files = [entry for entry in all_entries if os.path.isfile(os.path.join(directory, entry))]
        files.sort()
        for file in files:
            print(file)
    
    except FileNotFoundError:
        print(f"The directory '{directory}' does not exist.")
    except PermissionError:
        print(f"Permission denied to access the directory '{directory}'.")

def print_csv_in_chunks(file_path, chunk_size=500):
    try:
        # Use the chunksize parameter to read the CSV file in chunks
        chunk_iter = pd.read_csv(file_path, chunksize=chunk_size)

        for i, chunk in enumerate(chunk_iter):
            print(f"Chunk {i + 1}:\n")
            print(chunk)
            print("\n")
            chunk.to_csv("data/temp.csv")
            break

    except FileNotFoundError:
        print(f"The file '{file_path}' does not exist.")
    except pd.errors.EmptyDataError:
        print("No data found in the CSV file.")
    except pd.errors.ParserError:
        print("Error parsing the CSV file.")
    except Exception as e:
        print(f"An error occurred: {e}")





directory_path = r'D:\Projects\DataGuardian\airflow-docker\data\archive'
list_files_in_order(directory_path)
print_csv_in_chunks(r"D:\Projects\DataGuardian\airflow-docker\data\archive\yellow_tripdata_2019-01.csv")