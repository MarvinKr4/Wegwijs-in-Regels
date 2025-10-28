"""Azure Blob Storage implementation for Wegwijs in Regels."""

import os
from datetime import datetime, timedelta
from typing import Optional, Union
from urllib.parse import urlparse

from azure.storage.blob import (
    BlobSasPermissions,
    BlobServiceClient,
    ContentSettings,
    generate_blob_sas,
)

from .base import StorageBackend


class AzureBlobStorage(StorageBackend):
    """Azure Blob Storage implementation."""

    def __init__(self, connection_string: str, container_name: str):
        """Initialize Azure Blob Storage client.

        Args:
            connection_string: Azure Storage connection string
            container_name: Name of the container to use
        """
        self.client = BlobServiceClient.from_connection_string(connection_string)
        self.container_name = container_name
        self.container_client = self.client.get_container_client(container_name)

    def upload_file(self, file_path: str, content: Union[bytes, BinaryIO]) -> str:
        """Upload a file to Azure Blob Storage.

        Args:
            file_path: The path where the file should be stored
            content: The file content as bytes or a file-like object

        Returns:
            str: The URL of the uploaded blob
        """
        blob_client = self.container_client.get_blob_client(file_path)

        if isinstance(content, bytes):
            blob_client.upload_blob(content, overwrite=True)
        else:
            blob_client.upload_blob(content, overwrite=True)

        return blob_client.url

    def download_file(self, file_path: str) -> bytes:
        """Download a file from Azure Blob Storage.

        Args:
            file_path: The path of the file to download

        Returns:
            bytes: The file content
        """
        blob_client = self.container_client.get_blob_client(file_path)
        return blob_client.download_blob().readall()

    def delete_file(self, file_path: str) -> None:
        """Delete a file from Azure Blob Storage.

        Args:
            file_path: The path of the file to delete
        """
        blob_client = self.container_client.get_blob_client(file_path)
        blob_client.delete_blob()

    def list_files(self, prefix: Optional[str] = None) -> list[str]:
        """List files in Azure Blob Storage.

        Args:
            prefix: Optional prefix to filter files

        Returns:
            list[str]: List of file paths
        """
        blobs = self.container_client.list_blobs(name_starts_with=prefix)
        return [blob.name for blob in blobs]

    def get_file_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for accessing a file in Azure Blob Storage.

        Args:
            file_path: The path of the file
            expires_in: Optional expiration time in seconds for the URL

        Returns:
            str: The URL for accessing the file
        """
        blob_client = self.container_client.get_blob_client(file_path)

        if expires_in is None:
            return blob_client.url

        # Generate SAS token
        sas_token = generate_blob_sas(
            account_name=self.client.account_name,
            container_name=self.container_name,
            blob_name=file_path,
            account_key=self.client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(seconds=expires_in),
        )

        return f"{blob_client.url}?{sas_token}"

    def exists(self, file_path: str) -> bool:
        """Check if a file exists in Azure Blob Storage.

        Args:
            file_path: The path of the file to check

        Returns:
            bool: True if the file exists, False otherwise
        """
        blob_client = self.container_client.get_blob_client(file_path)
        return blob_client.exists()
