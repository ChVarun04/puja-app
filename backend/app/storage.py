import re
import uuid
import httpx
from .config import settings

BASE = f"{settings.SUPABASE_URL}/storage/v1"

# New-style keys (sb_secret_...) are not JWTs, so they go only in the apikey header.
if settings.SUPABASE_SERVICE_KEY.startswith("sb_"):
    HEADERS = {"apikey": settings.SUPABASE_SERVICE_KEY}
else:
    HEADERS = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_KEY,
    }


def upload_file(data: bytes, filename: str, content_type: str) -> str:
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", filename or "file")
    path = f"{uuid.uuid4().hex}_{safe_name}"
    r = httpx.post(
        f"{BASE}/object/{settings.SUPABASE_BUCKET}/{path}",
        headers={**HEADERS, "Content-Type": content_type},
        content=data,
        timeout=120,
    )
    if r.status_code >= 400:
        raise RuntimeError(f"Storage upload failed: {r.status_code} {r.text}")
    return path


def signed_url(path: str, expires: int = 3600) -> str:
    r = httpx.post(
        f"{BASE}/object/sign/{settings.SUPABASE_BUCKET}/{path}",
        headers=HEADERS,
        json={"expiresIn": expires},
        timeout=30,
    )
    if r.status_code >= 400:
        raise RuntimeError(f"Could not sign URL: {r.status_code} {r.text}")
    return f"{BASE}{r.json()['signedURL']}"