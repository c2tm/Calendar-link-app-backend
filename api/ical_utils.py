import base64
import re
import uuid
import json
from urllib.parse import unquote

DATA_URI_PREFIX = "data:text/calendar"

def normalize_crlf(s: str) -> str:
    # rfc 5545 wants CRLF line endings
    s = re.sub(r"\r?\n", "\r\n", s.strip())
    if not s.endswith("\r\n"):
        s += "\r\n"
    return s

def ics_from_data_uri(data_uri: str) -> str:
    """
    supports:
      data:text/calendar;charset=utf-8,<percent-encoded-ics>
      data:text/calendar;charset=utf-8;base64,<base64-ics>
    """
    if not data_uri.lower().startswith(DATA_URI_PREFIX):
        raise ValueError("not an ical data uri")

    header, payload = data_uri.split(",", 1)
    is_base64 = ";base64" in header.lower()

    if is_base64:
        ics_bytes = base64.b64decode(payload)
        ics_text = ics_bytes.decode("utf-8", "strict")
    else:
        ics_text = unquote(payload)

    return normalize_crlf(ics_text)

def looks_like_ics(s: str) -> bool:
    u = s.upper()
    return "BEGIN:VCALENDAR" in u and "END:VCALENDAR" in u

def _extract_first_json_object(text: str):
    dec = json.JSONDecoder()
    i = text.find("{")
    while i != -1:
        try:
            obj, end = dec.raw_decode(text[i:])
            return obj
        except json.JSONDecodeError:
            i = text.find("{", i + 1)
    return None