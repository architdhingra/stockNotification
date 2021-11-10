import logging
import time
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

sns_client = boto3.client('sns')


def subscribe(topic, protocol, endpoint):
    """
    :param topic: The topic to subscribe to.
    :param protocol: The protocol of the endpoint, such as 'sms' or 'email'.
    :param endpoint: The endpoint that receives messages, such as a phone number
                     (in E.164 format) for SMS messages, or an email address for
                     email messages.
    :return: The newly added subscription.
    """
    try:
        subscription = sns_client.subscribe(
            TopicArn=topic, Protocol=protocol, Endpoint=endpoint, ReturnSubscriptionArn=True)
        logger.info("Subscribed %s %s to topic %s.", protocol, endpoint, topic)
    except ClientError:
        logger.exception(
            "Couldn't subscribe %s %s to topic %s.", protocol, endpoint, topic)
        raise
    else:
        return subscription
