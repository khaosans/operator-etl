"""AWS / Azure object-store adapter unit tests (no live cloud)."""

from __future__ import annotations

from operator_etl.config import Settings
from operator_etl.extract.resolve_store import resolve_object_store


class _FakeBody:
    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data


class _FakeS3:
    def __init__(self, objects: dict[str, bytes]):
        self.objects = objects

    def get_paginator(self, _name: str):
        client = self

        class Paginator:
            def paginate(self, Bucket, Prefix=""):  # noqa: N803
                contents = [{"Key": k} for k in client.objects if k.startswith(Prefix)]
                yield {"Contents": contents}

        return Paginator()

    def get_object(self, Bucket, Key):  # noqa: N803
        return {"Body": _FakeBody(self.objects[Key])}


class _FakeBlob:
    def __init__(self, name: str):
        self.name = name


class _FakeContainer:
    def __init__(self, objects: dict[str, bytes]):
        self.objects = objects

    def list_blobs(self, name_starts_with=None):
        for name in self.objects:
            if name_starts_with and not name.startswith(name_starts_with):
                continue
            yield _FakeBlob(name)

    def download_blob(self, key: str):
        data = self.objects[key]

        class Downloader:
            def readall(self_inner) -> bytes:
                return data

        return Downloader()


def test_s3_inbox_uri_settings() -> None:
    s = Settings(inbox_uri="s3://my-bucket/incoming/")
    assert s.resolved_s3_bucket == "my-bucket"
    assert s.resolved_inbox_prefix == "incoming/"


def test_azure_inbox_uri_settings() -> None:
    s = Settings(inbox_uri="az://acct/inbox/incoming")
    assert s.resolved_azure_account == "acct"
    assert s.resolved_azure_container == "inbox"
    assert s.resolved_inbox_prefix == "incoming"


def test_s3_object_store_with_fake_client() -> None:
    from operator_etl_aws.extract.s3 import S3ObjectStore

    csv_body = b"comment_id,agency\n1,EPA\n"
    store = S3ObjectStore(
        "bucket",
        Settings(aws_region="us-east-1"),
        client=_FakeS3({"incoming/a.csv": csv_body, "incoming/x.txt": b"no"}),
    )
    assert store.list_csv_keys("incoming/") == ["incoming/a.csv"]
    assert b"EPA" in store.download_bytes("incoming/a.csv")


def test_azure_object_store_with_fake_client() -> None:
    from operator_etl_azure.extract.blob import AzureBlobObjectStore

    csv_body = b"comment_id,agency\n2,FCC\n"
    store = AzureBlobObjectStore(
        "inbox",
        Settings(azure_storage_account="acct"),
        container_client=_FakeContainer({"incoming/b.csv": csv_body}),
    )
    assert store.list_csv_keys("incoming/") == ["incoming/b.csv"]
    assert b"FCC" in store.download_bytes("incoming/b.csv")


def test_resolve_object_store_s3(monkeypatch) -> None:
    from operator_etl_aws.extract import s3 as s3_mod

    class Capturing(s3_mod.S3ObjectStore):
        def __init__(self, bucket, settings=None, **kwargs):
            super().__init__(bucket, settings, client=_FakeS3({}))

    monkeypatch.setattr(s3_mod, "S3ObjectStore", Capturing)
    settings = Settings(object_store_backend="s3", s3_inbox_bucket="b1")
    store = resolve_object_store(settings)
    assert store.bucket == "b1"


def test_resolve_object_store_azure(monkeypatch) -> None:
    from operator_etl_azure.extract import blob as blob_mod

    class Capturing(blob_mod.AzureBlobObjectStore):
        def __init__(self, container, settings=None, **kwargs):
            super().__init__(container, settings, container_client=_FakeContainer({}))

    monkeypatch.setattr(blob_mod, "AzureBlobObjectStore", Capturing)
    settings = Settings(
        object_store_backend="azure",
        azure_storage_account="acct",
        azure_inbox_container="inbox",
    )
    store = resolve_object_store(settings)
    assert store.container == "inbox"
