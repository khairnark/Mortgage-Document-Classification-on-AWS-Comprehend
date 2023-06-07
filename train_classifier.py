import train_data
import upload_train
# '''========================Preprocessing flow of document upload, ocr, merging before labelling=========================='''
'''----------------1.Pdf spliting------------------'''
# train_data.split_pdf(r"C:\Users\kkhairnar\comprehend-testing\New folder", r"C:\Users\kkhairnar\comprehend-testing\new")
# pdf_path = input("Enter pdf folder path:")
# output_path = input("Enter destination folder path:")
# train_data.split_pdf(pdf_path, output_path)

'''----------------2.Upload Pdf file to S3------------------'''
# train_data.upload_pdf_to_s3("split pdf file/", 'vstest-py')
pdf_folder = input("Enter pdf folder path end with slash(/): ")
bucket = input("Enter bucket name: ")
train_data.upload_pdf_to_s3(pdf_folder, bucket)

'''----------------3.OCR using aws textract API------------------'''
# train_data.adr("vstest-py", "csvfile.csv")
# adr = input("Enter Data Bucket Name to extract: ")
# adr1 = input("Enter output file name with extension(.csv): ")
# train_data.adr(adr, adr1)
# '''----------------4.Merging row of spliting pdf file in csv------------------'''
# # train_data.file_merge(r'C:\Users\kkhairnar\pyfunc\csvfile.csv', r'C:\Users\kkhairnar\pyfunc\csvfile1.csv')
# path1 = input("enter path of output file: ")
# path2 = input("enter path to store merged file with name: ")
# train_data.file_merge(path1, path2)

# # '''===========================Building and training classifier and performace visualization ==========================='''

# '''----------------1.Upload zipped training dataset to S3------------------'''
# # upload_train.upload_data('prod10-train.tar.gz', 'vstest-py', 'prod10-train.tar.gz')
# upload_data1 = input("Enter Zip file path: ")
# upload_data2 = input("Enter Bucket name to store train dataset: ")
# upload_data3 = input("Enter new name of Zip file with extension(.tar.gz): ")
# upload_train.upload_data(upload_data1, upload_data2, upload_data3)

# '''----------------2. zipped Traning dataset extraction------------------'''
# # upload_train.extract_train_data('vstest-py', 'prod10-train.tar.gz')
# bucket_name = input("Enter bucket name: ")
# zip_file = input("Enter uploaded Zip file name: ")
# upload_train.extract_train_data(bucket_name, zip_file)

# '''----------------3.Counting document file with respective classes------------------'''
# # upload_train.dataset_item("prod10-train/train_dataset.csv", 100)
# src_train_file = input("Enter extracted train data path: ")
# MAXITEMPERCLASS = input("Enter Maximum item count per class: ")
# upload_train.dataset_item(src_train_file, MAXITEMPERCLASS)

# '''----------------4.Mapping of classes------------------'''
# # upload_train.class_mapping("prod10-train/train_dataset.csv",
# # "{1:'Borrower_Certification_And_Authorization',2:'Borrower_Consent_To_Use_Of_Tax_Return_Information',3:'Equal_Credit_Opportunity_Act_Notice',4:'First_Payment_Letter',5:'Flood_Hazard_Notice',6:'IRS_4506',7:'Patriot_Act_Disclosure',8:'UCDP_Submission_Summary_Report',9:'Written_List_Of_Service_Providers',10:'Loan_Closing_Advisor_Feedback_Certificate'}",
# # "train11111-data.csv", "comprehend-experiment-344021507737")
# src_train_file = input("Enter train file:")
# mapping = input("class mapping: ")
# comprehend_train_file = input("enter filename for comprehend input: ")
# bucket_name = input("Enter bucket name: ")
# upload_train.class_mapping(src_train_file, mapping, comprehend_train_file, bucket_name)

# '''----------------5.Building aws comprehend classifier using API------------------'''
# # upload_train.build_classifier("arn:aws:iam::344021507737:role/ComprehendExperimentBucketAccessRole",
# # "arn:aws:iam::344021507737:policy/ComprehendExperimentDataAccessRolePolicy",
# # "arn:aws:s3:::comprehend-experiment-344021507737",
# # "adr-clssifier-prod12",
# # "train11111-data.csv")
# role_arn = input("Enter role arn:")
# Policy_ARN = input("policy arn:")
# Bucket_ARN = input("Enter bucket arn:")
# document_classifier_name = input("Enter name of classifier:")
# comprehend_train_file = input("Enter csv file name with extension:")
# upload_train.build_classifier(role_arn, Policy_ARN, Bucket_ARN, document_classifier_name, comprehend_train_file)

# '''----------------6.Train classifier------------------'''
# # upload_train.train_classifier("arn:aws:comprehend:us-east-1:344021507737:document-classifier/adr-clssifier-prod12")
# document_classifier_arn = input("Enter arn of classifier builded:")
# upload_train.train_classifier(document_classifier_arn)

# '''----------------7.Plot confusion matrix------------------'''
# # upload_train.ConfusionMatrix(r'C:\Users\kkhairnar\comprehend-testing\prod10-train\output\confusion_matrix.json', '(10,10)')
# cm_jsonpath = input("Enter confusion matrix json file path: ")
# figsize = input("Enter size of Confusion Matrix in the format (int,int): ")
# upload_train.ConfusionMatrix(cm_jsonpath, figsize)
