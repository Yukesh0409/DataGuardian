from airflow import DAG
from datetime import timedelta, datetime
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.providers.slack.notifications.slack_webhook import send_slack_webhook_notification


def testing_slack_notify():
    a = 3 + 4
    return a


def slack_alert(context):
    ti = context.get('task_instance')
    dag_name = context.get('task_instance').dag_id
    task_name = context.get('task_instance').task_id    
    execution_date = context.get('execution_date')
    log_url = context.get('task_instance').log_url 
    dag_run = context.get('dag_run') 
   
    mssg = f"""
        :red_circle: Pipeline Failed.        
        *Dag*:{dag_name}
        *Task*: {task_name}
        *Execution Date*: {execution_date}
        *Task Instance*: {ti}
        *Log Url*: {log_url}
        *Dag Run*: {dag_run}        
    """   
    slack_notification = SlackWebhookOperator(
            task_id = "tsk_slack_notification",
            http_conn_id = "slack_conn_id",
            message = mssg,
            channel = "#airflow-slack-integration-testing"
        )
    return slack_notification.execute(context=context)

def slack_alert_success(context):
    ti = context.get('task_instance')
    dag_name = context.get('task_instance').dag_id
    task_name = context.get('task_instance').task_id    
    execution_date = context.get('execution_date')
    log_url = context.get('task_instance').log_url 
    dag_run = context.get('dag_run') 
   
    mssg = f"""
        :green_circle: Pipeline Success.        
        *Dag*:{dag_name}
        *Task*: {task_name}
        *Execution Date*: {execution_date}
        *Task Instance*: {ti}
        *Log Url*: {log_url}
        *Dag Run*: {dag_run}        
    """   
    slack_notification = SlackWebhookOperator(
            task_id = "tsk_slack_notification",
            http_conn_id = "slack_conn_id",
            message = mssg,
            channel = "#airflow-slack-integration-testing"
        )
    return slack_notification.execute(context=context)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 8),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=3)
}

dag_failure_slack_webhook_notification = send_slack_webhook_notification(
        slack_webhook_conn_id="slack_conn_id", text=":red_circle: The task {{ task_instance.task_id }} in DAG {{ dag.dag_id }} failed"
    )

dag_success_slack_webhook_notification = send_slack_webhook_notification(
        slack_webhook_conn_id="slack_conn_id", text=":large_green_circle: The task {{ task_instance.task_id }} in DAG {{ dag.dag_id }} ran successfully"
    )

task_failure_slack_webhook_notification = send_slack_webhook_notification(
    slack_webhook_conn_id="slack_conn_id",
    text="The task {{ ti.task_id }} failed",
)

with DAG('Addition_Pipeline',
        default_args=default_args,
        schedule_interval = None,
        on_success_callback= [dag_success_slack_webhook_notification],
        on_failure_callback=[dag_failure_slack_webhook_notification],
        catchup=False) as dag:

        addtion_of_numbers = PythonOperator(
            task_id= 'tsk_addtion_of_numbers',
            python_callable=testing_slack_notify
            )