"""S3 storage implementation for Wegwijs in Regels."""

import os
from typing import Optional, Union
from urllib.parse import urlparse

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from .base import StorageBackend


class S3Storage(StorageBackend):
    """S3 storage implementation."""

    def __init__(
        self,
        endpoint_url: str,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
        region: str = "eu-west-1",
    ):
        """Initialize S3 client.

        Args:
            endpoint_url: S3 endpoint URL
            access_key_id: AWS access key ID
            secret_access_key: AWS secret access key
            bucket_name: Name of the S3 bucket
            region: AWS region (default: eu-west-1)
        """
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region,
            config=Config(signature_version="s3v4"),
        )
        self.bucket_name = bucket_name

    def upload_file(self, file_path: str, content: Union[bytes, BinaryIO]) -> str:
        """Upload a file to S3.

        Args:
            file_path: The path where the file should be stored
            content: The file content as bytes or a file-like object

        Returns:
            str: The URL of the uploaded object
        """
        if isinstance(content, bytes):
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_path,
                Body=content,
            )
        else:
            self.s3_client.upload_fileobj(
                content,
                self.bucket_name,
                file_path,
            )

        return self.get_file_url(file_path)

    def download_file(self, file_path: str) -> bytes:
        """Download a file from S3.

        Args:
            file_path: The path of the file to download

        Returns:
            bytes: The file content
        """
        response = self.s3_client.get_object(
            Bucket=self.bucket_name,
            Key=file_path,
        )
        return response["Body"].read()

    def delete_file(self, file_path: str) -> None:
        """Delete a file from S3.

        Args:
            file_path: The path of the file to delete
        """
        self.s3_client.delete_object(
            Bucket=self.bucket_name,
            Key=file_path,
        )

    def list_files(self, prefix: Optional[str] = None) -> list[str]:
        """List files in S3.

        Args:
            prefix: Optional prefix to filter files

        Returns:
            list[str]: List of file paths
        """
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix,
        )
        return [obj["Key"] for obj in response.get("Contents", [])]

    def get_file_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for accessing a file in S3.

        Args:
            file_path: The path of the file
            expires_in: Optional expiration time in seconds for the URL

        Returns:
            str: The URL for accessing the file
        """
        if expires_in is None:
            return f"{self.s3_client.meta.endpoint_url}/{self.bucket_name}/{file_path}"

        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": file_path,
            },
            ExpiresIn=expires_in,
        )

    def exists(self, file_path: str) -> bool:
        """Check if a file exists in S3.

        Args:
            file_path: The path of the file to check

        Returns:
            bool: True if the file exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_path,
            )
            return True
        except ClientError:
            return False
