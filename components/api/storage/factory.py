"""Storage backend factory for Wegwijs in Regels."""

from typing import Any, Dict

from .azure import AzureBlobStorage
from .base import StorageBackend
from .local import LocalStorage
from .s3 import S3Storage


def create_storage_backend(config: Dict[str, Any]) -> StorageBackend:
    """Create a storage backend based on configuration.

    Args:
        config: Storage configuration dictionary

    Returns:
        StorageBackend: The configured storage backend

    Raises:
        ValueError: If the storage backend type is not supported
    """
    backend_type = config.get("backend", "local")

    if backend_type == "azure":
        return AzureBlobStorage(
            connection_string=config["azure"]["connection_string"],
            container_name=config["azure"]["container_name"],
        )
    elif backend_type == "s3":
        return S3Storage(
            endpoint_url=config["s3"]["endpoint_url"],
            access_key_id=config["s3"]["access_key_id"],
            secret_access_key=config["s3"]["secret_access_key"],
            bucket_name=config["s3"]["bucket_name"],
            region=config["s3"].get("region", "eu-west-1"),
        )
    elif backend_type == "local":
        return LocalStorage(
            base_path=config["local"]["base_path"],
        )
    else:
        raise ValueError(f"Unsupported storage backend type: {backend_type}")
