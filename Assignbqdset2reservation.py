# assign_datasets_to_reservation_dag.py
from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from google.cloud import bigquery_reservation_v1

PROJECT_ID = "your-gcp-project-id"  # Replace with your GCP project ID
PRIMARY_REGION = "US_central1"
RESERVATION_ID = "your_enterprise_plus_reservation"  # Replace with your reservation ID
DATASET_IDS_TO_ASSIGN = ["your_dataset_us_central1_1", "your_dataset_us_central1_2"]  # Replace with your dataset IDs in US_central1

def assign_dataset(dataset_id: str, reservation_id: str, project_id: str, location: str):
    """Assigns a BigQuery dataset to a reservation."""
    client = bigquery_reservation_v1.ReservationServiceClient()
    reservation_name = client.reservation_path(project_id, location, reservation_id)
    dataset_name = f"projects/{project_id}/datasets/{dataset_id}"

    request = bigquery_reservation_v1.AssignReservationRequest(
        name=reservation_name,
        assignee=dataset_name,
    )
    try:
        response = client.assign_reservation(request=request)
        print(f"Successfully assigned dataset '{dataset_id}' to reservation '{reservation_id}' in {location}.")
        print(response)
    except Exception as e:
        print(f"Error assigning dataset '{dataset_id}' to reservation '{reservation_id}' in {location}: {e}")
        raise

with DAG(
    dag_id="assign_bigquery_datasets_to_reservation",
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    schedule=None,
    tags=["bigquery", "disaster_recovery", "reservation"],
) as dag:
    assign_tasks = [
        PythonOperator(
            task_id=f"assign_dataset_{dataset_id.replace('-', '_')}",
            python_callable=assign_dataset,
            op_kwargs={
                "dataset_id": dataset_id,
                "reservation_id": RESERVATION_ID,
                "project_id": PROJECT_ID,
                "location": PRIMARY_REGION,
            },
        )
        for dataset_id in DATASET_IDS_TO_ASSIGN
    ]
