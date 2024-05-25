from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


default_args = {
 'owner': 'Yukesh',
 'start_date': datetime (2024, 5, 24),
 'retries': 0,
}

dag = DAG ('my_second_dag', default_args=default_args, schedule_interval=None)

def task1():
 print ("Executing Task 1")

def task2():
 print ("Executing Task 2")

task_1 = PythonOperator(
 task_id='task_1',
 python_callable=task1,
 dag=dag,
)
task_2 = PythonOperator(
 task_id='task_2',
 python_callable=task2,
 dag=dag,
)

task_1 >> task_2