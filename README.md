# AWS Liham Serverless Mail Client
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


**Liham** is a Filipino word that means letters, or mails. it is a simple *Serverless Mail Client* that allows you to receive E-Mails with your custom domain using the Amazon Web Service (AWS) infrastructure, without maintaining any servers.


**Sample Use Case**
1. A User sent an e-mail to bot@domain.com, this e-mail contains an excel file that needs to be uploaded to the database using *Extract Transform Load*.
2. Liham can then received this e-mail by utilizing *AWS SES* this e-maill will then be processed from RAW format to JSON format.
3. Liham will then put the JSON formatted e-mail to the email folder of bot@domain.com.
4. Once the e-mail in the JSON format landed on the email folder of bot@domain.com a lambda function can then process it, triggered by the S3 Notification Configuration. The lambda function will then extract the Base64 Encoded Excel File from the JSON file.
5. After extracting the Lambda function can process it then upload its contents to the database and sent an automatic upload report back to the sender.


Melvin Perello, *AWS Certified Developer Associate*


You can verify my license [here](http://aws.amazon.com/verification), and use this validation number **P2N5X9W2G1V4QKSY**


> Before continuing, this project expects that you have basic knowledge with AWS Services and Cloudformation.


AWS Services:
- Simple Email Service (SES)
- Route 53
- Simple Storage Service (S3)
- Simple Queue Service (SQS)
- Lambda
- Identity and Access Management (IAM)


### DNS Configuration
In order to receive e-mails you need to configure your DNS for the domain. you need to register your domain with **AWS Simple Email Server**. Once your domain is registered with SES you need to verify.


If your domain is hosted with **AWS Route 53**, you just need to create a **Cloudformation Stack** using **aws-cfn-liham-dns-config.yaml** in the source code and fill up the following parameters:

- **Hosted Zone ID**: ID of the hosted zone for the domain in the Route 53.
- **Domain Name**: The Domain Name that you own and going to use.
- **SES Receiving Endpoint**: The endpoint of SES you are going to use, as of writing there are only 3 available regions for **AWS SES**. [Click Here For More Info](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/regions.html#region-endpoints)
- **DNS Record TTL**: This stack will register record set to your DNS, each records set will be having a time to live (TTL), please indicate the TTL in seconds.
- **Create Rule Set**: if you already have a rule set, select **skip**, by default this will **create** an e-mail rule set that will allow SES to follow rules on how it will handle e-mails coming from your registered domain.
- **Domain Verification Record Name** and **Domain Verification Record Name Value**, upon registering your domain with **AWS SES**, it will give you a verification entry to assure you own the domain you are using.
- **DKIM Record Name** and **DKIM Record Name Value**, you need to generate DKIM settings from **AWS SES** once these keys are generated you will receive 3 pairs of key value.


If your domain is hosted on a third-party you might need to read the documentation on how to configure these with your domain.


### Receiving E-Mails
Once your DNS is configured to receive e-mail for the domain you own. You need to create a **Cloudformation Stack** using **aws-cfn-liham-inc.yaml** in the source code and fill up the following parameters:


- **PLihamIncFunCodeBucket**: The bucket name where the ZIP file of the function was uploaded.
- **PLihamIncFunCodeKey**: The Key name of the ZIP file of the function uploaded to the bucket.
- **PFunDomain**: The Domain name that will receive emails.
- **PFunCleanup**: The clean up method for the function when processing e-mails.
    - **ALL** deletes the RAW e-mail from the S3 bucket and in the Function TMP folder.
    - **REMOTE** deletes the RAW e-mail from the S3 bucket only.
    - **LOCAL** deletes the RAW e-mail from the Function TMP folder only, and the original RAW e-mail retains in the S3 bucket.
    - **NONE** RAW e-mail will be retained in the S3 bucket, RAW e-mail downloaded to the Lambda TMP folder will also be retained, this can be a problem since TMP folder of a lambda function has a maximum size of 512MB. This can be helpful if you want to debug RAW e-mails.
- **PBucketId**: Liham generates the bucket name automatically, but this does not guarantee uniqueness, since AWS S3 Bucket Names needs to be unique, this parameter adds extra characters to the bucket name to assure uniqueness.
- **PEnvironment**: by default this template only contains 2 environment setup **dv** for development and **pr** for production. if you want to tinker with the template you may want to choose **dv** environment.
- **PClient**: This is a cost allocation tag, if you have no client just write your name or anything you want.
- **PAppName**: This is a cost allocation tag, by default only **liham** is the allowed value.
- **POwner**: This is a cost allocation tag, and also an identification tag on who owns and manages the staack.


**Default Addresses**


According to RFC 2142, the following addresses needs to be added. Please see this address for complete list and information. https://www.ietf.org/rfc/rfc2142.txt


**Your Addresses**


To add users to receive e-mails, you need to find the **LihamRuleUsers** Resource under the resource block.


```yaml
Rule:
    Actions:
        -   S3Action:
                BucketName: !Ref LihamStore
                ObjectKeyPrefix: !Sub "inbox/"
    Enabled: true
    Name: !Sub "rr.${PFunDomain}.pr.1"
    Recipients:
        # -- Users
        - !Sub "melvinperello@${PFunDomain}"

    ScanEnabled: true
    TlsPolicy: "Optional" # or "Require"
```


As indicated above there is a default user **melvinperello@codewizardsph.com**, that is mine as an example. you can add as much user you want. **codewizardsph.com** comes from the parameter I entered upon creating the stack.


What it does, when an e-mail is sent to the addresses indicated it will be uploaded to the S3 bucket in the **inbox/** folder, this is the RAW e-mail. **ScanEnabled: true** means that AWS SES will scan the e-mail for **SPAM** and **VIRUS**. **TlsPolicy: "Optional"** means that you can received e-mail encrypted or unecnrypted. If you only want to receive encrypted e-mails for security reasons, you may change this to **Require**.


**RAW E-Mail Processing**


Now we have reached the intersting part, going back we knew that all e-mails received by the registered addresses will go to **inbox/** folder. A notification configuration was setup with the S3 bucket in this stack, this configuration will then generate an event that will trigger a lambda function.


**Work Flow**


1. E-Mail Received by Domain
2. RAW E-Mail Stored in S3
3. S3 Generates Event
4. Event Triggers Lambda
5. Lambda Processes E-mail
6. Lambda uploads Processed E-Mail to user folder


The lambda function will read the RAW e-mail and will try to parse it and then converts it to a JSON readable file.


**JSON Mail Format**


```json
{
    "message_id": "",
    "isSpam": false,
    "isVirus": false,
    "headers": [],
    "received": [],
    "date": "",
    "timezone": "+0",
    "sender": [
        [
            "Kimi No Nawa",
            "kiminonawa@domain.jp"
        ]
    ],
    "recipients": [
        [
            "Whethering With You",
            "whetheringwithyou@domain.jp"
        ]
    ],
    "subject": "E-Mail Subject !!!!",
    "text": "Hi,\n Baka !!!",
    "html": "<html>Hi, <br> Baka !!!</html>",
    "attachments": []
}
```


After processing the e-mail to a JSON file, the Lambda function will then upload the JSON file to each user designated folder.


> The lambda function will upload the JSON file to every recipients folder, so this will have multiple copies depending on the number of recipients.


**Where will the lambda upload the JSON file ?**


```bash
s3://<bucket>/store/<domain.com>/<user@domain.com>/inbox/<yyyy>/<MM>/<dd>/<HH>/<mm>/<ss>/<sender>.json
```


- When **"isVirus": true** the JSON file will be uploaded to s3://<bucket>/store/<domain.com>/<user@domain.com>/**virus**/*
- When **"isSpam": true** the JSON file will be uploaded to s3://<bucket>/store/<domain.com>/<user@domain.com>/**spam**/*


### Post-Processing E-mails (The Best Part)
Now that the e-mails are processed and uploaded to the user folder, we can add some sugar and spice by adding again another notification configuration. For instance you can set an e-mail user that will receive e-mails from clients with an attached excel file. When the JSON file landed on the user folder a lambda function will then process again the JSON file and extract the base64 encoded excel file and process that excel file to upload the contents to the database and then replies automatically to the client with the result of the process. all these glitters running without servers all made using the Event Driven Architecture.



### Miscellaneous
You can also use liham to just simply receive e-mails and read them, you need to create a **Cloudformation Stack** using **aws-cfn-liham-users.yam** in the source code and fill up the following parameters:

- **PEnvironment**: by default this template only contains 2 environment setup **dv** for development and **pr** for production. if you want to tinker with the template you may want to choose **dv** environment.
- **PDomain**: Domain your users will be using.


After creating the stack will create users that will allow you to have credentials and read e-mails of the user from the user folder.


**Adding User Access Keys**

```yaml
LhmUsr01:
    Type: AWS::IAM::User
    Properties:
        Groups:
            - !Ref GrpLhmUsrRx
        Path: "/"
        Tags:
            -
                Key: "domain"
                Value: !Ref PDomain
            -
                Key: "application"
                Value: "liham"
            -
                Key: "env"
                Value: !Ref PEnvironment
        UserName: melvinperello@codewizardsph.com
```

You can add multiple user to have an access keys to access their mailbox. **It is important that the username that you will be going to assign is the same as their e-mail address.**


**Common Operations**


```sh
# Setting Up Variables (This is optional I just find it much easier)
export LIHAM_BUCKET="liham-store-codewizardsph.com-pr-zxcv"
export LIHAM_DOMAIN="codewizardsph.com"
export LIHAM_USER="melvinperello"

aws configure --profile liham

# view all mails in inbox
aws s3api list-objects-v2 --bucket $LIHAM_BUCKET \
--prefix "store/$LIHAM_DOMAIN/$LIHAM_USER@$LIHAM_DOMAIN/inbox/" \
--output json \
--profile liham

# view all mails in inbox for December 22, 2019
aws s3api list-objects-v2 --bucket $LIHAM_BUCKET \
--prefix "store/$LIHAM_DOMAIN/$LIHAM_USER@$LIHAM_DOMAIN/inbox/2019/12/22/" \
--output json \
--profile liham

# view all mails in inbox for a specific time
aws s3api list-objects-v2 --bucket $LIHAM_BUCKET \
--prefix "store/$LIHAM_DOMAIN/$LIHAM_USER@$LIHAM_DOMAIN/inbox/<yyyy>/<MM>/<dd>/<HH>/<mm>/<ss>/" \
--output json \
--profile liham

# view mail
aws s3api get-object --bucket $LIHAM_BUCKET \
--key "store/codewizardsph.com/melvinperello@codewizardsph.com/inbox/2019/12/22/11/11/03/someone-at-gmail.com.json" \
--profile liham \
mail.json

# delete mail
aws s3api delete-object --bucket $LIHAM_BUCKET \
--key "store/codewizardsph.com/melvinperello@codewizardsph.com/inbox/2019/12/22/07/35/55/someone-at-gmail.com.json" \
--profile liham
```


If you want to send e-mails using the created account above as you are also reading received e-mails, you can do so by adding more roles to the user and then updating the cloudformation. after adding the required roles you can then send the e-mail using the aws cli with SES.


Cheers,


Melvin
