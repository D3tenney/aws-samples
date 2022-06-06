import aws_cdk as core
import aws_cdk.assertions as assertions

from stacks.data_stack import LocalGlueDevStack

# example tests. To run these tests, uncomment this file along with the example
# resource in local_glue_dev/local_glue_dev_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = LocalGlueDevStack(app, "local-glue-dev")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
