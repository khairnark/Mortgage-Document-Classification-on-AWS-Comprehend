import sys
# !{sys.executable} -m pip install pandas==1.1.3

import boto3
import json
import logging
import pandas as pd
import random
import tarfile
from IPython.display import JSON
from botocore.exceptions import ClientError




# If a region is not specified, the bucket is created in the S3 default region (us-east-1).
region = boto3.session.Session().region_name
account_id = boto3.client('sts').get_caller_identity().get('Account')
bucket_name = 'comprehend-experiment-{}'.format(account_id)

try:
    if region == 'us-east-1':
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3 = boto3.client('s3', region_name=region)
        location = {'LocationConstraint': region}
        s3.create_bucket(Bucket=bucket_name,
                         CreateBucketConfiguration=location)
except ClientError as e:
    print(e)

bucket_arn = 'arn:aws:s3:::{}'.format(bucket_name)



iam = boto3.client('iam')

role_name = 'ComprehendExperimentBucketAccessRole'
role_arn = ''
policy_name = 'ComprehendExperimentDataAccessRolePolicy'
policy_arn = ''

# Principal — defines the entity which can assume this role
trust_relationship_policy_comprehend = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "comprehend.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}

# This policy grant access to the bucket created previously
policy_s3_comprehend = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": [
                "{}/*".format(bucket_arn)
            ],
            "Effect": "Allow"
        },
        {
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "{}".format(bucket_arn)
            ],
            "Effect": "Allow"
        }
    ]
}

# Create the role
try:
    create_role_res = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_relationship_policy_comprehend),
        Description='Comprehend Experiment Role',
    )
    role_arn = create_role_res['Role']['Arn']
except ClientError as error:
    if error.response['Error']['Code'] == 'EntityAlreadyExists':
        role_arn = 'arn:aws:iam::{0}:role/{1}'.format(account_id, role_name)
    else:
        print('Unexpected error occurred... Role could not be created')
    
# Create the policy
try:
    policy_res = iam.create_policy(
        PolicyName=policy_name,
        PolicyDocument=json.dumps(policy_s3_comprehend)
    )
    policy_arn = policy_res['Policy']['Arn']
except ClientError as error:
    if error.response['Error']['Code'] == 'EntityAlreadyExists':
        policy_arn = 'arn:aws:iam::{0}:policy/{1}'.format(account_id, policy_name)
    else:
        print('Unexpected error occurred... hence cleaning up')
        iam.delete_role(
            RoleName= role_name
        )

# Attach the policy to the role
try:
    policy_attach_res = iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )
except ClientError as error:
    print('Unexpected error occurred... hence cleaning up')
    iam.delete_role(
        RoleName=role_name
    )

print('Role ARN: "{}"'.format(role_arn))
print('Policy ARN: "{}"'.format(policy_arn))
print('Bucket ARN: "{}"'.format(bucket_arn))

bucket_name = 'comprehend-experiment-344021507737'

dataset_bucket_name = 'textract-a2i19'
dataset_object_name = '114newStrain.tar.gz'

s3 = boto3.client('s3')
with open(dataset_object_name, 'wb') as f:
    s3.download_fileobj(dataset_bucket_name, dataset_object_name, f)
    
tar = tarfile.open(dataset_object_name)
tar.extractall()
tar.close()

src_train_file='114newStrain/training114.csv'

with open(src_train_file) as myfile:
    head = [next(myfile) for x in range(5)]

JSON(head)
# Loading the train set
trainFrame = pd.read_csv(src_train_file, header=None)
print('Number of documents: {}'.format(len(trainFrame.index)))

# Count unique values 
trainFrame[0].value_counts()
MAXITEMPERCLASS=100
# Keeping MAXITEMPERCLASS for each class
for i in range(1, 20):
    num = len(trainFrame[trainFrame[0] == i])
    dropnum = num - MAXITEMPERCLASS
    indextodrop = trainFrame[trainFrame[0] == i].sample(n=dropnum).index
    trainFrame.drop(indextodrop, inplace=True)

print('Number of documents: {}'.format(len(trainFrame.index)))

# Count unique values 
trainFrame[0].value_counts()
