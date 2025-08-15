from azure.storage.blob import BlobServiceClient

from .config import configs

blob_service_client = BlobServiceClient.from_connection_string(
    configs.AZURE_STORAGE_CONNECTION_STRING
)
