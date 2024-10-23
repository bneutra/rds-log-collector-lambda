# RDS log collector
THIS IS A PROTOTYPE
Collects most recent db error logs and RDS events when an db failover occurs:
- RDS event subscription is created to send events to an SNS topic
- Lambda function is triggered by the SNS topic
- Logs and events get persisted to the cloudwatch log group associated with the Lambda
- To avoid over-collection, we have a rudimentary cache-ing scheme:
  we look back in cloudwatch logs to see if we've recently collected info

You'd probably want one of these per AWS region. i.e. The RDS event subscription resource doesn't belong in this root, it goes wherever your RDS instance is defined (it looks up the topic with a data source).