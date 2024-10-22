import json
import logging
import rds_events

logger = logging.getLogger()
logger.setLevel(logging.INFO)


TRIGGER_EVENTS = ["DB instance restarted"]
HOURS_TO_GATHER = 3

def lambda_handler(event: dict, context) -> dict:
    # Log the event for debugging purposes
    #logger.info("Event: " + json.dumps(event))

    # Extract the message from the SNS event
    sns_message = event['Records'][0]['Sns']['Message']
    logger.info(f"RDS Event received: {sns_message}")

    # Handle the RDS event accordingly
    rds_event = json.loads(sns_message)
    db_instance_id = rds_event.get("Source ID")
    event_message = rds_event.get("Event Message")
    if db_instance_id is None or event_message is None:
        raise ValueError("Invalid RDS event message format")
    rds_events.log_event_payload(db_instance_id, {"event_message" : event_message})
    # only collect logs once, ignore other events
    if event_message in TRIGGER_EVENTS:
        rds_events.gather_db_events(db_instance_id, HOURS_TO_GATHER)

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
