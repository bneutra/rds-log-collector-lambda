# RDS log collector
THIS IS A PROTOTYPE
Collects most recent db error logs and RDS events when an db failover occurs:
- RDS event subscription is created to send events to an SNS topic
- Lambda function is triggered by the SNS topic
- Logs and events get persisted to the cloudwatch log group associated with the Lambda
