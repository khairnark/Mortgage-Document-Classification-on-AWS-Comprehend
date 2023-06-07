import boto3
from trp import Document
import pandas as pd
import json
import csv
import pandas as pd
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
stop_words = set(stopwords.words('english'))
import os
from PyPDF2 import PdfFileWriter, PdfFileReader
from botocore.exceptions import NoCredentialsError

def split_pdf(pdf_path, output_path):
    # pdf_path = r'C:\Users\kkhairnar\comprehend-testing\New folder'
    # output_path = r'C:\Users\kkhairnar\comprehend-testing\new'
    for root, dirs, files in os.walk(pdf_path):
        for filename in files:
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(root, filename)
                inputpdf = PdfFileReader(open(pdf_path, "rb"))
                for i in range(inputpdf.numPages):
                    output = PdfFileWriter()
                    output.addPage(inputpdf.getPage(i))                    
                    output_pdf = output_path + '\\' + pdf_path.split('\\')[-1].split('.')[0] + '_' + str(i + 1) + '.pdf'                   
                    # print(output_pdf)
                    with open(output_pdf, "wb") as outputStream:
                        output.write(outputStream)
                        print('finished writing : ', output_pdf)
                    outputStream.close()

def upload_pdf_to_s3(pdf_folder, bucket_name):

    def upload_to_aws(local_file, bucket, s3_file):
        s3 = boto3.client('s3')
        try:
            s3.upload_file(local_file, bucket, s3_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

    for path, subdirs, files in os.walk(pdf_folder):
        for file in files:
            # pdf_folder = "split pdf file/"
            # bucket_name = 'vstest-py'
            image_path = pdf_folder + file
            print(image_path)
            uploaded = upload_to_aws(image_path, bucket_name,(file))  

    
def adr(s3BucketName, csv_name):
    # s3BucketName = "textract-a2i19"
    s3 = boto3.resource('s3')
    textractmodule = boto3.client('textract')
    my_bucket = s3.Bucket(s3BucketName)
    for s3_file in my_bucket.objects.all():
        response = textractmodule.detect_document_text(Document={'S3Object': {'Bucket': s3BucketName,'Name': s3_file.key}})
        text = ""
        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                textext = '\033[94m' + item["Text"] + '\033[0m'
                text = text + " " + item["Text"]
                text1 = text.lower()
                digitspattern = r'[0-9]'   
                string = re.sub(digitspattern, ' ', text1)    
                regex = "^0+(?!$)"    
                number = re.sub('[\W\_]',' ',string)    
                res1 = re.sub(r'(?:^| )\w(?:$| )', ' ', number).strip()    
                res2 = re.sub(' +', ' ', res1)    
                res3 = ' '.join([''.join(i) for i in res2.split() if i.lower() not in stop_words])
                res4 = res3.replace("/n", "")
    # #           Deduplication           
    #             words = res4.split(" ")
    #             my_string = (list(set(words)))
    #             my_string1 = ' '.join(my_string)           
        s3_client = boto3.client('s3')
        filename1 = s3_file.key
        print(filename1)
        # csv_name = 'final_out_time.csv'
        fields = ['file',  'text']
        rows = [filename1, res4]
        try:
            with open(csv_name, 'a' , newline = '', encoding='utf-8', errors='ignore') as csvfile:        
                writer_object = csv.writer(csvfile)
                # read_mode = io.open('ocrtest7.csv', 'r')
                read_mode = open(csv_name, 'r', encoding='utf-8', errors='ignore')
                if read_mode.readlines() == []:
                    writer_object.writerow(fields)
                writer_object.writerow(rows)
            csvfile.close()
        except:
            print("Error detected:", filename1)
            pass


def file_merge(csv_path, output_csv_path):
    # csv_path = r'C:\Users\kkhairnar\comprehend-testing\adr-prod10.csv'
    df = pd.read_csv(csv_path, encoding= 'unicode_escape')
    for i in range(len(df['file'])):
        temp = df['file'][i].split('_')[0] + '.pdf'
        df['file'][i] = temp
    df2 = df.groupby('file')['text'].apply(list).reset_index()
    for i in range(len(df2['file'])):
        final_filename = df2['file'][i].split('.')[0] + '.pdf'
        final_text = ' '.join(str(item) for item in df2['text'][i])
        df2['file'][i] = final_filename
        df2['text'][i] = final_text

    df2.columns = ['doc_name', 'doc_data']
    for i in range(len(df2['doc_data'])):
        res = re.sub(r'[^\w\s]', '', df2['doc_data'][i]) 
        digitspattern = r'[0-9]'   
        string = re.sub(digitspattern, ' ', res)    
        regex = "^0+(?!$)"    
        number = re.sub('[\W\_]',' ',string)    
        res1 = re.sub(r'(?:^| )\w(?:$| )', ' ', number).strip()    
        res2 = re.sub(' +', ' ', res1)    
        res3 = ' '.join([''.join(i) for i in res2.split() if i.lower() not in stop_words])
        df2['doc_data'][i] = res3
    # output_csv_path = r'C:\Users\kkhairnar\comprehend-testing\adr1-prod111110.csv'
    df2.to_csv(output_csv_path,index = False)
    print("result generated")
