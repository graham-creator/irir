from urllib.parse import urlparse, parse_qs


def extract_youtube_id(url: str):
    """Extract a YouTube video id from common URL formats.

    Returns the video id string or None.
    """
    try:
        parsed = urlparse(url)
        netloc = (parsed.netloc or '').lower()
        if 'youtu.be' in netloc:
            return parsed.path.lstrip('/') or None
        if 'youtube' in netloc:
            return parse_qs(parsed.query).get('v', [None])[0]
    except Exception:
        return None
    return None


def sanitize_id(name: str) -> str:
    """Produce a safe short id for UI element ids by keeping alphanumerics and dashes.

    Collapses consecutive separators and strips leading/trailing hyphens for nicer IDs.
    """
    if not name:
        return ''
    import re
    s = re.sub(r"[^a-zA-Z0-9_-]", "-", name)
    # collapse multiple dashes and underscores, then strip leading/trailing dashes/underscores
    s = re.sub(r"[-_]+", "-", s).strip("-_")
    return s.lower()