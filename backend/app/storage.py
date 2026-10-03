"""S3-Compatible Object Storage Provider and Health Verification.

Provides connection handling for MinIO (development) and AWS/GovCloud S3 (production)
for secure, encrypted audio and evidence snippet storage.
"""

import asyncio
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


def ensure_bucket_exists() -> bool:
    """Provision S3_BUCKET_NAME deterministically if missing during local bootstrap."""
    try:
        client = get_s3_client()
        client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        logger.info(f"S3 bucket '{settings.S3_BUCKET_NAME}' is present and verified.")
        return True
    except ClientError as exc:
        error_code = str(exc.response.get("Error", {}).get("Code", ""))
        if error_code in ("404", "NoSuchBucket"):
            try:
                client.create_bucket(Bucket=settings.S3_BUCKET_NAME)
                logger.info(f"Provisioned missing S3 bucket: '{settings.S3_BUCKET_NAME}'")
                return True
            except Exception as create_exc:
                logger.error(
                    f"Failed to provision S3 bucket '{settings.S3_BUCKET_NAME}': {create_exc}"
                )
                return False
        logger.error(f"S3 bucket check failed for '{settings.S3_BUCKET_NAME}': {exc}")
        return False
    except Exception as exc:
        logger.error(f"Unexpected error ensuring S3 bucket '{settings.S3_BUCKET_NAME}': {exc}")
        return False


def _sync_check_storage() -> tuple[bool, str]:
    """Execute synchronous S3 check verifying the exact configured bucket."""
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        return True, "Storage operational (configured bucket verified)"
    except ClientError as exc:
        error_code = str(exc.response.get("Error", {}).get("Code", ""))
        logger.warning(
            f"S3 bucket check failed for '{settings.S3_BUCKET_NAME}' (Code: {error_code}): {exc}"
        )
        if error_code in ("404", "NoSuchBucket"):
            return False, "Configured storage bucket not found"
        return False, "Storage service access denied or unavailable"
    except EndpointConnectionError as exc:
        logger.warning(f"S3 endpoint connection failed for {settings.S3_ENDPOINT_URL}: {exc}")
        return False, "Storage service unreachable"
    except Exception as exc:
        logger.warning(f"Unexpected S3 storage health check error: {exc}")
        return False, "Storage service unavailable"


async def check_storage_health() -> tuple[bool, float | None, str | None]:
    """Verify S3-compatible storage connectivity and exact configured bucket presence.

    Executes synchronous Boto3 network I/O safely outside the async event loop using asyncio.to_thread.
    Returns generic dependency state without leaking internal connection or infrastructure details.
    """
    start_time = time.perf_counter()
    try:
        ok, message = await asyncio.to_thread(_sync_check_storage)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return ok, latency_ms, message
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.warning(f"Storage health check execution failure: {exc}")
        return False, latency_ms, "Storage service unavailable"
