from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.providers.slack.notifications.slack_webhook import send_slack_webhook_notification
import pandas as pd
import csv

default_args = {
    'owner': 'Yukesh',
    'start_date': datetime(2024, 5, 24),
    'retries': 1,
    'retry_delay': timedelta(minutes=5), 
    'email_on_failure': True,
    'email': ['asyukesh@gmail.com'] 
}


def load_data(file_path, **kwargs):
    try:
        df = pd.read_csv(file_path)
        kwargs['ti'].xcom_push(key='loaded_df', value=df.to_json(date_format='iso'))
    except Exception as e:
        raise ValueError(f"Error loading data from {file_path}: {str(e)}")

def remove_unwanted_columns(ti, **kwargs):
    try:
        columns_to_keep = [
            'VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime',
            'passenger_count', 'trip_distance', 'PULocationID', 'DOLocationID',
            'fare_amount', 'total_amount'
        ]
        df = pd.read_json(ti.xcom_pull(task_ids='load_data', key='loaded_df'))
        df = df[columns_to_keep]
        ti.xcom_push(key='processed_df', value=df.to_json(date_format='iso'))
    except Exception as e:
        raise ValueError(f"Error removing unwanted columns: {str(e)}")

def validate_data(ti, **kwargs):
    try:
        df = pd.read_json(ti.xcom_pull(task_ids='remove_unwanted_columns', key='processed_df'))
        missing_values = df.isnull().sum()
        if missing_values.any():
            log_errors("validate_data", "Missing values", missing_values.to_dict())
            raise ValueError(f"Missing values in DataFrame: {missing_values.to_dict()}")

        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
        df['VendorID'] = df['VendorID'].astype(int)
        df['passenger_count'] = df['passenger_count'].astype(int)
        df['trip_distance'] = df['trip_distance'].astype(float)
        df['PULocationID'] = df['PULocationID'].astype(int)
        df['DOLocationID'] = df['DOLocationID'].astype(int)
        df['fare_amount'] = df['fare_amount'].astype(float)
        df['total_amount'] = df['total_amount'].astype(float)
        
        ti.xcom_push(key='validated_df', value=df.to_json(date_format='iso'))
    except Exception as e:
        log_errors("validate_data", "Validation error", str(e))
        raise ValueError(f"Error validating data: {str(e)}")

def generate_new_columns(ti, **kwargs):
    try:
        df = pd.read_json(ti.xcom_pull(task_ids='validate_data', key='validated_df'))
        df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
        df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
        df['trip_duration_minutes'] = (df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']).dt.total_seconds() / 60
        df['average_speed_mph'] = df['trip_distance'] / (df['trip_duration_minutes'] / 60)
        df['is_short_trip'] = df['trip_distance'].apply(lambda x: 1 if x < 1 else 0)
        df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
        df['pickup_day_of_week'] = df['tpep_pickup_datetime'].dt.dayofweek
        df['is_weekend'] = df['pickup_day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        df['tip_percentage'] = ((df['total_amount'] - df['fare_amount']) / df['fare_amount']) * 100

        def categorize_distance(distance):
            if distance < 1:
                return 'short'
            elif distance < 5:
                return 'medium'
            else:
                return 'long'
        df['trip_distance_category'] = df['trip_distance'].apply(categorize_distance)
        
        ti.xcom_push(key='final_df', value=df.to_json(date_format='iso'))
    except Exception as e:
        log_errors("generate_new_columns", "Column generation error", str(e))
        raise ValueError(f"Error generating new columns: {str(e)}")

def rename_columns(ti, **kwargs):
    try:
        df = pd.read_json(ti.xcom_pull(task_ids='generate_new_columns', key='final_df'))
        df.rename(columns={
            'VendorID': 'vendor_id',
            'tpep_pickup_datetime': 'pickup_datetime',
            'tpep_dropoff_datetime': 'dropoff_datetime',
            'passenger_count': 'num_passengers',
            'trip_distance': 'trip_distance_miles',
            'PULocationID': 'pickup_location_id',
            'DOLocationID': 'dropoff_location_id',
            'fare_amount': 'fare_amount_usd',
            'total_amount': 'total_amount_usd'
        }, inplace=True)
        
        ti.xcom_push(key='renamed_df', value=df.to_json(date_format='iso'))
    except Exception as e:
        log_errors("rename_columns", "Column renaming error", str(e))
        raise ValueError(f"Error renaming columns: {str(e)}")

def write_output_to_csv(ti, file_path, **kwargs):
    try:
        df = pd.read_json(ti.xcom_pull(task_ids='rename_columns', key='renamed_df'))
        df.to_csv(file_path, index=False)
    except Exception as e:
        log_errors("write_output_to_csv", "Output writing error", str(e))
        raise ValueError(f"Error writing output to {file_path}: {str(e)}")

def log_errors(task_id, error_type, error_message):
    error_log_path = '/opt/airflow/data/error.csv'
    with open(error_log_path, 'a', newline='') as error_file:
        writer = csv.writer(error_file)
        writer.writerow([datetime.now(), task_id, error_type, error_message])


dag_failure_slack_webhook_notification = send_slack_webhook_notification(
        slack_webhook_conn_id="slack_conn_id", text=":red_circle: The DAG {{ dag.dag_id }} run with ID {{ run_id }} failed"
    )

dag_success_slack_webhook_notification = send_slack_webhook_notification(
        slack_webhook_conn_id="slack_conn_id", text=":large_green_circle: The DAG {{ dag.dag_id }} run with ID {{ run_id }} ran successfully"
    )

dag = DAG('taxi_trip_data_pipeline',
          default_args=default_args,
          description='A DAG to process taxi trip data',
          schedule_interval=None,
          on_success_callback= [dag_success_slack_webhook_notification],
          on_failure_callback=[dag_failure_slack_webhook_notification]
          ) 

load_data_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    op_kwargs={'file_path': '/opt/airflow/data/temp.csv'},  
    dag=dag,
)

remove_columns_task = PythonOperator(
    task_id='remove_unwanted_columns',
    python_callable=remove_unwanted_columns,
    provide_context=True,
    dag=dag,
)

validate_data_task = PythonOperator(
    task_id='validate_data',
    python_callable=validate_data,
    provide_context=True,  
    dag=dag,
)

generate_columns_task = PythonOperator(
    task_id='generate_new_columns',
    python_callable=generate_new_columns,
    provide_context=True,
    dag=dag,
)

rename_columns_task = PythonOperator(
    task_id='rename_columns',
    python_callable=rename_columns,
    provide_context=True,
    dag=dag,
)

write_output_task = PythonOperator(
    task_id='write_output_to_csv',
    python_callable=write_output_to_csv,
    op_kwargs={'file_path': '/opt/airflow/data/output.csv'}, 
    provide_context=True, 
    dag=dag,
)


load_data_task >> remove_columns_task >> validate_data_task >> generate_columns_task >> rename_columns_task >> write_output_task
