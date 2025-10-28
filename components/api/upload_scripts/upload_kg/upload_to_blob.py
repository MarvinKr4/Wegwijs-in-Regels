import logging
import os
from pathlib import Path

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient

KG_CONTAINER_NAME = "knowledge-graphs"  # TODO:  create env and put in helm values

logger = logging.getLogger(__name__)


def upload_ttl_file(container_name: str, file_path: str, blob_name: str):
    # Get the connection string from environment variable
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    logger.info("Connection string: ", connection_string)
    if not connection_string:
        raise ValueError(
            "AZURE_STORAGE_CONNECTION_STRING environment variable is not set"
        )

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create the container if it does not exist
    try:
        container_client = blob_service_client.create_container(container_name)
        logger.info(f"Container '{container_name}' created.")
    except ResourceExistsError:
        container_client = blob_service_client.get_container_client(container_name)
        logger.info(f"Container '{container_name}' already exists.")

    # Get the blob client
    blob_client = container_client.get_blob_client(f"{blob_name}.ttl")

    # Upload the file
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
        logger.info(
            f"File '{file_path}' uploaded to container '{container_name}' as blob {blob_name}.ttl."
        )


# if __name__ == "__main__":
#     file_path = Path("Juridisch_Analyse_Schema.ttl")
#     blob_name = "JAS"
#     upload_ttl_file(KG_CONTAINER_NAME, file_path, blob_name)
