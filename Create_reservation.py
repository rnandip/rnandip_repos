from __future__ import annotations

import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

PROJECT_ID = "your-gcp-project-id"  # Replace with your GCP project ID
LOCATION = "asia-south1"  # Replace with your desired location (e.g., us-central1)
RESERVATION_NAME = "my-composer-reservation"
RESERVATION_SIZE_SLOTS = 500
RESERVATION_EDITION = "STANDARD"  # Optional: STANDARD, ENTERPRISE, ENTERPRISE_PLUS
AUTOSCALE_MAX_SLOTS = 1000  # Optional: For autoscaling

def check_reservation_exists(project_id: str, location: str, reservation_name: str) -> bool:
    """Checks if a BigQuery reservation exists."""
    client = bigquery.ReservationServiceClient()
    reservation_id = f"projects/{project_id}/locations/{location}/reservations/{reservation_name}"
    try:
        client.get_reservation(name=reservation_id)
        print(f"Reservation '{reservation_name}' already exists in {location}.")
        return True
    except NotFound:
        print(f"Reservation '{reservation_name}' does not exist in {location}.")
        return False
    except Exception as e:
        print(f"An error occurred while checking for reservation: {e}")
        return False

def create_bigquery_reservation(project_id: str, location: str, reservation_name: str, size_slots: int, edition: str | None = None, autoscale_max_slots: int | None = None) -> None:
    """Creates a BigQuery reservation."""
    client = bigquery.ReservationServiceClient()
    parent = client.location_path(project_id, location)
    reservation = bigquery.types.Reservation(
        name=reservation_name,
        slot_capacity=size_slots,
        edition=edition,
    )
    if autoscale_max_slots is not None:
        reservation.autoscale.max_slots = autoscale_max_slots

    try:
        if not check_reservation_exists(project_id, location, reservation_name):
            response = client.create_reservation(
                parent=parent,
                reservation_id=reservation_name,
                reservation=reservation,
            )
            print(f"Successfully created reservation: {response.name}")
        else:
            print("Skipping reservation creation as it already exists.")
    except Exception as e:
        print(f"An error occurred while creating the reservation: {e}")

with DAG(
    dag_id="create_bigquery_reservation",
    start_date=datetime.datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["bigquery", "reservation"],
) as dag:
    check_if_reservation_exists_task = PythonOperator(
        task_id="check_if_reservation_exists",
        python_callable=check_reservation_exists,
        op_kwargs={
            "project_id": PROJECT_ID,
            "location": LOCATION,
            "reservation_name": RESERVATION_NAME,
        },
    )

    create_reservation_task = PythonOperator(
        task_id="create_reservation",
        python_callable=create_bigquery_reservation,
        op_kwargs={
            "project_id": PROJECT_ID,
            "location": LOCATION,
            "reservation_name": RESERVATION_NAME,
            "size_slots": RESERVATION_SIZE_SLOTS,
            "edition": RESERVATION_EDITION,
            "autoscale_max_slots": AUTOSCALE_MAX_SLOTS,
        },
    )

    check_if_reservation_exists_task >> create_reservation_task
