# Mortgage Document Classification

Mortgage Document Classification is a specialized system designed to categorize US Mortgage documents using AWS Comprehend Classifier. With the capability to train 25 distinct categories, this tool efficiently organizes mortgage documents into relevant classes.

## Data Collection

- Gather PDF files of US Mortgage documents.
- Identify multipage PDF files and split them accordingly, naming each page with its corresponding page number.
- Upload the PDF files to an AWS S3 Bucket.

## Training Data Preparation

- Extract text from PDF files and save them into a CSV file, with the first column representing the filename and the second column containing the extracted text.
- Merge CSV rows based on filename to consolidate split files into a single merged file.
- Create a TXT file containing categories and label the training data accordingly.
- Save the TXT file and final CSV file into a tar zip file.
- Upload the tar zip file to an AWS S3 bucket.

## Build and Train Classifier

- Unzip or extract the tar zip file.
- Check the total items in the CSV file per class and specify the number as MAXITEMPERCLASS.
- Utilize the training data to construct the AWS Comprehend Classifier.
- Create a job to train the AWS Comprehend Classifier.

## Prediction on Test Dataset

- Collect PDF files of US Mortgage documents for testing.
- Split multipage PDF files and upload them to an AWS S3 Bucket.
- Extract text from the PDF files and save them into a CSV file.
- Save the test dataset as a CSV file with only one column of extracted text.
- Upload it to the S3 Bucket.
- Create an analysis job to generate predictions.
- Predictions will be generated as JSON files.
- Perform post-processing on the JSON files to convert them into CSV files, providing the final output with categories and confidence scores.

## Instructions to Run Python Files

1. Execute `train_data.py` file.
2. Run `upload_train.py` file.
3. Execute `train_classifier.py` file.
4. Run `test.py` file for prediction.
