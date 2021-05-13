# 버킷에 동영상 업로드 + 객체 URL 퍼블릭 설정
import boto3

AWS_ACCESS_KEY=""
AWS_SECRET_KEY=""
BUCKET_NAME=""

def s3_upload(filename, video_path):
    s3 = boto3.client('s3',aws_access_key_id= AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    response=s3.upload_file(filename,BUCKET_NAME,video_path+filename,ExtraArgs={'ContentType': 'video/mp4', 'ACL': 'public-read'})
    return response

result = s3_upload('filename','video_path')
print(result)