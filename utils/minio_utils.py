import minio
from minio import Minio
import json
from config.minio_config import minio_config

minio_client = Minio(
    endpoint=minio_config.endpoint,
    access_key=minio_config.access_key,
    secret_key=minio_config.secret_key,
    secure=False,
)

if not minio_client.bucket_exists("b123"):
    minio_client.make_bucket("b123")
policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::b123/*",
        }
    ]
}
minio_client.set_bucket_policy("b123", json.dumps(policy))
def get_minio_client():
    return minio_client

if __name__ == '__main__':
    minio_client = get_minio_client()
    print(minio_client.bucket_exists("b123"))