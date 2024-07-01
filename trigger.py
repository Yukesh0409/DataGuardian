import requests
from requests.auth import HTTPBasicAuth
import time
from datetime import datetime

AIRFLOW_BASE_URL = 'http://localhost:8080'
DAG_ID = 'taxi_trip_processing'
USERNAME = 'yukesh'
PASSWORD = 'yukesh'
RETRY_DELAY = 10  


def trigger_dag(dag_id, run_id):
    url = f"{AIRFLOW_BASE_URL}/api/v1/dags/{dag_id}/dagRuns"
    data = {
        "dag_run_id": run_id
    }
    response = requests.post(url, json=data, auth=HTTPBasicAuth(USERNAME, PASSWORD))
    if response.status_code == 200:
        print(f"Successfully triggered DAG {dag_id} with run_id {run_id}")
    elif response.status_code == 403:
        print(f"Failed to trigger DAG {dag_id}: Forbidden. Please check your user permissions.")
    elif response.status_code == 409:
        print(f"Failed to trigger DAG {dag_id}: Conflict. DAGRun ID {run_id} already exists.")
    else:
        print(f"Failed to trigger DAG {dag_id}: {response.text}")

def start_trigger():
    run_id = f"manual_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    trigger_dag(DAG_ID, run_id)
    time.sleep(2)  
