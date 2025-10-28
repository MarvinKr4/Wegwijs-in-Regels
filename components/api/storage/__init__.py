"""Storage package for Wegwijs in Regels."""

from .azure import AzureBlobStorage
from .base import StorageBackend
from .factory import create_storage_backend
from .local import LocalStorage
from .s3 import S3Storage

__all__ = [
    "StorageBackend",
    "AzureBlobStorage",
    "S3Storage",
    "LocalStorage",
    "create_storage_backend",
]
