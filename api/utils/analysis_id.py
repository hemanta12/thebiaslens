import base64
import hashlib

from .normalize import canonicalize_url


def make_analysis_id(url: str) -> str:
    """Create a deterministic short analysis id from a URL.

    Steps:
    - Canonicalize the input URL (lower-case host, strip fragments, remove UTM/trackers)
    - Compute SHA-256 of the canonical URL
    - Base32-encode the digest, drop padding, lower-case, and take first 10 chars

    Args:
        url: The input URL from the user

    Returns:
        A stable, URL-safe, 10-character slug identifier.
    """
    canon = canonicalize_url(url)
    digest = hashlib.sha256(canon.encode("utf-8")).digest()
    b32 = base64.b32encode(digest).decode("ascii").rstrip("=").lower()
    return b32[:10]
