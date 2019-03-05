import os
import sys
import boto3
from botocore.client import Config
import botocore

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_FOLDER = os.path.join(APP_ROOT, 'tmp', 'archive')

def create_subfolders(directory):
    os.chdir(ARCHIVE_FOLDER)
    os.mkdir(directory)
    os.mkdir(os.path.join(directory, 'M'))
    os.mkdir(os.path.join(directory, 'P'))
    os.chdir(APP_ROOT)

def transfer_from_s3(archive_name, directory, sortop):
    os.chdir(ARCHIVE_FOLDER)

    S3_BUCKET = os.environ.get('S3_BUCKET')
    s3 = boto3.resource('s3')
    local_dest = os.path.join(directory, sortop, archive_name)

    try:
        s3.Bucket(S3_BUCKET).download_file(archive_name, local_dest)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print(archive_name + " does not exist on S3.")
        else:
            raise

    os.chdir(APP_ROOT)

if __name__ == "__main__":
    try:
        os.mkdir(ARCHIVE_FOLDER)
    except:
        print('archive already exists')
        
    directory = 'IEM-Katowice-2019'
    create_subfolders('IEM-Katowice-2019')
    transfer_from_s3('IEM-Katowice-2019-SBP.zip', directory, 'P')
    transfer_from_s3('IEM-Katowice-2019-SBM.zip', directory, 'M')