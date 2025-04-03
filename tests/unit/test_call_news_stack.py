import aws_cdk as core
import aws_cdk.assertions as assertions

from call_news.call_news_stack import CallNewsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in call_news/call_news_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CallNewsStack(app, "call-news")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
