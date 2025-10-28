"""Local file system storage implementation for Wegwijs in Regels."""

import os
import shutil
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urljoin

from .base import StorageBackend


class LocalStorage(StorageBackend):
    """Local file system storage implementation."""

    def __init__(self, base_path: str):
        """Initialize local storage.

        Args:
            base_path: Base path for storing files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, file_path: str) -> Path:
        """Get the full path for a file.

        Args:
            file_path: The relative file path

        Returns:
            Path: The full file path
        """
        return self.base_path / file_path

    def upload_file(self, file_path: str, content: Union[bytes, BinaryIO]) -> str:
        """Upload a file to local storage.

        Args:
            file_path: The path where the file should be stored
            content: The file content as bytes or a file-like object

        Returns:
            str: The URL of the uploaded file
        """
        full_path = self._get_full_path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(content, bytes):
            full_path.write_bytes(content)
        else:
            with full_path.open("wb") as f:
                shutil.copyfileobj(content, f)

        return str(full_path)

    def download_file(self, file_path: str) -> bytes:
        """Download a file from local storage.

        Args:
            file_path: The path of the file to download

        Returns:
            bytes: The file content
        """
        full_path = self._get_full_path(file_path)
        return full_path.read_bytes()

    def delete_file(self, file_path: str) -> None:
        """Delete a file from local storage.

        Args:
            file_path: The path of the file to delete
        """
        full_path = self._get_full_path(file_path)
        full_path.unlink(missing_ok=True)

    def list_files(self, prefix: Optional[str] = None) -> list[str]:
        """List files in local storage.

        Args:
            prefix: Optional prefix to filter files

        Returns:
            list[str]: List of file paths
        """
        if prefix:
            base = self._get_full_path(prefix)
        else:
            base = self.base_path

        files = []
        for path in base.rglob("*"):
            if path.is_file():
                files.append(str(path.relative_to(self.base_path)))

        return files

    def get_file_url(self, file_path: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for accessing a file in local storage.

        Args:
            file_path: The path of the file
            expires_in: Optional expiration time in seconds for the URL (ignored for local storage)

        Returns:
            str: The file path
        """
        return str(self._get_full_path(file_path))

    def exists(self, file_path: str) -> bool:
        """Check if a file exists in local storage.

        Args:
            file_path: The path of the file to check

        Returns:
            bool: True if the file exists, False otherwise
        """
        return self._get_full_path(file_path).exists()
