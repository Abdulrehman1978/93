"""Response privacy controls for public, token-bearing endpoints."""

from fastapi import Response


def apply_public_privacy_headers(response: Response) -> None:
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Referrer-Policy"] = "no-referrer"
