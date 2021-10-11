"""
Copyright 2017 EMD Group (emdgroup.com)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import boto3
import json
import sys
from datetime import datetime, timezone
from urllib import parse

from awscli.customizations.commands import BasicCommand
from awscli.customizations.utils import create_client_from_parsed_globals
from awscli.customizations.s3.subcommands import PAGE_SIZE

def awscli_initialize(cli):
    cli.register('building-command-table.s3', _inject_touch)


def _inject_touch(command_table, session, **kwargs):
    command_table['touch'] = S3Touch(session)

class S3Touch(BasicCommand):
    """Toch objects in S3 and trigger events"""
    NAME = 'touch'

    DESCRIPTION = BasicCommand.FROM_FILE('s3touch_description.rst', root_module=sys.modules[__name__])

    EXAMPLES = BasicCommand.FROM_FILE('s3touch.rst', root_module=sys.modules[__name__])

    ARG_TABLE = [
        {
            'name': 'bucket',
            'help_text': 'Name of the bucket to list.',
            'positional_arg': True,
        },
        {
            'name': 'prefix',
            'required': False,
            'help_text': (
                "Limits the response to keys that begin with the spec- "
                "ified prefix."),
        },
        {
            'name': 'page-size', 'cli_type_name': 'integer',
            'help_text': (
                'The number of results to return in each response to a list '
                'operation. The default value is 1000 (the maximum allowed). '
                'Using a lower value may help if an operation times out.')
        },
        {
            'name': 'max-items', 'cli_type_name': 'integer',
            'help_text': (
                'The total number of items to process.')
        },
        {
            'name': 'starting-token',
            'help_text': (
                'A token to specify where to start paginating. This is the '
                'NextToken from a previous ``aws ls`` response.')
        },
        {
            'name': 'start-after',
            'help_text': (
                'StartAfter is where you want Amazon S3 to start listing '
                'from. Amazon S3 starts listing after this specified key. '
                'StartAfter can be any key in the bucket.')
        },
        {
            'name': 'delimiter',
            'help_text': ('Character you use to group keys.')
        },
    ]

    def _run_main(self, parsed_args, parsed_globals):
        s3 = create_client_from_parsed_globals(
            self._session, 's3', parsed_globals)
        self._lambda = create_client_from_parsed_globals(
            self._session, 'lambda', parsed_globals)
        self._sns = create_client_from_parsed_globals(
            self._session, 'sns', parsed_globals)
        self._sqs = create_client_from_parsed_globals(
            self._session, 'sqs', parsed_globals)
        sts = create_client_from_parsed_globals(
            self._session, 'sts', parsed_globals)

        self._notification_configuration = s3.get_bucket_notification_configuration(
            Bucket=parsed_args.bucket,
        )
        self._region = s3.get_bucket_location(Bucket=parsed_args.bucket)['LocationConstraint']
        self._caller = sts.get_caller_identity()

        paginator = s3.get_paginator('list_objects_v2')
        params = {
            'Bucket': parsed_args.bucket,
            'PaginationConfig': {}
        }
        if parsed_args.delimiter is not None:
            params['Delimiter'] = parsed_args.delimiter
        if parsed_args.start_after is not None:
            params['StartAfter'] = parsed_args.start_after
        if parsed_args.prefix is not None:
            params['Prefix'] = parsed_args.prefix
        if parsed_args.page_size is not None:
            params['PaginationConfig']['PageSize'] = parsed_args.page_size
        if parsed_args.max_items is not None:
            params['PaginationConfig']['MaxItems'] = parsed_args.max_items
        if parsed_args.starting_token is not None:
            params['PaginationConfig']['StartingToken'] = parsed_args.starting_token

        iterator = paginator.paginate(**params)

        for response in iterator:
            if(response['KeyCount'] == 0):
                print('We are done here')
            else:
                [self.process_file(parsed_args.bucket, file) for file in response['Contents']]
        return 0

    def process_file(self, bucket, file):
        for key in self._notification_configuration:
            if(key == 'ResponseMetadata'):
                continue
            configs = self._notification_configuration[key]
            for config in configs:
                if config.get('Filter') and not self.evaluate_filter(config['Filter'], file):
                    continue

                if(key == 'LambdaFunctionConfigurations'):
                    self.handle_lambda_notification(bucket, file, config)
                elif(key == 'TopicConfigurations'):
                    self.handle_topic_notification(bucket, file, config)
                elif(key == 'QueueConfigurations'):
                    self.handle_queue_notification(bucket, file, config)
                else:
                    print('{} is currently not supported'.format(key))

    def build_event(self, bucket, file, config):
        date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return json.dumps({
            'Records':[{
                'eventVersion': '2.0', 'eventSource': 'aws:s3', 'awsRegion': self._region,
                'userIdentity': { 'principalId': 'AWS:{}'.format(self._caller['UserId']) },
                'eventTime': date, 'eventName': 'ObjectCreated:Put', 's3': {
                    'configurationId': config['Id'], 's3SchemaVersion': '1.0', 'object': {
                        'eTag': json.loads(file['ETag']), 'key': parse.quote_plus(file['Key']), 'size': file['Size'],
                    }, 'bucket': { 'arn': 'arn:aws:s3:::{}'.format(bucket), 'name': bucket }
                }}]
        })

    def evaluate_filter(self, filter, file):
        for attr in filter:
            rules = filter[attr]['FilterRules']
            for rule in rules:
                if rule['Name'] == 'Prefix' and not file[attr].startswith(rule['Value']):
                    return False
                if rule['Name'] == 'Suffix' and not file[attr].endswith(rule['Value']):
                    return False
        return True

    def handle_lambda_notification(self, bucket, file, config):
        event = self.build_event(bucket, file, config);
        fn    = config['LambdaFunctionArn']
        self._lambda.invoke(
            FunctionName=fn,
            InvocationType='Event',
            Payload=event
        )
        sys.stdout.write('published "{}" to {}'.format(file['Key'], fn) + '\n')

    def handle_topic_notification(self, bucket, file, config):
        event = self.build_event(bucket, file, config);
        self._sns.publish(
            TopicArn=config['TopicArn'],
            Message=event
        )
        sys.stdout.write('published "{}" to {}'.format(file['Key'], config['TopicArn']) + '\n')

    def handle_queue_notification(self, bucket, file, config):
        event = self.build_event(bucket, file, config);
        if(config.get('QueueUrl') is None):
            config['QueueUrl'] = self._sqs.get_queue_url(
                QueueName=config['QueueArn'].split(':')[-1]
            )['QueueUrl']
        self._sqs.send_message(
            QueueUrl=config['QueueUrl'],
            MessageBody=event
        )
        sys.stdout.write('published "{}" to {}'.format(file['Key'], config['QueueArn']) + '\n')
