from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryExecuteQueryOperator
from airflow.utils.dates import days_ago

PROJECT_ID = "your-gcp-project-id"  # Replace with your GCP project ID
REGION = "your-bigquery-region"  # Replace with your BigQuery region (e.g., "US", "EU")
RESERVATION_ID = "your-reservation-id"  # Replace with your BigQuery reservation ID
DATASET_TO_ASSIGN = "your_dataset_to_assign" # Replace with the dataset ID you want to assign

with DAG(
    dag_id='assign_dataset_to_bigquery_reservation',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=['bigquery', 'reservation'],
) as dag:
    assign_dataset = BigQueryExecuteQueryOperator(
        task_id='assign_dataset_to_reservation',
        sql=f"""
            ALTER DATASET `{PROJECT_ID}.{DATASET_TO_ASSIGN}`
            SET OPTIONS (
              reservation_id='{RESERVATION_ID}'
            );
        """,
        use_legacy_sql=False,
        location=REGION,
        project_id=PROJECT_ID,
    )
