from sys import argv
from os import getenv

import boto3
from streamlit import secrets
from dotenv import load_dotenv
from botocore.client import Config

load_dotenv()

access_key = getenv("SCW_ACCESS_KEY")
secret_key = getenv("SCW_SECRET_KEY")
bucket_name = getenv("BUCKET_NAME")
s3_client = boto3.client(
    "s3",
    region_name=region,
    endpoint_url=f"https://s3.{getenv("REGION")}.scw.cloud",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    # config=Config(signature_version="s3v4"),
)

def upload_file_to_bucket(local_src_path: str, remote_dest_path: str):
    s3_client.upload_file(local_src_path, bucket_name, remote_dest_path)
    public_url = f"https://{bucket_name}.s3.{region}.scw.cloud/{remote_dest_path}"
    print("Public URL:", public_url)
    s3_client.put_object_acl(ACL="public-read", Bucket=bucket_name, Key=remote_dest_path)


if __name__ == "__main__":
    if len(argv) < 3:
        print("Please provide a local_src_path and remote_dest_path as arguments.")
        exit(1)
    upload_file_to_bucket(argv[1], argv[2])