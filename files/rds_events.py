import boto3
import json
import os
import sys
from datetime import datetime, timedelta, timezone


# If we see this message, no need to gather logs again
# for the same instance in the last N minutes
GATHERING_MSG="Gathering events and logs for %s"
COOLOFF_MINUTES = 30
LOG_GROUP_NAME = os.environ.get("CLOUDWATCH_LOG_GROUP_NAME")


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


def is_already_logged(database_instance_id: str, cloudwatch_logs_client, minutes: int = COOLOFF_MINUTES) -> bool:
    # if we've already gathered logs for this instance in the last N minutes
    # no need to do it again. We're basically using cloudwatch logs as state store here.
    time_now = datetime.now(timezone.utc)
    time_minutes_ago = time_now - timedelta(minutes=minutes)
    start_time = int(time_minutes_ago.timestamp() * 1000)
    end_time = int(time_now.timestamp() * 1000)
    msg = GATHERING_MSG % database_instance_id
    # Retrieve log events from the specified log group (and optionally log stream)
    response = cloudwatch_logs_client.filter_log_events(
        logGroupName=LOG_GROUP_NAME,
        startTime=start_time,
        endTime=end_time,
        filterPattern=f"%{msg}%",
        limit=10000
    )

    if len(response['events']):
        timestamp = response['events'][0]['timestamp']
        dt = datetime.fromtimestamp(timestamp / 1000.0)
        print(f"Already gathered events for {database_instance_id} at {dt}")
        return True
    return False


def gather_db_events(db_instance_id: str,hours: int = 3) -> None:
    client = boto3.client('logs')
    if is_already_logged(db_instance_id, client):
        return

    log_event_payload(db_instance_id, {"message": GATHERING_MSG % db_instance_id})
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
        log_event_payload(db_instance_id, dict(event))

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
