# initiate_bigquery_failover_dag.py
from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

PROJECT_ID = "your-gcp-project-id"  # Replace with your GCP project ID
PRIMARY_REGION = "US_central1"
SECONDARY_REGION = "US_east1"
DATASET_IDS_TO_FAILOVER = ["your_dataset_us_central1_1", "your_dataset_us_central1_2"]  # Replace with the dataset IDs you want to failover

with DAG(
    dag_id="initiate_bigquery_failover",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    schedule=None,
    tags=["bigquery", "disaster_recovery", "failover"],
) as dag:
    failover_tasks = [
        BashOperator(
            task_id=f"initiate_failover_{dataset_id.replace('-', '_')}",
            bash_command=f"bq mk --failover_region={SECONDARY_REGION} {PROJECT_ID}:{dataset_id}",
        )
        for dataset_id in DATASET_IDS_TO_FAILOVER
    ]
  
