# capture RDS events and db logs if we receive an RDS event
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Events.Messages.html#USER_Events.Messages.instance

import json
import logging
import rds_events

logger = logging.getLogger()
logger.setLevel(logging.INFO)


HOURS_TO_GATHER = 3

def lambda_handler(event: dict, context) -> dict:
    sns_message = event['Records'][0]['Sns']['Message']
    logger.info(f"RDS Event received: {sns_message}")

    rds_event = json.loads(sns_message)
    db_instance_id = rds_event.get("Source ID")
    event_message = rds_event.get("Event Message")
    if db_instance_id is None or event_message is None:
        raise ValueError("Invalid RDS event message format")
    rds_events.log_event_payload(db_instance_id, {"event_message" : event_message})
    rds_events.gather_db_events(db_instance_id, HOURS_TO_GATHER)

    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
