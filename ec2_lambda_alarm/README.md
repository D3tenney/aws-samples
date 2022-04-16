## Introduction
I'm bad at turning off EC2 instances when I'm done with them for the day.
This project runs a lambda on a scheduler and sends messages to an SNS
topic so a subscriber is alerted if EC2 instances are found in specified states,
such as 'pending' or 'running'.

The lambda can send a message per instance, one message listing all instances,
or both, and you can adjust this behavior by commenting out lines from `event_handler`
in `lambda_function.py`.

Instance tags, along with region and whether the message is for a
single instance or all instances
('message_type' of `instance` or `instance_list`),
are used to generate message
attributes, so subscribers can limit their subscription (ie: limit SNS
subscription to only be notified when the CreatedBy attribute of an instance
message is 'Devon'). Notifications for a list of all instances in a region
only have 'message_type' of 'instance_list' and 'region' attributes.

## Deployment
This project is created as an AWS SAM template. To deploy it, install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html#cliv2-linux-install)
and [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html).

Then edit to taste and run `. deploy.sh` and follow the prompts. The default
options should be fine. SAM will convert the resources described in
`template.yaml`
to a Cloudformation stack and deploy the stack to your AWS account using
the credentials of the profile you specify in `deploy.sh`.
The stack will print several outputs, including the
ARN for the SNS Topic, its name, and the name of the Lambda function, to help
you locate and identify the resources.

This project will only look at instances in the region it's deployed to,
so make sure to deploy it to the right region. An instance of this
application would have to be deployed in any region you want notifications for.

The application runs a bit slow, so if you have many EC2 instances, you may
need to adjust the `Timeout` property on the lambda function.

You can subscribe to the topic via the AWS CLI using the TopicArn you see
in the Outputs from deploying the stack.
(documentation [here](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sns/subscribe.html)).

For instance, if I only wanted to subscribe to messages listing all relevant
instances, I would run:
```bash
aws sns subscribe \
  --topic-arn <ARN here> \
  --protocol email \
  --notification-endpoint me@email.com \
  --attributes '{"FilterPolicy": "{\"message_type\": [\"instance_list\"]}"}'
```
 Note that subscriptions need to be confirmed.

Or you can subscribe to the SNS topic through the
Management Console. You can specify subscription filters there, too.

Once the stack is deployed and you've confirmed your subscription, you can
test the function with the function name from the stack outputs
(documentation [here](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/invoke.html)):
```bash
aws lambda invoke \
  --function-name <Function Name> \
  --invocation-type Event \
  response.json
```

## Teardown
Be Careful.

To tear down the stack when you're done with it, you can use `sam delete`.
If you changed the stack settings when you deployed it (name, region, profile,
  etc...), make sure you use the right settings here.
```bash
sam delete \
  --stack-name ec2-alarm \
  --region us-east-1 \
  --profile default
```
## Cost
Costs are pretty minimal for this project. Since the lambda runs on a scheduler,
you can make it run as often as you would like, but running many times a day
may be more annoying than costly.

Here's SNS pricing:
https://aws.amazon.com/sns/pricing/

And Lambda:
https://aws.amazon.com/lambda/pricing/

And the AWS Pricing Calculator:
https://calculator.aws/#/

## Testing
There's not much to this project, but I did write some messy little unit tests
for the lambda functionality.

To test (on Mac/Linux):
```bash
cd ./function
python3 -m venv venv
. ./venv/bin/activate
pip install --upgrade pip
pip install -r dev_requirements.txt
pytest
```

Then make sure you clean up before deploying the app:
```bash
deactivate
rm -rf ./__pycache__/
rm -rf ./venv/
rm -rf ./.pytest_cache/
```

## Notes
- Why not CloudWatch?
    Cloudwatch is great for ongoing resource monitoring. EC2 does not seem
    to provide a CloudWatch metric for state.
