import json
import boto3
from botocore.client import Config

"""
    Boto3 Doc : https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
    Boto3 S3 Doc : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
"""

class AwsBucketApi:

    def __init__(self, bucket_name = None):
        """
            Creating instance constructor method.
            bucket_name         : AWS Bucket name. If sets as None, bucket name will be pulled from settings file.
            self.bucket_name    : AWS Bucket name for using other functions
            self.bucket         : Boto3 S3 client object for using other functions.
        """
        settings = self.get_settings()
        self.bucket_name = bucket_name or settings.get("bucket_name")
        self.bucket  = boto3.client("s3", 
            aws_access_key_id = settings.get("user_access_id"),
            aws_secret_access_key = settings.get("user_secret"),
            region_name = settings.get("bucket_region"),
            config = Config(signature_version='s3v4', s3 = {"addressing_style" : "path"})
        )

    def get_settings(self):
        """
            Read settings file. 

            Return : dict -> Look at the RETURN-0 on bottom.
        """
        with open("settings.json") as f:
            return json.load(f)

    def generate_presigned_url(self, filename, expires = 3600):
        """
            Create pre-signed url for file download.
            filename    : AWS Bucket object full path name. Exp : "img/example.jpg"
            expires     : Expiration time for created url in seconds.

            Return : str -> "<pre-signed url>"
        """
        return self.bucket.generate_presigned_url(
            ClientMethod = "get_object",
            ExpiresIn = expires,
            Params = {
                "Bucket" : self.bucket_name,
                "Key" : filename
            }
        )

    def generate_presigned_post_fields(self, content_type = None, path_prefix = "", expires = 3600):
        """
            Create pre-signed action link for uploading file to AWS Bucket.
            content_type    : File content mime type. Exp : "image/jpg"
            path_prefix     : Path name or file prefix. Exp : "img/"
            expires         : Expiration time for created url in seconds.

            Return : dict -> Look at the RETURN-1 on bottom.
        """
        if content_type:
            return self.bucket.generate_presigned_post(
                self.bucket_name,
                path_prefix + "${filename}",
                ExpiresIn = expires,
                Conditions = [
                    ["starts-with", "$Content-Type", ""]
                ],
                Fields = {
                    "Content-Type" : content_type
                }
            )
        else:
            return self.bucket.generate_presigned_post(
                self.bucket_name,
                path_prefix + "${filename}",
                ExpiresIn = expires,
            )

    def get_files(self, path_prefix = ""):
        """
            Get filenames and pre-signed urls of bucket object in given path.
            path_prefix : Path name or file prefix. Exp : "img/"
            
            .list_object() return RETURN-2 (look at the bottom)

            Return  : list -> [
                {"url": "<pre-signed url>", "filename" : "<filename of object>"},...
            ]
        """
        object_list = self.bucket.list_objects(
            Bucket = self.bucket_name,
            Prefix = path_prefix
        )

        if "Contents" not in object_list:
            return []

        return [{"url": self.generate_presigned_url(file.get("Key")), "filename" : file.get("Key")} \
            for file in object_list.get("Contents")]

    def delete_file(self, filename):
        """
            Delete object from AWS Bucket with given filename.
            filename    : AWS Bucket object full path name. Exp : "img/example.jpg"

            Return  : bool -> True or False
        """
        response = self.bucket.delete_object(
            Bucket = self.bucket_name,
            Key = filename
        )
        return response.get("DeleteMarker")

    """
    RETURN-0:
        Example settings file:
        {
            "user_access_id" : "",
            "user_secret" : "",
            "bucket_name" : "",
            "bucket_region" : "us-east-2"
        }

    RETURN-1 : 
        Return result for presigned post fields.
        Referance : https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.generate_presigned_post

        {
            "fields": {
                "Content-Type": "image/jpg",
                "key": "pics/${filename}",
                "policy": "eyJleHBpcmF0aW9uIjogIjIwMjItMDEtMTFUMjE6NDU6MTZaIiwgImNvbmRpdGlvbnMiOiBbWyJzdGFydHMtd2l0aCIsICIkQ29udGVudC1UeXBlIiwgIiJdLCB7ImJ1Y2tldCI6ICJhcmVucGktdGVzdCJ9LCBbInN0YXJ0cy13aXRoIiwgIiRrZXkiLCAicGljcy8iXSwgeyJ4LWFtei1hbGdvcml0aG0iOiAiQVdTNC1ITUFDLVNIQTI1NiJ9LCB7IngtYW16LWNyZWRlbnRpYWwiOiAiQUtJQVJNV0VMQlpaNlNSUDNKR0gvMjAyMjAxMTEvdXMtZWFzdC0yL3MzL2F3czRfcmVxdWVzdCJ9LCB7IngtYW16LWRhdGUiOiAiMjAyMjAxMTFUMjA0NTE2WiJ9XX0=",
                "x-amz-algorithm": "AWS4-HMAC-SHA256",
                "x-amz-credential": "AKIARMWELBZZ6SRP3JGH/20220111/us-east-2/s3/aws4_request",
                "x-amz-date": "20220111T204516Z",
                "x-amz-signature": "d74f8ee191ea5d6f155af9a49def82adbeb055e92edb911a7dc5b44207d36bdd"
            },
            "url": "https://s3.us-east-2.amazonaws.com/presigned-test"
        }

    RETURN-2 : 
        Return result for .list_objects()
        {
            "Contents": [
                {
                    "ETag": "\"38cca22decbde960a23a9220717f9d6f\"",
                    "Key": "pics/test.jpg",
                    "LastModified": "2022-01-11 19:41:09+00:00",
                    "Owner": {
                        "ID": "cc3ed6bf853acf17c047078068f5dc9af45df2aaebdf8ce048a79a74e183ff1d"
                    },
                    "Size": 54320,
                    "StorageClass": "STANDARD"
                }
            ],
            "EncodingType": "url",
            "IsTruncated": false,
            "Marker": "",
            "MaxKeys": 1000,
            "Name": "presigned-test",
            "Prefix": "pics",
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-type": "application/xml",
                    "date": "Tue, 11 Jan 2022 20:45:17 GMT",
                    "server": "AmazonS3",
                    "transfer-encoding": "chunked",
                    "x-amz-bucket-region": "us-east-2",
                    "x-amz-id-2": "lG6LHbG4fieu7ON8SlcKdQnmSCgVR3N29HP5cZk/Ltwt/RHqIeuI8ICfLmAmLhuKSi4q7jMWsLE=",
                    "x-amz-request-id": "AV9TWPN2K6XAPAX4"
                },
                "HTTPStatusCode": 200,
                "HostId": "lG6LHbG4fieu7ON8SlcKdQnmSCgVR3N29HP5cZk/Ltwt/RHqIeuI8ICfLmAmLhuKSi4q7jMWsLE=",
                "RequestId": "AV9TWPN2K6XAPAX4",
                "RetryAttempts": 0
            }
        }
    
    """