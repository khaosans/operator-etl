"""Azure Blob object-store adapter for inbox CSV extract."""

from __future__ import annotations

from operator_etl.config import Settings, get_settings
from operator_etl.extract.csv import ExtractResult
from operator_etl.extract.object_store import extract_inbox, extract_object


class AzureBlobObjectStore:
    """Azure Blob-backed ObjectStore for Container Apps / Event Grid triggers."""

    def __init__(
        self,
        container: str,
        settings: Settings | None = None,
        *,
        account_name: str | None = None,
        container_client=None,
    ):
        self.container = container
        self.settings = settings or get_settings()
        self.account_name = account_name or self.settings.azure_storage_account
        self._container_client = container_client

    def _client(self):
        if self._container_client is None:
            from azure.identity import DefaultAzureCredential
            from azure.storage.blob import BlobServiceClient

            if not self.account_name:
                raise ValueError("OPERATOR_ETL_AZURE_STORAGE_ACCOUNT required for azure object store")
            account_url = f"https://{self.account_name}.blob.core.windows.net"
            service = BlobServiceClient(account_url, credential=DefaultAzureCredential())
            self._container_client = service.get_container_client(self.container)
        return self._container_client

    def list_csv_keys(self, prefix: str = "") -> list[str]:
        client = self._client()
        keys: list[str] = []
        for blob in client.list_blobs(name_starts_with=prefix or None):
            name = blob.name
            if name.endswith("/") or not name.lower().endswith(".csv"):
                continue
            keys.append(name)
        return keys

    def download_bytes(self, key: str) -> bytes:
        client = self._client()
        return client.download_blob(key).readall()


def extract_azure_inbox(
    container: str,
    prefix: str,
    settings: Settings | None = None,
) -> list[ExtractResult]:
    return extract_inbox(AzureBlobObjectStore(container, settings), prefix)
