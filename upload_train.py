#import required python packages
import boto3
import tarfile
from IPython.display import JSON
from botocore.exceptions import ClientError
import pandas as pd
import time
from datetime import datetime, timezone
import json
import seaborn as sn
import matplotlib.pyplot as plt

#Upload zipped training data set to AWS S3 bucket
def upload_data(tarfile, bucket_name, filename):
    s3 = boto3.client('s3')
    with open(tarfile, "rb") as f:
            s3.upload_fileobj(f,bucket_name, tarfile)
            print("uploaded")

#Unzipped or extract training dataset on AWS
def extract_train_data(dataset_bucket_name, dataset_object_name):
    # dataset_bucket_name = 'mytextdemo-a2i'
    # dataset_object_name = 'prod10-train.tar.gz'
    s3 = boto3.client('s3')
    with open(dataset_object_name, 'wb') as f:
        s3.download_fileobj(dataset_bucket_name, dataset_object_name, f)
        
    tar = tarfile.open(dataset_object_name)
    tar.extractall()
    tar.close()
    print("extracted")

#check the total classes in training dataset
def dataset_item(src_train_file, MAXITEMPERCLASS):
        # src_train_file='prod10-train/train_dataset.csv'
        # src_test_file='AWScomp/test_data.csv'
        with open(src_train_file) as myfile:
            print(myfile)
            head = [next(myfile) for x in range(5)]
        JSON(head)
        trainFrame = pd.read_csv(src_train_file, header=None)
        print('Number of documents: {}'.format(len(trainFrame.index)))

        # Count unique values 
        print(trainFrame[0].value_counts())
        # MAXITEMPERCLASS=100
        # Keeping MAXITEMPERCLASS for each class
        for i in range(1, 10):
            num = len(trainFrame[trainFrame[0] == i])
            dropnum = num - MAXITEMPERCLASS
            indextodrop = trainFrame[trainFrame[0] == i].sample(n=dropnum).index
            trainFrame.drop(indextodrop, inplace=True)

        print('Number of documents: {}'.format(len(trainFrame.index)))
        # Count unique values 
        print(trainFrame[0].value_counts())

#Class mapping
def class_mapping(src_train_file, mapping, comprehend_train_file, bucket_name):
    trainFrame = pd.read_csv(src_train_file, header=None)
    # trainFrame[0] = trainFrame[0].apply(mapping.get)
    # print(trainFrame.head(n=5))
    trainFrame['document'] = trainFrame[trainFrame.columns[1:]].apply(lambda x: ' \\n '.join(x.dropna().astype(str)),axis=1)
    trainFrame.drop([1], axis=1, inplace=True)
    trainFrame['document'] = trainFrame['document'].str.replace('<br />', '', regex=False)
    trainFrame['document'] = trainFrame['document'].str.replace('\n', ' ', regex=False)
    print(trainFrame.head(n=5))
    # comprehend_train_file='train-data.csv' 
    trainFrame.to_csv(path_or_buf=comprehend_train_file,header=False,index=False,encoding='utf-8')
    s3 = boto3.client('s3')
    # bucket_name = "comprehend-experiment-344021507737"
    train_object_name = 'train/' + comprehend_train_file
    response = s3.upload_file(comprehend_train_file, bucket_name, train_object_name)
    train_object_name_s3uri = 's3://{0}/{1}'.format(bucket_name, train_object_name)
    print('File uploaded to s3, uri: ' + train_object_name_s3uri)

#Build document classifier on AWS Comprehend
def build_classifier(role_arn, Policy_ARN, Bucket_ARN, document_classifier_name, comprehend_train_file):
    # role_arn = "arn:aws:iam::344021507737:role/ComprehendExperimentBucketAccessRole"
    # Policy_ARN: "arn:aws:iam::344021507737:policy/ComprehendExperimentDataAccessRolePolicy"
    # Bucket_ARN: "arn:aws:s3:::comprehend-experiment-344021507737"

    client = boto3.client('comprehend')
    region = boto3.session.Session().region_name
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    bucket_name = "comprehend-experiment-344021507737"
    train_object_name = 'train/' + comprehend_train_file
    train_object_name_s3uri = 's3://{0}/{1}'.format(bucket_name, train_object_name)
    train_output_s3uri = 's3://{0}/train/output/'.format(bucket_name)
    # document_classifier_name = 'adr-clssifier-prod10'
    document_classifier_arn = ''
    response = None

    try:
        response = client.create_document_classifier(
            DocumentClassifierName=document_classifier_name,
            DataAccessRoleArn=role_arn,
            InputDataConfig={
                'DataFormat': 'COMPREHEND_CSV',
                'S3Uri': train_object_name_s3uri
            },
            OutputDataConfig={
                'S3Uri': train_output_s3uri
            },
            LanguageCode='en'
        )
        document_classifier_arn = response['DocumentClassifierArn']
    except ClientError as error:
        if error.response['Error']['Code'] == 'ResourceInUseException':
            print('A classifier with the name "{0}" already exists. Hence not creating it.'.format(document_classifier_name))
            document_classifier_arn = 'arn:aws:comprehend:{0}:{1}:document-classifier/{2}'.format(region, account_id, document_classifier_name)
        
    print('Document Classifier ARN: ' + document_classifier_arn)

#Train AWS comprehend classifier
def train_classifier(document_classifier_arn):
    client = boto3.client('comprehend')
    response = None
    repeat = True
    status = ''
    submit_datetime = None
    end_datetime = None
    output_data_config_s3uri = ''

    while True:
        response = client.describe_document_classifier(
            DocumentClassifierArn=document_classifier_arn
        )
        status = response['DocumentClassifierProperties']['Status']
        submit_datetime = response['DocumentClassifierProperties']['SubmitTime']
            
        if status in ['SUBMITTED', 'TRAINING', 'DELETING', 'STOP_REQUESTED']: # status is going to change
            end_datetime = datetime.now(timezone.utc)
            if repeat:
                print('.', end = '')
                time.sleep(20)
            else:
                break
        else:
            end_datetime = response['DocumentClassifierProperties']['EndTime']
            break
            
    print('Job status: ' + status)
    print('Elasped time: {}'.format(end_datetime - submit_datetime))

    if status == 'TRAINED':
        output_data_config_s3uri = response['DocumentClassifierProperties']['OutputDataConfig']['S3Uri']
        accuracy = response['DocumentClassifierProperties']['ClassifierMetadata']['EvaluationMetrics']['Accuracy']
        print('Classifier Accuracy: {0:.{1}f}'.format(accuracy, 2))
        print('Output Data Config: {}'.format(output_data_config_s3uri))
		
#Plot confusion matrix to check postive negative and negative positive values
def ConfusionMatrix(confusion_matrix_file,figsize):
    # confusion_matrix_file = r'C:\Users\kkhairnar\comprehend-testing\prod10-train\output\confusion_matrix.json'
    data = None
    with open (confusion_matrix_file) as f:
        data = json.load(f)
    confusion_matrix = data['confusion_matrix']
    # df_cm = pd.DataFrame(confusion_matrix, index = [i for i in "049"],columns = [i for i in "049"])
    df_cm = pd.DataFrame(confusion_matrix)
    # plt.figure(figsize = (10, 10))
    plt.figure(figsize)
    sn.heatmap(df_cm, annot=True, fmt='d', cmap="YlGnBu")
    plt.title('heatmap confusion matrix')
    plt.show()

    print('Legend:')
    for i in range(len(data['labels'])):
        print('• {0}: {1}'.format(i, data['labels'][i]))
