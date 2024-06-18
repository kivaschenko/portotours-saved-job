import boto3
from django.conf import settings


def adjust_time_expires_for_image():
    session = boto3.Session()
    client = session.client('s3',
                            region_name=settings.AWS_S3_REGION_NAME,
                            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    directory_prefix = 'uploads/'

    response = client.list_objects_v2(Bucket=bucket_name, Prefix=directory_prefix)
    if 'Contents' in response:
        for obj in response['Contents']:
            client.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=obj['Key'])
            print(f"Adjusted time expires for image {obj['Key']}")
    else:
        print("No objects found in the specified directory")
    print("All files in the specified directory updated to public-read.")


def adjust_access_dump_files():
    session = boto3.Session()
    client = session.client('s3',
                            region_name=settings.AWS_S3_REGION_NAME,
                            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    directory_prefix = 'backups/'

    response = client.list_objects_v2(Bucket=bucket_name, Prefix=directory_prefix)
    if 'Contents' in response:
        for obj in response['Contents']:
            client.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=obj['Key'])
            print(f"Adjusted time expires for image {obj['Key']}")
    else:
        print("No objects found in the specified directory")
    print("All files in the specified directory updated to public-read.")
