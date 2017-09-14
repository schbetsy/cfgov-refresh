from __future__ import unicode_literals

import argparse
import boto3
import logging

from alerts.github_alert import GithubAlert
from alerts.mattermost_alert import MattermostAlert

logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser()

parser.add_argument(
    '--queue_url',
    required=True,
    help='The SQS queue URL to read messages from',
)
parser.add_argument(
    '--aws_access_key_id',
    required=True,
    help='AWS Access Key',
)
parser.add_argument(
    '--aws_secret_access_key',
    required=True,
    help='AWS Secret Access Key',
)
parser.add_argument(
    '--github_token',
    required=True,
    help='Access token for Github account'
)
parser.add_argument(
    '--github_url',
    required=True,
    help='URL for Github (enterprise)'
)
parser.add_argument(
    '--github_user',
    required=True,
    help='Github user that repo lives under'
)
parser.add_argument(
    '--github_repo',
    required=True,
    help='Github repo name to post to'
)
parser.add_argument(
    '--mattermost_webhook_url',
    help='Mattermost webhook URL to post to chatroom'

)
parser.add_argument(
    '--mattermost_username',
    help='Mattermost user that is posting the message'

)


def cleanup_message(message):
    return message.replace(
        '#', '# '  # Avoids erroneous Github issue link
    ).replace(
        '[Open]', ''  # We want to expand the link
    )


def process_sqs_message(message, github_alert, mattermost_alert):
    body = cleanup_message(message.get('Body'))
    title = body.split(" - ")[0]

    logger.debug('Retrieved message {} from SQS'.format(body))

    issue = github_alert.post(
        title=title,
        body=body
    )
    if mattermost_alert:
        mattermost_alert.post(
            text='Alert: {}. Github issue at {}'.format(
                body,
                issue.html_url
            )
        )


if __name__ == '__main__':
    args = parser.parse_args()

    # Initialize Amazon SQS client
    client = boto3.client(
        'sqs',
        aws_access_key_id=args.aws_access_key_id,
        aws_secret_access_key=args.aws_secret_access_key,
        region_name='us-east-1'
    )

    # Intialize GithubAlert class
    github_alert = GithubAlert({
        'repo_name': args.github_repo,
        'token': args.github_token,
        'url': args.github_url,
        'user': args.github_user
    })

    mattermost_alert = None
    # Initialize MattermostAlert class (optional)
    if args.mattermost_webhook_url and args.mattermost_username:
        mattermost_alert = MattermostAlert({
            'webhook_url': args.mattermost_webhook_url,
            'username': args.mattermost_username
        })

    # Receive messages from specified SQS queue
    response = client.receive_message(
        QueueUrl=args.queue_url,
        MaxNumberOfMessages=10
    )

    for message in response.get('Messages', {}):
        process_sqs_message(
            message=message,
            github_alert=github_alert,
            mattermost_alert=mattermost_alert
        )
        client.delete_message(
            QueueUrl=args.queue_url,
            ReceiptHandle=message.get('ReceiptHandle')
        )
        logger.debug(
            'Deleted message {} from SQS'.format(message.get('Body'))
        )