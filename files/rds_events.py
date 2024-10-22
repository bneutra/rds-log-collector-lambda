import boto3
import json
import sys
from datetime import datetime, timedelta, timezone


def log_event_payload(db_instance_id: str, payload: dict) -> None:
    event = {
        "db_instance_id": db_instance_id,
        "payload": payload,
    }
    print(json.dumps(event, default=str))


def download_log_file(rds_client, db_instance_id: str, log_file: str) -> dict:
    # returns the most recent 10k lines of the log file
    # which seems adequate in this context
    response = rds_client.download_db_log_file_portion(
        DBInstanceIdentifier=db_instance_id,
        LogFileName=log_file,
    )
    return response


def gather_db_events(db_instance_id: str,hours: int = 3) -> None:
    # Create a boto3 RDS client
    rds_client = boto3.client('rds')

    # Set up the start and end times for event collection
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)  # Events from the past N hours

    # Call the DescribeEvents API
    events = rds_client.describe_events(
        SourceType="db-instance",  # Change this to 'db-snapshot', 'db-cluster', etc., if needed
        StartTime=start_time,
        EndTime=end_time,
        SourceIdentifier=db_instance_id
    )

    # Print recent events
    for event in events['Events']:
        log_event_payload(db_instance_id, event)

    response = rds_client.describe_db_log_files(
        DBInstanceIdentifier=db_instance_id,
    )
    for item in response["DescribeDBLogFiles"]:
        log_file = item["LogFileName"]
        if start_time.timestamp() * 1000 < item['LastWritten']:
            response = download_log_file(rds_client, db_instance_id, log_file)
            for msg in response["LogFileData"].split("\n"):
                log_event_payload(db_instance_id, {"log_file": log_file, "message": msg})


if __name__ == "__main__":
    gather_db_events(sys.argv[1])
