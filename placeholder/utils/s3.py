# -*- coding: utf-8 -*-
import uuid

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings


class S3Service:
    def _get_s3_client(self):
        my_config = Config(
            region_name="ap-southeast-2", signature_version="s3v4", retries={"max_attempts": 10, "mode": "standard"}
        )
        return boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=my_config,
        )

    def create_presigned_url(
        self, object_name, content_type, bucket_name=settings.AWS_S3_MEDIA_BUCKET_NAME, expiration=10
    ):
        s3_client = self._get_s3_client()

        try:
            fields = {"Content-Type": content_type, "success_action_status": "201"}
            conditions = [
                {"success_action_status": "201"},
                ["starts-with", "$Content-Type", "image/"],
                ["content-length-range", 1024, 10485760],
            ]
            response = s3_client.generate_presigned_post(
                bucket_name, object_name, Fields=fields, Conditions=conditions, ExpiresIn=expiration
            )
        except ClientError:
            return None

        return response

    def create_multi_presigned_url(self, filepath, filetype_list: list):
        context = {"result": []}
        for type_ in filetype_list:
            ext = type_parts[1] if len(type_parts := type_.split("/")) == 2 else "jpg"
            path = f"{filepath}/{uuid.uuid4()}.{ext}"
            response = self.create_presigned_url(path, type_)
            context["result"].append(response)
        return context
