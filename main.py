import os
import time
import csv
import pandas as pd
from trigger import start_trigger

def list_files_in_order(directory):
    try:
        all_entries = os.listdir(directory)
        files = [entry for entry in all_entries if os.path.isfile(os.path.join(directory, entry))]
        files.sort()
        # for file in files:
            # print(file)      
        return files
    
    except FileNotFoundError:
        print(f"The directory '{directory}' does not exist.")
    except PermissionError:
        print(f"Permission denied to access the directory '{directory}'.")


def print_csv_in_chunks(file_path, chunk_size=500):
    try:
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

def csv_details(file_path):
    row_count = 0
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        column_count = len(headers)
        for _ in reader:
            row_count += 1
    row_count += 1

    return row_count, column_count

def file_order(file_list):
    for files_path in file_list:
        file_directory = os.path.join(directory_path,files_path)
        print("Starting data validation and transformation for",files_path)
        # rows, columns = csv_details(file_directory)
        # print(f'The CSV file has {rows} rows and {columns} columns.')
        # time.sleep(2)
        print("Splitting into chunks")
        print_csv_in_chunks(file_directory)
        time.sleep(2)
        print("Triggering Airflow")
        start_trigger()
        time.sleep(10)





if __name__ == "__main__":
    directory_path = r"D:\Projects\DataGuardian\airflow-docker\data\archive"
    file_list = []
    file_list = list_files_in_order(directory_path)
    file_order(file_list)
    # print_csv_in_chunks(file_directory)