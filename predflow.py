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
import time
from datetime import datetime, timezone

   # Preparation of the validation set
def testDataset(src_test_file, MAXITEM):
    src_test_file = r'C:\Users\kkhairnar\comprehend-testing\testdataset.csv'
    MAXITEM = 3
    validationFrame = pd.read_csv(src_test_file, header=None)
    # Here, we are limiting to 100 documents to test in order to reduce costs of this demo.
    # If you want to test Amazon Comprehend on the full dataset, set MAXITEM to None
    # MAXITEM=None
    # MAXITEM=1399
    # Keeping MAXITEM
    if MAXITEM:
        num = len(validationFrame)
        dropnum = num - MAXITEM
        indextodrop = validationFrame.sample(n=dropnum).index
        validationFrame.drop(indextodrop, inplace=True)        
    validationFrame.head(n=3)
    # Joining "Question title", "question content", and "best answer".
    validationFrame['document'] = validationFrame[validationFrame.columns[1:]].apply(
        lambda x: ' \\n '.join(x.dropna().astype(str)),
        axis=1
    )
    validationFrame.head(n=3)
    validationFrame['document'] = validationFrame['document'].str.replace('<br />', '\n', regex=False)
    validationFrame['document'] = validationFrame['document'].str.replace('\n', '', regex=False)
    validationFrame.head(n=5)

def finalTestDataset(comprehend_test_file):
    comprehend_test_file='testdataset.csv'
    validationFrame.to_csv(path_or_buf=comprehend_test_file,
                        header=False,
                        index=False,
                        encoding='utf-8')

def uploadTestDataset(src_test_file, comprehend_test_file, bucket_name):
    src_test_file = r'C:\Users\kkhairnar\comprehend-testing\testdataset.csv'
    comprehend_test_file = 'test11.csv'
    validationFrame.to_csv(path_or_buf=comprehend_test_file,
                        header=False,
                        index=False,
                        encoding='utf-8')
    s3 = boto3.client('s3')
    bucket_name = 'comprehend-experiment-344021507737'
    test_object_name = 'test/' + comprehend_test_file
    response = s3.upload_file(comprehend_test_file, bucket_name, test_object_name)
    test_object_name_s3uri = 's3://{0}/{1}'.format(bucket_name, test_object_name)
    print('File uploaded to s3, uri: ' + test_object_name_s3uri)

def analysisJob(document_classifier_arn, role_arn):    
    document_classifier_arn = "arn:aws:comprehend:us-east-1:344021507737:document-classifier/adr20new-classifier"
    role_arn = "arn:aws:iam::344021507737:role/ComprehendExperimentBucketAccessRole"
    client = boto3.client('comprehend')
    region = boto3.session.Session().region_name
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    test_output_s3uri = 's3://{0}/test/output/'.format(bucket_name)
    response = None
    job_id = ''
    response = client.start_document_classification_job(
        JobName= '%x' % random.getrandbits(32),
        DocumentClassifierArn=document_classifier_arn,
        DataAccessRoleArn=role_arn,
        InputDataConfig={
            'InputFormat': 'ONE_DOC_PER_LINE',
            'S3Uri': test_object_name_s3uri
        },
        OutputDataConfig={
            'S3Uri': test_output_s3uri
        },
    )
    job_id = response['JobId']
        
    print('Job Id: ' + job_id)

def prediction(job_id):
    client = boto3.client('comprehend')
    response = None
    repeat = True
    status = ''
    submit_datetime = None
    end_datetime = None
    test_output_s3uri = ''
    while True:
        response = client.describe_document_classification_job(
            JobId=job_id
        )
        status = response['DocumentClassificationJobProperties']['JobStatus']
        submit_datetime = response['DocumentClassificationJobProperties']['SubmitTime']
            
        if status in ['SUBMITTED', 'IN_PROGRESS', 'STOP_REQUESTED']: # status is going to change
            end_datetime = datetime.now(timezone.utc)
            if repeat:
                print('.', end = '')
                time.sleep(20)
            else:
                break
        else:
            end_datetime = response['DocumentClassificationJobProperties']['EndTime']
            test_output_s3uri = response['DocumentClassificationJobProperties']['OutputDataConfig']['S3Uri']
            break
    print('Job status: ' + status)
    print('Elasped time: {}'.format(end_datetime - submit_datetime))
    print('Output S3 Uri: {}'.format(test_output_s3uri))

def predFinal(csvPath, predJsonPath, finalPredPath):
    data = []
    doc_name = []
    score = []
    file_name = []
    csvPath = r'C:\Users\kkhairnar\comprehend-testing\demoMerged20jan.csv' 
    predJsonPath = r'C:\Users\kkhairnar\comprehend-testing\predictions.jsonl'   
    finalPredPath = r'C:\Users\kkhairnar\comprehend-testing\prediction.csv'
    # df = pd.read_csv(r'C:\Users\kkhairnar\comprehend-testing\ocrtest20zzz.csv')
    df = pd.read_csv(csvPath)    
    # with open(r'C:\Users\kkhairnar\comprehend-testing\Newflow\predictions.jsonl','r') as f:
    with open(predJsonPath,'r') as f:
        json_list = list(f)
    for i in range(len(df)):
        file_name.append(df['filename'][i])
    for i in range(len(df)):
        data.append(df['data'][i])
    for json_str in json_list:
        result = json.loads(json_str)
        doc_name.append(result['Classes'][0]['Name'])
        score.append(result['Classes'][0]['Score'])
    df1 = pd.DataFrame({'filename':file_name,'data': data,'Class_Name': doc_name,'Confidence': score})
    # df1.to_csv(r'C:\Users\kkhairnar\comprehend-testing\Newflow\ocrtest20zzz_predictions.csv',index = False)
    df1.to_csv(finalPredPath,index = False)
    print("Prediction Generated!")


testDataset(src_test_file, MAXITEM)
finalTestDataset(comprehend_test_file)
uploadTestDataset(src_test_file, comprehend_test_file, bucket_name)
analysisJob(document_classifier_arn, role_arn)
prediction(job_id)
predFinal(csvPath, predJsonPath, finalPredPath)
