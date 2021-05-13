# 버킷에 들어있는 object 출력
import boto3

AWS_ACCESS_KEY=""
AWS_SECRET_KEY=""
BUCKET_NAME=""

client = boto3.client('s3',aws_access_key_id= AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
response = client.list_objects(Bucket=BUCKET_NAME)

for content in response['Contents']:
    obj_dict = client.get_object(Bucket=BUCKET_NAME, Key=content['Key'])
    print(content['Key'], obj_dict['LastModified'])
