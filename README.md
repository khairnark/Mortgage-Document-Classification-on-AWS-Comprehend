# Mortgage-Document-Classification-on-AWS-Comprehend
Mortgage Document Classification is custom classification to organize US Mortgage documents into categories (classes) using AWS.
We can trained 25 categories with comprehend classifier.

Data collection:
1. Collect Pdf file of US Mortgage documents.
2. Identify the multipage pdf file or single page.
3. Split Multipage pdf file with same file name with page no.
(E.G.,Multipage pdf file name: "Loan Application. pdf" convert into first page: "Loan Application_1.pdf", "Loan Application_2.pdf",.,.,., "Loan Application_n.pdf").
4. Upload pdf file to AWS S3 Bucket.

Training Data Prepartion:
1. Extract text from pdf file and save to csv file. first column will be name filename and second column will be extracted text.
2. Merge csv row as per filename to merge splited file into merged file.
3. Create txt file with categories
4. label the train data as per categories in txt file by replacing category into specific number.
5. Save txt file and final csv file into tar zip file.
6. Upload tar zip file on AWS S3 bucket.
