from sys import argv
from os import getenv
from os.path import join

import boto3
from streamlit import secrets


BUCKET_NAME = secrets["BUCKET_NAME"]
REGION_NAME = secrets["REGION"]
ENPOINT_URL = f"https://s3.{secrets['REGION']}.scw.cloud"
s3_client = boto3.client(
    "s3",
    region_name=REGION_NAME,
    endpoint_url=ENPOINT_URL,
    aws_access_key_id=secrets["SCW_ACCESS_KEY"],
    aws_secret_access_key=secrets["SCW_SECRET_KEY"],
)

def upload_file_to_bucket(local_src_path: str, remote_dest_path: str) -> str:
    """
    ### Description:
    Uploads a file to the bucket.
    Sets it as public to make accessible.
    Returns an url to access it.
    """
    s3_client.upload_file(local_src_path, BUCKET_NAME, remote_dest_path)
    s3_client.put_object_acl(ACL="public-read", Bucket=BUCKET_NAME, Key=remote_dest_path)
    return f"https://{BUCKET_NAME}.s3.{REGION_NAME}.scw.cloud/{remote_dest_path}" #join(ENPOINT_URL, remote_dest_path)
# https://domnique-videos.s3.fr-par.scw.cloud/requirements.txt

if __name__ == "__main__":
    if len(argv) < 3:
        print("Please provide a local_src_path and remote_dest_path as arguments.")
        exit(1)
    print(upload_file_to_bucket(argv[1], argv[2]))