import base64
import hashlib

from .normalize import canonicalize_url


def make_analysis_id(url: str) -> str:
    # Create deterministic ID from URL:
    # - Canonicalize URL
    # - SHA-256 hash
    # - Base32 encode (truncated to 10 chars)
    canon = canonicalize_url(url)
    digest = hashlib.sha256(canon.encode("utf-8")).digest()
    b32 = base64.b32encode(digest).decode("ascii").rstrip("=").lower()
    return b32[:10]
