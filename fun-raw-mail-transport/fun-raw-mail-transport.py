# Copyright 2019 Melvin Perello <melvinperello@gmail.com>
# License: MIT Open Source License <https://opensource.org/licenses/MIT>
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import mailparser
import json
import boto3
import os
import shutil

# ------------------------------------------------------------------------------
# Static
# ------------------------------------------------------------------------------
S3_CLIENT = boto3.client('s3')

FUN_ENV = os.environ['FUN_ENV']
FUN_CLEANUP = os.environ['FUN_CLEANUP']
FUN_BUCKET = os.environ['FUN_BUCKET']
FUN_DOMAIN = os.environ['FUN_DOMAIN']

# ------------------------------------------------------------------------------
# X-Ray
# ------------------------------------------------------------------------------
# - https://docs.aws.amazon.com/xray/latest/devguide/scorekeep-lambda.html
# - https://medium.com/nordcloud-engineering/tracing-serverless-application-with-aws-x-ray-2b5e1a9e9447
#print('X-Ray Active Tracing Enabled.')
#from aws_xray_sdk.core import xray_recorder
#from aws_xray_sdk.core import patch_all
#patch_all()
# ------------------------------------------------------------------------------
# Liham Class
# ------------------------------------------------------------------------------
class Liham(object):
    def __init__(self):
        self._attachments = list()
        self.date = ''
        self._sender = list()
        self._headers = dict()
        self.message_id = ''
        self._received = list()
        self.subject = ''
        self.mail_text = ''
        self.mail_html = ''
        self._recipients = list()
        self.timezone = ''

    # --------------
    # attachments
    # --------------
    @property
    def attachments(self):
        return self._attachments

    # --------------
    # headers
    # --------------
    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = value

    # --------------
    # received
    # --------------
    @property
    def received(self):
        return self._received

    @received.setter
    def received(self, value):
        self._received = value

    # --------------
    # recipients
    # --------------
    @property
    def recipients(self):
        return self._recipients

    @recipients.setter
    def recipients(self, value):
        self._recipients = value

    # --------------
    # sender
    # --------------
    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, value):
        self._sender = value

    # --------------
    # methods
    # --------------
    def isSpam(self):
        try:
            return self._headers['X-SES-Spam-Verdict'] != 'PASS'
        except KeyError as ke:
            return True

    def isVirus(self):
        try:
            return self._headers['X-SES-Virus-Verdict'] != 'PASS'
        except KeyError as ke:
            return True

    def toJson(self):
        return {
            'message_id': self.message_id,
            'isSpam' : self.isSpam(),
            'isVirus' : self.isVirus(),
            'headers' : self._headers,
            'received' : self._received,
            'date' : str(self.date),
            'timezone' : self.timezone,
            'sender' : self._sender,
            'recipients' : self._recipients,
            'subject' : self.subject,
            'text' : self.mail_text,
            'html' : self.mail_html,
            'attachments' : self._attachments
        }


    @staticmethod
    def create_from_file(file):
        liham = Liham()
        mail = mailparser.parse_from_file(file)
        for attachment in mail.attachments:
            attach = dict()
            attach['filename'] = attachment.get('filename' , None)
            attach['payload'] = attachment.get('payload' , None)
            attach['binary'] = attachment.get('binary' , None)
            attach['mail_content_type'] = attachment.get('mail_content_type' , None)
            attach['content_id'] = attachment.get('content-id' , None)
            attach['charset'] = attachment.get('charset' , None)
            attach['content_transfer_encoding'] = attachment.get('content_transfer_encoding' , None)
            liham.attachments.append(attach)

        # set values
        liham.date = mail.date
        liham.sender = mail._from
        liham.headers = mail.headers
        liham.message_id = mail.message_id
        liham.received = mail.received
        liham.subject = mail.subject
        liham.mail_text = mail.text_plain
        liham.mail_html = mail.text_html
        liham.recipients = mail.to
        liham.timezone = mail.timezone
        return liham

    pass # End Liham Class

# ------------------------------------------------------------------------------
# Handler
# ------------------------------------------------------------------------------
def lambda_handler(event,context):
    # ---------------------
    # Start Up Logging
    # ---------------------
    print('Starting Raw Mail Transport Process')
    print(json.dumps(event))
    aws_request_id = context.aws_request_id
    request_folder = '/tmp/liham/%s' % (aws_request_id)

    # ---------------------
    # Create Request Folder
    # ---------------------
    print('Creating Request Folder . . . %s' % request_folder)
    if not os.path.exists('/tmp/liham'):
        os.mkdir('/tmp/liham') # liham tmp
        os.mkdir(request_folder)

    # ---------------------
    # Process Event
    # ---------------------
    for record_event in event['Records']:
        process_record_event(record_event , request_folder)

    # ---------------------
    # Clean Up
    # ---------------------
    if FUN_CLEANUP == 'ALL' or FUN_CLEANUP ==  'LOCAL':
        print('Deleting Request Folder . . . %s' % request_folder)
        shutil.rmtree(request_folder,ignore_errors=True)



# ------------------------------------------------------------------------------
# Handler Functions
# ------------------------------------------------------------------------------
def process_record_event(record_event,request_folder):
    # ------------------------------------------
    # Declaration
    # ------------------------------------------
    s3_event = record_event['s3']
    object_key = s3_event['object']['key']
    mail_item = object_key.split('/')[1] # remove inbox/ prefix
    local_file_name = '%s/%s' % (request_folder,mail_item)
    local_json_file_name = '%s.json' % (local_file_name)

    # ------------------------------------------
    # Download Object
    # ------------------------------------------
    print('Downloading E-Mail for processing . . . %s @ %s' % (object_key,FUN_BUCKET))
    #S3_CLIENT.download_file(FUN_BUCKET, object_key, local_file_name)
    S3_CLIENT.download_file(FUN_BUCKET, object_key, local_file_name)


    # ------------------------------------------
    # Parse Raw E-mail
    # ------------------------------------------
    liham = Liham.create_from_file(local_file_name)
    if len(liham.recipients) == 0:
        shutil.rmtree(request_folder,ignore_errors=True)
        raise ValueError('No recipients are listed')

    # ------------------------------------------
    # Create JSON File
    # ------------------------------------------
    print('Creating JSON . . .')
    with open(local_json_file_name, 'w') as f:
        json.dump(liham.toJson() , f , indent = 4)

    # ------------------------------------------
    # Detect Virus/Spam
    # ------------------------------------------
    print('Checking Spam/Virus verdict . . .')
    transfer_to_folder = 'inbox'
    if liham.isVirus():
        transfer_to_folder = 'virus'
    elif liham.isSpam():
        transfer_to_folder = 'spam'

    # ------------------------------------------
    # Process Mail Name
    # ------------------------------------------
    print('Generating mail name . . .')
    remote_file_name = generate_remote_name(str(liham.date) , str(liham.sender[0][1]) )

    # ------------------------------------------
    # upload mail to user folder
    # ------------------------------------------
    print('Uploading JSON Mail to user inbox . . .')
    upload_to_user_folder(liham.recipients , local_json_file_name , transfer_to_folder , remote_file_name)

    # ------------------------------------------
    # upload attachment to user folder
    # ------------------------------------------
    for atch in liham.attachments:
        # process attachments here
        pass

    # ------------------------------------------
    # Delete Raw Mail After Process
    # ------------------------------------------
    if FUN_CLEANUP == 'ALL' or FUN_CLEANUP ==  'REMOTE':
        S3_CLIENT.delete_object(Bucket = FUN_BUCKET , Key = object_key)


def generate_remote_name(date_string , sender):
    dateLabel = date_string.replace(' ','/').replace(':','/').replace('-','/')
    senderLabel = sender.replace('@','-at-')
    return '%s/%s' % (dateLabel , senderLabel)

def upload_to_user_folder(recipients, local_file , remote_folder ,remote_name):
    for recipient in recipients:
        domain = recipient[1].split('@')[1]
        print('Receiving E-Mail for: %s / %s' % (recipient[1] , domain))
        if domain == FUN_DOMAIN:
            domainAddress = str(recipient[1].split('@')[0]).lower()
            filename = 'store/%s/%s/%s/%s.json' % (FUN_DOMAIN , ('%s@%s' % (domainAddress , FUN_DOMAIN)) , remote_folder ,remote_name)
            print('Uploading file . . . %s @ %s' % (filename , FUN_BUCKET))
            S3_CLIENT.upload_file(local_file, FUN_BUCKET, filename, ExtraArgs={'ServerSideEncryption': 'AES256'})

def upload_attachments_to_user_folder():
    pass




# ------------------------------------------------------------------------------
# Tester
# ------------------------------------------------------------------------------


# class LambdaContext(object):
#     function_name = 'name'
#     function_version = 'version'
#     invoked_function_arn = 'arn'
#     memory_limit_in_mb = '128'
#     aws_request_id = '8a1c7914-301d-4b7a-96d6-153970ed0e46'
#     log_group_name = 'log_group'
#     log_stream_name = 'log_stream'
#     def get_remaining_time_in_millis(self):
#         return 1000
# TEST_EVENT = {
#     "Records": [
#         {
#             "eventVersion": "2.1",
#             "eventSource": "aws:s3",
#             "awsRegion": "ap-southeast-1",
#             "eventTime": "2019-06-17T00:37:27.207Z",
#             "eventName": "ObjectCreated:Put",
#             "userIdentity": {
#                 "principalId": "AWS:AIDAIE26RTG3F45XIHQFI"
#             },
#             "requestParameters": {
#                 "sourceIPAddress": "72.21.217.31"
#             },
#             "responseElements": {
#                 "x-amz-request-id": "E800B8F50914C171",
#                 "x-amz-id-2": "SI/DiqfhM+j/XrSzawvQXA/pmguhLHDBKpg1qXcGL31WHSD8LOVfYdopoHBvAfgy1g2XYjNmmHc="
#             },
#             "s3": {
#                 "s3SchemaVersion": "1.0",
#                 "configurationId": "db578f33-aa81-4e47-bfa7-8ae1fe4870d8",
#                 "bucket": {
#                     "name": "liham-storage-xatecfnfjf",
#                     "ownerIdentity": {
#                         "principalId": "A2PK7VYC6TDLOW"
#                     },
#                     "arn": "arn:aws:s3:::postman.codewizardsph.com"
#                 },
#                 "object": {
#                     "key": "inbox/t3qf1d2vc9lt653m98i7is6rgdh3366qsbu6okg1",
#                     "size": 4052,
#                     "eTag": "505b94cea912eaed26ab07222290a4f9",
#                     "sequencer": "005D06E0C6E9F9F728"
#                 }
#             }
#         }
#     ]
# }
#
# lambda_handler(TEST_EVENT , LambdaContext())
