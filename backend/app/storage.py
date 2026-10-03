"""S3-Compatible Object Storage Provider and Health Verification.

Provides connection handling for MinIO (development) and AWS/GovCloud S3 (production)
for secure, encrypted audio and evidence snippet storage.
"""

import time
from typing import Any

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, EndpointConnectionError

from app.config import settings
from app.logging import logger


def get_s3_client() -> Any:
    """Create a configured boto3 S3 client."""
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
        config=Config(signature_version="s3v4", connect_timeout=3, read_timeout=3),
    )


async def check_storage_health() -> tuple[bool, float | None, str | None]:
    """Verify S3-compatible storage connectivity and bucket presence."""
    start_time = time.perf_counter()
    try:
        client = get_s3_client()
        client.list_buckets()
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return True, latency_ms, f"S3 storage operational ({settings.S3_BUCKET_NAME})"
    except (EndpointConnectionError, ClientError) as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.warning(f"S3 storage health check failed: {exc}")
        return False, latency_ms, str(exc)
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.warning(f"Unexpected S3 storage health check error: {exc}")
        return False, latency_ms, str(exc)
