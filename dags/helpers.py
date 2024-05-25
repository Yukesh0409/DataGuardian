# airflow-docker/dags/helpers.py

import pandas as pd
import os

DATA_DIR = '/opt/airflow/dags/data'
TAXI_ZONE_FILE = '/opt/airflow/dags/data/taxi_zone.csv'

def read_csv_files():
    # Read CSV files from the data directory
    csv_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith('.csv') and f != 'taxi_zone.csv']
    # Your code to read CSV files goes here

def join_with_taxi_zone():
    # Read the taxi_zone.csv file
    taxi_zone_df = pd.read_csv(TAXI_ZONE_FILE)
    # Your code to join with taxi_zone data goes here

def transform_data():
    # Your code to transform data goes here
    print("transform_data")

def validate_data():
    print("validate_data")

def send_notifications():
    # Your code to send notifications goes here
    print("send_notification")

def save_to_postgres():
    # Your code to save valid data to PostgreSQL goes here
    print("save")
