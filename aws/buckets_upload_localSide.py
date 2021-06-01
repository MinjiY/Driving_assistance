import boto3
from datetime import datetime
from os import rename
import os
import pymysql

AWS_ACCESS_KEY=""
AWS_SECRET_KEY=""
BUCKET_NAME="yangjae-team04-s3"

def s3_connection():
    s3 = boto3.client('s3',aws_access_key_id= AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    return s3
 
# ex) 실행하는 파일 동일경로에 폴더 생성하고 동영상 저장함 =>폴더 생성하는 코드 
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

# 동영상 이름은 주행 시작으로 => 혹시 다른이름으로 저장했다면 rename
def fileRename(fileDir,movieName,startTime):
    try:
        rename('./'+fileDir+'\\'+movieName+'./'+fileDir+"\\"+startTime+'.mp4')
    except OSError:
        print ('파일 이미 존재')


userNumber = 1
fileDir='user'+str(userNumber)
# 폴더생성
createFolder('./'+fileDir)

s3 = s3_connection()


startTime=datetime.today().strftime("%Y%m%d%H%M%S")

# 로컬 filename
filename = fileDir+'\\'+startTime+'.mp4'

# filename: 로컬에 저장된 경로+동영상 (첫번째 arg)
# fileDir+'/'+startTime+'.mp4' : bucket 저장 경로 (세번째 arg)
response=s3.upload_file(filename,BUCKET_NAME,fileDir+'/'+startTime+'.mp4',ExtraArgs={'ContentType': 'video/mp4', 'ACL': 'public-read'})
print(response)


