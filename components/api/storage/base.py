"""Base storage interface for Wegwijs in Regels."""

from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Optional, Union


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def upload_file(self, file_path: str, content: Union[bytes, BinaryIO]) -> str:
        """Upload a file to storage.

        Args:
            file_path: The path where the file should be stored
            content: The file content as bytes or a file-like object

        Returns:
            str: The URL or identifier of the uploaded file
        """
        pass

    @abstractmethod
    def download_file(self, file_path: str) -> bytes:
        """Download a file from storage.

        Args:
            file_path: The path of the file to download

        Returns:
            bytes: The file content
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> None:
        """Delete a file from storage.

        Args:
            file_path: The path of the file to delete
        """
        pass

    @abstractmethod
    def list_files(self, prefix: Optional[str] = None) -> list[str]:
        """List files in storage.

        Args:
            prefix: Optional prefix to filter files

        Returns:
            list[str]: List of file paths
        """
        pass

    @abstractmethod
    def get_file_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for accessing a file.

        Args:
            file_path: The path of the file
            expires_in: Optional expiration time in seconds for the URL

        Returns:
            str: The URL for accessing the file
        """
        pass

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """Check if a file exists in storage.

        Args:
            file_path: The path of the file to check

        Returns:
            bool: True if the file exists, False otherwise
        """
        pass
