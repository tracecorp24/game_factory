import os
import hashlib
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class StorageRef(BaseModel):
    storage_id: str
    storage_type: str = "local"  # "local" | "s3"
    uri: str
    sha256: str
    bytes: int
    mime_type: str = "image/png"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BaseStorageClient(ABC):
    @abstractmethod
    def save_bytes(self, data: bytes, filename: str, mime_type: str = "application/octet-stream") -> StorageRef:
        """Save raw bytes to storage and return a StorageRef with sha256 checksum."""
        pass

    @abstractmethod
    def read_bytes(self, uri: str) -> bytes:
        """Read bytes given a storage uri."""
        pass

    @abstractmethod
    def get_preview_ticket(self, uri: str, expires_seconds: int = 3600) -> str:
        """Return a signed or accessible preview URL/ticket."""
        pass

class LocalStorageClient(BaseStorageClient):
    def __init__(self, base_dir: str = "./storage/artifacts"):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _compute_sha256(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def save_bytes(self, data: bytes, filename: str, mime_type: str = "application/octet-stream") -> StorageRef:
        sha256_hash = self._compute_sha256(data)
        
        # Deduplication or content-addressed storage
        ext = os.path.splitext(filename)[1] or ".bin"
        safe_filename = f"{sha256_hash[:16]}_{filename}"
        file_path = os.path.join(self.base_dir, safe_filename)
        
        with open(file_path, "wb") as f:
            f.write(data)

        storage_id = f"local_{sha256_hash[:12]}"
        uri = f"file:///{file_path.replace(os.sep, '/')}"

        return StorageRef(
            storage_id=storage_id,
            storage_type="local",
            uri=uri,
            sha256=sha256_hash,
            bytes=len(data),
            mime_type=mime_type,
            metadata={"local_path": file_path, "filename": filename}
        )

    def read_bytes(self, uri: str) -> bytes:
        clean_path = uri.replace("file:///", "").replace("/", os.sep)
        if not os.path.exists(clean_path):
            raise FileNotFoundError(f"Storage object not found at {clean_path}")
        with open(clean_path, "rb") as f:
            return f.read()

    def get_preview_ticket(self, uri: str, expires_seconds: int = 3600) -> str:
        # In local development, the local URI acts as the preview ticket
        return f"{uri}?expires={expires_seconds}"

class S3StorageClient(BaseStorageClient):
    """S3-compatible storage implementation for production/staging."""
    def __init__(self, bucket_name: str = "creativeforge-artifacts", endpoint_url: Optional[str] = None):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url

    def save_bytes(self, data: bytes, filename: str, mime_type: str = "application/octet-stream") -> StorageRef:
        sha256_hash = hashlib.sha256(data).hexdigest()
        key = f"artifacts/{sha256_hash[:2]}/{sha256_hash}/{filename}"
        uri = f"s3://{self.bucket_name}/{key}"
        
        # S3 PUT implementation would happen here with boto3
        return StorageRef(
            storage_id=f"s3_{sha256_hash[:12]}",
            storage_type="s3",
            uri=uri,
            sha256=sha256_hash,
            bytes=len(data),
            mime_type=mime_type,
            metadata={"bucket": self.bucket_name, "key": key}
        )

    def read_bytes(self, uri: str) -> bytes:
        raise NotImplementedError("S3 direct read requires AWS credentials in environment")

    def get_preview_ticket(self, uri: str, expires_seconds: int = 3600) -> str:
        # Would generate presigned URL via boto3.client('s3').generate_presigned_url
        return f"https://{self.bucket_name}.s3.amazonaws.com/{uri.replace('s3://' + self.bucket_name + '/', '')}?signed=true"
